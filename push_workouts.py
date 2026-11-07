"""Upload planned workouts from workouts/*.json to the Intervals.icu calendar.

Each file is a list of {date, type, name, description}. Re-running is safe:
events are upserted by external_id, so an edited file replaces the old workout.
Intervals.icu then sends planned workouts on to Garmin Connect (if enabled there).
"""
import base64, glob, json, os, sys, requests

athlete = os.environ["ATHLETE_ID"]
key = os.environ["INTERVALS_KEY"]
auth = "Basic " + base64.b64encode(f"API_KEY:{key}".encode()).decode()

events = []
for path in sorted(glob.glob("workouts/*.json")):
    for w in json.load(open(path)):
        events.append({
            "category": "WORKOUT",
            "start_date_local": w["date"] + "T00:00:00",
            "type": w["type"],
            "name": w["name"],
            "description": w["description"],
            "external_id": f"plan-{w['date']}-{w['type']}-{w['name']}".replace(" ", "_"),
        })

if not events:
    print("No workouts to upload"); sys.exit(0)

r = requests.post(
    f"https://intervals.icu/api/v1/athlete/{athlete}/events/bulk",
    params={"upsert": "true"},
    headers={"Authorization": auth, "Content-Type": "application/json"},
    data=json.dumps(events), timeout=60,
)
print(r.status_code, r.text[:500])
r.raise_for_status()
print(f"Uploaded {len(events)} workouts")
