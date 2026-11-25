import asyncio
import os
import pydantic
import sqlalchemy
import json
import time
from asyncio import Server

from archipelagopy import packets, structs
from archipelagopy.callback_interface import OnConnectExceptionUnion
from archipelagopy.client import Client
from archipelagopy.enums.item_handling_flag import ItemHandlingFlag
from .. import idol, system, const, serialcode, util
from ..data import schema
from ..db import main
from . import item_data
from ..config import config
from ..data import schema

muse = ["Honoka Kosaka", "Eli Ayase", "Kotori Minami", "Umi Sonoda", "Rin Hoshizora", "Maki Nishikino", "Nozomi Tojo", "Hanayo Koizumi", "Nico Yazawa"]
aquors = ["Chika Takami", "Riko Sakurauchi", "Kanan Matsuura", "Dia Kurosawa", "You Watanabe", "Yoshiko Tsushima", "Hanamaru Kunikida", "Mari Ohara", "Ruby Kurosawa"]
niji = ["Ayumu Uehara", "Kasumi Nakasu", "Shizuku Osaka", "Karin Asaka", "Ai Miyashita", "Kanata Konoe", "Setsuna Yuki", "Emma Verde", "Rina Tennoji", "Shioriko Mifune", "Mia Taylor", "Lanzhu Zhong"]
liella = ["Kanon Shibuya", "Keke Tang", "Chisato Arashi", "Sumire Heanna", "Ren Hazuki", "Kinako Sakurakoji", "Mei Yoneme", "Shiki Wakana", "Natsumi Onitsuka", "Wien Margarete", "Tomari Onitsuka"]

mainclient = None
ap_context = None
linked_user = None
is_connected = False
initialized = False
connectionerror = "Unknown error occured."
options = {}
game_data = {}
slot_info = {}
save_data = None
room_address = ""
room_seed = ""
user_id = -1
slot_name = ""
unclaimed_items = []
filler_item_counts = {}
progressive_items = [0,0]
ap_item_data = None
sticker_shop = []
secretbox_data = []
sloomber_event = None
fake_ach_items = []
fake_ach_check = False
destructible_ach_items = []

class SIFClient(Client):

    async def on_ready(self):
        print("Client is connected and ready")

    async def on_room_info(self, packet: packets.RoomInfo):
        global save_data
        global mainclient
        global initialized
        global room_seed
        gamelist = []

        for game in packet.games:
            gamelist.append(game)

        await mainclient.send(
            packets.ConnectUpdate(
                items_handling=ItemHandlingFlag.OWN_WORLD | ItemHandlingFlag.OTHER_WORLDS | ItemHandlingFlag.STARTING_INVENTORY,
                tags=["AP","DeathLink","NoText"]
            )
        )
        await mainclient.send(
            packets.GetDataPackage(
                games=gamelist
            )
        )

        room_info = packet
        room_seed = str(packet.seed_name)

        if os.path.isfile(os.path.join(config.ROOT_DIR, f"data\\apsaves\\{room_seed}.json")):
            save_data = json.load(open(os.path.join(config.ROOT_DIR, f"data\\apsaves\\{room_seed}.json"),"r"))
        

    async def on_data_package(self, packet: packets.DataPackage):
        global game_data
        game_data = packet.data.games

    async def on_location_info(self, packet: packets.LocationInfo):
        global sloomber_event
        global ap_item_data

        ap_item_data = packet.locations
        sloomber_event.set()

    def on_connect_error(self, error: OnConnectExceptionUnion):
        global connectionerror
        global is_connected
        global sloomber_event
        connectionerror = "Failed to connect: " + str(error)
        print("Failed to connect:", error)
        sloomber_event.set()
        is_connected = False
        with open(os.path.join(config.ROOT_DIR, "maintenance.txt"), "w") as maintenance:
            maintenance.write("Disconnected from APWorld. Please Reconnect.")

    async def on_connection_refused(self, packet: packets.ConnectionRefused):
        global connectionerror
        global sloomber_event
        connectionerror = "Connection refused: " + str(packet.errors)
        print("Connection refused:", packet.errors)
        sloomber_event.set()
        with open(os.path.join(config.ROOT_DIR, "maintenance.txt"), "w") as maintenance:
            maintenance.write("Disconnected from APWorld. Please Reconnect.")

    async def on_connected(self, packet: packets.Connected):
        global connectionerror
        global playerlist
        global linked_user
        global is_connected
        global initialized
        global options
        global sloomber_event
        global slot_info

        connectionerror = None
        is_connected = True
        options = packet.slot_data
        slot_info = packet.slot_info
        sloomber_event.set()

    #async def on_packet(self, packet: Server):
        #print(f">> ({packet})\n")

    async def on_received_items(self, packet: packets.ReceivedItems):
        global linked_user
        global playerlist
        global codes
        global ap_context
        global unclaimed_items
        global room_seed
        if packet.index == 0:
            unclaimed_items = []
        for received_item in packet.items:
            unclaimed_items.append(received_item)


    def on_connection_closed(self, close_code):
        global is_connected
        print("Connection Closed")
        is_connected = False
        with open(os.path.join(config.ROOT_DIR, "maintenance.txt"), "w") as maintenance:
            maintenance.write("Disconnected from APWorld. Please Reconnect.")

async def connect_to_server(address, port, slot, password):
    global mainclient
    global connectionerror
    global is_connected
    global slot_name
    global sloomber_event
    global room_address

    connectionerror = "Unknown error occured."
    is_connected = None
    slot_name = slot
    room_address = address + ":" + port
    if mainclient is not None:
        await mainclient.stop()
    mainclient = SIFClient(port=port,host=address,auto_reconnect=False)
    await mainclient.start()

    sloomber_event = asyncio.Event()
    sloomber_task = asyncio.create_task(connection_wait())

    await mainclient.send(
            packets.Connect(
            version=structs.Version(major=0, minor=6, build=7),
            tags=["AP", "NoText"],
            name=slot,
            game="Love Live! School idol festival",
            password=password,
            items_handling=ItemHandlingFlag.OWN_WORLD | ItemHandlingFlag.OTHER_WORLDS | ItemHandlingFlag.STARTING_INVENTORY,
            slot_data=True
        )
    )

    await sloomber_task
    sloomber_event = None

async def get_errors():
    global mainclient
    global connectionerror
    global is_connected
    if connectionerror is not None:
        is_connected = False
        return {"ok": False, "msg": connectionerror}
    is_connected = True
    return {"ok": True, "msg": "Connected Successfully!"}

async def send_check(checks: int | list[int]):
    global mainclient
    global connectionerror
    global is_connected

    if type(checks) == int:
        checks_list = [checks]
    else:
        checks_list = checks
    await mainclient.send(
        packets.LocationChecks(
            locations=checks_list
        )
    )

async def reward_sync():
    global mainclient
    global unclaimed_items
    global claimed_items
    global linked_user
    global ap_context
    global save_data
    global filler_item_counts

    item_list = unclaimed_items.copy()
    for received_item in item_list:
        if received_item.item < 1000 or received_item.item >= 10000:
            if not str(received_item.item) in save_data["filler_item_counts"]:
                save_data["filler_item_counts"][str(received_item.item)] = 0
            if not str(received_item.item) in filler_item_counts:
                filler_item_counts[str(received_item.item)] = 0

            if filler_item_counts[str(received_item.item)] >= save_data["filler_item_counts"][str(received_item.item)]:
                await receive_item(received_item)
                save_data["filler_item_counts"][str(received_item.item)] += 1
            filler_item_counts[str(received_item.item)] += 1
        elif received_item.item in range(4000,4003):
            if progressive_items[received_item.item-4001] >= save_data["progressive_item_counts"][str(received_item.item)]:
                if not progressive_items[received_item.item-4001] == 0:
                    for chapter in item_data.scenariolist:
                        if (received_item.item == 4001 and chapter["id"] == progressive_items[received_item.item-4001]) or (received_item.item == 4002 and chapter["id"] == 47 + progressive_items[received_item.item-4001]):
                            for part in chapter["episodes"]:
                                temp_item_id = received_item.item
                                received_item.item = 4000 + part["id"]
                                await receive_item(received_item)
                                received_item.item = temp_item_id
                            break
                save_data["progressive_item_counts"][str(received_item.item)] += 1
            progressive_items[received_item.item-4001] += 1
        else:
            if not received_item.item in save_data["normal_items"]:
                await receive_item(received_item)
                save_data["normal_items"].append(received_item.item)
        unclaimed_items.remove(received_item)

    write_save_file()

    
async def receive_item(received_item):
    global ap_context
    global linked_user
    global save_data
    async with idol.BasicSchoolIdolContext() as context:
        item_data = None
        if received_item.item in range(1000,2000):
            unlocked_lives = await system.live.get_all_normal_live_unlock(context, linked_user)
            if not (received_item.item - 1000) in unlocked_lives:
                item_data = await system.advanced.deserialize_item_data(ap_context, system.item_model.BaseItem(add_type=const.ADD_TYPE.LIVE, item_id=(received_item.item - 1000), amount=1))
        elif received_item.item in range(3000,4000):
            item_data = await system.advanced.deserialize_item_data(ap_context, system.item_model.BaseItem(add_type=const.ADD_TYPE.BACKGROUND, item_id=(received_item.item - 3000), amount=1))
        elif received_item.item in range(4000,5000):
            item_data = await system.advanced.deserialize_item_data(ap_context, system.item_model.BaseItem(add_type=const.ADD_TYPE.SCENARIO, item_id=(received_item.item - 4000), amount=1))
        elif received_item.item >= 10000:
            item_data = await system.advanced.deserialize_item_data(ap_context, system.item_model.BaseItem(add_type=const.ADD_TYPE.UNIT, item_id=(received_item.item - 10000), amount=1))
        elif received_item.item < 1000:
            async with idol.BasicSchoolIdolContext() as context:
                if received_item.item == 1:
                    item_data = await system.advanced.deserialize_item_data(ap_context, system.item_model.BaseItem(add_type=const.ADD_TYPE.LOVECA, item_id=4, amount=1))
                
                elif received_item.item == 2:
                    item_data = await system.advanced.deserialize_item_data(ap_context, system.item_model.BaseItem(add_type=const.ADD_TYPE.GAME_COIN, item_id=3, amount=100))
                elif received_item.item == 3:
                    item_data = await system.advanced.deserialize_item_data(ap_context, system.item_model.BaseItem(add_type=const.ADD_TYPE.GAME_COIN, item_id=3, amount=1000))
                elif received_item.item == 4:
                    item_data = await system.advanced.deserialize_item_data(ap_context, system.item_model.BaseItem(add_type=const.ADD_TYPE.GAME_COIN, item_id=3, amount=5000))
                elif received_item.item == 5:
                    item_data = await system.advanced.deserialize_item_data(ap_context, system.item_model.BaseItem(add_type=const.ADD_TYPE.GAME_COIN, item_id=3, amount=10000))

                elif received_item.item == 6:
                    item_data = await system.advanced.deserialize_item_data(ap_context, system.item_model.BaseItem(add_type=const.ADD_TYPE.SOCIAL_POINT, item_id=2, amount=100))
                elif received_item.item == 7:
                    item_data = await system.advanced.deserialize_item_data(ap_context, system.item_model.BaseItem(add_type=const.ADD_TYPE.SOCIAL_POINT, item_id=2, amount=500))
                elif received_item.item == 8:
                    item_data = await system.advanced.deserialize_item_data(ap_context, system.item_model.BaseItem(add_type=const.ADD_TYPE.SOCIAL_POINT, item_id=2, amount=1000))

                if received_item.item == 10:
                    item_data = await system.advanced.deserialize_item_data(ap_context, system.item_model.BaseItem(add_type=const.ADD_TYPE.LOVECA, item_id=4, amount=5))

        if not item_data is None:
            if received_item.player == 0:
                await system.reward.add_item(ap_context, linked_user, item_data, f"A gift from the heavens above!")
            else:
                await system.reward.add_item(ap_context, linked_user, item_data, f"A gift from {playerlist[received_item.player-1].name}!")

async def new_user(id: int):
    global user_id
    global save_data
    global room_seed
    global ap_context
    global linked_user

    if is_connected:
        base_data = json.load(open(os.path.join(config.ROOT_DIR, "data\\apsaves\\base.json"), "r"))
        user_id = id
        base_data["user_id"] = user_id
        save_data = base_data

        for live in options["starting_lives"]:
            save_data["normal_items"].append(live)
        
        write_save_file()

def write_save_file():
    global save_data
    global room_seed
    if not save_data is None and not room_seed == "":
        with open(os.path.join(config.ROOT_DIR, f"data\\apsaves\\{room_seed}.json"), "w") as save_file:
            save_file.write(json.dumps(save_data, indent=4))

async def live_complete(live_setting, score_rank, combo_rank):
    global save_data
    global options

    difficulties = ["Easy", "Normal", "Hard", "Expert"]
    track_id = live_setting.live_track_id
    difficulty = live_setting.difficulty
    real_score_rank = 5 - score_rank
    real_combo_rank = 5 - combo_rank
    checklist = []

    if not str(track_id) in save_data["completion"]:
        save_data["completion"][str(track_id)] = []
    if not str(track_id+1000) in save_data["tracker"]:
        save_data["tracker"][str(track_id+1000)] = [[],[],[],[],[]]
        for i in range(0,5):
            save_data["tracker"][str(track_id+1000)][i] = [False, False, False, False, False, False]


    if options["individual_difficulty"] == 0:
        save_data["tracker"][str(track_id+1000)][0] = [
            True,
            real_score_rank>=1,
            real_score_rank>=2,
            real_score_rank>=3,
            real_score_rank>=4,
            real_combo_rank==4
        ]

        if difficulty >= options["live_difficulty"]:
            if real_score_rank >= options["live_rank"]:
                if not 0 in save_data["completion"][str(track_id)]:
                    save_data["completion"][str(track_id)].append(0)

            checklist.append(100000 + track_id)
            if not real_score_rank == 0:
                for rank in range(1,real_score_rank+1):
                    checklist.append(100000 + (rank*1000) + track_id)
            if options["fc_checks"] == 1 and real_combo_rank == 4:
                checklist.append(105000 + track_id)
    elif difficulty <= 4:
        save_data["tracker"][str(track_id+1000)][difficulty] = [
            True,
            real_score_rank>=1,
            real_score_rank>=2,
            real_score_rank>=3,
            real_score_rank>=4,
            real_combo_rank==4
        ]

        if difficulties[difficulty-1] in options["included_difficulty"]:
            if real_score_rank >= options["live_rank"]:
                if not difficulty in save_data["completion"][str(track_id)]:
                    save_data["completion"][str(track_id)].append(difficulty)

            checklist.append(100000 + (difficulty*10000) + track_id)
            if not real_score_rank == 0:
                for rank in range(1,real_score_rank+1):
                    checklist.append(100000 + (difficulty*10000) + (rank*1000) + track_id)
            if options["fc_checks"] == 1 and real_combo_rank == 4:
                checklist.append(105000 + (difficulty*10000) + track_id)
    if len(checklist) > 0:
        await send_check(checklist)
    await check_completion()
    write_save_file()

async def send_deathlink():
    global mainclient
    global slot_name

    if options["send_deathlinks"] == 1:
        await mainclient.send(
            packets.Bounce(
                slots=[],
                tags=["DeathLink"],
                games=[],
                data={
                    "cause": f"{slot_name} failed a Live Show.",
                    "source": slot_name,
                    "time": time.time()
                }
            )
        )

async def update_sticker_shop(data: list):
    global sticker_shop
    global options
    global is_connected
    global mainclient
    global sloomber_event
    global ap_item_data
    global game_data
    global slot_info

    result = data
    if is_connected:
        if sticker_shop == []:
            if options["shop_checks"] > 0:

                sloomber_event = asyncio.Event()
                sloomber_task = asyncio.create_task(connection_wait())

                await mainclient.send(
                    packets.LocationScouts(
                        locations=range(1,options["shop_checks"]+1),
                        create_as_hint=2
                    )
                )

                await sloomber_task
                hint_ids = {}
                for game in game_data:
                    hint_ids[game] = {}
                hints = []
                for shop_item in ap_item_data:
                    hint_ids[slot_info[shop_item.player].game][shop_item.item] = None
                    hints.append({"id": shop_item.item, "location": shop_item.location, "player": shop_item.player, "name": f"{slot_info[shop_item.player].name}'s Unknown Item"})

                for game in game_data:
                    if not hint_ids[game] == {}:
                        for item, id in game_data[game].item_name_to_id.items():
                            if id in hint_ids[game]:
                                hint_ids[game][id] = item
                for hint in hints:
                    name = hint_ids[slot_info[hint["player"]].game][hint["id"]]
                    if name is not None:
                        hint["name"] = f"{slot_info[hint["player"]].name}'s {name}"
                
            for item in result:
                if "ap_item" in item.id_string:
                        id = int(item.id_string.split("_")[2])
                        if id <= options["shop_checks"]:
                            item = item.model_copy(update={"name_en": hints[id-1]["name"]})
                            sticker_shop.append(item)
                else:
                    sticker_shop.append(item)
        result = sticker_shop

    return result

async def connection_wait():
    global sloomber_event
    print("Attempting APWorld connection")
    await sloomber_event.wait()

def update_secretbox_data(data: schema.SerializedServerData):
    global is_connected
    global secretbox_data
    global options

    if is_connected:
        if secretbox_data == []:
            for box in data.secretbox_data:
                names = ["","myus","aqua","niji","lila"]
                if any(names[name_id] in box.id_string for name_id in options["included_groups"]):
                    secretbox_data.append(box)
        return secretbox_data
    else:
        return data.secretbox_data

async def check_completion():
    global save_data
    global options
    global mainclient
    count = 0
    difficulties = ["Easy", "Normal", "Hard", "Expert"]
    difficulty_ids = []
    for diff in options["included_difficulty"]:
        difficulty_ids.append(difficulties.index(diff)+1)

    if save_data is not None:
        count = 0
        for live in save_data["completion"]:
            data = save_data["completion"][live]
            if 0 in data or (options["individual_difficulty"] == 1 and all([diff in data for diff in difficulty_ids])):
                count += 1
        if count >= options["live_count"]:
            await mainclient.send(
                packets.StatusUpdate(
                    status = 30
                )
            )
    return count
        

def get_available_checks():
    global is_connected
    global item_data
    global options
    global save_data

    ranks = [None, "C", "B", "A", "S"]
    difficulties = [None, "Easy", "Normal", "Hard", "Expert"]

    if is_connected:
        result = []
        for live in item_data.tracklist:
            if live["id"]+1000 in save_data["normal_items"]:
                row = [live["name_en"]]

                if str(live["id"]+1000) in save_data["tracker"]:
                    if options["individual_difficulty"] == 0:
                        row.append(save_data["tracker"][str(live["id"]+1000)][0])
                        for i in range(1,5):
                            row.append([False,False,False,False,False,False])
                    else:
                        row.append([False,False,False,False,False,False])
                        for diff in range(1,5):
                            if difficulties[diff] in options["included_difficulty"]:
                                row.append(save_data["tracker"][str(live["id"]+1000)][diff])
                            else:
                                row.append([False,False,False,False,False,False])
                else:
                    for i in range(0,5):
                        row.append([False,False,False,False,False,False])
                row.append(True)
                result.append(row)
                if len(result) > 1:
                    result[len(result)-2][6] = False
        return result
    return []

def get_tracker_options():
    global options
    
    stories = get_tracker_stories()

    result = [
        bool(options["individual_difficulty"] == 1),
        bool("Easy" in options["included_difficulty"]),
        bool("Normal" in options["included_difficulty"]),
        bool("Hard" in options["included_difficulty"]),
        bool("Expert" in options["included_difficulty"]),
        options["live_rank"],
        bool(options["fc_checks"] == 1),
        len(options["included_difficulty"]),
    ]

    columns = 1
    if options["individual_difficulty"] == 1:
        columns += 1
    columns += options["live_rank"]
    if options["fc_checks"] == 1:
        columns += 1
    result.append(columns)
    result.append(options["live_count"])
    result.append(bool(1 in options["included_groups"] and not stories[0] == []))
    result.append(bool(2 in options["included_groups"] and not stories[1] == []))
    result.append(slot_name)
    result.append(room_address)
    result.append(bool(options["story_checks"] == 1))
    return result

def get_tracker_stories():
    global item_data

    result = [[],[]]
    counter = 0
    for chapter in item_data.scenariolist:
        id = chapter["id"]
        if id <= 47 and not id == 1000:
            if 1 in options["included_groups"]:
                if counter < save_data["progressive_item_counts"]["4001"]:
                    chap = [chapter["name_en"],len(chapter["episodes"]),[],True]
                    for ep in chapter["episodes"]:
                        if str(ep["id"]+4000) in save_data["tracker"]:
                            chap[2].append(True)
                        else:
                            chap[2].append(False)
                    result[0].append(chap)
                    if len(result[0]) > 1:
                        result[0][len(result[0])-2][3] = False
                    
        elif id <= 83 and not id == 2000:
            if 2 in options["included_groups"]:
                if id == 2000:
                    counter = 0
                if counter < save_data["progressive_item_counts"]["4002"]:
                    chap = [chapter["name_en"],len(chapter["episodes"]),[], True]
                    for ep in chapter["episodes"]:
                        if str(ep["id"]+4000) in save_data["tracker"]:
                            chap[2].append(True)
                        else:
                            chap[2].append(False)
                    result[1].append(chap)
                    if len(result[1]) > 1:
                        result[1][len(result[1])-2][3] = False
        counter += 1
    return result

def create_fake_ach_items(item_datas):
    global fake_ach_items
    global fake_ach_check
    fake_ach_items = []
    group = []
    for item_data in item_datas:
        if item_data.add_type == const.ADD_TYPE.LIVE or item_data.add_type == const.ADD_TYPE.SCENARIO:
            group.append(system.item_model.BaseItem(add_type=item_data.add_type, item_id=item_data.item_id, amount=1))
            if len(group) == 3:
                fake_ach_items.append(group)
                group = []
    if len(group) > 0:
        fake_ach_items.append(group)
    fake_ach_check = True
    return fake_ach_items
    
async def check_story_completion(scenario_id):
    global ap_context
    global linked_user
    counter = 1
    for chapter in item_data.scenariolist:
        for ep in chapter["episodes"]:
            if ep["id"] == scenario_id:
                for ep in chapter["episodes"]:
                    if chapter["id"] == 1000 or chapter["id"] == 2000 or (not ep["id"] == scenario_id and not await system.scenario.is_completed(ap_context, linked_user, ep["id"])):
                        return
                await send_check((4000 + counter))
                return
        counter += 1