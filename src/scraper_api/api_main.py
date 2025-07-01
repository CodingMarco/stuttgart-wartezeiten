from fastapi import FastAPI, Depends, HTTPException
from models import Office, WaitingTime, Snapshot, Status
from typing import Annotated
import common
import datetime as dt


from sqlalchemy import create_engine
from sqlalchemy.orm import Session

connect_args = {"check_same_thread": False}
engine = create_engine(common.get_db_path(), connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.get("/offices")
async def get_offices(session: SessionDep):
    """
    Retrieve a list of offices.
    """

    offices = session.query(Office).all()
    return offices


@app.get("/waiting_times/{date}")
async def get_waiting_times(date: str, session: SessionDep):
    """
    Retrieve waiting times for a specific date.
    Expected date format: YYYY-MM-DD
    """
    try:
        # Parse the date string
        target_date = dt.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid date format '{date}'. Expected YYYY-MM-DD"
        )

    # Define the date range for the target date (00:00:00 to 23:59:59 UTC)
    start_datetime = dt.datetime.combine(target_date, dt.time.min).replace(
        tzinfo=dt.UTC
    )
    end_datetime = dt.datetime.combine(target_date, dt.time.max).replace(tzinfo=dt.UTC)

    # Query waiting times for the specified date
    query = (
        session.query(
            Snapshot.captured_at,
            Office.id.label("office_id"),
            Status.id.label("status_id"),
        )
        .join(WaitingTime, Snapshot.id == WaitingTime.snapshot_id)
        .join(Office, WaitingTime.office_id == Office.id)
        .join(Status, WaitingTime.status_id == Status.id)
        .filter(Snapshot.captured_at >= start_datetime)
        .filter(Snapshot.captured_at <= end_datetime)
        .order_by(Snapshot.captured_at, Office.label)
    )

    results = query.all()

    if not results:
        raise HTTPException(
            status_code=404, detail=f"No waiting times found for date {date}"
        )

    # Convert results to dict that maps office ids to their waiting time IDs over time
    waiting_times = {}
    for captured_at, office_id, status_id in results:
        waiting_times.setdefault(office_id, []).append(
            {
                "captured_at": captured_at.isoformat(),
                "status_id": status_id,
            }
        )

    return waiting_times


@app.get("/waiting_times/today")
async def get_waiting_times_today(session: SessionDep):
    """
    Retrieve waiting times for today.
    """
    today = dt.datetime.now(dt.UTC).date()
    return await get_waiting_times(str(today), session)
