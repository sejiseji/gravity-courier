"""Patch Pyxel app2html output for Gravity Courier web publishing."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


DEFAULT_WEB_APP_NAME = "gravity-courier-public.pyxapp"
PATCH_MARKER = "<!-- gravity-courier mobile viewport patch -->"
GAME_WIDTH = 393
GAME_HEIGHT = 852


MOBILE_VIEWPORT_PATCH = f"""{PATCH_MARKER}
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no">
<style>
  :root {{
    --gc-vw: 100vw;
    --gc-vh: 100vh;
  }}

  html,
  body {{
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
    overflow: hidden;
    background: #000;
    overscroll-behavior: none;
    touch-action: none;
  }}

  body {{
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    width: var(--gc-vw);
    height: var(--gc-vh);
    box-sizing: border-box;
    padding:
      env(safe-area-inset-top)
      env(safe-area-inset-right)
      env(safe-area-inset-bottom)
      env(safe-area-inset-left);
  }}

  canvas {{
    display: block;
    image-rendering: pixelated;
    image-rendering: crisp-edges;
    touch-action: none;
  }}
</style>
<script>
(() => {{
  const GAME_WIDTH = {GAME_WIDTH};
  const GAME_HEIGHT = {GAME_HEIGHT};
  let pendingFrame = 0;

  const safeAreaProbe = () => {{
    let probe = document.getElementById("gc-safe-area-probe");
    if (!probe) {{
      probe = document.createElement("div");
      probe.id = "gc-safe-area-probe";
      probe.setAttribute("aria-hidden", "true");
      probe.style.cssText = [
        "position:fixed",
        "visibility:hidden",
        "pointer-events:none",
        "padding:env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)"
      ].join(";");
      document.documentElement.appendChild(probe);
    }}
    return probe;
  }};

  const readSafeArea = () => {{
    const style = getComputedStyle(safeAreaProbe());
    return {{
      top: parseFloat(style.paddingTop) || 0,
      right: parseFloat(style.paddingRight) || 0,
      bottom: parseFloat(style.paddingBottom) || 0,
      left: parseFloat(style.paddingLeft) || 0
    }};
  }};

  const viewportSize = () => {{
    const viewport = window.visualViewport;
    return {{
      width: Math.floor((viewport && viewport.width) || window.innerWidth || GAME_WIDTH),
      height: Math.floor((viewport && viewport.height) || window.innerHeight || GAME_HEIGHT)
    }};
  }};

  const fitCanvasToVisibleViewport = () => {{
    pendingFrame = 0;
    const viewport = viewportSize();
    const safe = readSafeArea();
    const body = document.body;
    if (body) {{
      body.style.width = `${{viewport.width}}px`;
      body.style.height = `${{viewport.height}}px`;
      document.documentElement.style.setProperty("--gc-vw", `${{viewport.width}}px`);
      document.documentElement.style.setProperty("--gc-vh", `${{viewport.height}}px`);
    }}

    const availableWidth = Math.max(1, viewport.width - safe.left - safe.right);
    const availableHeight = Math.max(1, viewport.height - safe.top - safe.bottom);
    const scale = Math.min(availableWidth / GAME_WIDTH, availableHeight / GAME_HEIGHT);
    const canvas = document.querySelector("canvas");
    if (!canvas) {{
      return;
    }}

    canvas.style.width = `${{Math.floor(GAME_WIDTH * scale)}}px`;
    canvas.style.height = `${{Math.floor(GAME_HEIGHT * scale)}}px`;
    canvas.style.maxWidth = `${{availableWidth}}px`;
    canvas.style.maxHeight = `${{availableHeight}}px`;
    canvas.style.margin = "0";
  }};

  const requestFit = () => {{
    if (pendingFrame) {{
      return;
    }}
    pendingFrame = requestAnimationFrame(fitCanvasToVisibleViewport);
  }};

  window.addEventListener("resize", requestFit, {{ passive: true }});
  window.addEventListener("orientationchange", requestFit, {{ passive: true }});
  document.addEventListener("DOMContentLoaded", requestFit);
  window.addEventListener("load", requestFit, {{ passive: true }});
  if (window.visualViewport) {{
    window.visualViewport.addEventListener("resize", requestFit, {{ passive: true }});
    window.visualViewport.addEventListener("scroll", requestFit, {{ passive: true }});
  }}

  new MutationObserver(requestFit).observe(document.documentElement, {{
    childList: true,
    subtree: true
  }});

  let warmupFrames = 0;
  const warmup = () => {{
    requestFit();
    warmupFrames += 1;
    if (warmupFrames < 20) {{
      window.setTimeout(warmup, 250);
    }}
  }};
  warmup();
}})();
</script>
"""


def patch_pyxel_html(
    html: str,
    *,
    app_name: str = DEFAULT_WEB_APP_NAME,
    gamepad: str = "disabled",
) -> str:
    """Return Pyxel app2html output with Gravity Courier web fixes applied."""

    html = re.sub(r'name:\s*"[^"]+\.pyxapp"', f'name: "{app_name}"', html, count=1)
    html = re.sub(r'gamepad:\s*"(enabled|disabled)"', f'gamepad: "{gamepad}"', html, count=1)
    if PATCH_MARKER in html:
        return html
    if "<!doctype html>\n" in html:
        return html.replace("<!doctype html>\n", "<!doctype html>\n" + MOBILE_VIEWPORT_PATCH, 1)
    return MOBILE_VIEWPORT_PATCH + html


def patch_file(source: Path, destination: Path, *, app_name: str, gamepad: str) -> None:
    html = source.read_text(encoding="utf-8")
    destination.write_text(
        patch_pyxel_html(html, app_name=app_name, gamepad=gamepad),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--app-name", default=DEFAULT_WEB_APP_NAME)
    parser.add_argument("--gamepad", choices=("enabled", "disabled"), default="disabled")
    args = parser.parse_args()

    patch_file(args.source, args.destination, app_name=args.app_name, gamepad=args.gamepad)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
