from datetime import date, datetime, time

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import false, func

from src.constants import Role


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(nullable=True)
    is_disabled: Mapped[bool] = mapped_column(server_default=false())
    role: Mapped[int] = mapped_column(server_default=str(Role.GUEST.value))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class Event(Base):
    __tablename__ = "events"

    event_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    event_date: Mapped[date] = mapped_column(nullable=False)
    event_time: Mapped[time] = mapped_column(nullable=False)
    sale_time: Mapped[datetime] = mapped_column(nullable=False)
    sale_end_time: Mapped[datetime] = mapped_column(nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    organizer: Mapped[str] = mapped_column(String(255), nullable=False)
    on_sale: Mapped[bool] = mapped_column(Boolean, default=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class EventPicture(Base):
    __tablename__ = "event_pictures"

    picture_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.event_id", ondelete="CASCADE"))
    picture_url: Mapped[str] = mapped_column(String(255), nullable=True)
    picture_file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    picture_order: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class EventTicketType(Base):
    __tablename__ = "event_ticket_types"

    ticket_type_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.event_id", ondelete="CASCADE"))
    ticket_name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. VIP, 一般票
    max_purchase_limit: Mapped[int | None] = mapped_column(nullable=True)  # null 表示不限
    price: Mapped[float] = mapped_column(nullable=False)
    stock: Mapped[int] = mapped_column(nullable=False)


class Section(Base):
    __tablename__ = "sections"

    section_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.event_id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # A區, VIP區...
    ticket_type_id: Mapped[int] = mapped_column(ForeignKey("event_ticket_types.ticket_type_id"))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)  # 前端排序用


class SeatingRow(Base):
    __tablename__ = "seating_rows"

    row_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.section_id", ondelete="CASCADE"))
    row_name: Mapped[str] = mapped_column(String(10))  # A, B, C...
    row_order: Mapped[int] = mapped_column(Integer, default=0)

    section = relationship("Section", backref="rows")


class Seat(Base):
    __tablename__ = "seats"

    seat_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    row_id: Mapped[int] = mapped_column(ForeignKey("seating_rows.row_id", ondelete="CASCADE"))
    seat_number: Mapped[str] = mapped_column(String(10))  # 01, 02, 03...
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    hold_expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"))

    row = relationship("SeatingRow", backref="seats")


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True
    )
    event_id: Mapped[int] = mapped_column(ForeignKey("events.event_id", ondelete="CASCADE"))
    order_number: Mapped[str] = mapped_column(String(30), unique=True)  # e.g. ORD20250612001
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False)
    total_amount: Mapped[float] = mapped_column(default=0.0)
    paid_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id", ondelete="CASCADE"))
    ticket_type_id: Mapped[int] = mapped_column(ForeignKey("event_ticket_types.ticket_type_id"))
    seat_id: Mapped[int | None] = mapped_column(
        ForeignKey("seats.seat_id", ondelete="SET NULL")
    )  # 若無選位可為 null
    price: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
