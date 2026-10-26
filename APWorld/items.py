from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

from .item_data import tracklist, unitlist, supportlist, bglist

if TYPE_CHECKING:
    from .world import LLSIFWorld

GROUP_ID_TO_NAME = ["N/A", "μ's", "Aqours", "Nijigasaki", "Liella!"]
live_options = []
progression_lives = []
extra_lives = []
starting_lives = []
support_units = []
filler_options = []
bg_options = []

ITEM_NAME_TO_ID = {
    "5 Love Gems": 1,
    "100 Gs": 2,
    "1000 Gs": 3,
    "5000 Gs": 4,
    "10000 Gs": 5,
    "100 Friend Points": 6,
    "500 Friend Points": 7,
    "1000 Friend Points": 8,
    "New Background": 9,
    "5 Love Gems*": 10,
}

DEFAULT_ITEM_CLASSIFICATIONS = {
    "5 Love Gems": ItemClassification.filler,
    "100 Gs": ItemClassification.filler,
    "1000 Gs": ItemClassification.filler,
    "5000 Gs": ItemClassification.filler,
    "10000 Gs": ItemClassification.filler,
    "100 Friend Points": ItemClassification.filler,
    "500 Friend Points": ItemClassification.filler,
    "1000 Friend Points": ItemClassification.filler,
    "New Background": ItemClassification.filler,
    "5 Love Gems*": ItemClassification.useful

}

for track in tracklist:
    ITEM_NAME_TO_ID[f"{GROUP_ID_TO_NAME[track["group"]]} - {track["name_en"]}"] = (1000 + track["id"])
    DEFAULT_ITEM_CLASSIFICATIONS[f"{GROUP_ID_TO_NAME[track["group"]]} - {track["name_en"]}"] = ItemClassification.progression_deprioritized_skip_balancing

for unit in supportlist:
    name = unit["name_en"]
    eponym = unit["eponym_en"]
    ITEM_NAME_TO_ID[f"{name} ({unit["id"]})"] = (10000 + unit["id"])
    DEFAULT_ITEM_CLASSIFICATIONS[f"{name} ({unit["id"]})"] = ItemClassification.filler
    support_units.append(f"{name} ({unit["id"]})")

for bg in bglist:
    ITEM_NAME_TO_ID[bg["name_en"]] = (3000 + bg["id"])
    DEFAULT_ITEM_CLASSIFICATIONS[bg["name_en"]] = ItemClassification.filler

ITEM_NAME_TO_ID["Progressive μ's Main Story"] = 4001
ITEM_NAME_TO_ID["Progressive Aqours Main Story"] = 4002
DEFAULT_ITEM_CLASSIFICATIONS["Progressive μ's Main Story"] = ItemClassification.progression_deprioritized_skip_balancing
DEFAULT_ITEM_CLASSIFICATIONS["Progressive Aqours Main Story"] = ItemClassification.progression_deprioritized_skip_balancing

class LLSIFItem(Item):
    game = "Love Live! School idol festival"

def get_random_filler_item_name(world: LLSIFWorld) -> str:
    global support_units
    global filler_options

    rand = world.random.randint(1,100)
    if rand <= world.options.filler_support_percentage:
        return world.random.choice(support_units)
    else:
        option = world.random.choice(filler_options)
        if option == "New Background":
            if len(bg_options) > 0:
                bg = world.random.choice(bg_options)
                bg_options.remove(bg)
                return bg
            else:
                new_filler_options = filler_options
                new_filler_options.remove("New Background")
                return world.random.choice(new_filler_options)
        else:
            return option


def create_item_with_correct_classification(world: LLSIFWorld, name: str) -> LLSIFItem:
    classification = DEFAULT_ITEM_CLASSIFICATIONS[name]

    return LLSIFItem(name, classification, ITEM_NAME_TO_ID[name], world.player)

def create_all_items(world: LLSIFWorld) -> None:
    global progression_lives
    global extra_lives
    global starting_lives
    global filler_options
    global bg_options
    global included_groups
    global included_group_ids

    #Average sticker per gacha pull, per Honor Scout box. 
    #Used to include ensured enough Love Gems items are in circulation to afford important Sticker Shop items.
    sticker_rates = [2.08654388075, 1.84680207989, 1.06009035698, 2.0663562753]

    for key, value in ITEM_NAME_TO_ID.items():
        if value < 1000:
            filler_options.append(key)
    bg_options = []
    for bg in bglist:
        if bg["group"] == 0 or bg["group"] in included_group_ids:
            bg_options.append(bg["name_en"])
    itempool: list[Item] = []

    for live in progression_lives:
        if not live in starting_lives:
            itempool.append(world.create_item(live))
    for live in extra_lives:
        itempool.append(world.create_item(live))
    for live in starting_lives:
        world.push_precollected(world.create_item(live))
        
    if 1 in included_group_ids:
        world.push_precollected(world.create_item("Progressive μ's Main Story"))
    if 2 in included_group_ids:
        world.push_precollected(world.create_item("Progressive Aqours Main Story"))

    for i in range(1,48):
        if 1 in included_group_ids:
            itempool.append(world.create_item("Progressive μ's Main Story"))

    for i in range(1,37):
        if 2 in included_group_ids:
            itempool.append(world.create_item("Progressive Aqours Main Story"))

    # Add ensured Love Gems to the item pool, to make affording shop items more consistent.
    if world.options.shop_checks > 0:
        big_number = 0
        for group in included_group_ids:
            big_number += sticker_rates[group-1]
        big_number /= len(included_group_ids)
        item_count = (world.options.shop_checks * 10) / big_number
        for item in range(0,round(item_count)):
            itempool.append(world.create_item("5 Love Gems*"))


    number_of_items = len(itempool)

    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))

    needed_number_of_filler_items = number_of_unfilled_locations - number_of_items

    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]

    world.multiworld.itempool += itempool

def get_lives():
    global progression_lives
    global extra_lives
    global starting_lives
    global goal_live_count
    global extra_live_count
    global live_start_count
    progression_ids = []
    extra_ids = []
    starting_ids = []
    for live in progression_lives:
        progression_ids.append(ITEM_NAME_TO_ID[live])
    for live in extra_lives:
        extra_ids.append(ITEM_NAME_TO_ID[live])
    for live in starting_lives:
        starting_ids.append(ITEM_NAME_TO_ID[live])
    return {"progression": progression_lives, "extra": extra_lives, "starting": starting_lives}, {"progression": progression_ids, "extra": extra_ids, "starting": starting_ids}

def calculate_available_lives(world: LLSIFWorld):
    global live_options
    global progression_lives
    global extra_lives
    global starting_lives
    global support_units
    global included_groups
    global goal_live_count
    global live_start_count
    global extra_live_count
    global included_group_ids




    # get a random selection of Live Show tracks to include in the item / location pool,
    # and select which tracks will be given as starting items
    live_options = []
    included_groups = []
    included_group_ids = []
    for unit in world.options.included_groups:
        if "Muse" in unit:
            unit = "μ's"
        included_groups.append(unit)
        included_group_ids.append(GROUP_ID_TO_NAME.index(unit))
    if included_group_ids == []:
        included_group_ids = [1,2,3,4]
        included_groups = ["μ's", "Aqours", "Nijigasaki", "Liella!"]

    for key, value in ITEM_NAME_TO_ID.items():
        if value in range(1000,2000):
            if any(group in key for group in included_groups):
                    live_options.append(key)

    goal_live_count = min(world.options.live_count, len(live_options))
    extra_live_count = min(world.options.live_extra, (len(live_options)-goal_live_count))
    live_start_count = min(world.options.live_start_count, goal_live_count)

    progression_lives = world.random.sample(live_options, k=goal_live_count)
    starting_lives = world.random.sample(progression_lives, k=live_start_count)

    live_options = [live for live in live_options if not live in progression_lives]
    extra_lives = world.random.sample(live_options, k=extra_live_count)


    

