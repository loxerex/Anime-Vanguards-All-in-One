import json
import os
import time
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Tools"))
import winTools as wt
import Function_Dictionary as fd
from threading import Thread
from threading import Event

def load_state():
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"Info", "state.json")
    with open(json_path, 'r') as file:
        return json.load(file)
def update_state(data):
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"Info", "state.json")
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)


def load_settings():
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Settings", "Event", "Whitebeard_Event.json")
    with open(json_path, 'r') as file:
        return json.load(file)   

rb_window = wt.get_window("Roblox")
offset = (rb_window.left, rb_window.top)

print(offset)
Settings = load_settings()["configs"][f"{load_settings()["selected"]}"]
Units = Settings["Units"]
Order = Settings["Order"]
Do_AutoPos = Settings["Auto_Pos"]

Thread_Event = Event()

def do_cards():
    while True:
        if Thread_Event.is_set():
            return
        if fd.does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or fd.does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
            break
        if fd.does_exist("WhitebeardCard.png",confidence=0.9,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.top+rb_window.height)):
            fd.click(408+offset[0], 311+offset[1])
            time.sleep(1)
        time.sleep(2)
import keyboard
def order_interpator(key,unit,action_index):
    if "setp" in key:  
        selected = Units.get(str(unit))
        action = selected.get("placements")[action_index]
        fd.select_unit(action, offset=offset)
        amount = key.split("_")[1]
        for i in range (int(amount)):
            keyboard.press_and_release('r')
        fd.click(305+offset[0], 232+offset[1])
    if "place" in key:
        print(key)
        selected = Units.get(str(unit))
        action = selected.get("placements")[action_index]
        if len(key.split("_")) > 1:
            fd.place_unit(unit, action,upg=key.split("_")[1],priority=int(key.split("_")[2]), offset=offset)
        else:
            fd.place_unit(unit, action, offset=offset)
    match key:
        case "upgrade":
            selected = Units.get(str(unit))
            print(selected.get("upgrades")[action_index])
            index,upgrade = selected.get("upgrades")[action_index]
            position = selected.get("placements")[index]
            fd.upgrade_unit(upgrade,position, offset=offset)
        case "sell":
            selected = Units.get(str(unit))
            position = selected.get("placements")[action_index]
            fd.sell_unit(unit, offset=offset)   
        case "ability":
            selected = Units.get(str(unit))
            print(selected.get("abilities")[action_index])
            index,ability,wave = selected.get("abilities")[action_index]
            if "AINZ_WORLDITEM_CALORIC" in ability.upper():
                ainz_caloric_unit = Settings["Caloric_Unit"]
                ainz_caloric_unit_position = Units.get("7").get("placements")[0]
                ability+= f"_{ainz_caloric_unit}_{ainz_caloric_unit_position[0]}_{ainz_caloric_unit_position[1]}"
            position = selected.get("placements")[index]
            print(ability)
            if wave is not None:
                while wave > fd.get_wave(offset=offset):
                    if fd.does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or fd.does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
                        break
                    time.sleep(1)
            fd.use_ability(position, ability, offset=offset)
        case "click":
            func = fd.click
            if action_index == 0:
                func(unit[0]+offset[0],unit[1]+offset[1])
            elif action_index == 1:
                func(unit[0]+offset[0],unit[1]+offset[1],right_click=True)
        case "wfs":
            func = fd.wait_for_spawn
            func(offset, action_index)
        case "start":
            func = fd.start
            func(offset)
        case "wfw":
            Thread_Event.clear()
            func = fd.wait_for_wave
            Thread(target=do_cards).start()
            func(action_index, offset)
            Thread_Event.set()
        case "rts":
            func = fd.return_to_spawn
            func(offset)
        case "press":
            func = fd.press
            func(unit,action_index)
        case "restart":
            func = fd.restart_match
            func(offset)
        case "wait":
            Thread_Event.clear()
            func = fd.wait
            Thread(target=do_cards).start()
            func(action_index)
            Thread_Event.set()


# action, unit_index, action_index
def load_aio_settings():
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Settings", "AIO_Settings.json")
    with open(json_path, 'r') as file:
        return json.load(file)   

def main():
    First_Match = True
    AINZ_SPELL = False
    fd.wait_for_spawn(offset,0)
    if Do_AutoPos:
        fd.auto_positioner("Frozen_Port",offset)
        time.sleep(1)
    while True:
        match_end = False
        win = False
        for func in Order:
            if "--worldlines" in sys.argv:
                if fd.does_exist("Challenge\\ModifierShow.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
                    fd.click(409+offset[0], 309+offset[1])
            # Win/Lose Check
            if fd.does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
                match_end = True
                win = True
                break
            if fd.does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
                match_end = True
                break
            
            # Pause
            while not load_state()["running"]:
                time.sleep(0.5)
                
            # Run through Order    
            if func[0] == "ability" and "AINZ_SPELLS" in Units.get(str(func[1])).get("abilities")[func[2]][1]:
                if not AINZ_SPELL:
                    order_interpator(func[0],func[1],func[2])
                    AINZ_SPELL = True
            else:
                # If the order is a first time event (only happens during the first match, then run it)
                if "end" not in func[0]:
                    if "FT_" in func[0]:    
                        arg = func[0].replace("FT_", "")
                        if First_Match:
                            order_interpator(arg,func[1],func[2])
                    else:
                        order_interpator(func[0],func[1],func[2])
                else:
                    match_end = True
                    win = True
                    break
        while not match_end:
            if "--worldlines" in sys.argv:
                if fd.does_exist("Challenge\\ModifierShow.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
                    fd.click(409+offset[0], 309+offset[1])
            if fd.does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
                match_end = True
                win = True
                break
            if fd.does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
                match_end = True
                break
            time.sleep(2)
        retry_button = (363, 471)  
        data = load_state()
        data["num_runs"]+=1
        if win:
            data["wins"]+=1
        else:
            data["losses"]+=1
        update_state(data)
        time.sleep(2)
        if  "--return" not in sys.argv:
            while fd.does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or fd.does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
                fd.click(retry_button[0]+offset[0],retry_button[1]+offset[1])
                time.sleep(1)
            if "--worldlines" in sys.argv:
                if win:
                    return
            First_Match = False # First match to false, so FT args wont repeat     
        else:
            fd.click(179+offset[0], 469+offset[1])
            return 
main()