## RSS Archive Linker - Colophon

This project provides an automated method to fetch and rewrite links within specified RSS feeds, directing them to the `archive.is` service. Utilizing GitHub Actions, the process runs on a schedule to maintain updated feeds, accessible via standard RSS readers through the repository's raw content URLs.

The system is designed for flexible configuration. Users can modify the `feeds.txt` file to manage the processed RSS sources or adjust the target archiving service according to their needs and preferences. _This project focuses on the technical transformation of RSS feed links and does not host or distribute original article content. Users are solely responsible for their interaction with the linked content and must ensure their usage complies with all applicable copyright laws and the terms of service of accessed websites. The importance of supporting journalism is acknowledged._


## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/orx365/rss-arch.git
cd rss-arch
```

### 2. Install Dependencies
Install the required Python libraries:

```bash
pip install requests feedparser PyRSS2Gen
```

### 3. Create or Update the feeds.txt File
The feeds.txt file contains the list of RSS feeds to process. Each line should follow this format:

```bash
<feed_url> <output_file> [<domain>]
```

- `<feed_url>`: The URL of the RSS feed.
- `<output_file>`: The path where the reformatted RSS feed will be saved.
- `[<domain>]` (optional): A domain filter to process only links from a specific domain.


### 4. Run the Script Manually (Optional)
You can run the script manually to test it:

```bash
python rss_reformatter.py --feed-file feeds.txt
```
This will process all feeds listed in feeds.txt and save the reformatted feeds to the specified output files.


## Automating Updates with GitHub Actions

The project is configured to update the feeds every 4 hours using GitHub Actions. The workflow file (`.github/workflows/rss_reformatter.yml`) is already set up to:

- Run the script on a schedule (cron: `"0 */4 * * *"`).
- Process all feeds listed in feeds.txt.

You don't need to do anything extra to enable this, as long as the repository is hosted on GitHub and GitHub Actions is enabled.


## Using the Reformatted Feeds

To use the reformatted feeds:

Copy the raw URLs of the output files (e.g., `https://raw.githubusercontent.com/USERNAME/REPOSITORY/main/output/ft-home.xml`).
Add these URLs to your preferred RSS reader app or service.


## Summary

1. Clone the repository and install dependencies.
2. Add your desired RSS feeds to `feeds.txt`.
3. Let GitHub Actions handle the updates automatically.
4. Use the raw URLs of the reformatted feeds in your RSS reader.

This setup provides a scalable and automated method for maintaining RSS feeds with links directed through `archive.is`.
