from uuid import UUID

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, delete, update
from db import get_session
from models import (
    CreateUpdatePersonSchema,
    Person,
    get_person_by_id_or_404,
    PartialUpdatePersonSchema,
    get_people_by_ids,
)

person_router = APIRouter(prefix="/api")


@person_router.post("/persons", tags=["person"], status_code=status.HTTP_201_CREATED)
async def create_person(
    create_data: CreateUpdatePersonSchema, db: AsyncSession = Depends(get_session)
):
    """This endpoint allows you to create a `Person` resource. Only the name is required in the payload data"""
    new_person = Person(**create_data.dict())
    db.add(new_person)
    await db.commit()
    await db.refresh(new_person)
    return new_person


@person_router.get("/persons", tags=["person"])
async def get_people(name: str | None = None, db: AsyncSession = Depends(get_session)):
    """This endpoint allows you to retrieve all the `Person` resource stored in the database.

    This endpoint can also be queried to retrieve a specific name

    Example:
        `BASE_URL/api/persons?name=John%20Doe` will retrieve all `Person` resource with
        name as `John Doe`

    Note:
        This current version does not support pagination.
    """
    # TODO: Pagination
    if name:
        query = select(Person).where(Person.name == name)
    else:
        query = select(Person)
    return (await db.execute(query)).scalars().all()


@person_router.get("/persons/{person_id}", tags=["person"])
async def get_person(
    person_id: UUID,
    db: AsyncSession = Depends(get_session),
    person: Person = Depends(get_person_by_id_or_404),
):
    """This endpoint lets you retrieve a specific `Person` by id"""
    return person


@person_router.put("/persons/{person_id}", tags=["person"])
async def update_person(
    person_id: UUID,
    update_data: CreateUpdatePersonSchema,
    db: AsyncSession = Depends(get_session),
    person: Person = Depends(get_person_by_id_or_404),
):
    """This endpoint lets you update the information on a `Person` resource with the provided `person_id`"""
    query = update(Person).where(Person.id == person_id).values(**update_data.dict())
    await db.execute(query)
    await db.commit()
    await db.refresh(person)
    return person


@person_router.patch("/persons/{person_id}", tags=["person"])
async def update_person_partial(
    person_id: UUID,
    update_data: PartialUpdatePersonSchema,
    db: AsyncSession = Depends(get_session),
    person: Person = Depends(get_person_by_id_or_404),
):
    """This endpoint lets you update the information on a `Person` resource with the provided `person_id`"""
    person.name = update_data.name or person.name
    person.age = update_data.age or person.age
    person.favourite_color = update_data.favourite_color or person.favourite_color
    db.add(person)
    await db.commit()
    await db.refresh(person)
    return person


@person_router.delete(
    "/persons/{person_id}", tags=["person"], status_code=status.HTTP_204_NO_CONTENT
)
async def delete_person(
    person_id: UUID,
    db: AsyncSession = Depends(get_session),
    person: Person = Depends(get_person_by_id_or_404),
):
    """This endpoint lets you delete a `Person` resource with the provided `person_id`"""
    query = delete(Person).where(Person.id == person_id)
    await db.execute(query)
    await db.commit()


@person_router.get(
    "/persons/{person_id}/friends",
    tags=["person"],
)
async def get_person_friends(
    person_id: UUID,
    db: AsyncSession = Depends(get_session),
    person: Person = Depends(get_person_by_id_or_404),
):
    """`Additional` This endpoint retrieves the friends (`Person`) of a `Person` with the `person_id` in the
    path"""
    if not person.friends:
        return []
    return await get_people_by_ids(person.friends, db)


@person_router.post("/persons/{person_id}/add-friends", tags=["person"])
async def add_friends(
    person_id: UUID,
    people_ids: list[UUID],
    db: AsyncSession = Depends(get_session),
    person: Person = Depends(get_person_by_id_or_404),
):
    """`Additional` This endpoint adds `People` as friends of a `Person`"""
    new_friends = await get_people_by_ids(
        [str(person_id) for person_id in people_ids], db
    )
    friend_ids = [str(friend.id) for friend in new_friends if friend.id != person_id]
    if not person.friends:
        person.friends = friend_ids
    else:
        person.friends = list(set(person.friends).union(set(friend_ids)))
    db.add(person)
    await db.commit()
    await db.refresh(person)
    return person


@person_router.post("/persons/{person_id}/remove-friends", tags=["person"])
async def remove_friends(
    people_ids: list[UUID],
    db: AsyncSession = Depends(get_session),
    person: Person = Depends(get_person_by_id_or_404),
):
    """`Additional` This endpoint removes `People` as friends of a `Person`"""
    friends_to_remove = await get_people_by_ids(people_ids, db)
    friends_to_remove_ids = [str(friend.id) for friend in friends_to_remove]
    if not person.friends:
        return person
    else:
        person.friends = list(
            set(person.friends).difference(set(friends_to_remove_ids))
        )
    db.add(person)
    await db.commit()
    await db.refresh(person)
    return person
