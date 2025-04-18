import requests
import feedparser
import PyRSS2Gen
import datetime
import argparse
import os
from urllib.parse import urlparse, urlunparse

def create_reformatted_rss(original_url, output_file, target_domain=None, archive_prefix="https://archive.is/newest/"):
    """
    Fetches, parses, modifies, and saves a new RSS feed to a file.
    
    Args:
        original_url (str): The URL of the original RSS feed to process
        output_file (str): Path where the new RSS feed should be saved
        target_domain (str, optional): Domain to filter for (e.g., 'ft.com'). If None, processes all links
        archive_prefix (str, optional): Prefix to prepend to original URLs
    """
    print(f"Processing feed: {original_url}")
    print(f"Outputting to: {output_file}")
    
    try:
        # 1. Fetch the original feed
        headers = {'User-Agent': 'RSS Reformatter Bot (Python; GitHub Actions)'}
        response = requests.get(original_url, headers=headers, timeout=20)
        response.raise_for_status()
        
        # 2. Parse the feed
        feed_data = feedparser.parse(response.content)
        
        # 3. Prepare new RSS items
        new_rss_items = []
        
        for entry in feed_data.entries:
            original_link = entry.get('link')
            
            # Process the link if it matches the target domain or if no target domain is specified
            if original_link and (target_domain is None or target_domain in original_link):
                # Parse the original link and remove query parameters
                parsed_url = urlparse(original_link)
                cleaned_link = urlunparse(parsed_url._replace(query="", fragment=""))  # Remove query and fragment
                
                # Prepend the archive prefix
                new_link = f"{archive_prefix}{cleaned_link}"
                
                item_title = entry.get('title', 'No Title')
                item_description = entry.get('summary', entry.get('description', 'No Description'))
                item_guid_str = entry.get('id', new_link)
                
                published_time_struct = entry.get('published_parsed')
                item_pub_date = datetime.datetime(*published_time_struct[:6]) if published_time_struct else datetime.datetime.now()
                
                new_item = PyRSS2Gen.RSSItem(
                    title=item_title,
                    link=new_link,
                    description=item_description,
                    guid=PyRSS2Gen.Guid(item_guid_str, isPermaLink=False),
                    pubDate=item_pub_date
                )
                new_rss_items.append(new_item)
        
        if not new_rss_items:
            domain_message = f"for domain '{target_domain}'" if target_domain else ""
            print(f"Warning: No items found or processed {domain_message} in feed: {original_url}")
            # Uncomment the next line if you want to exit when no items are found
            # return
        
        # 4. Build the new RSS feed structure
        domain_suffix = f" ({target_domain})" if target_domain else ""
        archive_service = archive_prefix.split('//')[1].split('/')[0]  # Extract service name from prefix
        
        new_rss_feed = PyRSS2Gen.RSS2(
            title=f"{feed_data.feed.get('title', 'Feed')}{domain_suffix} ({archive_service})",
            link=original_url,
            description=f"{feed_data.feed.get('description', 'Reformatted Feed')} via {archive_service}. Updated: {datetime.datetime.now().isoformat()}",
            lastBuildDate=datetime.datetime.now(),
            items=new_rss_items
        )
        
        # 5. Generate the XML output and save to file
        rss_xml = new_rss_feed.to_xml(encoding='utf-8')
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(rss_xml)
        
        print(f"Successfully saved feed to {output_file}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching feed {original_url}: {e}")
        # Uncomment to fail on error: raise e
    except Exception as e:
        print(f"Error processing feed {original_url}: {e}")
        # Uncomment to fail on error: raise e

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reformat RSS feed links to use archive service.')
    parser.add_argument('--url', required=True, help='URL of the original RSS feed.')
    parser.add_argument('--output', required=True, help='Path to save the generated XML file.')
    parser.add_argument('--domain', help='Domain to filter for (e.g., "ft.com"). If not specified, all links will be processed.')
    parser.add_argument('--archive-prefix', default='https://archive.is/newest/', 
                        help='Prefix to prepend to original URLs (default: "https://archive.is/newest/")')
    
    args = parser.parse_args()
    
    create_reformatted_rss(
        args.url, 
        args.output, 
        target_domain=args.domain,
        archive_prefix=args.archive_prefix
    )

    