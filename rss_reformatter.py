import requests
import feedparser
import PyRSS2Gen
import datetime
import argparse
import os
from urllib.parse import urlparse, urlunparse
import re
import xml.etree.ElementTree as ET

def load_rss_items_from_file(file_path):
    """
    Load RSS items from an existing RSS feed file.

    Args:
        file_path (str): Path to the RSS feed file.

    Returns:
        list: A list of PyRSS2Gen.RSSItem objects.
    """
    if not os.path.exists(file_path):
        return []

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        items = []
        for item in root.findall(".//item"):
            title_elem = item.find("title")
            link_elem = item.find("link")
            desc_elem = item.find("description")
            guid_elem = item.find("guid")
            pubDate_elem = item.find("pubDate")
            
            # Parse the publication date
            pub_date = None
            if pubDate_elem is not None and pubDate_elem.text:
                try:
                    time_tuple = feedparser._parse_date(pubDate_elem.text)
                    if time_tuple:
                        pub_date = datetime.datetime(*time_tuple[:6], tzinfo=datetime.timezone.utc)
                except:
                    pub_date = datetime.datetime.now(datetime.timezone.utc)
            
            if title_elem is not None and link_elem is not None:
                rss_item = PyRSS2Gen.RSSItem(
                    title=title_elem.text or "No Title",
                    link=link_elem.text or "",
                    description=desc_elem.text if desc_elem is not None else "",
                    guid=PyRSS2Gen.Guid(guid_elem.text if guid_elem is not None else link_elem.text, isPermaLink=False),
                    pubDate=pub_date or datetime.datetime.now(datetime.timezone.utc)
                )
                items.append(rss_item)
        return items
    except ET.ParseError as e:
        print(f"Error loading RSS feed from {file_path}: {e}")
        return []

def extract_image_from_content(content):
    """Extract the first image URL from HTML content."""
    if not content:
        return None
        
    # Look for img tags with src attribute
    img_pattern = re.compile(r'<img[^>]+src=["\'](https?://[^"\']+)["\'][^>]*>')
    match = img_pattern.search(content)
    if match:
        return match.group(1)
    
    # Look for media:content or media:thumbnail tags
    media_pattern = re.compile(r'<media:(?:content|thumbnail)[^>]+url=["\'](https?://[^"\']+)["\'][^>]*>')
    match = media_pattern.search(content)
    if match:
        return match.group(1)
        
    return None

def create_reformatted_rss(original_url, output_file, archive_prefix="https://archive.is/newest/"):
    """
    Fetches, parses, and merges RSS feeds, removing duplicates and truncating to 100 items.

    Args:
        original_url (str): The URL of the original RSS feed to process.
        output_file (str): Path where the new RSS feed should be saved.
        archive_prefix (str): Prefix to prepend to original URLs.
    """
    print(f"Processing feed: {original_url}")
    print(f"Outputting to: {output_file}")

    try:
        # 1. Fetch the new RSS feed
        headers = {'User-Agent': 'RSS Reformatter Bot (Python; GitHub Actions)'}
        response = requests.get(original_url, headers=headers, timeout=20)
        response.raise_for_status()
        feed_data = feedparser.parse(response.content)
        
        # Store the feed image information
        feed_image = None
        if 'image' in feed_data.feed:
            feed_image = PyRSS2Gen.Image(
                url=feed_data.feed.image.get('url', ''),
                title=feed_data.feed.image.get('title', ''),
                link=feed_data.feed.image.get('link', '')
            )

        # 2. Load existing RSS items
        existing_items = load_rss_items_from_file(output_file)

        # 3. Prepare new RSS items
        new_items = []
        for entry in feed_data.entries:
            original_link = entry.get('link')
            if original_link:
                # Clean the link
                parsed_url = urlparse(original_link)
                cleaned_link = urlunparse(parsed_url._replace(query="", fragment=""))

                # Prepend the archive prefix
                new_link = f"{archive_prefix}{cleaned_link}"

                item_title = entry.get('title', 'No Title')
                item_description = entry.get('summary', entry.get('description', 'No Description'))
                
                # Extract media content (header image)
                image_url = None
                
                # Check for media:content
                if hasattr(entry, 'media_content') and entry.media_content:
                    for media in entry.media_content:
                        if 'url' in media:
                            image_url = media['url']
                            break
                
                # Check for media:thumbnail
                if not image_url and hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                    for media in entry.media_thumbnail:
                        if 'url' in media:
                            image_url = media['url']
                            break
                
                # Check for enclosures
                if not image_url and hasattr(entry, 'enclosures') and entry.enclosures:
                    for enclosure in entry.enclosures:
                        if 'url' in enclosure and enclosure.get('type', '').startswith('image/'):
                            image_url = enclosure['url']
                            break
                
                # Try to extract from content
                if not image_url and 'content' in entry and entry.content:
                    for content_item in entry.content:
                        if 'value' in content_item:
                            extracted_img = extract_image_from_content(content_item['value'])
                            if extracted_img:
                                image_url = extracted_img
                                break
                
                # Try to extract from summary if still no image
                if not image_url:
                    image_url = extract_image_from_content(item_description)
                
                # Add image to description if found
                if image_url:
                    item_description = f'<img src="{image_url}" style="max-width:100%; height:auto; display:block; margin-bottom:15px;" />\n{item_description}'
                
                # Get author if available
                author = None
                if 'author' in entry:
                    author = entry.author
                elif 'dc_creator' in entry:
                    author = entry.dc_creator
                
                # Create the RSS item with all available information
                item_kwargs = {
                    "title": item_title,
                    "link": new_link,
                    "description": item_description,
                    "guid": PyRSS2Gen.Guid(entry.get('id', new_link), isPermaLink=False),
                }
                
                # Add publication date if available
                if 'published_parsed' in entry and entry.published_parsed:
                    item_kwargs["pubDate"] = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
                else:
                    item_kwargs["pubDate"] = datetime.datetime.now(datetime.timezone.utc)
                    
                # Add author if available
                if author:
                    item_kwargs["author"] = author
                    
                new_items.append(PyRSS2Gen.RSSItem(**item_kwargs))

        # 4. Merge and remove duplicates
        all_items = {item.guid.guid: item for item in (new_items + existing_items)}.values()

        # 5. Sort by pubDate and truncate to 100 items
        sorted_items = sorted(all_items, key=lambda x: x.pubDate, reverse=True)[:100]

        # 6. Build the new RSS feed with the original feed image
        rss_kwargs = {
            "title": feed_data.feed.get('title', 'Feed'),
            "link": original_url,
            "description": feed_data.feed.get('description', 'Reformatted Feed'),
            "lastBuildDate": datetime.datetime.now(datetime.timezone.utc),
            "items": sorted_items,
        }
        
        # Add the image if one was found
        if feed_image:
            rss_kwargs["image"] = feed_image
            
        # Add language if available
        if 'language' in feed_data.feed:
            rss_kwargs["language"] = feed_data.feed.language
            
        # Add copyright if available
        if 'rights' in feed_data.feed:
            rss_kwargs["copyright"] = feed_data.feed.rights
            
        new_rss_feed = PyRSS2Gen.RSS2(**rss_kwargs)

        # 7. Save the new RSS feed to file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(new_rss_feed.to_xml(encoding="utf-8"))

        print(f"Successfully saved feed to {output_file}")

    except Exception as e:
        print(f"Error processing feed {original_url}: {e}")

def process_feeds_from_file(feed_file, archive_prefix="https://archive.is/newest/"):
    """
    Reads a file containing feed URLs and processes each feed.

    Args:
        feed_file (str): Path to the text file containing feed URLs and output paths.
        archive_prefix (str): Prefix to prepend to original URLs.
    """
    try:
        with open(feed_file, "r") as f:
            for line in f:
                # Skip empty lines or comments
                if not line.strip() or line.startswith("#"):
                    continue
                
                # Parse the line
                parts = line.strip().split()
                if len(parts) < 2:
                    print(f"Invalid line in feed file: {line}")
                    continue
                
                original_url = parts[0]
                output_file = parts[1]
                
                # Process the feed
                create_reformatted_rss(
                    original_url=original_url,
                    output_file=output_file,
                    archive_prefix=archive_prefix
                )
    except Exception as e:
        print(f"Error reading feed file {feed_file}: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reformat RSS feed links to use archive service.')
    parser.add_argument('--feed-file', required=True, help='Path to the text file containing feed URLs and output paths.')
    parser.add_argument('--archive-prefix', default='https://archive.is/newest/', 
                        help='Prefix to prepend to original URLs (default: "https://archive.is/newest/")')
    
    args = parser.parse_args()
    
    process_feeds_from_file(
        feed_file=args.feed_file,
        archive_prefix=args.archive_prefix
    )
