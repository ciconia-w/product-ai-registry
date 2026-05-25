#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
from typing import Any


def resolve_profile() -> str:
    env_profile = os.environ.get("OPENCLI_PROFILE", "").strip()
    if env_profile:
        return env_profile
    proc = subprocess.run(["opencli", "profile", "list"], capture_output=True, text=True)
    text = (proc.stdout or proc.stderr or "").strip()
    match = re.search(r"^\s*([A-Za-z0-9_-]+)\s+— connected\b", text, re.MULTILINE)
    return match.group(1) if match else ""


def with_profile(cmd: list[str]) -> list[str]:
    if not cmd or cmd[0] != "opencli":
        return cmd
    profile = resolve_profile()
    if not profile:
        return cmd
    return ["opencli", "--profile", profile, *cmd[1:]]


def run(cmd: list[str]) -> str:
    env = os.environ.copy()
    env.setdefault("OPENCLI_WINDOW_FOCUSED", "0")
    proc = subprocess.run(with_profile(cmd), capture_output=True, text=True, check=True, env=env)
    return proc.stdout.strip()


def browser_eval(js: str, session: str = "default") -> Any:
    out = run(["opencli", "browser", session, "eval", js])
    try:
        payload = json.loads(out)
    except json.JSONDecodeError:
        return out
    if isinstance(payload, dict) and "data" in payload:
        data = payload["data"]
        if isinstance(data, str):
            try:
                return json.loads(data)
            except Exception:
                return data
        return data
    return payload


def ensure_page(url: str, session: str = "default", wait_seconds: int = 2) -> None:
    run(["opencli", "browser", session, "open", url])
    run(["opencli", "browser", session, "wait", "time", str(wait_seconds)])


def close_session(session: str = "default") -> None:
    try:
        listing = run(["opencli", "browser", session, "tab", "list"])
        pages = json.loads(listing) if listing else []
        for page in pages:
            page_id = page.get("page")
            if page_id:
                try:
                    run(["opencli", "browser", session, "tab", "close", page_id])
                except Exception:
                    pass
        run(["opencli", "browser", session, "close"])
    except Exception:
        pass


def get_token(session: str = "default") -> str:
    data = browser_eval(
        "JSON.stringify({token:(() => { try { return JSON.parse(localStorage.getItem('_token') || '{}').token || '' } catch(e){ return '' } })()})",
        session=session,
    )
    if isinstance(data, dict):
        return data.get("token", "")
    return ""


def live_fetch(path: str, body: dict, session: str = "default") -> dict:
    payload = json.dumps(body, ensure_ascii=False)
    js = f"""
    (async () => {{
      const raw = localStorage.getItem('_token') || '{{}}';
      const tk = JSON.parse(raw).token;
      const headers = {{
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'token': tk,
        'authtoken': 'Bearer ' + tk
      }};
      const res = await fetch('{path}', {{
        method: 'POST',
        headers,
        body: JSON.stringify({payload})
      }});
      const txt = await res.text();
      return JSON.stringify({{status: res.status, body: txt}});
    }})()
    """
    data = browser_eval(js, session=session)
    if isinstance(data, dict):
        if isinstance(data.get("body"), str):
            try:
                data["body_json"] = json.loads(data["body"])
            except Exception:
                pass
        return data
    return {"status": None, "body": data}
