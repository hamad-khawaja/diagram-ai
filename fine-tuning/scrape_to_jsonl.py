import requests
from bs4 import BeautifulSoup
import jsonlines
import re

# List of example URLs to scrape (expand as needed)
SCRAPE_URLS = [
    "https://diagrams.mingrammer.com/docs/getting-started/examples",
    "https://diagrams.mingrammer.com/docs/guides/diagram",
    "https://diagrams.mingrammer.com/docs/guides/node",
    "https://diagrams.mingrammer.com/docs/guides/cluster",
    "https://diagrams.mingrammer.com/docs/guides/edge",
    "https://diagrams.mingrammer.com/docs/nodes/aws",
    "https://diagrams.mingrammer.com/docs/nodes/azure",
    "https://diagrams.mingrammer.com/docs/nodes/gcp",
    # GitHub raw links for .py files
    "https://raw.githubusercontent.com/warrenpearson/diagrams/master/example_one.py",
    "https://raw.githubusercontent.com/warrenpearson/diagrams/master/example_two.py",
    "https://raw.githubusercontent.com/JeBear76/python-diagrams/main/EC2-Lambda-Architecture.py",
    
]

OUTPUT_FILE = "scraped_examples.jsonl"

SYSTEM_PROMPT = "You are a helpful assistant that generates diagrams code. Always follow best practices and only use supported nodes."

def extract_examples(soup):
    data = []
    # Find all code blocks and their preceding description (if any)
    for pre in soup.find_all("pre"):
        code = pre.get_text(strip=True)
        # Try to find a description above the code block
        desc = ""
        prev = pre.find_previous_sibling()
        while prev and not desc:
            if prev.name in ["p", "h2", "h3", "h4", "h5"]:
                desc = prev.get_text(strip=True)
            prev = prev.find_previous_sibling()
        if code and desc:
            data.append((desc, code))
    return data

def extract_github_py(url):
    # For raw .py files from GitHub, treat the whole file as code, and use the filename as description
    import os
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            code = resp.text.strip()
            desc = f"Python diagram example from {os.path.basename(url)}"
            return [(desc, code)]
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
    return []

def main():
    all_examples = []
    for url in SCRAPE_URLS:
        try:
            print(f"Scraping {url}")
            if url.endswith('.py') or 'raw.githubusercontent.com' in url:
                examples = extract_github_py(url)
            else:
                resp = requests.get(url)
                soup = BeautifulSoup(resp.text, "html.parser")
                examples = extract_examples(soup)
            all_examples.extend(examples)
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
    # Write to .jsonl
    with jsonlines.open(OUTPUT_FILE, mode='w') as writer:
        for desc, code in all_examples:
            writer.write({
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": desc},
                    {"role": "assistant", "content": code}
                ]
            })
    print(f"Saved {len(all_examples)} examples to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
