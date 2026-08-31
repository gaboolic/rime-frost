"""Download today's Zhihu hot list and save it as a benchmark corpus file.

Writes entries in the same layout as ``data/corpus/news.txt``: a ``链接：``
line with the question URL, then the question title and the top answer's
body text.

The hot list comes from a third-party aggregation API (no login needed).
The full answer bodies are read by rendering each ``/question/<id>`` page in a
real Chromium (Playwright). Zhihu gates its detail pages behind a JS challenge
(``__zse_ck`` / ``x-zse-96``) that flags plain HTTP clients *and* detectable
automation (e.g. ``navigator.webdriver``), returning HTTP 403 / ``40362``.
This script therefore launches Chromium with a stealth init script so the
challenge is solved normally and the answer text can be scraped from the DOM.
No Zhihu login is required.

Usage (from repository root):

  python scripts/download_zhihu_hotlist.py
  python scripts/download_zhihu_hotlist.py --limit 30 --delay 1
  python scripts/download_zhihu_hotlist.py --headed          # visible browser, for debugging

Requires: pip install playwright && playwright install chromium
"""

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

DEFAULT_API = "https://uapis.cn/api/v1/misc/hotboard?type=zhihu"
ROOT = Path(__file__).resolve().parent.parent

_TAG_RE = re.compile(r"<[^>]+>")
_QID_RE = re.compile(r"/question/(\d+)")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

_STEALTH_JS = r"""
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
window.chrome = { runtime: {} };
const _permQuery = navigator.permissions && navigator.permissions.query;
if (_permQuery) {
  navigator.permissions.query = (p) =>
    p && p.name === 'notifications'
      ? Promise.resolve({ state: Notification.permission })
      : _permQuery(p);
}
"""

_EXTRACT_JS = r"""() => {
  const items = document.querySelectorAll('.List-item');
  for (const item of items) {
    const rich = item.querySelector('.RichContent-inner');
    if (rich && rich.innerText.trim()) return rich.innerText.trim();
  }
  return '';
}"""


def _ssl_context():
    ctx = __import__("ssl").create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = __import__("ssl").CERT_NONE
    return ctx


def _fetch_json(url: str, proxy: str = "", timeout: int = 30) -> dict:
    handlers = []
    if proxy:
        handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    handlers.append(urllib.request.HTTPSHandler(context=_ssl_context()))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.build_opener(*handlers).open(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _clean(text: str) -> str:
    text = html.unescape(_TAG_RE.sub("", text or ""))
    return re.sub(r"\s+", " ", text).strip()


def download(limit: int = 30, api: str = DEFAULT_API, proxy: str = "") -> list:
    payload = _fetch_json(api, proxy=proxy)
    rows = payload.get("list", [])
    if not isinstance(rows, list):
        raise RuntimeError("unexpected payload from API: missing 'list'")
    return rows[:limit]


class _ZhihuBrowser:
    """Stealth Chromium session used to render question pages and read answers."""

    def __init__(self, proxy: str = "", headed: bool = False):
        from playwright.sync_api import sync_playwright

        self._pw = sync_playwright()
        self._playwright = self._pw.start()
        launch_kwargs = {"headless": not headed, "args": ["--disable-blink-features=AutomationControlled"]}
        if proxy:
            launch_kwargs["proxy"] = {"server": proxy}
        self._browser = self._playwright.chromium.launch(**launch_kwargs)
        self._context = self._browser.new_context(
            user_agent=UA,
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
            viewport={"width": 1600, "height": 900},
        )
        self._context.add_init_script(_STEALTH_JS)

    def fetch_top_answer(self, qid: str) -> str:
        page = self._context.new_page()
        try:
            page.goto(f"https://www.zhihu.com/question/{qid}", timeout=45000, wait_until="domcontentloaded")
            try:
                page.wait_for_selector(".List-item .RichContent-inner", timeout=30000)
            except Exception:
                return ""
            return _clean(page.evaluate(_EXTRACT_JS))
        except Exception as e:
            print(f"  [skip] {qid}: {e}", file=sys.stderr)
            return ""
        finally:
            page.close()

    def close(self) -> None:
        try:
            self._context.close()
        finally:
            self._playwright.stop()


def write_corpus(rows: list, out: Path, browser: "_ZhihuBrowser | None" = None, delay: float = 1.0) -> int:
    lines = []
    fetched = 0
    for i, item in enumerate(rows):
        url = item.get("url", "")
        title = _clean(item.get("title", ""))
        desc = _clean((item.get("extra") or {}).get("desc", ""))
        lines.append(f"链接：{url}")
        if title:
            lines.append(title)
        body = ""
        if browser:
            m = _QID_RE.search(url)
            if m:
                body = browser.fetch_top_answer(m.group(1))
        if body:
            fetched += 1
            lines.append(body)
        elif desc:
            lines.append(desc)
        if i < len(rows) - 1 and delay:
            time.sleep(delay)
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"fetched full bodies for {fetched}/{len(rows)} items (others use hot-list excerpt)")
    return len(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Download today's Zhihu hot list as a corpus file")
    parser.add_argument("--limit", type=int, default=30, help="how many hot-list items to fetch (default: 30)")
    parser.add_argument("--out", type=Path, default=None, help="output .txt path (default: data/corpus/zhihu_hotlist_YYYY-MM-DD.txt)")
    parser.add_argument("--api", default=DEFAULT_API, help="hot-list API URL (default: %(default)s)")
    parser.add_argument("--proxy", default=None, help="proxy for all requests, e.g. http://127.0.0.1:7890 (or set ALL_PROXY)")
    parser.add_argument("--headed", action="store_true", help="run Chromium with a visible window")
    parser.add_argument("--delay", type=float, default=1.0, help="extra seconds to wait between questions (default: 1)")
    args = parser.parse_args(argv)

    proxy = args.proxy or os.environ.get("ALL_PROXY") or os.environ.get("HTTPS_PROXY") or ""
    if args.out is None:
        args.out = ROOT / "data" / "corpus" / f"zhihu_hotlist_{date.today().isoformat()}.txt"

    rows = download(limit=args.limit, api=args.api, proxy=proxy)
    if not rows:
        print("no items returned by API", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)

    browser = None
    try:
        browser = _ZhihuBrowser(proxy=proxy, headed=args.headed)
    except ImportError:
        print("warning: playwright is not installed (pip install playwright && playwright install chromium); "
              "hot-list excerpt only", file=sys.stderr)

    try:
        n_lines = write_corpus(rows, args.out, browser=browser, delay=args.delay)
    finally:
        if browser:
            browser.close()
    print(f"wrote {len(rows)} hot-list items ({n_lines} lines) -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
