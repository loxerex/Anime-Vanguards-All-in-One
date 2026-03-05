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

# testing commit

class testclass: 
    pass

Settings = testclass()

def load_state():
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"Info", "state.json")
    with open(json_path, 'r') as file:
        return json.load(file)
    
def update_state(data):
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"Info", "state.json")
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)
def load_json_data():
    JSON_DATA = None
    if os.path.isfile(WE_Json):
        with open(WE_Json, 'r') as f:
            JSON_DATA = json.load(f)
    return JSON_DATA
def load_aio_settings():
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Settings", "AIO_Settings.json")
    with open(json_path, 'r') as file:
        return json.load(file)   
def load_pid():
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Info", "processpid.json")
    with open(json_path, 'r') as file:
        return json.load(file)
def update_pid(data):
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

Ainz_Spell_Locations =  [ (336,331), (240, 413), (427, 333), (430, 280), (230, 246), (245, 344), (430, 316), (225, 247), (354, 289), (429, 324), (562, 426),(408,366)]
Ainz_Caloric = [(336, 384),(359, 449), (221, 231), (216, 286), (305, 337)]

AINZ_SPELLS = False

noti_region =  (200+offset[0], 348+offset[1], 619+offset[0], 552+offset[1])
hotbar_region = (244+offset[0], 549+offset[1], 570+offset[0], 601+offset[1])
monarch_region = (354+offset[0], 421+offset[1], 463+offset[0], 448+offset[1])


def check_camera():
    return fd.does_exist("Winter\\Camera_Angled.png",confidence=0.8,grayscale=True,region=(int(rb_window.left),int(rb_window.top),rb_window.left+rb_window.width,rb_window.top+rb_window.height))

def check_location():
    return any([fd.does_exist("Winter\\DetectArea.png",confidence=0.8,grayscale=True,region=noti_region),fd.does_exist("Winter\\LootboxDetection.png",confidence=0.8,grayscale=True,region=noti_region),fd.does_exist("Winter\\HasMonarch.png",confidence=0.9,grayscale=True,region=monarch_region)])

def check_return():
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


def qrts(): # Returns to spawn
    locations = [(29, 607), (699, 322), (756, 148)]
    for loc in locations:
        fd.click(loc[0]+offset[0], loc[1]+offset[1], delay=0.1)
        time.sleep(0.1)
    
    
def path_winter(area: int, sub_area: int):
    '''
    1,1 = Speedwagon
    2,1 = Mirko
    3 = lootbox
    4 = upgrader
    5 = monarch
    '''
    time.sleep(1.5)
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
    '''
    Buys the upgrades for the winter event: fortune, range, damage, speed, armor
    '''
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
def secure_select(pos: tuple[int,int]):
    fd.click(307+offset[0], 230+offset[1], delay=0.2)
    time.sleep(0.5)
    pos = (pos[0]+offset[0],pos[1]+offset[1])
    fd.click(pos[0],pos[1],delay=0.2)
    time.sleep(0.5)
    time_out = 20
    while not pyautogui.pixel(305+offset[0], 233+offset[1]) == (255,255,255):
        while not load_state()["running"]:
            time.sleep(0.5)
        if fd.does_exist('Alert.png',confidence=0.8,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.height+rb_window.top)):
            fd.click(406+offset[0], 358+offset[1],delay=0.2) # ERZAfd.click
            time.sleep(0.6)
        fd.click(pos[0],pos[1],delay=0.2)
        time.sleep(0.8)
        if time_out<0:
            print("timeout failure")
            break
        time_out-=1

    print(f"Selected unit at {pos}")


def place_unit(unit: str, pos : tuple[int,int], close: bool | None=None, auto_upg: bool | None=None):
    '''
    Places a unit found in Winter\\UNIT_hb.png, at location given in pos. 
    '''
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
        
def buy_monarch(): # this just presses e untill it buys monarch, use after direction('5')
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
    # Scans and places all units in your hotbar, tracking them too
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
            if fd.does_exist(f"Winter\\{unit}.png", confidence=0.8, grayscale=False,region=hotbar_region):
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
            
def ainz_setup(unit:str): 
    '''
    Set's up ainz's abilities and places the unit given.
    '''
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


def repair_barricades(): # Repair barricades 
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
    
def set_boss(): # Sets unit priority to boss
    keyboard.press_and_release("r")
    keyboard.press_and_release("r")
    keyboard.press_and_release("r")
    keyboard.press_and_release("r")
    keyboard.press_and_release("r")
    
def detect_loss():
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

Thread(target=detect_loss,daemon=True).start()
def main():
    print("Launched")
    First_match = False
    print("Starting Winter Event")
    if fd.does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
        if fd.does_exist('Alert.png',confidence=0.8,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.height+rb_window.top)):
            fd.click(406+offset[0], 358+offset[1],delay=0.2) # ERZAfd.click
            time.sleep(0.6)
        while fd.does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
            fd.click(375+offset[0], 469+offset[1])
            time.sleep(1)
    while True:#[(414, 207) TAK, (142, 137) NAMI]
        print("Waiting for spawn")
        fd.wait_for_spawn(offset=offset,case=0)
        print("Found Spawn")
        if not First_match:
            print("Setting up camera")
            First_match = True
            pydirectinput.keyDown("i")
            time.sleep(2)
            pydirectinput.keyUp("i")
            ctypes.windll.user32.mouse_event(0x0001, 0, 100000, 0, 0)
            print("o")
            time.sleep(0.5)
            pydirectinput.keyDown("o")
            time.sleep(2)
            pydirectinput.keyUp("o")
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
        
        print("Match Starting")
        qrts()
        has_mirko_0 = False
        while not has_mirko_0:
            path_winter(2,1)
            pydirectinput.press('e',_pause = False)
            pydirectinput.press('e',_pause = False)
            qrts()
            time.sleep(1.5)
            if fd.does_exist("Winter\\Mirko.png",confidence=0.7,grayscale=False, region=hotbar_region):
                print("Got mirko")
                has_mirko_0 = True
            else:
                print("Didnt detect mirko, retrying purchase")
        Mirko_Placements = Settings.Unit_Positions.get("Mirko")
        Speed_Placements = Settings.Unit_Positions.get("Speedwagon")
        Tak_Placements = Settings.Unit_Positions.get("Takaroda")
        
        fd.start(offset)
        
        # Placing mirko
        place_unit("Mirko",Mirko_Placements[0],True)
        place_unit("Mirko",Mirko_Placements[1],True)
        
        has_mirko_1 = False
        while not has_mirko_1:
            path_winter(2,1)
            pydirectinput.press('e',_pause = False)
            qrts()
            time.sleep(1.5)
            if fd.does_exist("Winter\\Mirko.png",confidence=0.7,grayscale=False, region=hotbar_region):
                print("Got mirko")
                has_mirko_1 = True
            else:
                print("Didnt detect mirko, retrying purchase")
                
        # Placing mirko
        place_unit("Mirko",Mirko_Placements[2],True)
        
        # Speedwagon
        path_winter(1,1)
        pydirectinput.press("e",presses=3,_pause=False)
        for i in range(3):
            place_unit("Speedwagon",Speed_Placements[i],close=True,auto_upg=True)
        
        # Path to tak
        fd.click(414+offset[0], 207+offset[1],right_click=True)
        
        time.sleep(1)
        while not fd.does_exist("Winter\\Takaroda.png",confidence=0.8,grayscale=False, region=hotbar_region):
            while not load_state()["running"]:
                time.sleep(0.5)
            pydirectinput.press("e")
            time.sleep(0.5)
        #Place
        place_unit("Takaroda",Tak_Placements[0],close=True,auto_upg=True)

        #Path to nami
        fd.click(142+offset[0], 137+offset[1],right_click=True)
        time.sleep(3)
        while not fd.does_exist("Winter\\Nami.png",confidence=0.8,grayscale=False, region=hotbar_region):
            while not load_state()["running"]:
                time.sleep(0.5)
            pydirectinput.press("e")
            time.sleep(0.5)
        qrts()
        place_unit("Nami",pos=(397, 437),auto_upg=True,close=True)
        
        # Get first upgrade
        path_winter(4,0)
        upgrader("fortune")
        qrts()
        # Auto first mirko
        secure_select(Mirko_Placements[0])
        pydirectinput.press("z")
        fd.click(305+offset[0], 233+offset[1])
        # Get damage
        path_winter(4,0)
        upgrader("damage")
        qrts()
        # Auto rest
        secure_select(Mirko_Placements[1])
        pydirectinput.press("z")
        fd.click(305+offset[0], 233+offset[1])
        
        secure_select(Mirko_Placements[2])
        pydirectinput.press("z")
        fd.click(305+offset[0], 233+offset[1])
        
        # Get first monarch
        path_winter(5,0)
        buy_monarch()
        qrts()
        secure_select(Mirko_Placements[0])
        
        wave_19 = False
        while not wave_19:
            while not load_state()["running"]:
                time.sleep(0.5)
            if fd.get_wave(offset)>=19:
                wave_19 = True
                keyboard.press('d')
                time.sleep(Settings.BUY_MAIN_LANE_DELAYS[0])
                keyboard.release('d')
                keyboard.press_and_release('e')
                keyboard.press_and_release('e')
                keyboard.press('w')
                time.sleep(Settings.BUY_MAIN_LANE_DELAYS[1])
                keyboard.release('w')
                keyboard.press_and_release('e')
                keyboard.press_and_release('e')
            time.sleep(1.5)
        
        # rest of monarchs
        qrts()
        path_winter(5,0)
        buy_monarch()
        qrts()
        secure_select(Mirko_Placements[1])
        
        path_winter(5,0)
        buy_monarch()
        qrts()
        secure_select(Mirko_Placements[2])
        
        # all upgrades
        path_winter(4,0)
        upgrader('range')
        upgrader('speed')
        upgrader('armor')
        qrts()
        
        path_winter(3,0)
        Ben_Upgraded = False
        Erza_Upgraded = False
        gamble_done = False
        ainz_placed = False
        while not gamble_done:
            keyboard.press_and_release('e')
            while not load_state()["running"]:
                time.sleep(0.5)
            if check_return():
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
                    fd.click(307+offset[0], 230+offset[1], delay=0.2)
                    ainz_placed = True
                    path_winter(3,0)
            if not Erza_Upgraded:
                if Unit_Placements_Left["Erza"] == 0:
                    Erza_Placements = Settings.Unit_Positions['Erza']
                    qrts()
                    fd.click(307+offset[0], 230+offset[1], delay=0.2)
                    time.sleep(1)
                    
                    fd.upgrade_unit("5",pos=Erza_Placements[2],offset=offset)
                    fd.use_ability(Erza_Placements[2],"MAGE_3",offset=offset)
                    
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
        fd.click(307+offset[0], 230+offset[1], delay=0.2)
        time.sleep(1)
        
        if Settings.USE_WD:
            fd.upgrade_unit("10",Settings.Unit_Positions['Caloric_Unit'],offset=offset)
        elif Settings.USE_DIO:
            fd.upgrade_unit("8",Settings.Unit_Positions['Caloric_Unit'],offset=offset)
        
        if fd.does_exist("Winter\\HasMonarch.png",confidence=0.9,grayscale=True,region=monarch_region):
                pydirectinput.press('q')    
        for ice in Settings.Unit_Positions['Rukia']: 
            while not load_state()["running"]:
                time.sleep(0.5)
            secure_select(ice)
            set_boss()
            fd.click(307+offset[0], 230+offset[1], delay=0.2)
            fd.upgrade_unit("13",pos=ice,offset=offset)
            path_winter(5,0)
            buy_monarch()
            qrts()
            secure_select(ice)
            fd.click(307+offset[0], 230+offset[1], delay=0.2)
        if fd.does_exist("Winter\\HasMonarch.png",confidence=0.9,grayscale=True,region=monarch_region):
                pydirectinput.press('q')
        for gamer in Settings.Unit_Positions['TrashGamer']: 
            while not load_state()["running"]:
                time.sleep(0.5)
            secure_select(gamer)
            set_boss()
            fd.click(307+offset[0], 230+offset[1], delay=0.2)
            fd.upgrade_unit("AUTO",pos=gamer,offset=offset)
            path_winter(5,0)
            buy_monarch()
            qrts()
            secure_select(gamer)
            fd.click(307+offset[0], 230+offset[1], delay=0.2)
        if fd.does_exist("Winter\\HasMonarch.png",confidence=0.9,grayscale=True,region=monarch_region):
                pydirectinput.press('q')
        for kuzan in Settings.Unit_Positions['Kuzan']: 
            while not load_state()["running"]:
                time.sleep(0.5)
            secure_select(kuzan)
            set_boss()
            fd.click(307+offset[0], 230+offset[1], delay=0.2)
            fd.upgrade_unit("AUTO",pos=kuzan,offset=offset)
            path_winter(5,0)
            buy_monarch()
            qrts()
            secure_select(kuzan)
            fd.click(307+offset[0], 230+offset[1], delay=0.2)
        if fd.does_exist("Winter\\HasMonarch.png",confidence=0.9,grayscale=True,region=monarch_region):
                pydirectinput.press('q')
        for esc in Settings.Unit_Positions['Escanor']: 
            while not load_state()["running"]:
                time.sleep(0.5)
            secure_select(esc)
            set_boss()
            fd.click(307+offset[0], 230+offset[1], delay=0.2)
            fd.upgrade_unit("AUTO",pos=esc,offset=offset)
            path_winter(5,0)
            buy_monarch()
            qrts()
            secure_select(esc)
            fd.click(307+offset[0], 230+offset[1], delay=0.2)
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
            if fd.get_wave(offset)==139 and not done_path:
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
                fd.click(328+offset[0], 341+offset[1],right_click=True)
                time.sleep(4)
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
            if fd.get_wave(offset)==140:
                wave_140 = True
            else:
                if fd.get_wave(offset)%2==0 or fd.get_wave(offset) == 139 and done_path:
                    repair_barricades()
                    qrts()
                    time.sleep(2)
        add_data = load_state()
        add_data["num_runs"]+=1
        add_data["wins"]+=1
        update_state(add_data)
        fd.restart_match(offset)
        time.sleep(1)

keyboard.press_and_release("w")
keyboard.press_and_release("a")    
keyboard.press_and_release("s")
keyboard.press_and_release("d")
main()



