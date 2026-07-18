"""Fetch the Airbnb iCal feed and write availability.json for the site calendar."""
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

ics = urllib.request.urlopen(url, timeout=30).read().decode("utf-8", "replace")
busy = []
for event in re.findall(r"BEGIN:VEVENT.*?END:VEVENT", ics, re.S):
    s = re.search(r"DTSTART;VALUE=DATE:(\d{8})", event)
    e = re.search(r"DTEND;VALUE=DATE:(\d{8})", event)
    if s and e:
        fmt = lambda x: f"{x[:4]}-{x[4:6]}-{x[6:]}"
        busy.append([fmt(s.group(1)), fmt(e.group(1))])

busy.sort()
out = {
    "updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    "busy": busy,
}
with open("availability.json", "w") as f:
    json.dump(out, f, indent=1)
print(f"Wrote availability.json with {len(busy)} busy ranges.")
