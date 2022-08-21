from typing import Dict
import json

from database.db import db
from modules.pets.data.models import Pet


def store_pet(user_id: int, pet: Pet):
    namespace = f'{user_id}:pet'
    current_pet = {"name": pet.name,
                   "emoji": pet.pet_emoji,
                   "level": pet.level,
                   "xp": pet.xp,
                   "stats": pet.pet_stats,
                   "max_hp": pet.max_hp,
                   "current_hp": pet.current_hp}
    json_pet = json.dumps(current_pet)
    db.set(namespace, json_pet)


def get_pet(user_id: int) -> Pet:
    namespace = f'{user_id}:pet'
    unpacked_pet = json.loads(db.get(namespace).decode('utf-8'))
    pet_data = unpacked_pet

    pet = Pet()
    pet.name = pet_data["name"]
    pet.pet_emoji = pet_data["emoji"]
    pet.level = pet_data["level"]
    pet.xp = pet_data["xp"]
    pet.pet_stats = pet_data["stats"]
    pet.max_hp = pet_data["max_hp"]
    pet.current_hp = pet_data["current_hp"]

    return pet


def check_pet(user_id: int) -> bool:
    namespace = f'{user_id}:pet'
    return db.exists(namespace)


def delete_pet(user_id: int):
    namespace = f'{user_id}:pet'
    db.delete(namespace)
