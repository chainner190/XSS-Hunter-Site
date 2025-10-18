#!/usr/bin/env python3
# simple_crawler.py
# Usage: python3 simple_crawler.py https://example.com --depth 2 --max 200

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import argparse
import os

BANNER = r"""
             (       ) (   (               
             )\ ) ( /( )\ ))\ )  *   )     
 (   (    ( (()/( )\()|()/(()/(` )  /((    
 )\  )\   )\ /(_)|(_)\ /(_))(_))( )(_))\   
((_)((_) ((_|_))  _((_|_))(_)) (_(_()|(_)  
\ \ / / | | | |  | \| / __|_ _||_   _| __| 
 \ V /| |_| | |__| .` \__ \| |   | | | _|  
  \_/  \___/|____|_|\_|___/___|  |_| |___| 
                                           
                                           
   Mr.Chainner                 v1.1     
   MR.R                 
    +──────────────────────────────────────────────+
               XSS & SQL INJECTION TOOLS 
          Fast Automatic XSS, SQL INJECTION
                 don't use it wrongly
               - Thanks To ALL Friends -             
   +──────────────────────────────────────────────+                                        
"""

def main():
    parser = argparse.ArgumentParser(...)
    # parse args...
    print(BANNER)
    print(color("🚨 scan_web.py — Ordered XSS then SQLi (auto-result)", C.BOLD))
    # rest of main...

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
DEFAULT_TIMEOUT = 10
RESULT_DIR = "result"

def ensure_result_dir():
    os.makedirs(RESULT_DIR, exist_ok=True)
    return RESULT_DIR

def is_same_domain(seed_netloc, url):
    try:
        return urlparse(url).netloc == seed_netloc
    except Exception:
        return False

def fetch(url, timeout=DEFAULT_TIMEOUT, headers=None, max_retries=2):
    headers = headers or {'User-Agent': USER_AGENT}
    for attempt in range(max_retries):
        try:
            r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            # Some sites return status 200 but content is not HTML; still return for inspection
            return r
        except requests.RequestException as e:
            if attempt + 1 == max_retries:
                return None
            time.sleep(1)
    return None

def extract_links_from_html(base_url, html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    links = set()
    # <a href="">
    for a in soup.find_all("a", href=True):
        href = a.get("href").strip()
        if href and not href.startswith("mailto:") and not href.startswith("tel:"):
            full = urljoin(base_url, href)
            links.add(full)
    # form actions
    for f in soup.find_all("form", action=True):
        act = f.get("action").strip()
        if act:
            full = urljoin(base_url, act)
            links.add(full)
    # meta refresh
    for m in soup.find_all("meta", attrs={"http-equiv": True, "content": True}):
        if m['http-equiv'].lower() == 'refresh':
            parts = m['content'].split(';')
            if len(parts) > 1 and 'url=' in parts[1].lower():
                urlpart = parts[1].split('=', 1)[1].strip()
                full = urljoin(base_url, urlpart)
                links.add(full)
    return links

def crawl(seed_url, max_depth=2, max_links=200, timeout=DEFAULT_TIMEOUT, rate_delay=0.2, user_agent=USER_AGENT):
    seed_url = seed_url.strip()
    parsed_seed = urlparse(seed_url)
    scheme = parsed_seed.scheme or "http"
    base = f"{scheme}://{parsed_seed.netloc}"
    seed_netloc = parsed_seed.netloc

    result_dir = ensure_result_dir()
    out_file = os.path.join(result_dir, f"{seed_netloc.replace(':','_')}_urls.txt")

    visited = set()
    queue = [(seed_url, 0)]
    found = []

    headers = {'User-Agent': user_agent}

    print(f"[~] Crawling {seed_url} (max_depth={max_depth}, max_links={max_links})")
    while queue and len(found) < max_links:
        url, depth = queue.pop(0)
        if url in visited:
            continue
        if depth > max_depth:
            continue
        visited.add(url)

        r = fetch(url, timeout=timeout, headers=headers)
        if r is None:
            print(f"[!] Could not fetch {url}")
            continue

        content_type = (r.headers.get("Content-Type") or "").lower()
        if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
            # still record the URL but don't parse for links
            if url not in found:
                found.append(url)
                print(f"[+] Found (non-html): {url}")
                with open(out_file, "a", encoding="utf-8") as fh:
                    fh.write(url + "\n")
            continue

        body = r.text
        # Save URL
        if url not in found:
            found.append(url)
            print(f"[+] Found: {url} (depth={depth})")
            with open(out_file, "a", encoding="utf-8") as fh:
                fh.write(url + "\n")

        # extract links and enqueue same-domain ones
        try:
            links = extract_links_from_html(url, body)
        except Exception as e:
            print(f"[!] HTML parse failed for {url}: {e}")
            links = set()

        for link in links:
            # normalize: remove fragment only
            parsed = urlparse(link)
            normalized = parsed._replace(fragment="").geturl()
            # keep only same-domain (including subdomain? here we only accept exact netloc)
            if is_same_domain(seed_netloc, normalized):
                if normalized not in visited and (normalized, depth + 1) not in queue:
                    if len(found) + len(queue) < max_links:
                        queue.append((normalized, depth + 1))
        time.sleep(rate_delay)

    print(f"[~] Crawl finished. {len(found)} URLs saved to {out_file}")
    return found

# If run as script
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Simple in-domain crawler")
    ap.add_argument("url", help="Seed URL (include scheme https:// )")
    ap.add_argument("--depth", type=int, default=2, help="Max crawl depth")
    ap.add_argument("--max", type=int, default=200, help="Max URLs to collect")
    ap.add_argument("--timeout", type=int, default=10, help="Request timeout seconds")
    ap.add_argument("--delay", type=float, default=0.2, help="Delay between requests (seconds)")
    args = ap.parse_args()

    crawl(args.url, max_depth=args.depth, max_links=args.max, timeout=args.timeout, rate_delay=args.delay)
