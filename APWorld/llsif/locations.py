from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Location

from . import items

from .item_data import tracklist, unitlist, supportlist, scenariolist

if TYPE_CHECKING:
    from .world import LLSIFWorld

LOCATION_NAME_TO_ID = {}
difficulties = ["Easy", "Normal", "Hard", "Expert"]
included_live_locations = []

for track in tracklist:
    name = track["name_en"]
    LOCATION_NAME_TO_ID[f"{name} - Clear"] = (100000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - C Rank"] = (101000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - B Rank"] = (102000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - A Rank"] = (103000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - S Rank"] = (104000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Full Combo"] = (105000 + track["id"])

    LOCATION_NAME_TO_ID[f"{name} - Easy Clear"] = (110000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Easy C Rank"] = (111000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Easy B Rank"] = (112000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Easy A Rank"] = (113000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Easy S Rank"] = (114000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Easy Full Combo"] = (115000 + track["id"])

    LOCATION_NAME_TO_ID[f"{name} - Normal Clear"] = (120000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Normal C Rank"] = (121000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Normal B Rank"] = (122000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Normal A Rank"] = (123000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Normal S Rank"] = (124000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Normal Full Combo"] = (125000 + track["id"])

    LOCATION_NAME_TO_ID[f"{name} - Hard Clear"] = (130000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Hard C Rank"] = (131000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Hard B Rank"] = (132000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Hard A Rank"] = (133000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Hard S Rank"] = (134000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Hard Full Combo"] = (135000 + track["id"])

    LOCATION_NAME_TO_ID[f"{name} - Expert Clear"] = (140000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Expert C Rank"] = (141000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Expert B Rank"] = (142000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Expert A Rank"] = (143000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Expert S Rank"] = (144000 + track["id"])
    LOCATION_NAME_TO_ID[f"{name} - Expert Full Combo"] = (145000 + track["id"])

for id in range(1,51):
    LOCATION_NAME_TO_ID[f"Sticker Shop - Item {id}"] = id

# Disabled for now, needlessly bloats location data and is useless until I add the evil feature its used for
for unit in unitlist:
    break
    name = unit["name_en"]
    eponym = unit["eponym_en"]

    if eponym is None:
        LOCATION_NAME_TO_ID[f"{name} ({unit["id"]})"] = (200000 + unit["id"])
    else:
        LOCATION_NAME_TO_ID[f"{eponym} - {name}"] = (200000 + unit["id"])

# Same as above
for support in supportlist:
    break
    name = support["name_en"]
    eponym = support["eponym_en"]

    if eponym is None:
        LOCATION_NAME_TO_ID[f"{name} ({support["id"]})"] = (200000 + support["id"])
    else:
        LOCATION_NAME_TO_ID[f"{eponym} - {name}"] = (200000 + support["id"])

counter = 1
for chapter in scenariolist:
    if chapter["id"] < 100 or chapter["id"] == 1000 or chapter["id"] == 2000:
        chap = chapter["name_en"].split(" - ")
        LOCATION_NAME_TO_ID[f"{chap[len(chap)-1]}"] = 4000 + counter
        counter += 1


class LLSIFLocation(Location):
    game = "Love Live! School idol festival"

def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_NAME_TO_ID[location_name] for location_name in location_names}


def create_all_locations(world: LLSIFWorld) -> None:
        
    create_regular_locations(world)


def create_regular_locations(world: LLSIFWorld) -> None:

    all_lives = world.all_lives
    live_names = []
    included_live_locations = []
    for live in all_lives:
        live_names.append(live.split(" - ")[1])
    
    region = world.get_region("Menu")
    if not world.options.shop_checks == 0:
        for id in range(1,world.options.shop_checks+1):
            region_location = get_location_names_with_ids([f"Sticker Shop - Item {id}"])
            region.add_locations(region_location, LLSIFLocation)

    for key, value in LOCATION_NAME_TO_ID.items():
        if value in range(100000, 200000):
            if key.split(" - ")[0] in live_names:
                if world.options.individual_difficulty and len(list(world.options.included_difficulty)) > 0:
                    difficulty_values = []
                    for dif in world.options.included_difficulty:
                        difficulty_values.append(difficulties.index(dif)+1)
                    for dif_value in difficulty_values:
                        if value in range(100000 + (dif_value*10000), 101000 + (dif_value*10000)):
                            region.add_locations(get_location_names_with_ids([key]), LLSIFLocation)
                            included_live_locations.append(key)
                        if world.options.live_rank > 0 and value in range(101000 + (dif_value*10000), 100000 + (dif_value*10000) + ((world.options.live_rank+1) * 1000)):
                            region.add_locations(get_location_names_with_ids([key]), LLSIFLocation)
                            included_live_locations.append(key)
                        if world.options.fc_checks:
                            if value in range(105000 + (dif_value*10000), 106000 + (dif_value*10000)):
                                region.add_locations(get_location_names_with_ids([key]), LLSIFLocation)
                                included_live_locations.append(key)
                else:
                    if value in range(100000, 101000):
                        region.add_locations(get_location_names_with_ids([key]), LLSIFLocation)
                        included_live_locations.append(key)
                    if world.options.live_rank > 0 and value in range(101000, ((world.options.live_rank+1) * 1000)+100000):
                        region.add_locations(get_location_names_with_ids([key]), LLSIFLocation)
                        included_live_locations.append(key)
                    if world.options.fc_checks:
                        if value in range(105000,106000):
                            region.add_locations(get_location_names_with_ids([key]), LLSIFLocation)
                            included_live_locations.append(key)
    world.included_live_locations = included_live_locations

    counter = 1
    if world.options.story_checks:
        for chapter in scenariolist:
            if chapter["id"] < 100 or chapter["id"] == 1000 or chapter["id"] == 2000:
                chap = chapter["name_en"].split(" - ")
                if counter <= 48:
                    if 1 in world.included_group_ids and not counter == 1:
                        region.add_locations(get_location_names_with_ids([f"{chap[len(chap)-1]}"]), LLSIFLocation)
                else:
                    if 2 in world.included_group_ids and not counter == 49:
                        region.add_locations(get_location_names_with_ids([f"{chap[len(chap)-1]}"]), LLSIFLocation)
                counter += 1

    if world.options.unitsanity:
        for unit in unitlist:
            name = unit["name_en"]
            eponym = unit["eponym_en"]
            if eponym is None:
                region.add_locations(get_location_names_with_ids([f"{name} ({unit["id"]})"]), LLSIFLocation)
            else:
                region.add_locations(get_location_names_with_ids([f"{eponym} - {name}"]), LLSIFLocation)

        for support in supportlist:
            name = support["name_en"]
            eponym = support["eponym_en"]

            if eponym is None:
                region.add_locations(get_location_names_with_ids([f"{name} ({support["id"]})"]), LLSIFLocation)
            else:
                region.add_locations(get_location_names_with_ids([f"{eponym} - {name}"]), LLSIFLocation)

    #region.add_event("Goal Live Count Completed", "Victory", location_type=LLSIFLocation, item_type=items.LLSIFItem)