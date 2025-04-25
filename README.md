[![website](https://img.shields.io/badge/Github_Page-grey)](https://orx365.github.io/rss-arch/)
[![Feeds Updated](https://img.shields.io/github/last-commit/orx365/rss-arch.svg?label=Feeds%20Updated)](#available-feeds)
[![Access Financial Times Feed](https://img.shields.io/badge/Financial%20Times-Access%20RSS-blue)](output/ft-home.xml)
[![Access The Economist Feed](https://img.shields.io/badge/The%20Economist-Access%20RSS-blue)](output/economist.xml)

## RSS Archive Proxy

This project automatically **fetches and reformats RSS feeds** from select news sources using a script that runs periodically. The output provides **updated RSS feeds** that can be easily added to your favorite RSS reader app. Article links are modified to go through `archive.is`, allowing you to *usually* access content without a direct subscription. **Feeds are automatically updated every 4 hours.**

> **Important Disclaimer:** This project automatically modifies RSS feeds every few hours, replacing original article links with `archive.is` links. **This process does not involve hosting any article content.** Users bear full responsibility for their interaction with the linked content and must respect copyright and website terms of service. The value of journalism is understood.

## Available Feeds

The following RSS feeds are currently processed by this project:

-   **[Financial Times - (FT)](./output/ft-home.xml)**

    URL → `https://orx365.github.io/rss-arch/output/ft-home.xml`

-   **[The Economist](./output/economist.xml)** - (RSS follows the *Finance & Economic* topics)

    URL → `https://orx365.github.io/rss-arch/output/economist.xml`

-   **[The New York Times - (Economy)](https://orx365.github.io/rss-arch/output/nyt_econ.xml)**

    URL → `https://orx365.github.io/rss-arch/output/nyt_econ.xml`

-   **The Wall Street Journal** → [`World News`](./output/wsj_world.xml), [`Economy`](./output/wsj_econ.xml)

    World News → `https://orx365.github.io/rss-arch/output/wsj_world.xml`

    Economy → `https://orx365.github.io/rss-arch/output/wsj_econ.xml`

---

### How to Use

1.  Copy the Feed URL of the news source you are interested in from the "Available Feeds" section above.
2.  Paste this URL into your preferred RSS reader application (e.g., Reeder, feeeed).

**Recommended RSS Readers** - [**Reeder**](https://reeder.app) and [**feeeed**](https://feeeed.nateparrott.com)

For highly customized RSS feeds or if you'd like to host your own version of this project [`clone this repo`](colophon.md). A basic project overview can be found in **[colophon](colophon.md)**. This offers the most efficient way to tailor the feeds to your specific needs.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
