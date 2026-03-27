import os
import sys
import time
import json
import pydirectinput
import pyautogui
import keyboard
import ctypes
from pynput.mouse import Controller
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Tools import Function_Dictionary as fd # type: ignore
from Tools import winTools as wt# type: ignore
import subprocess
from threading import Thread
rb_window = wt.get_window("Roblox")
offset = (rb_window.left, rb_window.top)

WE_Json = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Settings", "Event", "Winter.json")

# testing commitasdasd

class testclass: 
    pass

Settings = testclass()

def load_state():
    """
    Load  state from Info/state.json.

    Returns:
        dict: Current runtime state, usually containing flags like:
            - running (bool): Whether the macro should actively continue
            - num_runs (int): Total completed runs
            - wins (int): Total wins
            - losses (int): Total losses
    """
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"Info", "state.json")
    with open(json_path, 'r') as file:
        return json.load(file)
    
def update_state(data):
    """
    Save runtime state to Info/state.json.

    Args:
        data (dict): Updated runtime state dictionary to write.
    """
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"Info", "state.json")
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)
def load_json_data():
    """
    Load Winter event settings JSON if it exists.

    Returns:
        dict | None:
            Parsed JSON data from Settings/Event/Winter.json,
            or None if the file does not exist.
    """
    JSON_DATA = None
    if os.path.isfile(WE_Json):
        with open(WE_Json, 'r') as f:
            JSON_DATA = json.load(f)
    return JSON_DATA
def load_aio_settings():
    """
    Load global AIO settings from Settings/AIO_Settings.json.

    Returns:
        dict: Parsed AIO settings data.
    """
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Settings", "AIO_Settings.json")
    with open(json_path, 'r') as file:
        return json.load(file)   
def load_pid():
    """
    Load tracked process IDs from Info/processpid.json.

    Returns:
        dict: PID tracking data used for restart handling.
    """
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Info", "processpid.json")
    with open(json_path, 'r') as file:
        return json.load(file)
def update_pid(data):
    """
    Save tracked process IDs to Info/processpid.json.

    Args:
        data (dict): PID tracking dictionary to write.
    """
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Info", "processpid.json")
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)

if os.path.exists(WE_Json):
    if os.path.exists(WE_Json):
        data = load_json_data()
        for variable in data:
            value = data.get(variable)
            try:
                if variable == "Unit_Positions" or variable == "Unit_Placements_Left":
                    if type(value[0]) is dict:
                        setattr(Settings, variable, value[0])
                else:
                    setattr(Settings, variable, value)
            except Exception as e:
                print(e)
else:
    print("Failed to find settings file. Closing in 10 seconds")
    time.sleep(10)
    sys.exit(0)

Ainz_Spell_Locations =  [ (336,331), (240, 413), (427, 333), (230, 246), (245, 344), (430, 316), (225, 247), (354, 289), (429, 324), (562, 426),(408,366)]
Ainz_Caloric = [(336, 384),(359, 449), (221, 231), (216, 286), (305, 337)]

AINZ_SPELLS = False

noti_region =  (190+offset[0], 348+offset[1], 619+offset[0], 552+offset[1])
hotbar_region = (191+offset[0], 518+offset[1], 633+offset[0], 627+offset[1])
monarch_region = (354+offset[0], 421+offset[1], 463+offset[0], 448+offset[1])


def check_camera():
    """
    Check whether the camera is currently in the expected angled position.

    Returns:
        bool: True if the expected camera orientation image is detected,
        False otherwise.

    Notes:
        Used as a safety check before pathing, since movement relies on
        consistent camera orientation.
    """
    return fd.does_exist("Winter\\Camera_Angled.png",confidence=0.7,grayscale=True,region=(int(rb_window.left),int(rb_window.top),rb_window.left+rb_window.width,rb_window.top+rb_window.height))

def check_location():
    """
    Check whether the player is currently at or near the lootbox / monarch area.

    Returns:
        bool: True if any known indicator for the target area is detected:
            - DetectArea
            - LootboxDetection
            - HasMonarch
    """
    return any([fd.does_exist("Winter\\DetectArea.png",confidence=0.8,grayscale=True,region=noti_region),fd.does_exist("Winter\\LootboxDetection.png",confidence=0.8,grayscale=True,region=noti_region),fd.does_exist("Winter\\HasMonarch.png",confidence=0.9,grayscale=True,region=monarch_region)])

def check_return():
    """
    Check whether the script should return to spawn from the lootbox interaction flow.

    Returns:
        bool: True if either a known return indicator is visible:
            - DetectArea
            - Full_Hotbar
    """
    return any([fd.does_exist("Winter\\DetectArea.png",confidence=0.8,grayscale=True,region=noti_region),fd.does_exist("Winter\\Full_Hotbar.png",confidence=0.8,grayscale=True,region=noti_region)])
Unit_Placements_Left =  {
            "Ainz": 1,
            "Beni": 3,
            "Rukia": 3,
            "Erza": 3,
            "Escanor": 1,
            "TrashGamer": 3,
            "Kuzan": 4,
            }

Units_Placeable = {
        "Ainz",
        "Beni",
        "Rukia",
        "Erza",
        "Escanor",
        "TrashGamer",
        "Kuzan",
        "Doom"
        }


def qrts():
    """
    Quick return to spawn.

    Performs the fixed click sequence used to return the player to spawn.
    Intended as a recovery / reset utility before re-pathing.
    """
    locations = [(29, 607), (699, 322), (756, 148)]
    for loc in locations:
        fd.click(loc[0]+offset[0], loc[1]+offset[1], delay=0.1)
        time.sleep(0.1)
    
    
def path_winter(area: int, sub_area: int):
    """
    Path the player from spawn to a specific Winter event area.

    Args:
        area (int): Main destination area.
            1 = Farm Area
            2 = Unit Area 1 (Mirko Area)
            3 = Lootbox
            4 = Upgrader
            5 = Monarch upgrader

        sub_area (int): Optional sub-destination within the area.
            For current usage:
            - area 1, sub_area 1 = Speedwagon exact position
            - area 2, sub_area 1 = Mirko exact position
            - otherwise often 0 when no sub-area is needed

    Behavior:
        - Dismisses alert popups if present
        - Verifies camera orientation and resets if needed
        - Uses hardcoded movement/click paths depending on area
        - Repeats and recovers automatically for lootbox pathing

    Notes:
        This function assumes the camera is configured exactly for the event.
    """
    time.sleep(1.5)
    if fd.does_exist('Alert.png',confidence=0.8,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.height+rb_window.top)):
        fd.click(406+offset[0], 358+offset[1],delay=0.2) # ERZAfd.click
        time.sleep(0.2)
        fd.click(696+offset[0],165+offset[1],delay=0.2)
        time.sleep(0.3)
    if not check_camera():
        while not check_camera():
            pydirectinput.press("v")
            qrts()
            time.sleep(3)
    match area:
        case 1: # speed wagon area
            pydirectinput.press("v")
            time.sleep(2)
            CTM = [(351+offset[0], 192+offset[1]), (405+offset[0], 50+offset[1])]
            fd.click(CTM[0][0],CTM[0][1],right_click=True,delay=0.2)
            time.sleep(1)
            fd.click(CTM[1][0],CTM[1][1],right_click=True,delay=0.2)
            time.sleep(1.5)
            match sub_area:
                case 1:
                    fd.click(241+offset[0], 395+offset[1],right_click=True)
                    time.sleep(1)
            pydirectinput.press('v')
            print('Pathed')
        case 2: # mirko area
            pydirectinput.press("v")
            time.sleep(2)
            CTM = [(351+offset[0], 192+offset[1]), (405+offset[0], 50+offset[1]), (25+offset[0],262+offset[1])]
            fd.click(CTM[0][0],CTM[0][1],right_click=True,delay=0.2)
            time.sleep(1)
            fd.click(CTM[1][0],CTM[1][1],right_click=True,delay=0.2)
            time.sleep(1.5)
            fd.click(CTM[2][0],CTM[2][1],right_click=True,delay=0.2)
            time.sleep(1.5)
            match sub_area:
                case 1:
                    fd.click(291+offset[0], 227+offset[1],right_click=True)
                    time.sleep(1)
            pydirectinput.press('v')
            print('Pathed')
        case 3: #lootbox
            at_loot_box = False
            while not at_loot_box:
                pydirectinput.press("v")
                time.sleep(2)
                pydirectinput.keyDown('a')
                time.sleep(1.2)
                pydirectinput.keyUp('a')
                pydirectinput.keyDown('s')
                time.sleep(1.9)
                pydirectinput.keyUp('s')
                pydirectinput.press('v')
                pydirectinput.press('e')
                time.sleep(0.5)
                check_time = 2
                while check_time > 0:
                    if check_location():
                        at_loot_box = True
                        break
                    check_time-=0.2
                    time.sleep(0.2)
                if not at_loot_box:
                    qrts()
                    time.sleep(1.5)
                    if not check_camera():
                        while not check_camera():
                            pydirectinput.press("v")
                            qrts()
                            time.sleep(3)
        case 4: #upgrader
            pydirectinput.press('v')
            time.sleep(2)
            pydirectinput.keyDown('a')
            time.sleep(Settings.AREA_4_DELAYS[0])
            pydirectinput.keyUp('a')
    
            pydirectinput.keyDown('s')
            time.sleep(Settings.AREA_4_DELAYS[1])
            pydirectinput.keyUp('s')
            pydirectinput.press('v')
            time.sleep(2)
        case 5: #monarch
            pydirectinput.press('v')
            time.sleep(2)
            pydirectinput.keyDown('a')
            time.sleep(Settings.AREA_5_DELAYS[0])
            pydirectinput.keyUp('a')

            pydirectinput.keyDown('w')
            time.sleep(Settings.AREA_5_DELAYS[1])
            pydirectinput.keyUp('w')
            pydirectinput.press('v')
            time.sleep(2)
def upgrader(upgrade: str):
    Mouse = Controller()
    """
    Buy a Winter event permanent upgrade from the upgrader NPC/UI.

    Args:
        upgrade (str): Upgrade name to purchase. Supported values:
            - "fortune"
            - "range"
            - "damage"
            - "speed"
            - "armor"

    Behavior:
        - Opens the upgrader UI
        - Recovers and re-paths if the UI fails to open
        - Selects the upgrade either via:
            - direct mouse UI interaction, or
            - keyboard/UI navigation mode (Settings.USE_UI_NAV)
        - Waits until the purchase appears successful before closing

    Notes:
        Relies on exact UI coordinates and pixel color checks.
    """
    e_delay = 0.2
    timeout = 3/e_delay
    pydirectinput.press('e')
    while not pyautogui.pixel(675+offset[0], 189+offset[1]) == (255,255,255):
        if timeout < 0:
            qrts()
            path_winter(4,0)
            timeout = 3/e_delay
        timeout-=1
        pydirectinput.press('e')
        time.sleep(e_delay)
    fd.click(307+offset[0], 230+offset[1], delay=0.2)
    time.sleep(0.5)
    if not Settings.USE_UI_NAV:
        if upgrade == 'fortune':
            fd.click(564+offset[0], 307+offset[1], delay=0.2)
            time.sleep(0.5)
            while not pyautogui.pixelMatchesColor(564+offset[0], 307+offset[1],expectedRGBColor=(24, 24, 24),tolerance=40):
                while not load_state()["running"]:
                    time.sleep(0.5)
                fd.click(564+offset[0], 307+offset[1], delay=0.2)
                time.sleep(0.8)
            fd.click(675+offset[0],189+offset[1],delay=0.2)
        if upgrade == 'range':
            fd.click(563+offset[0], 420+offset[1], delay=0.2)
            time.sleep(0.5)
            while not pyautogui.pixelMatchesColor(563+offset[0], 420+offset[1],expectedRGBColor=(24, 24, 24),tolerance=40):
                while not load_state()["running"]:
                    time.sleep(0.5)
                fd.click(563+offset[0], 420+offset[1], delay=0.2)
                time.sleep(0.8)
            fd.click(675+offset[0],189+offset[1],delay=0.2)
        if upgrade == "damage":
            fd.click(393+offset[0], 277+offset[1], delay=0.1)#556, 425
            pos = (556+offset[0], 425+offset[1])
            Mouse.scroll(0,-1)
            time.sleep(0.2)
            fd.click(pos[0], pos[1], delay=0.2)
            time.sleep(0.5)
            while not pyautogui.pixelMatchesColor(pos[0], pos[1],expectedRGBColor=(24, 24, 24),tolerance=40):
                while not load_state()["running"]:
                    time.sleep(0.5)
                fd.click(pos[0], pos[1], delay=0.2)
                time.sleep(1)
            Mouse.scroll(0,10)
            fd.click(675+offset[0],189+offset[1],delay=0.2)
        if upgrade == "speed":
            fd.click(393+offset[0], 277+offset[1], delay=0.1)#(561, 252)n
            pos = (561+offset[0], 252+offset[1])
            Mouse.scroll(0,-4)
            time.sleep(0.2)
            fd.click(pos[0], pos[1], delay=0.2)
            time.sleep(0.5)
            while not pyautogui.pixelMatchesColor(pos[0], pos[1],expectedRGBColor=(24, 24, 24),tolerance=40):  
                while not load_state()["running"]:
                    time.sleep(0.5)
                fd.click(pos[0], pos[1], delay=0.2)
                time.sleep(0.8)
            Mouse.scroll(0,10)
            fd.click(675+offset[0],189+offset[1],delay=0.2)
        if upgrade == "armor":
            fd.click(393+offset[0], 277+offset[1], delay=0.1)
            pos = (561+offset[0], 357+offset[1])
            Mouse.scroll(0,-4)
            time.sleep(0.2)
            fd.click(pos[0], pos[1], delay=0.2)
            time.sleep(0.5)
            while not  pyautogui.pixelMatchesColor(pos[0], pos[1],expectedRGBColor=(24, 24, 24),tolerance=40):
                while not load_state()["running"]:
                    time.sleep(0.5)
                fd.click(pos[0], pos[1], delay=0.2)
                time.sleep(0.8)
            Mouse.scroll(0,10)
            fd.click(675+offset[0],189+offset[1],delay=0.2)
    else:
        if upgrade == 'fortune':
            pos = (562+offset[0], 260+offset[1])
            print("hi")
            fd.click(393+offset[0], 277+offset[1], delay=0.1)
            ctypes.windll.user32.mouse_event(0x0800, 0, 0, -1000, 0)
            time.sleep(0.2)
            pydirectinput.press('\\')
            pydirectinput.press('\\')
            while not pyautogui.pixelMatchesColor(pos[0], pos[1],expectedRGBColor=(24, 24, 24),tolerance=40):
                while not load_state()["running"]:
                    time.sleep(0.5)
                fd.click(pos[0], pos[1], delay=0.2)
                time.sleep(0.8)
            ctypes.windll.user32.mouse_event(0x0800, 0, 0, 1000, 0)
            fd.click(675+offset[0],189+offset[1],delay=0.2)
        if upgrade == 'range':
            pos = (559+offset[0], 373+offset[1])
            print("hi")
            fd.click(393+offset[0], 277+offset[1], delay=0.1)
            ctypes.windll.user32.mouse_event(0x0800, 0, 0, -1000, 0)
            time.sleep(0.2)
            pydirectinput.press('\\')
            pydirectinput.press('\\')
            while not pyautogui.pixelMatchesColor(pos[0], pos[1],expectedRGBColor=(24, 24, 24),tolerance=40):
                while not load_state()["running"]:
                    time.sleep(0.5)
                fd.click(pos[0], pos[1], delay=0.2)
                time.sleep(0.8)
            ctypes.windll.user32.mouse_event(0x0800, 0, 0, 1000, 0)
            fd.click(675+offset[0],189+offset[1],delay=0.2)
        if upgrade == "damage":
            pos = (560+offset[0], 262+offset[1])
            print("hi")
            fd.click(393+offset[0], 277+offset[1], delay=0.1)
            ctypes.windll.user32.mouse_event(0x0800, 0, 0, -1000, 0)
            time.sleep(0.2)
            pydirectinput.press('\\')
            pydirectinput.press('down')
            pydirectinput.press('down')
            pydirectinput.press('down')
            pydirectinput.press('down')
            pydirectinput.press('\\')
            while not pyautogui.pixelMatchesColor(pos[0], pos[1],expectedRGBColor=(24, 24, 24),tolerance=40):
                while not load_state()["running"]:
                    time.sleep(0.5)
                fd.click(pos[0], pos[1], delay=0.2)
                time.sleep(0.8)
            ctypes.windll.user32.mouse_event(0x0800, 0, 0, 1000, 0)
            fd.click(675+offset[0],189+offset[1],delay=0.2)
        if upgrade == "speed":
            pos = (559+offset[0], 375+offset[1])
            print("hi")
            fd.click(393+offset[0], 277+offset[1], delay=0.1)
            ctypes.windll.user32.mouse_event(0x0800, 0, 0, -1000, 0)
            time.sleep(0.2)
            pydirectinput.press('\\')
            pydirectinput.press('down')
            pydirectinput.press('down')
            pydirectinput.press('down')
            pydirectinput.press('down')
            pydirectinput.press('\\')
            while not pyautogui.pixelMatchesColor(pos[0], pos[1],expectedRGBColor=(24, 24, 24),tolerance=40):
                while not load_state()["running"]:
                    time.sleep(0.5)
                fd.click(pos[0], pos[1], delay=0.2)
                time.sleep(0.8)
            ctypes.windll.user32.mouse_event(0x0800, 0, 0, 1000, 0)
            fd.click(675+offset[0],189+offset[1],delay=0.2)
        if upgrade == "armor":
            pos = (560+offset[0], 377+offset[1])
            print("hi")
            fd.click(393+offset[0], 277+offset[1], delay=0.1)
            ctypes.windll.user32.mouse_event(0x0800, 0, 0, -1000, 0)
            time.sleep(0.2)
            pydirectinput.press('\\')
            pydirectinput.press('down')
            pydirectinput.press('down')
            pydirectinput.press('down')
            pydirectinput.press('down')
            pydirectinput.press('down')
            pydirectinput.press('\\')
            while not pyautogui.pixelMatchesColor(pos[0], pos[1],expectedRGBColor=(24, 24, 24),tolerance=40):
                while not load_state()["running"]:
                    time.sleep(0.5)
                fd.click(pos[0], pos[1], delay=0.2)
                time.sleep(0.8)
            ctypes.windll.user32.mouse_event(0x0800, 0, 0, 1000, 0)
            fd.click(675+offset[0],189+offset[1],delay=0.2)
    
    
    print(f"Purchased {upgrade}")
def secure_select(pos: tuple[int, int]):
    """
    Reliably select a placed unit at a given map position.

    Args:
        pos (tuple[int, int]): Unit position in local map coordinates
            (before Roblox window offset is applied).

    Behavior:
        - Opens the unit panel area
        - Clicks the target position repeatedly until the unit UI opens
        - Handles pause state while waiting
        - Dismisses alert popups if needed
        - Times out after repeated failed attempts

    Notes:
        Useful when normal clicking is unreliable due to UI overlap or lag.
    """
    fd.click(307+offset[0], 230+offset[1], delay=0.2)
    time.sleep(0.5)
    pos = (pos[0]+offset[0],pos[1]+offset[1])
    fd.click(pos[0],pos[1],delay=0.2)
    time.sleep(0.5)
    time_out = 20
    while not pyautogui.pixel(305+offset[0], 233+offset[1]) == (255,255,255):
        while not load_state()["running"]:
            time.sleep(0.5)
        if fd.does_exist("Unit_Open.png", confidence=0.8, grayscale=True, region=(100+offset[0],400+offset[1], 153, 416)):
            break
        if fd.does_exist('Alert.png',confidence=0.8,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.height+rb_window.top)):
            fd.click(406+offset[0], 358+offset[1],delay=0.2) # ERZAfd.click
            time.sleep(0.6)
        fd.click(pos[0],pos[1],delay=0.2)
        time.sleep(1.2)
        if time_out<0:
            print("timeout failure")
            break
        time_out-=1

    print(f"Selected unit at {pos}")


def place_unit(unit: str, pos: tuple[int, int], close: bool | None = None, auto_upg: bool | None = None):
    """
    Place a unit from the hotbar at a specific map position.

    Args:
        unit (str): Unit name to place. Common supported values include:
            - "Ainz"
            - "Beni"
            - "Rukia"
            - "Erza"
            - "Escanor"
            - "TrashGamer"
            - "Kuzan"
            - "Mirko"
            - "Speedwagon"
            - "Takaroda"
            - "Caloric_Unit"
            - "Nami"
            - "Doom"

        pos (tuple[int, int]): Placement position in local map coordinates

        close (bool | None): If True, close the unit UI after placement.

        auto_upg (bool | None): If True, press Z after placement
            (used for auto-upgrade / toggle behavior).

    Behavior:
        - Waits for the unit to appear in the hotbar
        - Clicks the hotbar icon
        - Attempts placement
        - Retries if the unit UI does not open after placement
        - Optionally toggles auto-upgrade and/or closes the unit UI
    """
    region = hotbar_region
    time_out = 20
    time_out_2 = 50
    noti_region
    #fd.click on the unit

    while not fd.does_exist(f"Winter\\{unit}.png", confidence=0.8, grayscale=False,region=region):
        while not load_state()["running"]:
            time.sleep(0.5)
        if time_out_2 <= 0:
            break
        time_out_2-=1
        time.sleep(0.3)
    fd.click_image(f'Winter\\{unit}.png', confidence=0.8,grayscale=False,offset=(0,0),region=region)   
    time.sleep(0.2)
    fd.click(pos[0]+offset[0], pos[1]+offset[1], delay=0.67)
    time.sleep(0.5)
    while not pyautogui.pixel(305+offset[0], 233+offset[1]) == (255,255,255):
        while not load_state()["running"]:
            time.sleep(0.5)
        time_out-=1
        if time_out<=0:
            print("timed out")
            break
        fd.click(pos[0]+offset[0], pos[1]+offset[1], delay=0.67)
        print(f"Target Color: (255,255,255), got: {pyautogui.pixel(305+offset[0], 233+offset[1])}")
        time.sleep(0.1)
        pydirectinput.press('q')
        time.sleep(0.5)
        fd.click(pos[0]+offset[0], pos[1]+offset[1], delay=0.1)
        time.sleep(1)
        if fd.does_exist("Unit_Open.png",confidence=0.9,grayscale=True,region=(15+offset[0], 430+offset[1], 310+offset[0], 476+offset[1])):
            break
        if pyautogui.pixel(305+offset[0], 233+offset[1]) == (255,255,255):
            break
        if True: # if u want it to re-click
            print("Retrying placement...")
            try:
                #fd.click on the unit
                fd.click_image(f'Winter\\{unit}.png', confidence=0.8,grayscale=False,offset=(0,0),region=region)
                time.sleep(0.2)
            except Exception as e:
                print(F"Error {e}")
        time.sleep(0.2)
    if auto_upg:
        pydirectinput.press("z")
    if close:
        fd.click(305+offset[0], 233+offset[1])
    print(f"Placed {unit} at {pos}")
        
def buy_monarch():
    """
    Purchase/apply Monarch at the monarch station.

    Behavior:
        - Presses E until the monarch area is detected
        - Re-paths if interaction times out
        - Continues pressing E until the 'HasMonarch' indicator is detected

    Notes:
        Intended to be used after path_winter(5, 0).
    """
    e_delay = 0.4
    timeout = 3/e_delay
    pydirectinput.press('e')
    while not check_location():
        if timeout < 0:
            qrts()
            path_winter(5,0)
            timeout = 3/e_delay
        timeout-=1
        pydirectinput.press('e')
        time.sleep(e_delay)
    print("Found area")
    while not fd.does_exist('Winter\\HasMonarch.png',confidence=0.7,grayscale=True,region=monarch_region):
        while not load_state()["running"]:
            time.sleep(0.5)
        pydirectinput.press('e')
        time.sleep(0.8)
    print("got monarch")

def place_hotbar_units():
    """
    Automatically scan the hotbar and place all recognized placeable units.

    Behavior:
        - Repeatedly scans the hotbar for any unit in Units_Placeable
        - Uses Settings.Unit_Positions for placement targets
        - Tracks remaining placements via Unit_Placements_Left
        - Handles special logic for the Doom unit:
            - places Doom
            - sets boss targeting
            - applies monarch
            - re-selects Doom afterward

    Notes:
        Stops once no more recognized units remain placeable in the hotbar.
    """
    # Scans and places all units in your hotbar, tracking them too
    try:
        if not check_camera():
            while not check_camera():
                pydirectinput.press("v")
                qrts()
                time.sleep(3)
        placing = True
        while placing:
            is_unit = False
            for unit in Units_Placeable:
                keyboard.press_and_release('e')
                while not load_state()["running"]:
                    time.sleep(0.5)
                if fd.does_exist(f"Winter\\{unit}.png", confidence=0.75, grayscale=False,region=hotbar_region):
                    if unit != "Doom":
                        is_unit = True
                        unit_pos = Settings.Unit_Positions.get(unit)
                        index = Unit_Placements_Left.get(unit)-1
                        if index <0:
                            is_unit = False
                        print(f"Placing unit {unit} {index+1} at {unit_pos}")
                        place_unit(unit, unit_pos[index])
                        
                    else:#(347, 390)
                        doom = (487, 446)
                        place_unit(unit,doom)
                        time.sleep(2)
                        set_boss()
                        pydirectinput.press('z')
                        fd.click(305+offset[0], 233+offset[1], delay=0.2)
                        path_winter(5,0)
                        buy_monarch()
                        qrts()
                        secure_select(doom)
                    if unit != "Doom":
                        Unit_Placements_Left[unit]-=1
                        print(f"Placed {unit} | {unit} has {Unit_Placements_Left.get(unit)} placements left.")
                    else:
                        print("Placed doom slayer.")
            if not is_unit:
                placing = False
    except Exception as error:
        print(f"Error occured during placing hotbar units, Error: {error}")
            
def ainz_setup(unit: str):
    """
    Configure Ainz's spell/ability loadout and set the Caloric Stone summon target.

    Args:
        unit (str): Text to type into the Ainz unit selection field.
            Common examples:
            - "world des"
            - "god"
            - custom value from Settings.USE_AINZ_UNIT

    Behavior:
        - If Ainz spells have not been configured yet, clicks all spell slots
        - Selects Ainz until the World Item UI is detected
        - Clicks through the Caloric Stone setup UI
        - Types the provided target unit name at the appropriate prompt

    Notes:
        Controlled by the global AINZ_SPELLS flag so the spell setup only happens once.
    """
    print("doing ainz set up")
    if not AINZ_SPELLS:
        for i in Ainz_Spell_Locations:
            print(i)
            fd.click(i[0]+offset[0],i[1]+offset[1],delay=0.2)
            time.sleep(0.2)
        time.sleep(1)
    while not fd.does_exist('Winter\\WorldItem.png',confidence=0.8,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.height+rb_window.top)):
        fd.click(Settings.Unit_Positions.get("Ainz")[0][0]+offset[0],Settings.Unit_Positions.get("Ainz")[0][1]+offset[1])
        time.sleep(1)
    for i in Ainz_Caloric:
        fd.click(i[0]+offset[0],i[1]+offset[1],delay=0.2)
        if i == (221, 231):
            keyboard.write(unit)
            time.sleep(0.5)
        time.sleep(0.2)


def repair_barricades():
    """
    Move through the barricade repair route and spam repairs.

    Behavior:
        - Toggles camera
        - Moves through the barricade path
        - Presses E repeatedly at several repair points
        - Returns camera to normal afterward

    Notes:
        Used during endgame maintenance loops.
    """
    #DIR_BARRICADE
    pydirectinput.press('v')
    time.sleep(1)
    pydirectinput.keyDown('a')
    time.sleep(0.7)
    pydirectinput.keyUp('a')
    
    keyboard.press_and_release("e")
    keyboard.press_and_release("e")
    keyboard.press_and_release("e")
    
    pydirectinput.keyDown('w')
    time.sleep(0.2)
    pydirectinput.keyUp('w')
    
    keyboard.press_and_release("e")
    keyboard.press_and_release("e")
    
    pydirectinput.keyDown('s')
    time.sleep(0.4)
    pydirectinput.keyUp('s')
    
    keyboard.press_and_release("e")
    keyboard.press_and_release("e")
    time.sleep(1)
    pydirectinput.press('v')
    time.sleep(2)
    
def set_boss():
    """
    Cycle unit targeting priority until it reaches Boss priority.

    Behavior:
        Presses R five times to rotate targeting modes.

    Notes:
        Assumes unit is open
    """
    keyboard.press_and_release("r")
    keyboard.press_and_release("r")
    keyboard.press_and_release("r")
    keyboard.press_and_release("r")
    keyboard.press_and_release("r")
    
def detect_loss():
    """
    Background loss detector that auto-restarts the script process.

    Behavior:
        - Waits 60 seconds before beginning checks
        - Monitors for the 'Failed' screen
        - On failure:
            - increments num_runs and losses in state.json
            - relaunches the current script as a new process
            - updates tracked PID data
            - force-exits the current process

    Notes:
        Intended to run in a daemon thread for continuous monitoring.
    """
    time.sleep(60)
    while True:
        if fd.does_exist("Failed.png",confidence=0.8,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
            add_data =  load_state()
            add_data["num_runs"]+=1
            add_data["losses"]+=1
            update_state(add_data) #restart, cant capture text tho

            p = subprocess.Popen([sys.executable, *sys.argv])
            pids = load_pid()
            pids["pid"] = []
            pids["pid"]+=[p.pid]
            update_pid(pids)
            os._exit(0)
        time.sleep(3)

def press_key(key: str, delay):
    """
    Hold a key for a specified duration.

    Args:
        key (str): Key name to hold.
        delay (float): Duration in seconds to hold the key.
    """
    pydirectinput.keyDown(key=key)
    time.sleep(delay)
    pydirectinput.keyUp(key=key)

def buy_mirko(amount: int):
    """
    Buy Mirko copies until at least one Mirko is detected in the hotbar.

    Args:
        amount (int): Number of E presses to send during each purchase attempt.

    Behavior:
        - Returns to spawn
        - Paths to Mirko
        - Attempts purchase
        - Verifies success via hotbar image detection
        - Retries until Mirko is detected
    """
    qrts()
    has_mirko_0 = False
    while not has_mirko_0:
        path_winter(2,1)
        pydirectinput.press('e',_pause = False,presses=amount)
        qrts()
        time.sleep(1.5)
        if fd.does_exist("Winter\\Mirko.png",confidence=0.7,grayscale=False, region=hotbar_region):
            print("Got mirko")
            has_mirko_0 = True
        else:
            print("Didnt detect mirko, retrying purchase")
    qrts()
def get_monarch():
    """
    Full helper to acquire Monarch from spawn.

    Behavior:
        - Returns to spawn
        - Paths to the monarch station
        - Purchases monarch
        - Returns to spawn
    """
    qrts()
    path_winter(5,0)
    buy_monarch()
    qrts()

def buy_speedwagon():
    """
    Path to Speedwagon and attempt to buy 3 copies.

    Notes:
        Assumes the player is at/near spawn and that the Speedwagon path is valid.
    """
    path_winter(1,1)
    pydirectinput.press("e",presses=3,_pause=False)

def buy_takaroda():
    """
    Repeatedly interact until Takaroda is detected in the hotbar.

    Behavior:
        - Presses E until the Takaroda unit icon appears in the hotbar.

    Notes:
        Assumes the player is pathed to Takaroda
    """
    while not fd.does_exist("Winter\\Takaroda.png",confidence=0.8,grayscale=False, region=hotbar_region):
            while not load_state()["running"]:
                time.sleep(0.5)
            pydirectinput.press("e")
            time.sleep(0.5)

def path_takaroda():
    """
    Move from the Speedwagon area toward Takaroda using click-to-move.

    Notes:
        Intended to be called after buying/placing Speedwagon.
    """
    fd.click(414+offset[0], 207+offset[1],right_click=True)

def path_nami():
    """
    Move from the Takaroda area toward Nami using click-to-move.

    Notes:
        Intended to be called after path_takaroda().
    """
    fd.click(142+offset[0], 137+offset[1],right_click=True)

def buy_nami():
    """
    Repeatedly interact until Nami is detected in the hotbar.

    Behavior:
        - Presses E until the Nami unit icon appears in the hotbar.
    
    Notes:
        Assumes player is pathed to Nami
    """
    while not fd.does_exist("Winter\\Nami.png",confidence=0.8,grayscale=False, region=hotbar_region):
        while not load_state()["running"]:
            time.sleep(0.5)
        pydirectinput.press("e")
        time.sleep(0.5)
def buy_upgrade(upgrade: str, path: bool, return_to_spawn: bool):
    """
    Convenience wrapper for purchasing a Winter upgrade.

    Args:
        upgrade (str): Upgrade name to buy.
            Valid values: "fortune", "damage", "range", "speed", "armor"

        path (bool): If True, path to the upgrader before purchasing.

        return_to_spawn (bool): If True, return to spawn after purchase.

    Notes:
        Internally routes to upgrader() after optional pathing.
    """
    if path:
        path_winter(4,0)
    match upgrade:
        case "fortune": 
            upgrader("fortune")
        case "damage":
            upgrader("damage")
        case "range":
            upgrader("range")
        case "speed":
            upgrader("speed")
        case "armor":
            upgrader("armor")
    if return_to_spawn:
        qrts()

Mirko_Placements = Settings.Unit_Positions.get("Mirko")
Speed_Placements = Settings.Unit_Positions.get("Speedwagon")
Tak_Placements = Settings.Unit_Positions.get("Takaroda")    
Erza_Placements = Settings.Unit_Positions['Erza']
Nami_Placement = (397, 437)  

def close_unit():
    """
    Close the currently open unit UI panel by clicking its close area.
    """
    fd.click(305+offset[0], 233+offset[1])

def buy_lanes():
    """
    Buy the main lanes using configured movement timings.

    Behavior:
        - Moves to lane purchase points using Settings.BUY_MAIN_LANE_DELAYS
        - Interacts at each point by pressing E multiple times
    """
    press_key("d",Settings.BUY_MAIN_LANE_DELAYS[0])
    keyboard.press_and_release('e')
    keyboard.press_and_release('e')
    press_key("w",Settings.BUY_MAIN_LANE_DELAYS[1])
    keyboard.press_and_release('e')
    keyboard.press_and_release('e')
def lootbox(ainz: bool, erza: bool, beni: bool, erza_buff: bool):
    """
    Run the lootbox placement and late-game setup loop.

    Args:
        ainz (bool): If True, fully set up Ainz when his placements are complete.
            Includes:
            - selecting Ainz
            - configuring spells
            - placing/upgrading Caloric unit
            - applying monarch where configured

        erza (bool): If True, fully upgrade + monarch Erza when all Erza placements are done.

        beni (bool): If True, fully upgrade + monarch Beni when all Beni placements are done.

        erza_buff (bool): If True, use the special Erza buffer placement and trigger its ability once.

    Behavior:
        - Repeatedly interacts with the lootbox
        - Detects when the player should return to spawn and place units
        - Places all hotbar units found
        - Handles Ainz special setup
        - Handles Erza buffer logic
        - Handles Erza/Beni upgrade+monarch logic
        - Ends once all tracked unit placements are exhausted

    Notes:
        This is the main midgame automation loop for converting lootbox pulls
        into placed and upgraded units.
    """
    ainz_placed = not ainz
    Erza_Upgraded = not erza
    Ben_Upgraded = not beni

    Erza_Placements = Settings.Unit_Positions['Erza']
    gamble_done = False
    while not gamble_done:
        keyboard.press_and_release('e')
        while not load_state()["running"]:
            time.sleep(0.5)
        if check_return():
                print("return")
                qrts()
                time.sleep(1)
                keyboard.press_and_release('e')
                time.sleep(2)
                place_hotbar_units()
                path_winter(3,0)
        if not ainz_placed:
                if Unit_Placements_Left["Ainz"] == 0:
                    qrts()
                    fd.click(307+offset[0], 230+offset[1], delay=0.2)
                    time.sleep(2)
                    Ainz_Placements = Settings.Unit_Positions['Ainz']
                    
                    secure_select(Ainz_Placements[0])
                    pydirectinput.press('z')
                    
                    if Settings.USE_WD == True:  # noqa: E712
                            ainz_setup(unit="world des")
                    elif Settings.USE_DIO == True:  # noqa: E712
                            ainz_setup(unit="god")
                    else:
                        ainz_setup(unit=Settings.USE_AINZ_UNIT)
                    global AINZ_SPELLS
                    if not AINZ_SPELLS:
                        AINZ_SPELLS = True
                    time.sleep(8)
                    if Settings.MAX_UPG_AINZ_PLACEMENT == True:  # noqa: E712
                        fd.place_unit(0,pos=Settings.Unit_Positions['Caloric_Unit'],offset=offset,no_cancel=True,upg="a")
                    else:
                        fd.place_unit(0,pos=Settings.Unit_Positions['Caloric_Unit'],offset=offset,no_cancel=True)
                    
                    if Settings.MONARCH_AINZ_PLACEMENT ==True:# noqa: E712
                        path_winter(5,0)
                        buy_monarch()
                        qrts()
                        secure_select(Settings.Unit_Positions['Caloric_Unit'])
                    fd.click(307+offset[0], 230+offset[1], delay=0.2)
                    path_winter(5,0)
                    buy_monarch()
                    qrts()
                    secure_select(Ainz_Placements[0])
                    close_unit()
                    ainz_placed = True
                    if Settings.USE_WD == True:
                        upgrade_caloric("10")
                        close_unit()
                    path_winter(3,0)
        if erza_buff:
            if Unit_Placements_Left["Erza"] < 3:
                qrts()
                close_unit()
                time.sleep(1)
                fd.upgrade_unit("5",pos=Erza_Placements[2],offset=offset)
                fd.use_ability(Erza_Placements[2],"MAGE_3",offset=offset)
                erza_buff = False

        if not Erza_Upgraded:
                if Unit_Placements_Left["Erza"] == 0:
                    
                    qrts()
                    fd.click(307+offset[0], 230+offset[1], delay=0.2)
                    time.sleep(1)
                
                    secure_select(Erza_Placements[1])
                    set_boss()
                    fd.upgrade_unit("AUTO",pos=Erza_Placements[1],offset=offset)
                    fd.use_ability(Erza_Placements[1],"MAGE_2",offset=offset)
                    
                    secure_select(Erza_Placements[0])
                    set_boss()
                    fd.upgrade_unit("AUTO",pos=Erza_Placements[0],offset=offset)
                    fd.use_ability(Erza_Placements[0],"MAGE_2",offset=offset)
                    
                    path_winter(5,0)
                    buy_monarch()
                    qrts()
                    secure_select(Erza_Placements[1])
                    
                    path_winter(5,0)
                    buy_monarch()
                    qrts()
                    secure_select(Erza_Placements[0])
                    fd.click(307+offset[0], 230+offset[1], delay=0.2)
                    Erza_Upgraded = True
                    path_winter(3,0)
        if not Ben_Upgraded:
                if Unit_Placements_Left["Beni"] == 0:
                    Beni_Placements = Settings.Unit_Positions['Beni']
                    qrts()
                    for i in range(3):
                        secure_select(Beni_Placements[i])
                        set_boss()
                        keyboard.press_and_release('z')
                        fd.click(307+offset[0], 230+offset[1], delay=0.2)
                        path_winter(5,0)
                        buy_monarch()
                        qrts()
                        secure_select(Beni_Placements[i])
                        fd.click(307+offset[0], 230+offset[1], delay=0.2)
                    Ben_Upgraded = True
                    path_winter(3,0)
        print("===============================")
        is_done = True
        for unit in Units_Placeable:
                if unit != "Doom":
                    if Unit_Placements_Left[unit] > 0:
                        is_done = False
                        print(f"{unit} has {Unit_Placements_Left[unit]} placements left.")
        print("===============================")
        if is_done:
            gamble_done = True
            time.sleep(0.1)
    qrts()
    close_unit()
    time.sleep(1)
def upgrade_caloric(upgrade: str):
    """
    Upgrade the Caloric_Unit at its configured placement.

    Args:
        upgrade (str): Upgrade amount / mode passed directly to fd.upgrade_unit().
            Examples:
            - "10"
            - "max"
            - other values supported by fd.upgrade_unit()
    """
    fd.upgrade_unit(upgrade,Settings.Unit_Positions['Caloric_Unit'],offset=offset)
def upgrade_monarch_all(unit: str, upgrade: str):
    """
    Upgrade and monarch every placed copy of a given unit type.

    Args:
        unit (str): Unit type name. Common supported values:
            - "Ainz"
            - "Beni"
            - "Rukia"
            - "Erza"
            - "Escanor"
            - "TrashGamer"
            - "Kuzan"
            - "Mirko"

        upgrade (str): Upgrade mode/value passed to fd.upgrade_unit().
            Common values:
            - "13"
            - "max"
            - other fd-supported values

    Behavior:
        - Iterates through all configured placements for the unit
        - Skips Erza's 3rd placement (special-case buffer slot)
        - Selects the unit
        - Sets boss targeting
        - Applies upgrades
        - Travels to monarch station
        - Applies monarch
        - Returns and re-selects the unit

    Notes:
        If the player already has monarch equipped, the function first unequips it
        by pressing Q, then restores a clean state at the end.
    """
    if fd.does_exist("Winter\\HasMonarch.png",confidence=0.9,grayscale=True,region=monarch_region):
            pydirectinput.press('q')
    for placements in Settings.Unit_Positions[unit]: 
            if placements == Settings.Unit_Positions['Erza'][2]:
                continue
            while not load_state()["running"]:
                time.sleep(0.5)
            secure_select(placements)
            set_boss()
            close_unit()
            fd.upgrade_unit(upgrade,pos=placements,offset=offset)
            path_winter(5,0)
            buy_monarch()
            qrts()
            secure_select(placements)
            close_unit()
    if fd.does_exist("Winter\\HasMonarch.png",confidence=0.9,grayscale=True,region=monarch_region):
            pydirectinput.press('q')

def end_loop(wave: int):
    """
    Run the endgame loop until a target wave is reached.

    Args:
        wave (int): Target wave number to stop at.

    Behavior:
        - Monitors current wave using fd.get_wave()
        - At wave-1:
            - paths to final lane purchase route
            - starts a background E-spam thread
            - buys final lanes using Settings.BUY_FINAL_LANE_DELAYS
        - On even waves (and some late conditions), repairs barricades
        - Continues until the target wave is reached

    Notes:
        Includes camera validation, monarch cleanup, and recovery behavior.
    """
    wave_140 = False
    done_path = False
    while not wave_140:
            if fd.does_exist("Winter\\HasMonarch.png",confidence=0.9,grayscale=True,region=monarch_region):
                pydirectinput.press('q')
            while not load_state()["running"]:
                time.sleep(0.5)
            if not check_camera():
                while not check_camera():
                    pydirectinput.press("v")
                    qrts()
                    time.sleep(3)
            if fd.get_wave(offset)==wave-1 and not done_path:
                def spam_e():
                    while not done_path:
                        while not load_state()["running"]:
                            time.sleep(0.5)
                        keyboard.press_and_release('e')
                        time.sleep(0.2)
                    print("Done buying lanes")
                if not check_camera():
                    while not check_camera():
                        pydirectinput.press("v")
                        qrts()
                        time.sleep(3)
                time.sleep(1)
                pydirectinput.keyDown('a')
                time.sleep(0.4)
                pydirectinput.keyUp('a')
                time.sleep(3)
                pydirectinput.press("v")
                Thread(target=spam_e).start()
                time.sleep(2)
                pydirectinput.keyDown("w")
                time.sleep(Settings.BUY_FINAL_LANE_DELAYS[0])
                pydirectinput.keyUp("w")
                
                pydirectinput.keyDown("s")
                time.sleep(Settings.BUY_FINAL_LANE_DELAYS[1])
                pydirectinput.keyUp("s")
                pydirectinput.press("v")
                done_path=True
                qrts()
                time.sleep(2)
            if fd.get_wave(offset)==wave:
                wave_140 = True
            else:
                if fd.get_wave(offset)%2==0 or fd.get_wave(offset) == wave-1 and done_path:
                    repair_barricades()
                    qrts()
                    time.sleep(2)
Thread(target=detect_loss,daemon=True).start()
def main():
    print("Launched")
    First_match = False
    print("Starting Winter Event")
    if fd.does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
        if fd.does_exist('Alert.png',confidence=0.8,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.height+rb_window.top)):
            fd.click(406+offset[0], 358+offset[1],delay=0.2) # ERZAfd.click
            time.sleep(0.6)
        if fd.does_exist('RestartCon.png',confidence=0.8,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.height+rb_window.top)):
            fd.click(467+offset[0], 365+offset[1],delay=0.2) # ERZAfd.click
            time.sleep(0.6)
        while fd.does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
            fd.click(375+offset[0], 469+offset[1])
            time.sleep(1)
    while True:
        # Loop Setups
        print("Waiting for spawn")
        fd.wait_for_spawn(offset=offset,case=0)
        print("Found Spawn")
        if not First_match:
            print("Setting up camera")
            First_match = True
            press_key("i",2.0)
            ctypes.windll.user32.mouse_event(0x0001, 0, 100000, 0, 0)
            time.sleep(0.5)
            press_key("o",2.0)
        while not load_state()["running"]:
            time.sleep(0.5)
        Reset_Dict =  {
            "Ainz": 1,
            "Beni": 3,
            "Rukia": 3,
            "Erza": 3,
            "Escanor": 1,
            "TrashGamer": 3,
            "Kuzan": 4,
            }
        global Unit_Placements_Left
        Unit_Placements_Left = Reset_Dict.copy()
        # =========================
        # Function Index
        # =========================
        # Detection:
        # - check_camera()
        # - check_location()
        # - check_return()
        #
        # Helpers / Utility:
        # - secure_select(pos)
        # - close_unit()
        # - qrts()
        # - get_monarch()
        #
        # Movement / Pathing:
        # - path_winter(area, sub_area)
        # - path_takaroda()
        # - path_nami()
        #
        # Purchases / Upgrades:
        # - upgrader(upgrade)
        # - buy_upgrade(upgrade, path, return_to_spawn)
        # - buy_monarch()
        # - buy_mirko(amount)
        # - buy_speedwagon()
        # - buy_takaroda()
        # - buy_nami()
        #
        # Unit Interaction:
        # - place_unit(unit, pos, close=None, auto_upg=None)
        # - place_hotbar_units()
        # - set_boss()
        #
        # Special Logic:
        # - ainz_setup(unit)
        # - upgrade_caloric(upgrade)
        # - upgrade_monarch_all(unit, upgrade)
        # - lootbox(ainz, erza, beni, erza_buff)
        #
        # Endgame / Runtime:
        # - end_loop(wave)
        buy_mirko(2)
        place_unit("Mirko", Mirko_Placements[0],close=True)

        fd.start(offset)

        place_unit("Mirko", Mirko_Placements[1],close=True)
        buy_mirko(1)
        place_unit("Mirko", Mirko_Placements[2],close=True)

        buy_speedwagon()
        place_unit("Speedwagon",Speed_Placements[0],close=True,auto_upg=True)
        place_unit("Speedwagon",Speed_Placements[1],close=True,auto_upg=True)
        place_unit("Speedwagon",Speed_Placements[2],close=True,auto_upg=True)

        path_takaroda()
        buy_takaroda()
        place_unit("Takaroda",Tak_Placements[0],auto_upg=True,close=True)

        path_nami()
        buy_nami()
        place_unit("Nami",Nami_Placement,auto_upg=True,close=True)
        qrts()
        buy_upgrade("fortune",path=True,return_to_spawn=True)

        secure_select(Mirko_Placements[0])
        press_key("z",delay=0.1)
        close_unit()
        get_monarch()
        secure_select(Mirko_Placements[0])
        close_unit()

        buy_lanes()
        buy_upgrade("damage",path=True,return_to_spawn=False)
        buy_upgrade("speed",path=False,return_to_spawn=False)
        buy_upgrade("range",path=False,return_to_spawn=True)

        secure_select(Mirko_Placements[1])
        press_key("z",delay=0.1)
        close_unit()
        get_monarch()
        secure_select(Mirko_Placements[1])
        close_unit()

        secure_select(Mirko_Placements[2])
        press_key("z",delay=0.1)
        close_unit()
        get_monarch()
        secure_select(Mirko_Placements[2])
        close_unit()

        buy_upgrade("armor",path=True,return_to_spawn=True)

        path_winter(3,0)
        lootbox(ainz=True,erza=False,beni=False,erza_buff=True)

        upgrade_monarch_all(unit="Rukia",upgrade="13")

        upgrade_monarch_all(unit="Erza",upgrade="max")
        fd.use_ability(Erza_Placements[1],"MAGE_2",offset=offset)
        fd.use_ability(Erza_Placements[0],"MAGE_2",offset=offset)

        upgrade_monarch_all(unit="Beni",upgrade="max")
        upgrade_monarch_all(unit="TrashGamer",upgrade="max")
        upgrade_monarch_all(unit="Kuzan",upgrade="max")
        upgrade_monarch_all(unit="Escanor",upgrade="max")

        end_loop(wave=140)

        #send win 
        add_data = load_state()
        add_data["num_runs"]+=1
        add_data["wins"]+=1
        update_state(add_data)
        fd.restart_match(offset)
        time.sleep(1)

main()
