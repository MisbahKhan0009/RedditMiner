import requests
import http.cookiejar
import json
import os
import time
from datetime import datetime, timezone
import argparse

class RedditImageScraper:
    def __init__(self, cookie_file):
        self.cookie_file = cookie_file
        self.session = requests.Session()
        self.load_cookies()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }

    def load_cookies(self):
        cj = http.cookiejar.MozillaCookieJar(self.cookie_file)
        cj.load(ignore_discard=True, ignore_expires=True)
        self.session.cookies = cj

    def get_subreddit_posts(self, subreddit, limit=100, sort='new'):
        print(f"\n📸 Extracting Images from r/{subreddit}...")
        print(f"   (Sort: {sort}, Target: {limit} posts)")
        
        posts_collected = []
        after = None
        
        while len(posts_collected) < limit:
            url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit=100"
            if after:
                url += f"&after={after}"
            
            response = self.session.get(url, headers=self.headers)
            if response.status_code != 200:
                print(f"❌ Error: {response.status_code}")
                break

            data = response.json()
            children = data.get("data", {}).get("children", [])
            if not children:
                break

            for p in children:
                p_data = p.get("data", {})
                
                # Check for image/gallery URLs
                image_url = p_data.get("url", "")
                is_image = any(image_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])
                
                # Handle Reddit Galleries
                gallery_urls = []
                if "is_gallery" in p_data and p_data["is_gallery"]:
                    media_metadata = p_data.get("media_metadata", {})
                    for item_id in media_metadata:
                        # Extract the highest resolution version
                        s = media_metadata[item_id].get("s", {})
                        if "u" in s:
                            gallery_urls.append(s["u"].replace("&amp;", "&"))

                if is_image or gallery_urls:
                    posts_collected.append({
                        "title": p_data.get("title"),
                        "author": p_data.get("author"),
                        "created_utc": datetime.fromtimestamp(p_data.get("created_utc", 0), timezone.utc).isoformat(),
                        "permalink": f"https://www.reddit.com{p_data.get('permalink')}",
                        "image_url": image_url if is_image else None,
                        "gallery_images": gallery_urls if gallery_urls else None
                    })

                if len(posts_collected) >= limit:
                    break
            
            after = data.get("data", {}).get("after")
            if not after:
                break
            
            print(f"   ...found {len(posts_collected)} images so far...")
            time.sleep(1) # Be nice to Reddit

        return posts_collected[:limit]

def main():
    parser = argparse.ArgumentParser(description="Reddit Image Scraper")
    parser.add_argument("--subreddit", type=str, required=True, help="Subreddit name to scrape images from")
    parser.add_argument("--limit", type=int, default=100, help="Number of posts to scrape (default: 100)")
    parser.add_argument("--sort", type=str, default="new", help="Sort order (default: new)")
    args = parser.parse_args()

    subreddit = args.subreddit
    limit = args.limit
    sort = args.sort

    if not os.path.exists("cookies.txt"):
        print("❌ Error: cookies.txt not found!")
        return

    scraper = RedditImageScraper("cookies.txt")
    images = scraper.get_subreddit_posts(subreddit, limit=limit, sort=sort)

    if images:
        filename = f"images_{subreddit}_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(images, f, indent=4, ensure_ascii=False)
        print(f"✅ Success! Saved {len(images)} image entries to {filename}")

if __name__ == "__main__":
    main()
