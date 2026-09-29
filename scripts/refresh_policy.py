#!/usr/bin/env python3
"""Publish a short-lived Podmate policy without secrets or fake purchase state."""

import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "plan-config.json"
OUTPUT = ROOT / "docs" / "managed-policy.json"
ALLOWED = {"schemaVersion", "policyID", "currency", "catalogProductID",
           "catalogPriceCents", "freeAllowanceNanoUSD", "monthlyLimitNanoUSD"}


def main() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    if set(config) != ALLOWED or config["schemaVersion"] != 1 or config["currency"] != "USD":
        raise ValueError("invalid policy schema")
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,64}", config["policyID"]):
        raise ValueError("invalid policy ID")
    product = config["catalogProductID"]
    price = config["catalogPriceCents"]
    if (product is None) != (price is None):
        raise ValueError("product and reference price must be configured together")
    if product is not None and (not re.fullmatch(r"[A-Za-z0-9._-]{8,128}", product)
                                or not isinstance(price, int) or not 1 <= price <= 100_000_000):
        raise ValueError("invalid product or price")
    free = config["freeAllowanceNanoUSD"]
    limit = config["monthlyLimitNanoUSD"]
    if (not isinstance(free, int) or not isinstance(limit, int)
            or not 0 <= free <= limit <= 1_000_000_000_000 or limit == 0):
        raise ValueError("invalid allowance")
    previous = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else {}
    now = int(time.time())
    revision = max(now, int(previous.get("revision", 0)) + 1)
    result = {**config, "revision": revision, "effectiveAtEpoch": now - 60,
              "expiresAtEpoch": now + 6 * 86400}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n",
                      encoding="utf-8")
    print(f"policy_revision={revision}; valid_for_days=6")


if __name__ == "__main__":
    main()
