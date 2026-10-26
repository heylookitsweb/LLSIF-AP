from collections.abc import Mapping
from typing import Any, Dict, Set

from worlds.AutoWorld import World

from . import items, locations, regions, rules
from . import options as yaml_options
from .item_data import unitlist, supportlist

class LLSIFWorld(World):
    """
    Play through Live Shows, read stories about the many interesting and unique characters, join in the events, and create and strengthen your own team of school idols!
    """

    game = "Love Live! School idol festival"

    options_dataclass = yaml_options.LLSIFOptions
    options: yaml_options.LLSIFOptions

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID
    item_name_groups: Dict[str, Set] = {
        "Live Shows": set()
    }   
    
    origin_region_name = "Menu"
    all_lives = []
    included_live_locations = []
    start_lives = []
    start_ids = []

    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        items.calculate_available_lives(self)
        lives, live_ids = items.get_lives()
        self.included_live_locations = locations.included_live_locations
        for live in lives["progression"]:
            self.all_lives.append(live)
        for live in lives["extra"]:
            self.all_lives.append(live)
        self.item_name_groups["Live Shows"] = frozenset(self.all_lives)
        for live in lives["starting"]:
            self.all_lives.append(live)
            self.start_lives.append(live)
        self.start_ids = live_ids["starting"]
        locations.create_all_locations(self)

    def set_rules(self) -> None:
        rules.set_all_rules(self)

    def create_items(self) -> None:
        items.create_all_items(self)

    def create_item(self, name: str) -> items.LLSIFItem:
        return items.create_item_with_correct_classification(self, name)

    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    def fill_slot_data(self) -> Mapping[str, Any]:
        char_names = [
            ["Honoka Kosaka", "Eli Ayase", "Kotori Minami", "Umi Sonoda", "Rin Hoshizora", "Maki Nishikino", "Nozomi Tojo", "Hanayo Koizumi", "Nico Yazawa"],
            ["Chika Takami", "Riko Sakurauchi", "Kanan Matsuura", "Dia Kurosawa", "You Watanabe", "Yoshiko Tsushima", "Hanamaru Kunikida", "Mari Ohara", "Ruby Kurosawa"],
            ["Ayumu Uehara", "Kasumi Nakasu", "Shizuku Osaka", "Karin Asaka", "Ai Miyashita", "Kanata Konoe", "Setsuna Yuki", "Emma Verde", "Rina Tennoji", "Shioriko Mifune", "Lanzhu Zhong", "Mia Taylor"],
            ["Kanon Shibuya", "Keke Tang", "Chisato Arashi", "Sumire Heanna", "Ren Hazuki", "Kinako Sakurakoji", "Mei Yoneme", "Shiki Wakana", "Natsumi Onitsuka"]
        ]

        options_dict = self.options.as_dict(
            "live_count",
            "live_start_count",
            "live_extra",
            "live_difficulty",
            "live_rank",
            "fc_checks",
            "shop_checks",
            "individual_difficulty",
            "included_difficulty",
            "filler_support_percentage",
            "send_deathlinks",
            "fc_deathlinks",
            "unitsanity",
        )
        options_dict["starting_lives"] = self.start_ids
        # resetting / capping options based on if they are possible / invalid
        options_dict["live_count"] = int(items.goal_live_count)
        options_dict["included_groups"] = items.included_group_ids
        options_dict["individual_difficulty"] = bool(len(list(options_dict["included_difficulty"])) > 0)

        # randomize the UR cards given to you when you start a save, accounting for all variations of included groups
        included_groups = items.included_group_ids

        unit_options = [[],[],[],[]]
        for id in range(0,len(char_names)):
            for name in char_names[id]:
                unit_options[id].append([])

        for unit in unitlist:
            if unit["rarity"] == 4 and not unit["group"] == 0 and unit["group"] in items.included_group_ids:
                unit_options[unit["group"]-1][char_names[unit["group"]-1].index(unit["name_en"])].append(unit["id"])

        if 1 in included_groups and 2 in included_groups:
            group_1 = 1
            group_2 = 2
        elif included_groups == [1]:
            group_1 = 1
            group_2 = 1
        elif included_groups == [2]:
            group_1 = 2
            group_2 = 2
        elif included_groups == [3]:
            group_1 = 3
            group_2 = 3
        elif included_groups == [4]:
            group_1 = 4
            group_2 = 4
        elif 1 in included_groups:
            included_groups.remove(1)
            group_1 = 1
            group_2 = self.random.choice(included_groups)
        elif 2 in included_groups:
            included_groups.remove(2)
            group_1 = self.random.choice(included_groups)
            group_2 = 2
        else:
            group_1 = 3
            group_2 = 4

        starting_units = [[],[]]
        chars = self.random.sample(range(0,len(unit_options[group_1-1])), 9)
        chars.sort()
        for char in chars:
            starting_units[0].append(self.random.choice(unit_options[group_1-1][char]))
        if group_1 == group_2:
            starting_units[1] = starting_units[0]
        else:
            chars = self.random.sample(range(0,len(unit_options[group_2-1])), 9)
            chars.sort()
            for char in chars:
                starting_units[1].append(self.random.choice(unit_options[group_2-1][char]))

        options_dict["starting_units"] = starting_units

        # randomize the set of N Girls that the new save file is given
        support_options = []
        for support in supportlist:
            support_options.append(support["id"])
        starting_supports = self.random.sample(support_options, 8)
        starting_supports.insert(4, 0)
        options_dict["starting_supports"] = starting_supports
        return options_dict
