import common
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import datetime as dt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Status, Office, WaitingTime, Snapshot

# Analysis module for Stuttgart waiting times data
# Features interactive legends - click on legend entries to hide/show corresponding lines


def make_legend_interactive(ax, legend):
    """
    Make a legend interactive - clicking on legend entries will hide/show the corresponding lines.
    Starts with all plots hidden except for the first one.

    Args:
        ax: matplotlib axis object
        legend: matplotlib legend object
    """
    # Dictionary to keep track of original line visibility and properties
    lined = {}

    # Get all lines from the plot
    lines = ax.get_lines()

    # Create mapping between legend lines and plot lines
    for i, (legline, origline) in enumerate(zip(legend.get_lines(), lines)):
        legline.set_picker(True)  # Enable picking on legend lines
        legline.set_pickradius(10)  # Set pick radius for easier clicking
        lined[legline] = origline

        # Hide all lines except the first one on initialization
        if i > 0:
            origline.set_visible(False)
            legline.set_alpha(0.3)
        else:
            origline.set_visible(True)
            legline.set_alpha(1.0)

    def on_pick(event):
        """Handle pick events on legend lines."""
        legline = event.artist
        origline = lined[legline]

        # Check if Shift key is pressed
        if hasattr(event, "mouseevent") and event.mouseevent.key == "shift":
            # Shift+click: Show only this plot, hide all others
            for leg, line in lined.items():
                if leg == legline:
                    # Show the clicked line
                    line.set_visible(True)
                    leg.set_alpha(1.0)
                else:
                    # Hide all other lines
                    line.set_visible(False)
                    leg.set_alpha(0.3)
        else:
            # Normal click: Toggle visibility
            visible = not origline.get_visible()
            origline.set_visible(visible)

            # Change legend line appearance to reflect state
            if visible:
                legline.set_alpha(1.0)
            else:
                legline.set_alpha(0.3)

        # Redraw the plot
        ax.figure.canvas.draw()

    # Connect the pick event to our handler
    ax.figure.canvas.mpl_connect("pick_event", on_pick)

    print("Legend is now interactive! Click on legend entries to hide/show lines.")
    print(
        "Starting with only the first plot visible - click legend entries to show/hide others."
    )
    print("Hold Shift while clicking to show only that plot and hide all others.")


def get_system_timezone():
    """Get the system's local timezone."""
    return dt.datetime.now().astimezone().tzinfo


def get_today_6am_utc():
    """Get today's 6am local time converted to UTC."""
    local_tz = get_system_timezone()

    # Get current local time
    now_local = dt.datetime.now(local_tz)

    # Create today at 6am local time
    today_6am_local = now_local.replace(hour=6, minute=0, second=0, microsecond=0)

    # Convert to UTC for database queries
    today_6am_utc = today_6am_local.astimezone(dt.timezone.utc)

    return today_6am_utc


def convert_utc_to_local(timestamp, local_tz=None):
    """Convert UTC timestamp to local timezone."""
    if local_tz is None:
        local_tz = get_system_timezone()

    # Ensure timestamp is timezone-aware UTC
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=dt.timezone.utc)
    elif timestamp.tzinfo != dt.timezone.utc:
        timestamp = timestamp.astimezone(dt.timezone.utc)

    # Convert to local timezone
    return timestamp.astimezone(local_tz)


def create_waiting_times_chart():
    """Create a chart showing waiting times for all offices from today at 6am local time."""

    # Connect to the database
    engine = create_engine(common.get_db_path())

    # Calculate the time range (from today at 6am local time)
    start_time = get_today_6am_utc()

    with Session(engine) as db:
        # Query waiting times from today at 6am
        query = (
            db.query(
                Snapshot.captured_at,
                Office.label.label("office_name"),
                Status.meaning.label("status_meaning"),
                Status.id.label("status_id"),
            )
            .join(WaitingTime, Snapshot.id == WaitingTime.snapshot_id)
            .join(Office, WaitingTime.office_id == Office.id)
            .join(Status, WaitingTime.status_id == Status.id)
            .filter(Snapshot.captured_at >= start_time)
            .order_by(Snapshot.captured_at, Office.label)
        )

        results = query.all()

        if not results:
            print("No data found from today at 6am local time.")
            return

        # Convert to pandas DataFrame for easier manipulation
        df = pd.DataFrame(
            [
                {
                    "timestamp": row.captured_at,
                    "office": row.office_name,
                    "status": row.status_meaning,
                    "status_id": row.status_id,
                }
                for row in results
            ]
        )

        # Convert timestamp to datetime and convert from UTC to local timezone
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        local_tz = get_system_timezone()
        df["timestamp_local"] = df["timestamp"].apply(
            lambda x: convert_utc_to_local(x, local_tz)
        )

        # Create the plot
        fig, ax = plt.subplots(figsize=(15, 10))

        # Get unique offices
        offices = df["office"].unique()

        # Create a color map for different offices
        import numpy as np

        colors = plt.get_cmap("tab10")(np.linspace(0, 1, len(offices)))

        # Plot each office's waiting times
        for i, office in enumerate(offices):
            office_data = df[df["office"] == office].copy()
            office_data = office_data.sort_values("timestamp_local")

            # Convert status to numeric for plotting (use status_id)
            ax.plot(
                office_data["timestamp_local"],
                office_data["status_id"],
                label=office,
                color=colors[i],
                linewidth=1.5,
                alpha=0.7,
            )

        # Customize the plot
        ax.set_xlabel("Time (Local)", fontsize=12)
        ax.set_ylabel("Waiting Time Status", fontsize=12)
        ax.set_title(
            "Waiting Times for All Offices - From Today 6am (Local Time)",
            fontsize=14,
            fontweight="bold",
        )

        # Format x-axis to show time nicely with local timezone
        local_tz = get_system_timezone()
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=local_tz))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))

        plt.xticks(rotation=45)

        # Create custom y-axis labels based on status meanings
        status_labels = db.query(Status.id, Status.meaning).all()
        status_dict = {status.id: status.meaning for status in status_labels}

        # Set y-axis ticks and labels
        y_ticks = sorted(status_dict.keys())
        y_labels = [status_dict[tick] for tick in y_ticks]
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels, fontsize=10)

        # Add legend
        legend = ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=10)

        # Make the legend interactive
        make_legend_interactive(ax, legend)

        # Add grid for better readability
        ax.grid(True, alpha=0.3)

        # Adjust layout to prevent legend cutoff
        plt.tight_layout()

        # Show the plot
        plt.show()

        # Print some statistics
        local_tz = get_system_timezone()
        print("\nData Summary:")
        print(
            f"Time range (local {local_tz}): {df['timestamp_local'].min()} to {df['timestamp_local'].max()}"
        )
        print(f"Number of offices: {len(offices)}")
        print(f"Total data points: {len(df)}")
        print(f"Offices included: {', '.join(offices)}")


def create_average_waiting_times_chart():
    """Create a chart showing average waiting times by hour for all offices from today at 6am local time."""

    engine = create_engine(common.get_db_path())
    start_time = get_today_6am_utc()

    with Session(engine) as db:
        query = (
            db.query(
                Snapshot.captured_at,
                Office.label.label("office_name"),
                Status.id.label("status_id"),
            )
            .join(WaitingTime, Snapshot.id == WaitingTime.snapshot_id)
            .join(Office, WaitingTime.office_id == Office.id)
            .join(Status, WaitingTime.status_id == Status.id)
            .filter(Snapshot.captured_at >= start_time)
            .order_by(Snapshot.captured_at)
        )

        results = query.all()

        if not results:
            print("No data found from today at 6am local time.")
            return

        df = pd.DataFrame(
            [
                {
                    "timestamp": row.captured_at,
                    "office": row.office_name,
                    "status_id": row.status_id,
                }
                for row in results
            ]
        )

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        local_tz = get_system_timezone()
        df["timestamp_local"] = df["timestamp"].apply(
            lambda x: convert_utc_to_local(x, local_tz)
        )
        df["hour"] = df["timestamp_local"].dt.hour

        # Calculate average waiting time by hour and office
        hourly_avg = df.groupby(["hour", "office"])["status_id"].mean().reset_index()

        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 8))

        offices = hourly_avg["office"].unique()
        import numpy as np

        colors = plt.get_cmap("tab10")(np.linspace(0, 1, len(offices)))

        for i, office in enumerate(offices):
            office_data = hourly_avg[hourly_avg["office"] == office]
            ax.plot(
                office_data["hour"],
                office_data["status_id"],
                label=office,
                color=colors[i],
                linewidth=2,
            )

        ax.set_xlabel("Hour of Day (Local Time)", fontsize=12)
        ax.set_ylabel("Average Waiting Time Status", fontsize=12)
        ax.set_title(
            "Average Waiting Times by Hour - From Today 6am (Local Time)",
            fontsize=14,
            fontweight="bold",
        )
        ax.set_xticks(range(0, 24))

        # Add legend and make it interactive
        legend = ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        make_legend_interactive(ax, legend)

        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    print("Creating waiting times analysis charts...")
    create_waiting_times_chart()
    print("\nCreating average waiting times by hour...")
    create_average_waiting_times_chart()
