# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# ============================================================
"""
GitHub Webhook: Bei Push-Event git pull im konfigurierten Verzeichnis ausführen.
Für G-MTHO Option 5 – Cloud Agents erhalten sofort aktuellen Stand.
Credentials/Secret nur über Env: GITHUB_WEBHOOK_SECRET, GIT_PULL_DIR.
"""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import os
import json
from typing import Optional

from fastapi import APIRouter, Request, Response
from loguru import logger

router = APIRouter(prefix="/webhook", tags=["webhooks"])

GITHUB_WEBHOOK_SECRET = (os.getenv("GITHUB_WEBHOOK_SECRET") or "").strip()
GIT_PULL_DIR = (os.getenv("GIT_PULL_DIR") or "").strip()
GIT_PULL_BRANCH_FILTER = (os.getenv("GIT_PULL_BRANCH_FILTER") or "").strip()  # optional, e.g. "refs/heads/master"


def _verify_github_signature(payload: bytes, signature_header: Optional[str]) -> bool:
    if not GITHUB_WEBHOOK_SECRET or not signature_header:
        return False
    if not signature_header.startswith("sha256="):
        return False
    expected = signature_header[7:]
    computed = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(f"sha256={computed}", signature_header)


@router.post("/github")
async def receive_github_webhook(request: Request) -> Response:
    """
    GitHub Webhook: X-Hub-Signature-256 prüfen, bei push-Event git pull in GIT_PULL_DIR.
    In GitHub: Settings → Webhooks → Payload URL = https://<vps>/webhook/github, Content type application/json.
    """
    payload = await request.body()
    sig = request.headers.get("X-Hub-Signature-256")

    if not _verify_github_signature(payload, sig):
        logger.warning("[github_webhook] Invalid or missing signature")
        return Response(status_code=401, content="Unauthorized")

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return Response(status_code=400, content="Invalid JSON")

    event = request.headers.get("X-GitHub-Event", "")
    if event != "push":
        return Response(status_code=200, content="ignored")

    ref = data.get("ref", "")
    if GIT_PULL_BRANCH_FILTER and ref != GIT_PULL_BRANCH_FILTER:
        logger.info(f"[github_webhook] Push ref {ref} does not match filter {GIT_PULL_BRANCH_FILTER}")
        return Response(status_code=200, content="filtered")

    if not GIT_PULL_DIR or not os.path.isdir(GIT_PULL_DIR):
        logger.warning("[github_webhook] GIT_PULL_DIR not set or not a directory")
        return Response(status_code=500, content="GIT_PULL_DIR not configured")

    try:
        proc = await asyncio.create_subprocess_exec(
            "git", "pull",
            cwd=GIT_PULL_DIR,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.warning(f"[github_webhook] git pull failed: {stderr.decode() if stderr else 'unknown'}")
            return Response(status_code=502, content=(stderr or b"git pull failed").decode()[:500])
        logger.info(f"[github_webhook] git pull ok in {GIT_PULL_DIR}")
        return Response(status_code=200, content="ok")
    except Exception as e:
        logger.exception("[github_webhook] git pull exception")
        return Response(status_code=500, content=str(e)[:500])
