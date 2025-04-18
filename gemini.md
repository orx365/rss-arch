Okay, combining a static Hugo frontend with GitHub Actions for automating the RSS feed generation is an excellent approach. This leverages free hosting (GitHub Pages) and automation (GitHub Actions).

Here’s a breakdown of how to set it up:

**1. Project Structure**

Organize your project in a GitHub repository like this:

```
.
├── .github/
│   └── workflows/
│       └── update_feeds.yml    # GitHub Actions workflow file
├── hugo-site/                # Your Hugo project root
│   ├── archetypes/
│   ├── content/
│   │   └── _index.md         # Homepage content (can list feeds here)
│   ├── data/
│   ├── layouts/
│   ├── static/               # Static assets
│   │   └── feeds/            # <== Generated RSS XML files will go here
│   │       └── .gitkeep      # Placeholder to keep the directory
│   ├── themes/               # Your Hugo theme
│   └── config.toml           # Hugo configuration
├── scripts/
│   └── generate_feed.py      # Your Python script (modified)
├── requirements.txt          # Python dependencies
└── README.md
```

**Key Points:**

* **`hugo-site/static/feeds/`**: This directory within your Hugo site's `static` folder is crucial. Hugo automatically copies everything from `static` directly into the root of the final built site (`public`). Placing your generated `.xml` files here means they will be accessible at `your-site-url.com/feeds/your_feed.xml`.
* **`scripts/generate_feed.py`**: Your Python script, slightly modified to accept arguments and save output to a file.
* **`.github/workflows/update_feeds.yml`**: The automation heart of the project.

**2. Modify the Python Script (`scripts/generate_feed.py`)**

Adapt your Python script to take command-line arguments for the input feed URL and the output file path.

```python
import requests
import feedparser
import PyRSS2Gen
import datetime
import argparse # Use argparse for command-line arguments
import os

def create_reformatted_rss(original_url, output_file):
    """Fetches, parses, modifies, and saves the new RSS feed to a file."""
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
            if original_link and 'ft.com' in original_link:
                new_link = f"https://archive.is/newest/{original_link}"
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
            # else: # Optionally skip or include non-FT items
            #    pass

        if not new_rss_items:
             print(f"Warning: No FT.com items found or processed for {original_url}")
             # Decide if you want to create an empty feed or skip file creation
             # return # Exit if you don't want empty files

        # 4. Build the new RSS feed structure
        new_rss_feed = PyRSS2Gen.RSS2(
            title=f"{feed_data.feed.get('title', 'FT Feed')} (Archive.is)",
            link=original_url,
            description=f"{feed_data.feed.get('description', 'Reformatted FT Feed')} via archive.is. Updated: {datetime.datetime.now().isoformat()}",
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
        # Decide if the script should fail entirely, e.g., raise e
    except Exception as e:
        print(f"Error processing feed {original_url}: {e}")
        # Decide if the script should fail entirely, e.g., raise e

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reformat RSS feed links to use archive.is.')
    parser.add_argument('--url', required=True, help='URL of the original RSS feed.')
    parser.add_argument('--output', required=True, help='Path to save the generated XML file.')
    args = parser.parse_args()

    create_reformatted_rss(args.url, args.output)
```

**3. Create `requirements.txt`**

List the Python dependencies in `requirements.txt` at the root of your repository:

```
requests
feedparser
PyRSS2Gen
```

**4. Set up Hugo Site (`hugo-site/`)**

* Initialize a new Hugo site if you haven't: `hugo new site hugo-site`
* Choose and configure a theme.
* Edit `hugo-site/config.toml` (or `.yaml`/`.json`) - **importantly, set the `baseURL`** to what your GitHub Pages URL will be (e.g., `https://your-username.github.io/your-repo-name/`).
* Edit `hugo-site/content/_index.md` to add some introductory text and links to where the feeds will be. For example:

```markdown
---
title: "FT Archive Feeds"
---

Welcome! This page hosts automatically updated RSS feeds from FT.com, with links modified to use archive.is.

Available Feeds:

* [FT World News (Archive.is)](/feeds/ft_world.xml)
* [FT Companies (Archive.is)](/feeds/ft_companies.xml)
* [FT UK News (Archive.is)](/feeds/ft_uk.xml)

*Feeds updated periodically.*
```

**5. Create GitHub Actions Workflow (`.github/workflows/update_feeds.yml`)**

This workflow will run on a schedule (e.g., every 6 hours), run your Python script to generate the XML files into `hugo-site/static/feeds/`, build the Hugo site, and deploy it to GitHub Pages.

```yaml
name: Update FT Archive Feeds and Deploy Site

on:
  schedule:
    # Runs every 6 hours (adjust cron schedule as needed)
    # See: https://crontab.guru/
    - cron: '0 */6 * * *'
  workflow_dispatch: # Allows manual triggering from the Actions tab

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: write # Needed to commit changes back to the repo
      pages: write    # Needed for modern GitHub Pages deployment
      id-token: write # Needed for modern GitHub Pages deployment

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10' # Choose your desired Python version
          cache: 'pip' # Cache dependencies

      - name: Install Python Dependencies
        run: pip install -r requirements.txt

      - name: Generate FT Feeds
        run: |
          # Ensure output directory exists (though script also does this)
          mkdir -p hugo-site/static/feeds/

          # Run the script for each feed you want
          python scripts/generate_feed.py --url "https://www.ft.com/rss/world" --output "hugo-site/static/feeds/ft_world.xml"
          python scripts/generate_feed.py --url "https://www.ft.com/rss/companies" --output "hugo-site/static/feeds/ft_companies.xml"
          python scripts/generate_feed.py --url "https://www.ft.com/rss/uk" --output "hugo-site/static/feeds/ft_uk.xml"
          # Add more lines for other feeds...

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: 'latest' # Or pin to a specific version
          # extended: true # Uncomment if your theme needs the extended version

      - name: Build Hugo Site
        run: hugo --minify --source hugo-site # Build the site from the hugo-site directory

      # ----- Option 1: Commit generated feeds back to main branch (Good practice) -----
      # This keeps the generated files in your repo history
      - name: Commit Feed Updates
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "Automated feed update"
          file_pattern: "hugo-site/static/feeds/*.xml" # Only commit the generated feeds
          # Optional: Add other patterns if needed
          commit_user_name: github-actions[bot]
          commit_user_email: 41898282+github-actions[bot]@users.noreply.github.com
          commit_author: github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>
          # Important: Only push if there are changes
          push_options: '--force' # Overwrite if needed, maybe remove if causing issues
          skip_dirty_check: false
          skip_fetch: true

      # ----- Option 2: Deploy directly without committing build output -----
      # This uses the official GitHub Pages action and deploys the 'public' folder
      - name: Upload GitHub Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./hugo-site/public # Path to the built Hugo site

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4 # This uses the artifact uploaded before

```

**6. Configure GitHub Pages**

1.  Go to your repository on GitHub.
2.  Go to `Settings` -> `Pages`.
3.  Under `Build and deployment`, select `Source` as `GitHub Actions`.
4.  GitHub should automatically detect the workflow above that uses `actions/deploy-pages`.

**7. Push and Test**

1.  Commit all your files (`.github`, `hugo-site`, `scripts`, `requirements.txt`, etc.) to your main branch.
2.  Push to GitHub.
3.  Go to the `Actions` tab in your GitHub repository. You should see the `Update FT Archive Feeds and Deploy Site` workflow. You can trigger it manually using the `Run workflow` button (because we included `workflow_dispatch`).
4.  Monitor the action's progress. Check for any errors in the Python script execution or Hugo build.
5.  Once the action completes successfully, your GitHub Pages site should be deployed within a few minutes. Access it via `https://your-username.github.io/your-repo-name/`.
6.  Verify that the homepage loads and that the links to `/feeds/your_feed.xml` work and contain the reformatted RSS content.
7.  Add the feed URLs (e.g., `https://your-username.github.io/your-repo-name/feeds/ft_world.xml`) to your RSS reader.

Now, GitHub Actions will automatically run your Python script on the defined schedule, update the `.xml` files in `hugo-site/static/feeds/`, commit them back to your repository, rebuild the Hugo site, and deploy the latest version to GitHub Pages.