# RSS Archive Reformatter

This project automatically fetches RSS feeds from paywalled news sources and reformats the links to use archive.is for easier reading. Using GitHub Actions, it runs on a scheduled basis to keep feeds updated, making them accessible through any standard RSS reader. The reformatted feeds can be accessed directly from this repository's raw content URLs without requiring any frontend interface.

The system is designed to be easily expandable to additional news sources beyond the initial configuration. By modifying the `feeds.txt` file, you can add or remove sources as needed, or change the archiving service used for the links.

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY
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

Example:
```
https://www.ft.com/rss/home.xml output/ft-home.xml ft.com
https://www.economist.com/rss economist.xml output/economist.com
https://www.theatlantic.com/feed/all/ output/atlantic.xml theatlantic.com
```

- <feed_url>: The URL of the RSS feed.
- <output_file>: The path where the reformatted RSS feed will be saved.
- [<domain>] (optional): A domain filter to process only links from a specific domain.


### 4. Run the Script Manually (Optional)**
You can run the script manually to test it:

```bash
python rss_reformatter.py --feed-file feeds.txt
```
This will process all feeds listed in feeds.txt and save the reformatted feeds to the specified output files.


## Automating Updates with GitHub Actions

The project is configured to update the feeds every 2 hours using GitHub Actions. The workflow file (`.github/workflows/rss_reformatter.yml`) is already set up to:

- Run the script on a schedule (cron: `"0 */2 * * *"`).
- Process all feeds listed in feeds.txt.

You don't need to do anything extra to enable this, as long as the repository is hosted on GitHub and GitHub Actions is enabled.


## Using the Reformatted Feeds

To use the reformatted feeds:

Copy the raw URLs of the output files (e.g., `https://raw.githubusercontent.com/USERNAME/REPOSITORY/main/output/ft-home.xml`).
Add these URLs to your preferred RSS reader app or service.
The feeds will automatically update every 2 hours, ensuring you always have the latest content.

--- 

## Summary

1. Clone the repository and install dependencies.
2. Add your desired RSS feeds to `feeds.txt`.
3. Let GitHub Actions handle the updates automatically.
4. Use the raw URLs of the reformatted feeds in your RSS reader.

This setup ensures a scalable and automated way to access paywalled RSS feeds reformatted for easier reading.