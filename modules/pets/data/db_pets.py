from typing import Dict

from database.db import db
from modules.pets.data.models import Pet


def store_pet(user_id: int, pet: Pet):
    namespace = f'{user_id}:pet'
    db.set(name=namespace, mapping={"name": Pet.name,
                                    "level": Pet.level,
                                    "xp": Pet.xp,
                                    "stats": Pet.pet_stats,
                                    "max_hp": Pet.max_hp,
                                    "current_hp": Pet.current_hp})


def get_pet(user_id: int, pet: Pet):
    namespace = f'{user_id}:pet'
    if check_pet(user_id):
        pet_data = db.get(namespace)
        Pet.name = pet_data["name"]
        Pet.level = pet_data["level"]
        Pet.xp = pet_data["xp"]
        Pet.pet_stats = pet_data["stats"]
        Pet.max_hp = pet_data["max_hp"]
        Pet.current_hp = pet_data["current_hp"]


def check_pet(user_id: int) -> bool:
    return db.hexists(name=f'{user_id}:pet')
