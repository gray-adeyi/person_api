import httpx
from rich import print

BASE_URL = "http://127.0.0.1:9001/api"
NAMES = ["Guido van Rossum", "Gbenga Adeyi", "Graydon Hoare"]

created_people = []
print(":boom: People API test script :boom:")

# Create Person
print(f"attempting to create people {NAMES}...")
for name in NAMES:
    response = httpx.post(BASE_URL + "/persons", json={"name": name})
    person = response.json()
    print(f"successfully created person: {name}...")
    print(person)
    created_people.append(person)

# Get People
print("attempting to fetch all people")
response = httpx.get(BASE_URL + "/persons")
people = response.json()
print("successfully retrieved people...")
print(people)

# Get one Person by name
response = httpx.get(BASE_URL + "/persons?name=Gbenga Adeyi")
person = response.json()
print("successfully retrieved person with name Gbenga Adeyi")
print(person)

# Update Person
person_id = created_people[0]["id"]
old_name = created_people[0]["name"]
new_name = "Benevolent Dictator"
response = httpx.put(
    BASE_URL + f"/persons/{person_id}",
    json={"name": new_name, "favourite_color": "black", "age": 49},
)
updated_person = response.json()
created_people[0] = updated_person
print(f"sucessfully updated person name from {old_name} to {new_name}")

# Delete Person
name = created_people[-1]["name"]
id = created_people[-1]["id"]
print(f"attempting to delete person with name {name}")
response = httpx.delete(BASE_URL + f"/persons/{id}")
print(f"successfully deleted {name}")
print(":boom: Done! :boom:")
