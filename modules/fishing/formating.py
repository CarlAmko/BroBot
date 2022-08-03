from modules.fishing.data import FishingEquipment


def format_durability(item) -> str:
	return f'{item.durability} uses remaining' if isinstance(item, FishingEquipment) else ''


def format_cost(item) -> str:
	cost = item.value * item.quantity
	return f"{cost} diggit{'y' if cost == 1 else 'ies'}"


def format_quantity(item) -> str:
	return f' x{item.quantity}' if item.quantity > 1 else ''


def format_fishing_power(item) -> str:
	return f'+{item.fishing_power} FP' if isinstance(item, FishingEquipment) else ''


def format_description(item) -> str:
	return item.description if isinstance(item, FishingEquipment) else ''
