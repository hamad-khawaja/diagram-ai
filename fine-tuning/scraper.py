import requests
from bs4 import BeautifulSoup
import jsonlines
import re


OUTPUT_FILE = "diagrams_data.jsonl"

# List of URLs to scrape
SCRAPE_URLS = [
    "https://diagrams.mingrammer.com/docs/getting-started/examples",
    "https://diagrams.mingrammer.com/docs/guides/diagram",
    "https://diagrams.mingrammer.com/docs/guides/node",
    "https://diagrams.mingrammer.com/docs/guides/cluster",
    "https://diagrams.mingrammer.com/docs/guides/edge",
    "https://diagrams.mingrammer.com/docs/nodes/aws",
    "https://diagrams.mingrammer.com/docs/nodes/azure",
    "https://diagrams.mingrammer.com/docs/nodes/gcp",
]

def extract_prompt_completion(soup):
    # Example: prompt = section title or description, completion = code block
    data = []
    for section in soup.find_all(["section", "div", "article"]):
        # Find code blocks
        codes = section.find_all("code")
        if codes:
            # Use the section's text as prompt, code as completion
            prompt = section.get_text(separator=" ", strip=True)
            for code in codes:
                code_text = code.get_text(strip=True)
                if code_text and len(code_text) > 10:
                    data.append({
                        "prompt": prompt,
                        "completion": code_text
                    })
    return data


def main():
    print("Scraping selected URLs...")
    all_data = []
    for url in SCRAPE_URLS:
        try:
            print(f"Scraping {url}")
            resp = requests.get(url)
            soup = BeautifulSoup(resp.text, "html.parser")
            data = extract_prompt_completion(soup)
            all_data.extend(data)
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
    # Write to .jsonl in OpenAI chat format
    with jsonlines.open(OUTPUT_FILE, mode='w') as writer:
        for item in all_data:
            chat_obj = {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that generates diagrams code."},
                    {"role": "user", "content": item["prompt"]},
                    {"role": "assistant", "content": item["completion"]}
                ]
            }
            writer.write(chat_obj)
    print(f"Saved {len(all_data)} chat-format examples to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
