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
    live_names = []
    for live in world.all_lives:
        live_names.append(live.split(" - ")[1])
    for live_loc in world.included_live_locations:
        world.set_rule(world.get_location(live_loc), Has(world.all_lives[live_names.index(live_loc.split(" - ")[0])]))
        
    if world.options.story_checks:
        chap_counter = 1
        for chapter in scenariolist:
            if chapter["id"] < 100 or chapter["id"] == 1000 or chapter["id"] == 2000:
                chap = chapter["name_en"].split(" - ")
                if chap_counter <= 48:
                    if 1 in world.included_group_ids and not chap_counter == 1:
                        world.set_rule(world.get_location(f"{chap[len(chap)-1]}"), Has("Progressive μ's Main Story", count=chap_counter))
                else:
                    if 2 in world.included_group_ids and not chap_counter == 49:
                        world.set_rule(world.get_location(f"{chap[len(chap)-1]}"), Has("Progressive Aqours Main Story", count=chap_counter-48))
            chap_counter += 1        

# Currently unused as the client sends a completion flag directly, 
# but I'm keeping it here for potential future Universal Tracker support.

    #can_complete_goal_count: Rule = HasGroupUnique(item_name_group = "Live Shows", count = int(goal_live_count))
    #world.set_rule(world.get_location("Goal Live Count Completed"), can_complete_goal_count)
    #world.set_completion_rule(Has("Victory"))