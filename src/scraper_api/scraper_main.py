import os
import sys
import time
import json
import common
import random
import requests
import datetime
from loguru import logger
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, Status, Feature, Office, WaitingTime, Snapshot


STATUS_URL = "https://wartezeiten.stuttgart.de/bb/status?r="
STATUS_VALUES = [
    (0, "outside opening hours"),
    (1, "< 30 min"),
    (2, "30 min"),
    (3, "45 min"),
    (4, "60 min"),
    (5, "75 min"),
    (6, "90 min"),
    (7, "105 min"),
    (8, "120 min"),
    (10, "> 120 min"),
    (11, "no waiting stamps left"),
]


def fetch_and_check_json() -> list[dict]:
    url = f"{STATUS_URL}{random.randint(1000000000, 9999999999)}"
    resp = requests.get(url)
    if resp.status_code != 200:
        logger.error(f"Failed to fetch data from {url}: {resp.status_code}")
        raise ValueError(f"Unexpected status code {resp.status_code} from {url}")

    try:
        data = resp.json()
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        raise ValueError("Failed to parse JSON response")

    if not isinstance(data, list):
        logger.error("Expected a list of office data, but got something else.")
        raise ValueError("Expected a list of office data, but got something else.")

    if not all(isinstance(entry, dict) for entry in data):
        logger.error("Expected each entry in the list to be a dictionary.")
        raise ValueError("Expected each entry in the list to be a dictionary.")

    return data


def wait_for_next_minute():
    now = datetime.datetime.now()
    next_minute = (now + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
    sleep_time = (next_minute - now).total_seconds()
    time.sleep(sleep_time)


def setup_db_once(engine):
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        if db.get(Status, 1) is None:  # bootstrap only once
            for id, meaning in STATUS_VALUES:
                db.add(Status(id=id, meaning=meaning))

            db.commit()


def insert_data(db, data: list[dict]):
    feature_cache: dict[str, Feature] = {f.name: f for f in db.query(Feature).all()}
    office_cache: dict[int, Office] = {o.id: o for o in db.query(Office).all()}

    for entry in data:
        office = office_cache.get(entry["id"])
        if office is None:
            office = Office(
                id=entry["id"],
                label=entry["label"],
                url=entry["url"],
            )
            db.add(office)
            office_cache[office.id] = office
        else:
            # update name or URL if they changed
            office.label = entry["label"]
            office.url = entry["url"]

        # features
        office.features.clear()
        for feat in entry["features"]:
            obj = feature_cache.get(feat)
            if obj is None:
                obj = Feature(name=feat)
                db.add(obj)
                feature_cache[feat] = obj
            office.features.append(obj)

    # create snapshot + waiting-time rows
    snap = Snapshot()
    db.add(snap)
    db.flush()  # gives snap.id

    for entry in data:
        db.add(
            WaitingTime(
                office_id=entry["id"],
                snapshot_id=snap.id,
                status_id=entry["status"],
            )
        )

    db.commit()


def all_offices_closed(data):
    return all(entry["status"] == 0 for entry in data)


def it_is_nighttime():
    now = datetime.datetime.now()
    return now.hour < 5 or now.hour > 22


def main():
    logger.info("Starting waiting time scraper...")
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    engine = create_engine(common.get_db_path())
    setup_db_once(engine)
    logger.debug("Database setup completed.")

    previous_all_closed = None

    while True:
        wait_for_next_minute()

        if it_is_nighttime():
            logger.debug("It's nighttime, skipping data ingestion.")
            continue

        try:
            data = fetch_and_check_json()
            current_all_closed = all_offices_closed(data)

            should_store = False
            if previous_all_closed is None:  # First run
                should_store = True
            elif previous_all_closed != current_all_closed:  # State change
                should_store = True
            elif not current_all_closed:  # Normal operation
                should_store = True
            else:
                pass  # All offices closed and no state change - skip

            if should_store:
                with Session(engine) as db:
                    insert_data(db, data)
                logger.debug("Data ingestion completed.")

            # Update previous state
            previous_all_closed = current_all_closed

        except Exception as e:
            logger.error(f"Error during data ingestion: {e}")

        logger.debug("Waiting for the next minute...")


if __name__ == "__main__":
    is_debug = os.getenv("DEBUG", "0") == "1" or os.getenv("DEBUG", "0") == "true"
    loglevel = "DEBUG" if is_debug else "INFO"

    logger.remove()
    logger.add(sys.stderr, level=loglevel)
    logger.add("scraper.log", rotation="1 MB", level=loglevel)

    main()
