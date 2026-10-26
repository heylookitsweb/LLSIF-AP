from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.options import OptionFilter
from rule_builder.rules import Has, Rule, HasGroupUnique, HasAny
from .item_data import tracklist, scenariolist
from . import items
GROUP_ID_TO_NAME = ["N/A", "μ's", "Aqours", "Nijigasaki", "Liella!"]

if TYPE_CHECKING:
    from .world import LLSIFWorld

def set_all_rules(world: LLSIFWorld) -> None:
    live_shows = list(world.item_name_groups["Live Shows"])
    start_lives = world.start_lives
    live_names = []
    for live in live_shows:
        live_names.append(live.split(" - ")[1])
    
    included_live_locations = world.included_live_locations.copy()
    for live_loc in included_live_locations:
        world.set_rule(world.get_location(live_loc), Has(live_shows[live_names.index(live_loc.split(" - ")[0])]))
    
    chap_counter = 1
    counter = 1
    for chapter in scenariolist:
        for story in chapter["episodes"]:
            if chapter["id"] < 100 or chapter["id"] == 1000 or chapter["id"] == 2000:
                if chapter["id"] == 2000:
                    chap_counter = 1
                chap = chapter["name_en"].split(" - ")
                if counter <= 183:
                    if 1 in items.included_group_ids:
                        world.set_rule(world.get_location(f"{chap[len(chap)-1]} - {story["name_en"]}"), Has("Progressive μ's Main Story", count=chap_counter))
                else:
                    if 2 in items.included_group_ids:
                        world.set_rule(world.get_location(f"{chap[len(chap)-1]} - {story["name_en"]}"), Has("Progressive Aqours Main Story", count=chap_counter))
                counter += 1
        chap_counter += 1
    can_complete_goal_count: Rule = HasGroupUnique(item_name_group = "Live Shows", count = int(items.goal_live_count))
    world.set_rule(world.get_location("Goal Live Count Completed"), can_complete_goal_count)
    world.set_completion_rule(Has("Victory"))