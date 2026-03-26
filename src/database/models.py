import datetime
from typing import Annotated
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import (
    String,
    Integer,
    DateTime,
    text,
    MetaData,
    Table,
    Column,
    ForeignKey,
    Float,
    Date,
    TIMESTAMP
)

str_100 = Annotated[str, 100]
str_256 = Annotated[str, 256]

intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime.datetime, mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.now(datetime.timezone.utc),
    )]


class Base(DeclarativeBase):
    type_annotation_map = {
        str_256: String(256),
        str_100: String(100)
    }    

class OwnersOrm(Base):
    __tablename__ = "owners"
    __table_args__ = {'schema': 'hpay'}
    id: Mapped[intpk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    name: Mapped[str_100]

class PlacesOrm(Base):
    __tablename__ = "places"
    __table_args__ = {'schema': 'hpay'}
    id: Mapped[intpk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    owner_id: Mapped[Integer] = mapped_column(ForeignKey("hpay.owners.id", ondelete="CASCADE"), index=True)
    name: Mapped[str_100]
    address: Mapped[str_100 | None]

class ServicesOrm(Base):
    __tablename__ = "services"
    __table_args__ = {'schema': 'hpay'}
    id: Mapped[intpk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    place_id: Mapped[Integer] = mapped_column(ForeignKey("hpay.places.id", ondelete="CASCADE"), index=True)
    name: Mapped[str_100 | None]
    accnum: Mapped[str_100 | None]
    cmt: Mapped[str_256 | None]

class PaymentsOrm(Base):
    __tablename__ = "payments"
    __table_args__ = {"schema": "hpay"}
    id: Mapped[intpk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    service_id: Mapped[Integer] = mapped_column(ForeignKey("hpay.services.id", ondelete="CASCADE"), index=True)
    amount: Mapped[float]
    pay_date: Mapped[datetime.date | None]
    service_start_date: Mapped[datetime.date | None]
    service_finish_date: Mapped[datetime.date | None]
    cmt: Mapped[str_256 | None]

class MeterKindsOrm(Base):
    __tablename__ = "meterkinds"
    __table_args__ = {"schema": "hpay"}
    id: Mapped[intpk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    name: Mapped[str_100]

class MetersOrm(Base):
    __tablename__ = "meters"
    __table_args__ = {"schema": "hpay"}
    id: Mapped[intpk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    place_id: Mapped[Integer] = mapped_column(ForeignKey("hpay.places.id", ondelete="CASCADE"), index=True)
    meterkind_id: Mapped[Integer] = mapped_column(ForeignKey("hpay.meterkinds.id", ondelete="CASCADE"))
    name: Mapped[str_100]

class CutoffsOrm(Base):
    __tablename__ = "cutoffs"
    __table_args__ = {"schema": "hpay"}
    id: Mapped[intpk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    meter_id: Mapped[Integer] = mapped_column(ForeignKey("hpay.meters.id", ondelete="CASCADE"), index=True)
    value: Mapped[float]
    read_date: Mapped[datetime.date]


metadata_obj = MetaData()

owners_table = Table(
    "owners",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("created_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())")),
    Column("updated_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.now(datetime.timezone.utc)),
    Column("name", String),
    schema="hpay"
)

places_table = Table(
    "places",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("created_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())")),
    Column("updated_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.now(datetime.timezone.utc)),
    Column("owner_id", Integer),
    Column("name", String),
    Column("address", String),
    schema="hpay"
)

services_table = Table(
    "services",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("created_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())")),
    Column("updated_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.now(datetime.timezone.utc)),
    Column("place_id", Integer),
    Column("name", String),
    Column("accnum", String, nullable=True),
    Column("cmt", String, nullable=True),
    schema="hpay"
)

payments_table = Table(
    "payments",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("created_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())")),
    Column("updated_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.now(datetime.timezone.utc)),
    Column("service_id", Integer),
    Column("amount", Float),
    Column("pay_date", Date),
    Column("service_start_date", Date, nullable = True),
    Column("service_finish_date", Date, nullable = True),
    Column("cmt", String, nullable=True),
    schema="hpay"
)

meterkinds_table = Table(
    "meterkinds",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("created_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())")),
    Column("updated_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.now(datetime.timezone.utc)),
    Column("name", String),
    schema="hpay"
)

meters_table = Table(
    "meters",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("created_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())")),
    Column("updated_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.now(datetime.timezone.utc)),
    Column("place_id", Integer),
    Column("meterkind_id", Integer),
    Column("name", String),
    schema="hpay",
)

cutoffs_table = Table(
    "cutoffs",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("created_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())")),
    Column("updated_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.now(datetime.timezone.utc)),
    Column("meter_id", Integer),
    Column("value", Float),
    Column("read_date", Date),
    schema="hpay",
)
