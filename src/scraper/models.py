import datetime as dt
from typing import List

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class Status(Base):
    """
    Lookup table for the numeric waiting-time codes published by the city.

    Examples
    --------
    1  -> "< 30 min"
    2  -> "30 min"
    ...
    15 -> "No waiting stamps left"
    """

    __tablename__ = "status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meaning: Mapped[str] = mapped_column(String(64), nullable=False)

    samples: Mapped[List["WaitingTime"]] = relationship(
        back_populates="status", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"Status(code={self.id}, meaning={self.meaning!r})"


class Feature(Base):
    """
    A service characteristic of an office (e.g. 'Keine Parkausweise').
    """

    __tablename__ = "feature"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)

    offices: Mapped[List["Office"]] = relationship(
        secondary="office_feature", back_populates="features"
    )

    def __repr__(self):  # pragma: no cover
        return f"Feature(id={self.id}, name={self.name!r})"


class Office(Base):
    """
    A citizen's office (Bürgerbüro).
    """

    __tablename__ = "office"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships ----------------------------------------------------------
    features: Mapped[List[Feature]] = relationship(
        secondary="office_feature", back_populates="offices"
    )

    samples: Mapped[List["WaitingTime"]] = relationship(
        back_populates="office", cascade="all, delete-orphan"
    )

    def __repr__(self):  # pragma: no cover
        return f"Office(id={self.id}, label={self.label!r})"


class Snapshot(Base):
    """
    One scraping run - normally one per minute.
    """

    __tablename__ = "snapshot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    captured_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc),
        index=True,
    )

    samples: Mapped[List["WaitingTime"]] = relationship(
        back_populates="snapshot", cascade="all, delete-orphan"
    )

    def __repr__(self):  # pragma: no cover
        return f"Snapshot(id={self.id}, captured_at={self.captured_at.isoformat()})"


class OfficeFeature(Base):
    """
    Plain M-N link table between Office and Feature.
    """

    __tablename__ = "office_feature"
    office_id: Mapped[int] = mapped_column(
        ForeignKey("office.id", ondelete="CASCADE"), primary_key=True
    )
    feature_id: Mapped[int] = mapped_column(
        ForeignKey("feature.id", ondelete="CASCADE"), primary_key=True
    )


class WaitingTime(Base):
    """
    Fact table: the status of one office at one snapshot.
    """

    __tablename__ = "waiting_time"
    __table_args__ = (
        UniqueConstraint(
            "office_id", "snapshot_id", name="uq_waiting_time_office_snapshot"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    office_id: Mapped[int] = mapped_column(
        ForeignKey("office.id", ondelete="CASCADE"), nullable=False, index=True
    )
    snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("snapshot.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status_id: Mapped[int] = mapped_column(
        ForeignKey("status.id"), nullable=False, index=True
    )

    # Relationships ----------------------------------------------------------
    office: Mapped[Office] = relationship(back_populates="samples")
    snapshot: Mapped[Snapshot] = relationship(back_populates="samples")
    status: Mapped[Status] = relationship(back_populates="samples")

    def __repr__(self):  # pragma: no cover
        return (
            f"WaitingTime(id={self.id}, office={self.office_id}, "
            f"snapshot={self.snapshot_id}, status={self.status_id})"
        )
