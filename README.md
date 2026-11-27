# SFFLibrary

The reading-list website for the **Kelley Library Science Fiction and Fantasy Bookclub**: one page with a live search box and a table you can sort, showing every book the club has read since 2002.

See `SPEC.md` for the full specification.

## What's in this folder

| Item | What it is |
|---|---|
| `build.py` | Reads the master list and writes `docs/data/books.json` and `books.js` (plus `docs/images/images.js` from `images.json`) |
| `build_config.json` | Where the master list lives on the Mac |
| `fetch_images.py` | Downloads the 16 banner images from Wikimedia Commons into `docs/images/` |
| `tests/` | Checks for the build script and the theme colors |
| `docs/` | The website itself. GitHub Pages publishes this folder. |

The master list (`Bookclub_Master_List.md`) stays in `Documents/Claude Projects/Bookclub`. It is never copied here.

## First-time setup

1. **Get the images** (needs internet, takes about a minute). In Terminal:
   ```
   cd ~/Claude/Code/SFFLibrary
   python3 fetch_images.py
   ```
   Until you do this, each theme shows a plain color background instead of a picture.

2. **Put it on GitHub** with GitHub Desktop:
   - **File → Add Local Repository…** and choose the `SFFLibrary` folder. When it says this isn't a Git repository yet, choose **create a repository**.
   - Make the first commit, then **Publish repository**. It can be public (GitHub Pages needs that on a free account) or private if you have GitHub Pro.

3. **Turn on GitHub Pages** on github.com:
   - Open the repository → **Settings → Pages**.
   - Under **Build and deployment**, choose **Deploy from a branch**, branch **main**, folder **/docs**, then **Save**.
   - After a minute or two the site is at `https://<your-username>.github.io/SFFLibrary/`.

## Updating the list

1. Edit `Bookclub_Master_List.md` as usual.
2. In Terminal:
   ```
   cd ~/Claude/Code/SFFLibrary
   python3 build.py
   ```
   It checks the list first. If something doesn't add up (a missing month, or counts that don't match the Summary section), it says what and where, and changes nothing.
3. Look at it on your Mac: double-click `docs/index.html` to open it in Safari.
4. In GitHub Desktop, commit and **Push origin**. The website updates within a few minutes.

## Running the checks

```
python3 -m unittest discover tests
```

## Changing the pictures

Everything about the banners is in `docs/images/images.json`: which theme each image belongs to, its credit and licence, and `focus`, which sets the crop. For example, `"center 30%"` shows more of the top of a tall picture. To add an image, add an entry there, then run `python3 fetch_images.py`.
