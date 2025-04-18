[![Access Financial Times Feed](https://img.shields.io/badge/Financial%20Times-Access%20Feed-blue)](.output/ft-home.xml)
[![Access The Economist Feed](https://img.shields.io/badge/The%20Economist-Access%20Feed-blue)](.output/economist.xml)

## Available Feeds

The following RSS feeds are currently processed by this project:

- **[Financial Times - (FT)](./output/ft-home.xml)**
  Raw URL: `.output/ft-home.xml`
  GitHub Pages URL: `https://orx365.github.io/rss-arch/output/ft-home.xml`

- **[The Economist](.output/economist.xml)**
  Raw URL: `.output/economist.xml`
  GitHub Pages URL: `https://orx365.github.io/rss-arch/output/economist.xml`




# RSS Archive Reformatter

This project automatically fetches RSS feeds from paywalled news sources and reformats the links to use archive.is for easier reading. Using GitHub Actions, it runs on a scheduled basis to keep feeds updated, making them accessible through any standard RSS reader. The reformatted feeds can be accessed directly from this repository's raw content URLs without requiring any frontend interface.

The system is designed to be easily expandable to additional news sources beyond the initial configuration. By modifying the GitHub Action workflow file, you can add or remove sources as needed, or change the archiving service used for the links.

## Setup Instructions

1. Clone this repository
2. Install dependencies: `pip install requests feedparser PyRSS2Gen`
3. Run manually: `python rss_reformatter.py --url "[feed-url]" --output "output/[output-name].xml" --domain "[domain]"`
4. Or let the GitHub Action run automatically according to the schedule

## Usage

Simply add the raw URLs listed above to your preferred RSS reader app or service. The feeds will update according to the GitHub Action schedule (currently set to run hourly).