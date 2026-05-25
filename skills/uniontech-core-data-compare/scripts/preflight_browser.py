#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
import subprocess

from opencli_live_common import close_session, with_profile


def run(cmd: list[str]) -> tuple[int, str]:
    env = os.environ.copy()
    env.setdefault("OPENCLI_WINDOW_FOCUSED", "0")
    proc = subprocess.run(with_profile(cmd), capture_output=True, text=True, env=env)
    return proc.returncode, (proc.stdout or proc.stderr).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", default="core-data-preflight")
    parser.add_argument("--url", default="https://datan.uniontech.com/#/point/point-overview")
    args = parser.parse_args()

    checks = {}

    try:
        checks["opencli_doctor"] = run(["opencli", "doctor"])
        run(["opencli", "browser", args.session, "open", args.url])
        _, page = run(["opencli", "browser", args.session, "eval", "JSON.stringify({href:location.href,title:document.title,token:!!localStorage.getItem('_token'),tokenRaw:localStorage.getItem('_token'),body:(document.body.innerText||'').slice(0,500)})"])

        checks["target_url"] = args.url
        checks["page_probe"] = page

        page_has_token = False
        page_loaded = False
        route_ok = False
        permission_ok = True
        logged_in = False
        token_expired = None
        token_expired_at = ""
        try:
            outer = json.loads(page)
            inner = json.loads(outer.get("data", "{}")) if isinstance(outer, dict) else {}
            page_has_token = bool(inner.get("token"))
            page_loaded = bool(inner.get("title"))
            href = inner.get("href", "")
            route_ok = href.startswith("https://datan.uniontech.com/#/point/") or href.startswith("https://datan.uniontech.com/#/app/")
            body = inner.get("body", "")
            token_raw = inner.get("tokenRaw", "")
            if token_raw:
                try:
                    token_obj = json.loads(token_raw)
                    exp = token_obj.get("expired")
                    if exp:
                        token_expired_at = datetime.fromtimestamp(exp).strftime("%Y-%m-%d %H:%M:%S")
                        token_expired = datetime.now().timestamp() >= exp
                except Exception:
                    pass
            logged_in = page_has_token and "#/login" not in href and "未登录或登录已过期" not in body
            permission_ok = "暂无权限" not in body and "401" not in body
        except Exception:
            page_has_token = "\"token\":true" in page.replace(" ", "")
            page_loaded = "title" in page
            route_ok = "#/point/" in page or "#/app/" in page
            logged_in = page_has_token and "#/login" not in page and "未登录或登录已过期" not in page
            permission_ok = "暂无权限" not in page and "401" not in page

        result = {
            "browser_bridge_ready": checks["opencli_doctor"][0] == 0,
            "target_url_ok": True,
            "page_loaded": page_loaded,
            "logged_in": logged_in,
            "token_found": page_has_token,
            "token_expired": token_expired,
            "token_expired_at": token_expired_at,
            "route_ok": route_ok,
            "permission_ok": permission_ok,
            "session": args.session,
            "raw": checks,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        close_session(args.session)


if __name__ == "__main__":
    main()
