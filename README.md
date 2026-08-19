# IMDb Automated Movie Tracker & Watchlist Scraper

An automated Python tool built with **Playwright** that reads a list of movies from a text file, searches for them on **IMDb**, and automatically marks them as **"Watched"**.

---

## 📌 Features

- **Automated IMDb Interaction:** Uses Playwright to search for movie titles and mark them as watched on IMDb [cite: 1].
- **Session Management:** Saves and restores IMDb browser session cookies (`imdb_session.json`) so you only need to log in once [cite: 1, 2].
- **Smart Query Sanitization:** Cleans movie titles by stripping year strings (e.g., `Anand (1971)` $\rightarrow$ `Anand`) for accurate search results [cite: 1, 3].
- **Multi-Strategy Detection:** Attempts three distinct approaches to mark titles:
  1. Direct "Watched" button click [cite: 1].
  2. "More Actions" / three-dot context menu item selection [cite: 1].
  3. Pre-existing rating/tracking detection [cite: 1].
- **State Tracking & Resuming:** Logs execution results in `results.json` to prevent re-processing previously finished items on subsequent runs [cite: 1, 4].

---

## 📁 Repository File Structure

| File | Description |
| :--- | :--- |
| `main.py` | Primary automation script containing search, session handling, and UI interactions [cite: 1]. |
| `movies.txt` | Input list of movie titles (with optional release years) to be processed [cite: 3]. |
| `imdb_session.json` | Stored browser cookies and local storage tokens for maintaining login state [cite: 1, 2]. |
| `results.json` | Execution log tracking the success status and details for each movie title [cite: 1, 4]. |

---

## 🛠️ Prerequisites & Installation

### 1. Requirements
- Python 3.8+
- Brave Browser (or standard Chromium browser) installed on your system [cite: 1].

### 2. Install Dependencies

Install Playwright and initialize the browser binaries:

```bash
pip install playwright
playwright install chromium
```

### 3. Configuration
Ensure the executable path for Brave Browser (or Chromium) in `main.py` matches your local setup [cite: 1]:
```python
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
```

---

## 🚀 Usage

1. **Populate Movie List:** Add movie titles to `movies.txt` (one title per line) [cite: 1, 3].
2. **Execute Script:** Run the main script via terminal:
   ```bash
   python main.py
   ```
3. **Log In (First Run Only):**
   - A browser window will launch to `https://www.imdb.com` [cite: 1].
   - Manually log into your IMDb account [cite: 1].
   - Return to the terminal and press **ENTER** to proceed [cite: 1].
   - Your session details will be exported to `imdb_session.json` for future seamless runs [cite: 1, 2].

---

## 📊 File Formats

### Input: `movies.txt`
```text
Anand (1971)
Deewar (1975)
The Shawshank Redemption (1994)
Inception (2010)
```

### Output: `results.json`
```json
{
  "Anand (1971)": {
    "success": true,
    "detail": "Anand"
  },
  "Inception (2010)": {
    "success": true,
    "detail": "Inception"
  }
}
```

---

## ⚡ How It Works

1. **Session Restore:** Checks if `imdb_session.json` exists to reuse saved login state [cite: 1].
2. **Query Processing:** Trims unnecessary whitespace and regex-strips trailing parenthetical dates [cite: 1].
3. **IMDb Search:** Opens IMDb's search URL (`https://www.imdb.com/find/?q=...`) directly to find the title link [cite: 1].
4. **Action Execution:** Navigates to the first search match and attempts to click the watched button or option [cite: 1].
5. **Log Persistence:** Appends status into `results.json` and pauses for `3` seconds (`DELAY_BETWEEN_MOVIES`) before processing the next item [cite: 1, 4].
