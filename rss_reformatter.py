import requests
import feedparser
import PyRSS2Gen
import datetime
import argparse
import os
from urllib.parse import urlparse, urlunparse
import re
from xml.sax.saxutils import escape

def get_feed_logo(feed_data):
    """Extracts the feed logo information."""
    if 'image' in feed_data.feed and 'url' in feed_data.feed.image:
        return PyRSS2Gen.Image(
            url=feed_data.feed.image.url,
            title=feed_data.feed.image.get('title', feed_data.feed.get('title', '')),
            link=feed_data.feed.image.get('link', feed_data.feed.get('link', ''))
        )
    return None

def extract_image_and_credit(entry):
    """Extracts the best image URL and credit from a feed entry."""
    image_url = None
    credit = None

    # Priority 1: media:content
    if hasattr(entry, 'media_content') and entry.media_content:
        for media in entry.media_content:
            if 'url' in media and media.get('medium') == 'image':
                image_url = media['url']
                if hasattr(media, 'credit'):
                    credit = media.credit
                return image_url, credit # Return first image found

    # Priority 2: media:thumbnail
    if not image_url and hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
        for media in entry.media_thumbnail:
            if 'url' in media:
                image_url = media['url']
                return image_url, None # Thumbnails usually don't have credits

    # Priority 3: Enclosures
    if not image_url and hasattr(entry, 'enclosures') and entry.enclosures:
        for enclosure in entry.enclosures:
            if 'url' in enclosure and enclosure.get('type', '').startswith('image/'):
                image_url = enclosure['url']
                return image_url, None

    # Priority 4: Image tag in content or summary
    content_html = ''
    if 'content' in entry and entry.content:
        content_html = entry.content[0].get('value', '')
    if not content_html:
        content_html = entry.get('summary', entry.get('description', ''))

    img_match = re.search(r'<img[^>]+src=["\'](https?://[^"\']+)["\']', content_html)
    if img_match:
        image_url = img_match.group(1)
        # Simple check for alt text as potential credit
        alt_match = re.search(r'<img[^>]+alt=["\']([^"\']+)["\']', content_html)
        if alt_match:
            credit = alt_match.group(1)
        return image_url, credit

    return None, None

def add_media_tags_to_xml(xml_string, media_data):
    """Adds media namespace and media:content tags to the generated XML."""
    # Add media namespace
    xml_string = xml_string.replace(
        '<rss version="2.0">',
        '<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">',
        1
    )

    # Add media:content tags within each item
    for guid, (url, credit) in media_data.items():
        guid_tag = f'<guid isPermaLink="false">{guid}</guid>'
        guid_pos = xml_string.find(guid_tag)
        if guid_pos != -1:
            insert_pos = guid_pos + len(guid_tag)
            media_tag = f'\n      <media:content url="{escape(url)}" medium="image" type="image/jpeg">'
            if credit:
                media_tag += f'\n        <media:credit>{escape(credit)}</media:credit>\n      '
            media_tag += '</media:content>'
            xml_string = xml_string[:insert_pos] + media_tag + xml_string[insert_pos:]

    return xml_string

def create_reformatted_rss(original_url, output_file, archive_prefix="https://archive.is/newest/"):
    """Fetches, parses, and reformats a single RSS feed."""
    print(f"Processing feed: {original_url}")
    try:
        # 1. Fetch and Parse Feed
        headers = {'User-Agent': 'RSS Reformatter Bot (Python)'}
        response = requests.get(original_url, headers=headers, timeout=30)
        response.raise_for_status()
        feed_data = feedparser.parse(response.content)

        # 2. Extract Feed Logo
        feed_logo = get_feed_logo(feed_data)

        # 3. Process Feed Items
        rss_items = []
        media_data = {} # Store media info: {guid: (url, credit)}
        processed_guids = set()

        for entry in feed_data.entries:
            original_link = entry.get('link')
            if not original_link:
                continue

            # Generate GUID (use entry ID or link)
            guid_text = entry.get('id', original_link)
            if guid_text in processed_guids:
                continue # Skip duplicates within the same fetch
            processed_guids.add(guid_text)

            # Clean and archive link
            parsed_url = urlparse(original_link)
            cleaned_link = urlunparse(parsed_url._replace(query="", fragment=""))
            archived_link = f"{archive_prefix}{cleaned_link}"

            # Extract image and credit
            image_url, image_credit = extract_image_and_credit(entry)
            if image_url:
                media_data[guid_text] = (image_url, image_credit)

            # Get publication date
            pub_date = datetime.datetime.now(datetime.timezone.utc)
            if 'published_parsed' in entry and entry.published_parsed:
                pub_date = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)

            # Create RSS Item
            rss_item = PyRSS2Gen.RSSItem(
                title=entry.get('title', 'No Title'),
                link=archived_link,
                description=entry.get('summary', entry.get('description', '')),
                guid=PyRSS2Gen.Guid(guid_text, isPermaLink=False),
                pubDate=pub_date,
                author=entry.get('author')
            )
            rss_items.append(rss_item)

        # Limit to latest 100 items (optional, if needed)
        rss_items.sort(key=lambda x: x.pubDate, reverse=True)
        rss_items = rss_items[:100]

        # 4. Build Basic RSS Feed
        rss_feed = PyRSS2Gen.RSS2(
            title=feed_data.feed.get('title', 'Reformatted Feed'),
            link=original_url,
            description=feed_data.feed.get('description', ''),
            lastBuildDate=datetime.datetime.now(datetime.timezone.utc),
            items=rss_items,
            image=feed_logo, # Add the logo here
            language=feed_data.feed.get('language'),
            copyright=feed_data.feed.get('rights', feed_data.feed.get('copyright'))
        )

        # 5. Generate XML and Add Media Tags
        base_xml = rss_feed.to_xml(encoding='utf-8')
        final_xml = add_media_tags_to_xml(base_xml, media_data)

        # 6. Save the Feed
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_xml)

        print(f"Successfully saved feed to {output_file}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching feed {original_url}: {e}")
    except Exception as e:
        print(f"Error processing feed {original_url}: {e}")

def process_feeds_from_file(feed_file, archive_prefix):
    """Reads feed URLs from a file and processes each."""
    if not os.path.exists(feed_file):
        print(f"Error: Feed file not found at {feed_file}")
        return

    try:
        with open(feed_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split()
                if len(parts) < 2:
                    print(f"Warning: Skipping invalid line {line_num} in {feed_file}: {line}")
                    continue

                original_url, output_file = parts[0], parts[1]
                create_reformatted_rss(original_url, output_file, archive_prefix)

    except Exception as e:
        print(f"Error reading or processing feed file {feed_file}: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch, reformat, and archive RSS feed links.')
    parser.add_argument('--feed-file', required=True,
                        help='Path to a text file listing feed URLs and output XML paths (one per line).')
    parser.add_argument('--archive-prefix', default='https://archive.is/newest/',
                        help='Prefix for archiving links (default: https://archive.is/newest/).')

    args = parser.parse_args()
    process_feeds_from_file(args.feed_file, args.archive_prefix)