from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Column, TEXT


class Subscriber(SQLModel):
    __tablename__ = "subscriber"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(sa_column=Column(TEXT(128), nullable=False, unique=True))
    created_at: datetime = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"Subscriber {self.name}, email {self.email}"
