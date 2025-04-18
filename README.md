# RSS Archive Reformatter

[![Access Financial Times Feed](https://img.shields.io/badge/Financial%20Times-Access%20Feed-blue)](https://raw.githubusercontent.com/USERNAME/REPOSITORY/main/output/ft-home.xml)
[![Access The Economist Feed](https://img.shields.io/badge/The%20Economist-Access%20Feed-blue)](https://raw.githubusercontent.com/USERNAME/REPOSITORY/main/output/economist.xml)

This project automatically fetches RSS feeds from paywalled news sources and reformats the links to use archive.is for easier reading. Using GitHub Actions, it runs on a scheduled basis to keep feeds updated, making them accessible through any standard RSS reader. The reformatted feeds can be accessed directly from this repository's raw content URLs without requiring any frontend interface.

The system is designed to be easily expandable to additional news sources beyond the initial configuration. By modifying the GitHub Action workflow file, you can add or remove sources as needed, or change the archiving service used for the links.

## Available Feeds

The following RSS feeds are currently processed by this project:

- **Financial Times (FT)**: Access the Financial Times home feed via archive.is  
  Raw URL: `https://raw.githubusercontent.com/orx365/rss-arch/main/output/ft-home.xml`

- **The Economist**: Access The Economist's main feed via archive.is  
  Raw URL: `https://raw.githubusercontent.com/orx365/rss-arch/main/output/economist.xml`

## Setup Instructions

1. Clone this repository
2. Install dependencies: `pip install requests feedparser PyRSS2Gen`
3. Run manually: `python rss_reformatter.py --url "[feed-url]" --output "output/[output-name].xml" --domain "[domain]"`
4. Or let the GitHub Action run automatically according to the schedule

## Usage

Simply add the raw URLs listed above to your preferred RSS reader app or service. The feeds will update according to the GitHub Action schedule (currently set to run hourly).