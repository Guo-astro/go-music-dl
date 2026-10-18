import json
import re
import time
import urllib.request

from playwright.sync_api import sync_playwright


BASE_URL = "http://127.0.0.1:18093"
PLAYLIST_PATH = (
    "/music/playlist?id=2237551001&source=netease"
    "&track_count=211&page_size=200"
)
SOURCE_PAGE_URL = "http://127.0.0.1:8083" + PLAYLIST_PATH


def main():
    with urllib.request.urlopen(SOURCE_PAGE_URL, timeout=90) as response:
        html = response.read().decode("utf-8")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        context.route(
            re.compile(r".*/music/playlist\?.*"),
            lambda route: route.fulfill(
                status=200,
                content_type="text/html; charset=utf-8",
                body=html,
            ),
        )
        page = context.new_page()
        page.add_init_script(
            """
            (() => {
              const nativeFetch = window.fetch.bind(window);
              const state = {
                startedAt: performance.now(),
                lastStartAt: 0,
                finished: 0,
                active: 0,
                maxActive: 0,
              };
              window.__inspectBenchmark = state;
              const wait = (delay, signal) => new Promise((resolve, reject) => {
                const timer = setTimeout(resolve, delay);
                if (!signal) return;
                const abort = () => {
                  clearTimeout(timer);
                  reject(new DOMException("Aborted", "AbortError"));
                };
                if (signal.aborted) abort();
                else signal.addEventListener("abort", abort, { once: true });
              });
              window.fetch = async (input, init = {}) => {
                const rawUrl = typeof input === "string" ? input : input.url;
                const url = new URL(rawUrl, window.location.href);
                if (!url.pathname.endsWith("/inspect")) {
                  return nativeFetch(input, init);
                }
                state.lastStartAt = performance.now() - state.startedAt;
                state.active++;
                state.maxActive = Math.max(state.maxActive, state.active);
                try {
                  await wait(100, init.signal);
                } finally {
                  state.active--;
                }
                state.finished++;
                return new Response(
                  JSON.stringify({
                    valid: true,
                    status: "valid",
                    size: "4.2MB",
                    bitrate: "320 kbps",
                  }),
                  {
                    status: 200,
                    headers: { "Content-Type": "application/json" },
                  },
                );
              };
            })();
            """
        )
        started = time.perf_counter()
        page.goto(BASE_URL + PLAYLIST_PATH, wait_until="commit", timeout=60000)
        page.wait_for_selector(".song-card", timeout=60000)
        cards = page.locator(".song-card").count()
        page.wait_for_function(
            "count => window.__inspectBenchmark.finished >= count",
            arg=cards,
            timeout=30000,
        )
        result = page.evaluate("window.__inspectBenchmark")
        result["cards"] = cards
        result["wallSeconds"] = round(time.perf_counter() - started, 3)
        print(json.dumps(result, indent=2), flush=True)
        browser.close()

    if result["maxActive"] > 32:
        raise SystemExit("same-source concurrency exceeded 32")


if __name__ == "__main__":
    main()
