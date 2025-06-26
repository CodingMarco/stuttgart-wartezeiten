import time
import json
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
    (5, "90 min"),
    (6, "120 min"),
    (7, "180 min"),
    (8, "120 min"),
    (10, "very long"),
    (11, "very long"),
    (12, "very long"),
    (13, "very long"),
    (14, "very long"),
    (15, "no waiting stamps left"),
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


def main():
    logger.info("Starting waiting time scraper...")
    engine = create_engine("sqlite:///waiting_times.sqlite")
    setup_db_once(engine)

    while True:
        try:
            data = fetch_and_check_json()
            with Session(engine) as db:
                insert_data(db, data)
        except Exception as e:
            logger.error(f"Error during data ingestion: {e}")

        logger.debug("Data ingestion completed, waiting for the next minute...")
        wait_for_next_minute()


if __name__ == "__main__":
    logger.add("scraper.log", rotation="1 MB", level="INFO")
    main()
