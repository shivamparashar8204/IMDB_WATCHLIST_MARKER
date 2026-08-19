import os
import re
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
MOVIES_FILE = Path(__file__).parent / "movies.txt"
SESSION_FILE = Path(__file__).parent / "imdb_session.json"
RESULTS_FILE = Path(__file__).parent / "results.json"
DELAY_BETWEEN_MOVIES = 3


def load_movies(filepath):
    movies = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                movies.append(line)
    return movies


def clean_search_query(movie_line):
    name = movie_line.strip()
    name = re.sub(r"\s*\(\d{4}\)\s*$", "", name)
    name = re.sub(r"\s+\d{4}\s*$", "", name)
    name = name.strip()
    return name


def load_results():
    if RESULTS_FILE.exists():
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_results(results):
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def mark_as_watched(page, movie_line):
    query = clean_search_query(movie_line)
    search_url = f"https://www.imdb.com/find/?q={query.replace(' ', '+')}&s=tt&exact=true"
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(2500)

    results = page.locator('a[href*="/title/tt"]')
    if results.count() == 0:
        return False, "No search results found"

    first_link = results.first
    href = first_link.get_attribute("href")
    title_text = first_link.inner_text().strip()
    first_link.click()
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    # --- Approach 1: direct "watched" button ---
    try:
        btn = page.locator('button:has-text("watched"), button:has-text("Watched")')
        if btn.count() > 0:
            btn.first.click()
            page.wait_for_timeout(1000)
            return True, title_text
    except Exception:
        pass

    # --- Approach 2: three-dot "More actions" menu ---
    try:
        more = page.locator(
            'button[aria-label="More actions"], '
            'button[aria-label="More Options"], '
            'button[data-testid="ttbm-overflow-button"]'
        )
        if more.count() > 0:
            more.first.click()
            page.wait_for_timeout(1500)

            watched_item = page.locator(
                '[role="menuitem"]:has-text("atched"), '
                'li:has-text("atched"), '
                'div:has-text("Mark as watched")'
            )
            if watched_item.count() > 0:
                watched_item.first.click()
                page.wait_for_timeout(1000)
                return True, title_text
    except Exception:
        pass

    # --- Approach 3: check if already rated (rating implies watched) ---
    try:
        rate_btn = page.locator(
            'button[data-testid="hero-rating-bar__aggregate-rating__score"] ~ button, '
            'button:has-text("Rate")'
        )
        if rate_btn.count() > 0:
            return True, f"{title_text} (found rate button, may already be tracked)"
    except Exception:
        pass

    return False, f"Could not find watched button for: {title_text}"


def main():
    movies = load_movies(MOVIES_FILE)
    results = load_results()
    print(f"Loaded {len(movies)} movies. {len(results)} already processed.\n")

    with sync_playwright() as p:
        launch_args = {
            "executable_path": BRAVE_PATH,
            "headless": False,
        }
        browser = p.chromium.launch(**launch_args)

        context = None
        if SESSION_FILE.exists():
            try:
                context = browser.new_context(storage_state=str(SESSION_FILE))
                print("Loaded saved session.")
            except Exception:
                context = None

        if context is None:
            context = browser.new_context()

        page = context.new_page()
        page.goto("https://www.imdb.com")
        input("Log in to IMDb, then press ENTER to continue...\n")

        context.storage_state(path=str(SESSION_FILE))
        print("Session saved for future runs.\n")

        for i, movie in enumerate(movies):
            if movie in results:
                status = "skipped" if results[movie]["success"] else "retry"
                if status == "skipped":
                    print(f"[{i+1}/{len(movies)}] SKIP (done): {movie}")
                    continue
                else:
                    print(f"[{i+1}/{len(movies)}] RETRY: {movie}")
            else:
                print(f"[{i+1}/{len(movies)}] Processing: {movie}")

            try:
                success, detail = mark_as_watched(page, movie)
                results[movie] = {"success": success, "detail": detail}
                save_results(results)

                icon = "OK" if success else "FAIL"
                print(f"  [{icon}] {detail}")
            except Exception as e:
                results[movie] = {"success": False, "detail": str(e)}
                save_results(results)
                print(f"  [ERROR] {e}")

            time.sleep(DELAY_BETWEEN_MOVIES)

        context.storage_state(path=str(SESSION_FILE))
        browser.close()

    done = sum(1 for v in results.values() if v["success"])
    failed = sum(1 for v in results.values() if not v["success"])
    print(f"\nDone! {done} marked, {failed} failed out of {len(movies)} total.")


if __name__ == "__main__":
    main()
