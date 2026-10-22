"""Archive processed comments and clear zero ratings from a backed-up host review."""
import json
import time
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / "build/pixel-host-review-20261018.json"
target = root / "build/processed-host-review-20261018.json"
data = json.loads(source.read_text(encoding="utf-8"))
reviews = data.setdefault("reviews", {})
resolved = data.setdefault("resolvedReviews", [])
to_resolve = [qid for qid, review in reviews.items()
              if review.get("comment", "").strip() or review.get("difficulty") == 0]
now = int(time.time() * 1000)
for qid in to_resolve:
    old = reviews[qid]
    resolved.append({"review": old, "resolvedAt": now})
    rating = old.get("difficulty")
    if rating and rating > 0:
        cleared = dict(old, comment="", updatedAt=now)
        reviews[qid] = cleared
    else:
        del reviews[qid]

if any(r.get("comment", "").strip() or r.get("difficulty") == 0 for r in reviews.values()):
    raise SystemExit("Active comments or zero ratings remain after processing")
target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Archived {len(to_resolve)} feedback records; cleared {sum(1 for qid in to_resolve if qid not in reviews)} zero-rating reviews; retained {len(reviews)} positive ratings.")
