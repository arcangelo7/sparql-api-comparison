import contextlib
import http.client
import http.cookiejar
import json
import logging
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[%(name)s] %(message)s")
logger = logging.getLogger("register")

BASE = os.environ["BASIL_BASE"]
USER = "demo"
PASS = "demo"  # noqa: S105
STATE = Path("/state/api-id")

opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
)


def request(
    url: str,
    data: bytes | None = None,
    method: str | None = None,
    headers: dict[str, str] | None = None,
) -> http.client.HTTPResponse:
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    return opener.open(req, timeout=120)


def reachable(url: str) -> bool:
    try:
        request(url)
    except urllib.error.URLError:
        return False
    return True


while not reachable(f"{BASE}/basil/"):
    time.sleep(3)

if STATE.exists():
    api_id = STATE.read_text().strip()
    if reachable(f"{BASE}/basil/{api_id}/spec"):
        logger.info("API already registered: %s", api_id)
        sys.exit(0)

with contextlib.suppress(urllib.error.HTTPError):
    request(
        f"{BASE}/basil/users",
        data=json.dumps(
            {"username": USER, "password": PASS, "email": f"{USER}@example.org"},
        ).encode(),
        method="POST",
        headers={"Content-type": "application/json"},
    )

request(
    f"{BASE}/basil/auth/login",
    data=json.dumps({"username": USER, "password": PASS}).encode(),
    method="POST",
    headers={"Content-type": "application/json"},
)

resp = (
    request(
        f"{BASE}/basil/?endpoint=https://sparql.opencitations.net/meta",
        data=Path("/init/meta.rq").read_bytes(),
        method="PUT",
        headers={"Content-type": "application/sparql-query"},
    )
    .read()
    .decode()
)

api_id = json.loads(resp)["location"].rstrip("/").rsplit("/", 1)[-1]
STATE.write_text(api_id)
