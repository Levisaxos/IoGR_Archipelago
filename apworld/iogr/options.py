import inspect
from dataclasses import make_dataclass
from enum import Enum
from typing import Any, Dict, List, Sequence, Set, Tuple, Type

from Options import Choice, Option, PerGameCommonOptions, Range, OptionGroup

from .iogr.models.randomizer_data import RandomizerData

# Settings that never appear in the YAML. The apworld sets these itself.
HIDDEN_SETTINGS: Set[str] = {
    "seed",
    "logic",
    "firebird",
    "ohko",
    "red_jewel_madness",
    "allow_glitches",
    "open_mode",
    "z3",
    "race_mode",
    "printlevel",
    "break_on_error",
    "break_on_init",
    "ingame_debug",
    "infinite_inventory",
    "ds_warp",
}

# Hidden settings that differ from IoGR's defaults for Archipelago.
# The settings builder should pass these to RandomizerData.
FIXED_SETTINGS: Dict[str, Any] = {
    "infinite_inventory": True,
    "ds_warp": True,
}

# Options players can change, and the enum values they can pick.
# Anything not listed here stays locked to its IoGR default.
# Example: "difficulty": list(enums.Difficulty)
UNLOCKED_VALUES: Dict[str, Sequence[Enum]] = {}

# Display name and description, keyed by the RandomizerData setting name.
# Settings without an entry get a generated name and a default description.
OPTION_TEXT: Dict[str, Tuple[str, str]] = {
    "statues": ("Statues Required", "Number of Mystic Statues required to face Dark Gaia."),
    "goal": ("Goal", "What you need to do to complete the game."),
    "difficulty": ("Difficulty", "Overall game difficulty. Only Normal is available for now."),
}

DEFAULT_DESCRIPTION = "Not yet implemented; Using IoGR default setting."


def option_text(setting: str) -> Tuple[str, str]:
    generated_name = setting.replace("_", " ").title()
    return OPTION_TEXT.get(setting, (generated_name, DEFAULT_DESCRIPTION))


def class_name_for(setting: str) -> str:
    return "".join(word.capitalize() for word in setting.split("_"))


def build_choice(setting: str, default_name: str, values: Dict[str, int]) -> Type[Choice]:
    display_name, description = option_text(setting)
    attributes: Dict[str, Any] = {
        "__doc__": description,
        "__module__": __name__,
        "display_name": display_name,
        "default": values[default_name],
    }
    for name, value in values.items():
        attributes[f"option_{name}"] = value
    return type(class_name_for(setting), (Choice,), attributes)


def enum_option(setting: str, default: Enum) -> Type[Choice]:
    enum_type = type(default)
    members: List[Enum] = list(enum_type)
    selected: List[Enum] = list(UNLOCKED_VALUES.get(setting, [default]))

    def option_value(member: Enum) -> int:
        # Sprite uses text values, and AP needs numbers, so use its position.
        return member.value if isinstance(member.value, int) else members.index(member)

    values = {member.name.lower(): option_value(member) for member in selected}
    return build_choice(setting, default.name.lower(), values)


def bool_option(setting: str, default: bool) -> Type[Choice]:
    name = "on" if default else "off"
    return build_choice(setting, name, {name: int(default)})

def range_option(setting: str, start: int, end: int, default: int) -> Type[Range]:
    display_name, description = option_text(setting)
    return type(class_name_for(setting), (Range,), {
        "__doc__": description,
        "__module__": __name__,
        "display_name": display_name,
        "range_start": start,
        "range_end": end,
        "default": default,
    })

def build_option(setting: str, default: Any) -> Type[Option[Any]]:
    if setting == "statues":
        return range_option(setting, 0, 6, int(default))
    if isinstance(default, Enum):
        return enum_option(setting, default)
    if isinstance(default, bool):
        return bool_option(setting, default)
    raise TypeError(
        f"IoGR setting '{setting}' has an unsupported type. "
        "Add it to build_option or HIDDEN_SETTINGS."
    )


def build_option_fields() -> List[Tuple[str, Type[Option[Any]]]]:
    parameters = inspect.signature(RandomizerData.__init__).parameters
    return [
        (setting, build_option(setting, parameter.default))
        for setting, parameter in parameters.items()
        if setting != "self" and setting not in HIDDEN_SETTINGS
    ]


OPTION_CLASSES: Dict[str, Type[Option[Any]]] = dict(build_option_fields())

IoGROptions = make_dataclass(
    "IoGROptions",
    list(OPTION_CLASSES.items()),
    bases=(PerGameCommonOptions,),
)

OPTION_GROUP_SETTINGS: Dict[str, List[str]] = {
    "Goal": ["goal", "difficulty", "statues", "statue_req"],
    "World Layout": [
        "start_location", "coupled_exits", "town_shuffle",
        "dungeon_shuffle", "overworld_shuffle",
    ],
    "Enemies": ["enemizer", "boss_shuffle"],
    "Extras": ["orb_rando", "darkrooms", "flute", "sprite"],
}

OPTION_GROUPS: List[OptionGroup] = [
    OptionGroup(name, [OPTION_CLASSES[setting] for setting in settings])
    for name, settings in OPTION_GROUP_SETTINGS.items()
]