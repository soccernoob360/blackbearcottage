"""Fetch the booking-calendar iCal feed (Lodgify or Airbnb) and write availability.json."""
import datetime
import json
import os
import re
import sys
import urllib.request

url = os.environ.get("AIRBNB_ICAL_URL", "").strip()
if not url:
    print("AIRBNB_ICAL_URL secret is not set - skipping (add it in repo Settings > Secrets > Actions).")
    sys.exit(0)

req = urllib.request.Request(url, headers={"User-Agent": "blackbearcottage-site-calendar"})
ics = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

def get_date(event, field):
    """Match DTSTART/DTEND in any common iCal form: DTSTART;VALUE=DATE:20260718,
    DTSTART:20260718T140000Z, DTSTART;TZID=America/New_York:20260718T150000."""
    m = re.search(field + r"(?:;[^:\n]*)?:(\d{8})", event)
    return m.group(1) if m else None

busy = []
for event in re.findall(r"BEGIN:VEVENT.*?END:VEVENT", ics, re.S):
    s = get_date(event, "DTSTART")
    e = get_date(event, "DTEND")
    if s and e:
        fmt = lambda x: f"{x[:4]}-{x[4:6]}-{x[6:]}"
        start, end = fmt(s), fmt(e)
        if end <= start:  # zero/negative-length safety: block at least one night
            end = (datetime.date.fromisoformat(start) + datetime.timedelta(days=1)).isoformat()
        busy.append([start, end])

busy.sort()
# merge overlapping/adjacent ranges so the JSON stays small
merged = []
for start, end in busy:
    if merged and start <= merged[-1][1]:
        merged[-1][1] = max(merged[-1][1], end)
    else:
        merged.append([start, end])

out = {
    "updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    "busy": merged,
}
with open("availability.json", "w") as f:
    json.dump(out, f, indent=1)
print(f"Wrote availability.json with {len(merged)} busy ranges.")
