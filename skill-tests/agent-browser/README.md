# agent-browser capability tour

Artifacts produced by a single end-to-end run on 2026-05-21 to demonstrate
distinctive agent-browser capabilities. Each numbered group is one demo.

## 00 — Annotated UI map (multimodal)

Visible labels `[N]` on the screenshot map 1:1 to `@eN` refs returned by
`snapshot -i`. Lets a vision model "see" actionable elements without HTML.

- `jbhifi-annotated.png` — JB Hi-Fi homepage with 436 ref labels
- `30-hn-annotated.png` — Hacker News annotated

## 01–05 — Real login flow on saucedemo.com

Sandbox e-commerce login + product extraction. Demonstrates form fill,
keyboard fallback when `click` ignored, JS-eval extraction of structured
data.

- `01-login-success.png` — post-login inventory page
- `02-products.json` — six products extracted into JSON
- `03-cart-3items.png`, `04-cart-page.png` — cart flow attempt
  (saucedemo's session storage purges across direct CDP nav, included as
  honest failure mode)

## 10–11 — Live scrape on Hacker News

`screenshot --full` for full scroll height + structured top-10 extraction
via `eval --stdin` against the page DOM.

- `10-hn-fullpage.png` — full-page screenshot (entire scroll height)
- `11-hn-top10.json` — title, url, score, author, age, comments per story

## 20–22 — Search + structured article extraction

DDG hit a "select all squares with a duck" bot challenge — kept the
screenshot as a real-world capability boundary. Switched to Wikipedia,
which redirected straight to the article; extracted infobox + first
paragraph + section headings.

- `20-search-results.png` — Wikipedia article post-redirect
- `20-ddg-results.png` — DDG bot challenge screenshot
- `21-search-results.json` — empty (page redirected straight to article)
- `22-rust-wikipedia.json` — title, summary, sections, 12 infobox rows

## 40 — Time-lapse (rotating banners)

Two screenshots ~4s apart of the JB Hi-Fi homepage. Useful for visual
regression / rotating-content detection.

- `40-jbhifi-t0.png`, `40-jbhifi-t4.png`

## 50 — Mega-menu interaction

Clicked the "Brands" nav button and captured the open mega-menu state.

- `50-jbhifi-brands-menu.png`

## 60 — App-level state lift

`eval --stdin` reaches into `window.Shopify` / `window.ShopifyAnalytics`
to extract platform metadata that's invisible to plain `fetch` /
`WebFetch`. JB Hi-Fi turned out to be Shopify, not Next.js.

- `60-jbhifi-state.json` — Next.js probe (negative result, but useful
  diagnostic)
- `60-jbhifi-shopify.json` — Shopify shop id, currency, country, locale,
  page type

## Capabilities exercised

| Capability                                  | Demo |
|---------------------------------------------|------|
| `open` + `wait --load networkidle`          | all  |
| `snapshot -i -c -d N` (a11y tree + refs)    | 00, 01 |
| `screenshot` / `--full` / `--annotate`      | 00, 10, 30 |
| `fill` + `press Enter` (form submit)        | 01, 04 |
| `click @eN` (ref-based action)              | 01, 06 |
| `find role/text/testid` (semantic locators) | 06 |
| Raw CSS selectors                           | 04 |
| `eval --stdin` (arbitrary JS in page)       | 02, 05, 11, 22, 60 |
| `tab new/close/<id>` (multi-tab)            | 03 |
| `get url`/`get text`/`get count`            | 03, 04 |
| `wait --fn`                                 | 04 |
| `close --all`                               | end |

## Capabilities NOT exercised here

- Auth vault (`auth save/login`) — needs real creds
- `state save/load` for persistent sessions
- Video recording
- Electron-app driving (would need `electron` skill)
- Slack automation (would need `slack` skill)
- Vercel Sandbox / AWS Bedrock AgentCore cloud browsers
