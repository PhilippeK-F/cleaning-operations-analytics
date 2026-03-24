import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_PATH = Path("data/raw/cleaning_tasks.csv")

SITES = [
    ("SITE-001", "Strasbourg Production Site", 48.5734, 7.7521),
    ("SITE-002", "Lyon Logistics Center", 45.7640, 4.8357),
    ("SITE-003", "Paris Headquarters", 48.8566, 2.3522),
    ("SITE-004", "Marseille Laboratory", 43.2965, 5.3698),
]

ZONE_TYPES = {
    "production": ["Assembly Line A", "Assembly Line B", "Packaging Area"],
    "warehouse": ["Storage Zone 1", "Storage Zone 2", "Loading Dock"],
    "office": ["Open Space", "Meeting Rooms", "Reception"],
    "restroom": ["Restroom North", "Restroom South"],
    "laboratory": ["Chemistry Lab", "Testing Lab"],
}

TASKS_BY_ZONE = {
    "production": [
        ("Floor scrubbing", "machine", 60),
        ("Machine surface cleaning", "manual", 45),
        ("Degreasing", "manual", 90),
        ("Safety area cleaning", "manual", 30),
    ],
    "warehouse": [
        ("Floor sweeping", "machine", 45),
        ("Dock cleaning", "manual", 60),
        ("Dust removal", "manual", 30),
        ("Spill cleanup", "manual", 20),
    ],
    "office": [
        ("Desk area cleaning", "manual", 30),
        ("Floor vacuuming", "machine", 45),
        ("Trash collection", "manual", 20),
        ("Glass cleaning", "manual", 25),
    ],
    "restroom": [
        ("Disinfection", "disinfection", 40),
        ("Restocking supplies", "manual", 20),
        ("Floor cleaning", "manual", 30),
        ("Waste removal", "manual", 15),
    ],
    "laboratory": [
        ("Surface disinfection", "disinfection", 45),
        ("Controlled area cleaning", "manual", 60),
        ("Equipment exterior cleaning", "manual", 40),
        ("Contamination prevention cleaning", "disinfection", 50),
    ],
}

TEAMS = ["Team A", "Team B", "Team C", "Team D"]
STATUSES = ["planned", "in_progress", "completed", "delayed"]
RISK_LEVELS = ["low", "medium", "high"]
FOOT_TRAFFIC = ["low", "medium", "high"]


def random_date(days_back: int = 45) -> datetime:
    now = datetime.now()
    return now - timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )


def compute_priority_score(
    zone_type: str,
    dirt_level: int,
    status: str,
    days_since_last_cleaning: int,
    foot_traffic: str,
    risk_level: str,
) -> int:
    score = 0

    if zone_type in ["production", "laboratory"]:
        score += 3
    if dirt_level >= 4:
        score += 2
    if status == "delayed":
        score += 2
    if days_since_last_cleaning > 7:
        score += 2
    if foot_traffic == "high":
        score += 1
    if risk_level == "high":
        score += 1

    return score


def generate_row(i: int) -> dict:
    site_id, site_name, lat, lon = random.choice(SITES)
    zone_type = random.choices(
        ["production", "warehouse", "office", "restroom", "laboratory"],
        weights=[25, 25, 20, 15, 15],
        k=1,
    )[0]
    zone_name = random.choice(ZONE_TYPES[zone_type])

    task_type, cleaning_method, estimated_duration_min = random.choice(TASKS_BY_ZONE[zone_type])

    status = random.choices(
        STATUSES,
        weights=[25, 15, 45, 15],
        k=1,
    )[0]
    dirt_level = random.randint(1, 5)
    risk_level = random.choices(RISK_LEVELS, weights=[35, 40, 25], k=1)[0]
    foot_traffic = random.choices(FOOT_TRAFFIC, weights=[25, 35, 40], k=1)[0]
    days_since_last_cleaning = random.randint(0, 14)
    quality_score = round(random.uniform(60, 100), 1)

    if status == "delayed":
        quality_score = round(random.uniform(45, 80), 1)
    if dirt_level >= 4:
        quality_score = min(quality_score, round(random.uniform(50, 85), 1))

    scheduled_date = random_date()
    completed_date = scheduled_date + timedelta(minutes=estimated_duration_min)
    if status in ["planned", "delayed"]:
        completed_value = ""
    else:
        completed_value = completed_date.strftime("%Y-%m-%d %H:%M:%S")

    priority_score = compute_priority_score(
        zone_type=zone_type,
        dirt_level=dirt_level,
        status=status,
        days_since_last_cleaning=days_since_last_cleaning,
        foot_traffic=foot_traffic,
        risk_level=risk_level,
    )

    return {
        "task_id": f"TASK-{i:04d}",
        "site_id": site_id,
        "site_name": site_name,
        "zone_id": f"ZONE-{random.randint(100, 999)}",
        "zone_name": zone_name,
        "zone_type": zone_type,
        "task_type": task_type,
        "cleaning_method": cleaning_method,
        "estimated_duration_min": estimated_duration_min,
        "cleaning_team": random.choice(TEAMS),
        "scheduled_date": scheduled_date.strftime("%Y-%m-%d %H:%M:%S"),
        "completed_date": completed_value,
        "status": status,
        "dirt_level": dirt_level,
        "risk_level": risk_level,
        "foot_traffic": foot_traffic,
        "days_since_last_cleaning": days_since_last_cleaning,
        "quality_score": quality_score,
        "priority_score": priority_score,
        "latitude": lat,
        "longitude": lon,
    }


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows = [generate_row(i) for i in range(1, 501)]

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "task_id",
                "site_id",
                "site_name",
                "latitude",
                "longitude",
                "zone_id",
                "zone_name",
                "zone_type",
                "task_type",
                "cleaning_method",
                "estimated_duration_min",
                "cleaning_team",
                "scheduled_date",
                "completed_date",
                "status",
                "dirt_level",
                "risk_level",
                "foot_traffic",
                "days_since_last_cleaning",
                "quality_score",
                "priority_score",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(rows)} cleaning tasks generated in {OUTPUT_PATH}")


if __name__ == "__main__":
    main()