from typing import ClassVar, Dict

from BaseClasses import Item
from worlds.AutoWorld import WebWorld, World

from .options import IoGROptions, OPTION_GROUPS


class IoGRWeb(WebWorld):
    option_groups = OPTION_GROUPS


class IoGRWorld(World):
    """Illusion of Gaia Randomizer for Archipelago."""

    game = "Illusion of Gaia"
    web = IoGRWeb()

    options_dataclass = IoGROptions
    options: IoGROptions

    # AP requires these two tables on this class, even while they're empty.
    # They'll be filled from IoGR's data, using IoGR ids plus an offset.
    item_name_to_id: ClassVar[Dict[str, int]] = {}
    location_name_to_id: ClassVar[Dict[str, int]] = {}

    def create_item(self, name: str) -> Item:
        raise NotImplementedError("Items aren't implemented yet.")