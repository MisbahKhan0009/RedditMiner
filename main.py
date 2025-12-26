import argparse
import os
import json
import time
from redditminer.scraper import RedditImageScraper

def main():
    parser = argparse.ArgumentParser(description="Reddit Image Scraper")
    parser.add_argument("--subreddit", type=str, required=True, help="Subreddit name to scrape images from")
    parser.add_argument("--limit", type=int, default=100, help="Number of posts to scrape (default: 100)")
    parser.add_argument("--sort", type=str, default="new", help="Sort order (default: new)")
    parser.add_argument("--output-mode", type=str, default="post", choices=["post", "post_with_comments", "image_url"], help="Output mode: post (default), post_with_comments, image_url")
    parser.add_argument("--download-images", action="store_true", help="Download images if output mode is image_url")
    parser.add_argument("--output-dir", type=str, default="images", help="Directory to save images if downloading")
    parser.add_argument("--max-workers", type=int, default=8, help="Number of parallel downloads if downloading")
    args = parser.parse_args()

    subreddit = args.subreddit
    limit = args.limit
    sort = args.sort
    output_mode = args.output_mode
    download_images = args.download_images
    output_dir = args.output_dir
    max_workers = args.max_workers

    if not os.path.exists("cookies.txt"):
        print("❌ Error: cookies.txt not found!")
        return

    scraper = RedditImageScraper("cookies.txt")
    images = scraper.get_subreddit_posts(subreddit, limit=limit, sort=sort)

    # Add subreddit name to each image entry
    for post in images:
        post["subreddit"] = subreddit

    # Ensure output directory exists
    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if images:
        filename = f"images_{subreddit}_{int(time.time())}"
        if output_mode == "image_url":
            # Save only image URLs (image_url or gallery_images)
            urls = []
            for post in images:
                if post.get("image_url"):
                    urls.append(post["image_url"])
                if post.get("gallery_images"):
                    urls.extend(post["gallery_images"])
            txt_path = os.path.join(output_folder, f"{filename}.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                for url in urls:
                    f.write(url + "\n")
            print(f"✅ Success! Saved {len(urls)} image URLs to {txt_path}")
            if download_images:
                from redditminer.downloader import download_images_from_txt
                print(f"⬇️  Downloading images to '{output_dir}'...")
                download_images_from_txt(txt_path, output_dir, max_workers)
        else:
            # For now, 'post_with_comments' is the same as 'post' until comment fetching is implemented
            json_path = os.path.join(output_folder, f"{filename}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(images, f, indent=4, ensure_ascii=False)
            print(f"✅ Success! Saved {len(images)} image entries to {json_path}")

if __name__ == "__main__":
    main()
