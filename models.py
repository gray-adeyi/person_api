import uuid
from datetime import datetime
from typing import Annotated
from uuid import UUID

from sqlalchemy import Column, String
from sqlalchemy.types import ARRAY
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, Field, select

from db import get_session


class Person(SQLModel, table=True):
    __tablename__ = "people"

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    age: int | None
    favourite_color: str | None
    friends: list[str] | None = Field(
        default=[], sa_column=Column("friends", ARRAY(String))
    )
    created_at: datetime = Field(default_factory=datetime.now)


class CreateUpdatePersonSchema(SQLModel):
    name: str
    age: int | None = None
    favourite_color: str | None = None


class PartialUpdatePersonSchema(SQLModel):
    name: str | None = None
    age: int | None = None
    favourite_color: str | None = None


async def get_person_by_id_or_404(
    person_id: UUID, db: Annotated[AsyncSession, Depends(get_session)]
) -> Person:
    query = select(Person).where(Person.id == person_id)
    result = (await db.execute(query)).scalar_one_or_none()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"person with id {person_id} not found.",
        )
    return result


async def get_people_by_ids(
    people_ids: list[str], db: Annotated[AsyncSession, Depends(get_session)]
) -> list[Person]:
    # TODO: Bulk fetch
    people: list[Person] = []
    for person_id in people_ids:
        query = select(Person).where(Person.id == person_id)
        person = (await db.execute(query)).scalar_one_or_none()
        if person:
            people.append(person)
    return people
