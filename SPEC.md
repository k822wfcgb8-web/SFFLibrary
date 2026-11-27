# SFFLibrary — Specification

_v1.0 (as built) · 24 Nov 2026 · Owner: Bob Wade (Salem SciFi & Fantasy Book Club)_

## 1. Purpose

**Kelley Library Science Fiction and Fantasy Bookclub** is a one-page website where club members can browse everything the Salem SciFi & Fantasy Book Club has read since January 2002. It shows the master reading list as a sortable, searchable table that behaves like a small embedded spreadsheet.

The site only **reads** the club's master list. It never becomes a second copy of it.

## 2. Goals and non-goals

**Goals**
- A member can type part of a title or an author's name and see matching books right away, on a phone or a computer.
- The table sorts by date, title, author or series with one click.
- Large, clear type with no clutter, readable for members of every age.
- Colorful and fun to look at, with a few themes to choose from and open-licence space and fantasy art.
- Bob updates the site in one step after he edits the master list.
- No cost to host, and no server, database or accounts.

**Non-goals (v1)**
- No other pages (By Year, Authors, Stats, book detail pages). See §10.
- No member logins, comments, ratings or voting.
- No editing in the browser. All changes go through `Bookclub_Master_List.md`.
- No library-availability lookups.

## 3. Users

| User | Needs |
|---|---|
| Club member | Find a book or an author fast; sort the list; use it on a phone |
| Bob (maintainer) | Edit the master list as now, rebuild, check locally, publish |

## 4. Source of truth

- **Master:** `~/Documents/Claude Projects/Bookclub/Bookclub_Master_List.md`. It stays where it is and in its current format.
- A build script reads the master list and writes `docs/data/books.json`. The JSON is a generated file that nobody edits by hand, and every build overwrites it.
- The SFFLibrary repo **never** stores a copy of the master list.
- The script reads only the master list. It never touches the `.mbox` email archive, the `.ods` spreadsheet or the synopsis files.

### 4.1 Master-list format the parser must handle

- A `## YYYY` heading for each year, each followed by a table: `Month | Title | Author | Series / Book # | Previously Read`.
- **Status rows** in italics: `*No meeting*`, `*Unknown*`, `*Meeting, no book (planning)*`, `*Upcoming*`.
- **Several books in one month** (for example Oct 2004 and Aug 2020): two rows with the same month.
- **One book over several months:** `Title *(part 1 of 2)*`.
- **Special entry:** Jan 2026 `Multiple Titles | Multiple Authors | —`, shown as a normal row.
- **Authors** written "Last, First", with co-authors joined by " and " (`Niven, Larry and Pournelle, Jerry`). Suffixes stay with the surname (`Modesitt Jr., L. E.`). Editors are marked `(editor)`.
- **Undated picks** section: `Title | Author | Series / Book # | Also Read`.
- **Summary** section: the parser ignores it, except for the check in §4.2.
- The **Previously Read** and **Also Read** columns are read and kept in the JSON for later phases, but not shown in v1.

### 4.2 Validation (the build fails with a clear message if any check fails)

- Every year from 2002 to the current year is present, and each month appears at least once.
- The counts match the master list's Summary section. As of 22 Nov 2026 these are: 264 dated book rows, 11 undated picks, 13 no-meeting months, 23 unknown months.
- Any row the parser can't read is reported with its line number.

## 5. Data model (`books.json`)

One record per table row in the master list, in master-list order:

```json
{
  "generated": "2026-11-24T15:00:00-05:00",
  "source": "Bookclub_Master_List.md",
  "rows": [
    { "year": 2026, "month": 10, "status": "read",
      "title": "Cryptonomicon", "part": "part 1 of 2",
      "author": "Stephenson, Neal",
      "series": "Standalone",
      "previouslyRead": ["2005-09"] },
    { "year": null, "month": null, "status": "undated",
      "title": "Ender's Game", "part": null,
      "author": "Card, Orson Scott",
      "series": "Ender's Saga #1",
      "previouslyRead": [] }
  ]
}
```

- `status` is one of `read`, `undated`, `no-meeting`, `unknown`, `planning` or `upcoming`.
- `author` stays exactly as written in the master list.

## 6. The page (v1)

One page with four parts, from top to bottom: a banner, a search bar, the table, and a footer.

### 6.1 Banner and title
- The browser tab title and the main heading both read exactly: **Kelley Library Science Fiction and Fantasy Bookclub**.
- A subheading underneath: "Everything we've read since 2002".
- A line underneath: "Last updated 24 Nov 2026", taken from `generated`.
- The heading sits over a wide banner image drawn from the current theme's image pool (§6.5). A dark or light overlay keeps the text readable.
- A small caption in the banner's bottom corner credits the image shown, for example "Banner: *Root Trolls*, John Bauer, 1917". It links to the full credits.
- The **style picker** (§6.4) sits at the top right of the banner.
- The site does not use the Kelley Library logo unless the library supplies it and agrees.

### 6.2 Search box
- A single box labelled **"Search title or author"**.
- **Live filtering:** the table updates on every keystroke, with no Search button and no Enter needed.
- **Matching:**
  - It ignores **case**: "niv", "Niv" and "NIV" give the same results.
  - It ignores **accents**: "Mieville" finds "Miéville".
  - It matches **anywhere** in the title or author text, so a partial word works. "Niv" finds every Larry Niven book. "Larry" works too, and so does "Pournelle".
  - It looks at **title and author only**. Series text is not searched, so "Niv" does not match "Diving Universe".
  - Spaces at the start or end are ignored.
- A **× clear button** appears inside the box once something is typed. Pressing Esc also clears it.
- The matched text is **highlighted** in the results.
- A count beside the box: "Showing 7 of 275 books". With nothing typed it shows "275 books".
- If nothing matches: "No books match 'xyz'" in the table area.

### 6.3 Table
- **Columns:** Date · Title · Author · Series / Book #.
- **Date** is shown as "Oct 2026". A book read over two months appears on two rows, with "(part 1 of 2)" after the title, just as in the master list.
- **Undated picks** appear in the same table with "Undated" in the Date column.
- **Sorting:**
  - Click a column header to sort by it. Click it again to reverse the order. An arrow (▲/▼) shows the sorted column and its direction.
  - **Default:** Date, newest first.
  - **Date** sorts by year and then month. Undated rows always sort to the bottom, whichever direction is chosen.
  - **Title** sorts A–Z and ignores a leading "The", "A" or "An", so *The Hunger Games* files under H. Case and accents are ignored.
  - **Author** sorts by the text as written, which is surname first (Asimov, Bujold, Card …).
  - **Series** sorts A–Z.
  - **Ties** (for example several books by the same author) are broken by date, newest first.
  - Sorting and search work together: a sort applies to the filtered rows, and typing keeps the current sort.
- **"Show all months" checkbox** under the search box, unticked by default.
  - Ticked, it adds the No meeting, Unknown, planning-meeting and Upcoming months to the table, in grey italics, with the Title cell reading "No meeting", "Unknown" and so on.
  - These rows are left out of the book count and never match a search.
- **Spreadsheet feel:**
  - The header row stays visible while scrolling.
  - Rows are lightly striped, and the row under the pointer is highlighted.
  - Full-width on a computer. On a phone the table scrolls sideways if needed, with the Date and Title columns kept visible.
- The page remembers the sort choice while it is open. The theme choice is the only thing kept between visits (§6.4).

### 6.4 Style picker
- A small menu labelled **"Style"** offers four themes. Choosing one changes the page immediately, without reloading.

| Theme | Feel | Colors | Banner image |
|---|---|---|---|
| **Deep Space** (default) | Dark, starry | Navy and black, with cyan and amber highlights | A nebula or galaxy photo |
| **Enchanted Forest** | Fantasy | Deep green and parchment, with gold highlights | A public-domain fairy-tale painting or forest scene |
| **Retro Pulp** | 1930s–50s magazine | Cream background, with red, mustard and teal | Public-domain pulp-magazine cover art |
| **Library Classic** | Calm, light, highest contrast | Off-white and charcoal, with burgundy highlights | A public-domain engraving of books or a library |

- Each theme changes the page background, the banner image (picked at random from that theme's pool, §6.5), the heading font style, the table's stripe and header colors, link and highlight colors, and the search-match highlight.
- Every theme keeps the same layout, so nothing moves when you switch.
- **Library Classic** is also used automatically when the device's "reduce motion" or "increase contrast" setting is on, until the member picks a theme.
- The choice is saved in the browser (`localStorage`) so the site opens in the same theme next time. This isn't a cookie and is never sent anywhere. If the browser blocks storage, the site falls back to Deep Space without an error.
- Themes are built with CSS custom properties (one block of variables for each theme), so a fifth theme can be added later in a few lines.

### 6.5 Images
- Images are decoration only and never needed to use the table.
- **Allowed licences:** public domain, CC0, CC BY or CC BY-SA. Every image is credited in the footer and in `docs/images/CREDITS.md` with its title, creator, source link and licence.
- **Not allowed:** book covers, film stills, or any copyrighted or trademarked art, including fan art of existing characters.
- **Sources to choose from:**
  - NASA images: public domain, for example Hubble and James Webb nebula and galaxy photos.
  - ESA/Webb and ESA/Hubble images: CC BY 4.0, credited as the agencies ask.
  - Wikimedia Commons, public-domain category only: for example Arthur Rackham, Gustave Doré and John Bauer illustrations, and pulp-magazine covers published before 1929.
  - Internet Archive and the Library of Congress: public-domain scans.
- All images are **downloaded and stored in the repo** under `docs/images/` and never loaded live from another site.
- Each image is resized for the web (at most 1600 px wide, WebP or JPEG, under 300 KB).
- **16 banner images**, four or five for each theme (§6.5.1), plus optional small corner art (a rocket, a dragon, a quill).
- Decorative images use empty `alt` text so screen readers skip them.
- Bob approved all 16 candidates in the gallery page (`docs/images/preview.html`) on 24 Nov 2026.

#### 6.5.1 Banner pools and rotation
- Each theme has its own **pool** of banner images:

| Theme | Pool |
|---|---|
| Deep Space | *Cosmic Cliffs* (Webb) · *Pillars of Creation* (Hubble) · *Carina Nebula field* (Webb) |
| Enchanted Forest | Bauer: *Tuvstarr Gazing into the Water*, *The Princess and the Trolls*, *Root Trolls* · Rackham: *Fafnir Guards the Gold Hoard* · Doré: *Hippogriff* |
| Retro Pulp | *Amazing Stories* Aug, Sep and Nov 1927 (Frank R. Paul) · *Weird Tales* Mar 1923 |
| Library Classic | Reading rooms of the Library of Congress, the Boston Public Library and Widener Library · *Incunabula Room, British Museum* |

- **Rotation:**
  - On every page load, and every time a theme is picked in the Style menu, the banner shows an image chosen **at random** from that theme's pool.
  - The same image never appears twice in a row.
  - A **"↻ New picture"** button beside the Style menu shows another image from the current theme's pool. (A dropdown menu can't detect someone picking the theme that is already showing, so the button does that job.)
  - The banner crossfades to the new image over about half a second, or switches straight away if the device's "reduce motion" setting is on.
- Each image has a **focal point** (for example `"center 40%"`), set by hand, so the banner crop shows the interesting part of tall pictures such as the *Pillars* and the pulp covers.
- The pools are listed in one small file, `docs/images/images.json`, with each image's file name, theme, title, creator, date, licence, source link and focal point. The page, the banner credit and the credits list all read from it, so adding or removing an image means changing one file.
- Only the banner currently showing is downloaded. Other images load only when they're picked.
- **Before launch:** the three images marked "to confirm" in `CREDITS.md` (the two Webb pictures and the British Museum engraving) must have their licences checked on their Commons pages. If one doesn't meet the licence rules above, it's dropped from its pool.

### 6.6 Footer
- "Kelley Library Science Fiction and Fantasy Bookclub · Salem, NH".
- An "Image credits" link that opens the credits list.
- The build date.

## 7. Non-functional requirements

- **Readability:** body text at least 18 px, high contrast, nothing that needs hovering, and tap targets at least 44 px. Meets WCAG 2.1 AA. The table headers are real buttons, so keyboard and screen-reader users can sort.
- **Devices:** current Safari, Firefox and Edge, including iPhone and iPad.
- **Speed:** the page loads in under 1 s, and filtering 300 rows feels instant (under 50 ms per keystroke).
- **Printing:** printing gives just the table as it is currently filtered and sorted, with no search box or buttons.
- **Contrast in every theme:** text, table and highlight colors in every theme meet WCAG 2.1 AA (at least 4.5:1 for body text). The build checks the theme colors with a small contrast test (§8).
- **Visibility:** anyone with the link can open the site. It is kept out of search engines (`noindex` meta tag plus `robots.txt`).
- **Privacy and third parties:**
  - No member names, email addresses or meeting locations anywhere on the site.
  - No analytics, cookies or tracking.
  - **No Google or Meta services of any kind**: no Google Fonts, Google Analytics, reCAPTCHA, YouTube embeds, Google Books covers or Facebook links. Fonts are the fonts already on members' devices; each theme lists a few in order of preference (for example Palatino, then Georgia).
  - After the page loads it makes no requests to other sites. Every file comes from the site itself.

## 8. Technical design

- **Static site:** plain HTML, CSS and vanilla JavaScript. No framework, no table library and no npm build.
- **Build script:** `build.py`, Python 3 standard library only. Run it with `python3 build.py`. The master-list path is saved in `build_config.json` and can be overridden with `--source "<path>"`.
- **Local preview:** double-click `docs/index.html`. The build also writes the data as `books.js` and `images/images.js`, so the page works straight from the disk, where browsers block reading `.json` files.
- **Hosting:** GitHub Pages under Bob's existing GitHub account. SFFLibrary is its own repository, published from its `docs/` folder (GitHub Pages can publish only from the top of a repository or from a folder named `docs`), at `https://<username>.github.io/SFFLibrary/`. It's published with GitHub Desktop, the same way as the Middle-earth Genealogy site.
- All links and file paths inside the site are relative, so it works both at that address and in local preview.
- **Tests:** `tests/test_parser.py` (standard-library `unittest`) runs on a small sample file covering every case in §4.1. `tests/test_contrast.py` checks each theme's color pairs against WCAG AA.

### Repo layout

```
SFFLibrary/
├── SPEC.md
├── README.md            # how to rebuild and publish
├── build.py
├── build_config.json
├── fetch_images.py      # downloads the banner images from Wikimedia Commons
├── tests/
│   ├── sample_master.md
│   └── test_parser.py
└── docs/
    ├── index.html
    ├── css/style.css
    ├── js/app.js
    ├── data/books.json  # generated — do not edit
    ├── images/
    │   ├── CREDITS.md
    │   ├── images.json  # banner pools, credits, focal points
    │   └── preview.html # gallery for approving images
    └── robots.txt
```

## 9. Update workflow

0. Once, and again after changing `images.json`: run `python3 fetch_images.py` to download the banner images.
1. Edit `Bookclub_Master_List.md` as usual.
2. Run `python3 build.py`. It checks the list (§4.2) and rewrites `books.json`.
3. Preview the site locally.
4. Commit and push in GitHub Desktop. The site updates within a few minutes.

## 10. Later phases (not in v1)

- A "Coming up" panel showing the next upcoming pick(s).
- A "Times read" or "Reread" column, using the Previously Read data the build already keeps.
- Other views: By Year, Authors A–Z, club stats.
- Links from each title to the Kelley Library and NH statewide (NHAIS) catalogs.
- An SF / Fantasy genre column, from a small `genres.json` beside the build script.
- A "Candidates" page drawn from `SFF_Popular_Picks_NH_Holdings.md`, with NH copy counts.

## 11. Open decisions

None for v1. Image choices are approved before launch (§6.5).

## 12. Acceptance criteria (v1)

- [ ] The build runs on the real master list with no validation errors, and the counts match §4.2.
- [ ] With nothing typed, the table shows 275 books (264 dated plus 11 undated), newest first, with Nov 2026 *Cryptonomicon (part 2 of 2)* at the top and the undated picks at the bottom.
- [ ] Typing "Niv" shows exactly the 7 rows with Larry Niven as author or co-author (Footfall, Lucifer's Hammer, Inferno, The Mote in God's Eye, Saturn's Race, Bowl of Heaven, Shipstar), and the count reads "Showing 7 of 275 books". *Diving into the Wreck* does not appear.
- [ ] "niv", "NIV" and "Niv" give the same results. "mieville" finds *Perdido Street Station* twice.
- [ ] Clicking Title sorts A–Z with *The Hunger Games* under H. Clicking it again sorts Z–A.
- [ ] Clicking Author puts Asimov near the top. Within an author, the newest reading comes first.
- [ ] Ticking "Show all months" adds the 37 rows with no book (13 No meeting, 23 Unknown, 1 planning meeting) plus the Dec 2026 Upcoming row, in grey. The book count doesn't change.
- [ ] × and Esc both clear the search and bring back the full table.
- [ ] The browser tab and the page heading both read "Kelley Library Science Fiction and Fantasy Bookclub".
- [ ] Each of the four themes can be picked from the Style menu. The page changes immediately, and after a reload it opens in the last theme picked.
- [ ] Reloading the page or picking a theme shows a randomly chosen banner from that theme's pool, never the same image twice in a row, and the banner credit matches the image shown.
- [ ] Every image's crop shows its subject, not an empty patch of sky or a magazine masthead cut in half.
- [ ] The contrast test passes for all four themes.
- [ ] Every image on the site is listed in `CREDITS.md` with an allowed licence, and the footer credits link works.
- [ ] It works and reads well on an iPhone in portrait, in every theme.
- [ ] The site loads at `https://<username>.github.io/SFFLibrary/`.
- [ ] The browser's network panel shows requests only to the site's own address, with no Google, Meta or analytics requests.
