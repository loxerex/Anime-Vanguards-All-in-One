import time
import pyautogui
import ctypes
import cv2
import pytesseract
import os
import numpy as np
from PIL import ImageGrab
import pydirectinput
import keyboard
import json
from threading import Thread
from pynput.mouse import Controller
import subprocess
import pygetwindow as gw



def load_state():
    json_test = os.path.join(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))), "Info", "state.json")
    with open(json_test, 'r') as file:
        return json.load(file)


def load_settings():
    json_path = os.path.join(os.path.dirname((os.path.dirname(os.path.abspath(__file__)))), "Settings", "AIO_Settings.json")
    with open(json_path, 'r') as file:
        return json.load(file)   
    
pytesseract.pytesseract.tesseract_cmd = os.path.join( # ocr
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tesseract", "tesseract.exe"
)

os.environ["TESSDATA_PREFIX"] = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tesseract", "tessdata"
)

def does_exist(imageDirectory: str, confidence: float, grayscale: bool, region: tuple | None=None) -> bool:
    try:
   
        imageDirectory = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "Resources",
        imageDirectory)
        if region is None:
            check = pyautogui.locateOnScreen(imageDirectory, grayscale=grayscale, confidence=confidence)
        else:
            check = pyautogui.locateOnScreen(imageDirectory, grayscale=grayscale, confidence=confidence, region=region)
     
        if check is not None:
            return True
        return False
    except Exception as e:
        return False

def click_image(imageDirectory: str, confidence: float, grayscale: bool, offset: tuple[int,int], region: tuple| None=None) -> bool:
    try:
        imageDirectory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"Resources", imageDirectory)
        if region is None:
            image_location = pyautogui.locateOnScreen(imageDirectory, grayscale=grayscale, confidence=confidence)
        else:
            image_location = pyautogui.locateOnScreen(imageDirectory, grayscale=grayscale, confidence=confidence, region=region)
        if image_location is not None:
            image_center = pyautogui.center(image_location)
            if offset == (0,0):
                click(image_center.x, image_center.y)
                return True
            else:
                click(image_center.x+offset[0], image_center.y+offset[1])
                return True
    except Exception as e:
        return False

def get_image_center(imageDirectory: str, confidence: float, grayscale: bool, offset: tuple[int,int], region: tuple| None=None) -> tuple[int,int] | None:
    try:
        imageDirectory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"Resources", imageDirectory)
        if region is None:
            image_location = pyautogui.locateOnScreen(imageDirectory, grayscale=grayscale, confidence=confidence)
        else:
            image_location = pyautogui.locateOnScreen(imageDirectory, grayscale=grayscale, confidence=confidence, region=region)
        if image_location is not None:
            image_center = pyautogui.center(image_location)
            return (image_center.x+offset[0], image_center.y+offset[1])
        else:
            return None
    except Exception as e:
        return None

def screenshot_region(region: tuple[int, int]):
    '''
    Region: Where the screenshot will be taken (x,y,width,height)
    Returns: NumPy array (BGR), Ment for EasyOCR and CV2 usage
    '''
    try:
        img = ImageGrab.grab(bbox=region)
        img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        return img_np
    except Exception as e:
        print(f"Region {region} experienced an error when screenshotting : {e}")

def get_wave(offset: tuple[int,int]) -> int: # Gets the current wave of the match
    try:
        #(t="327", top="123
        regionArea = [
            248+offset[0],
            46+offset[1],
            287+offset[0],
            70+offset[1]
        ]
        numbers = str(load_settings()["Settings"]["WaveNumbers"])
        image_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Resources", "WaveRecon", numbers)
        probs = []
        wave = []
        for i in range(10):
            template = cv2.imread(os.path.join(image_dir,f"{i}.png"))
            left, top, bottom, right = regionArea
            img_o = ImageGrab.grab(bbox=(left, top, bottom,right))
            img_cv2 = cv2.cvtColor(np.array(img_o),cv2.COLOR_RGB2BGR)
        

            template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            _, template = cv2.threshold(template, 250, 255, cv2.THRESH_BINARY_INV)

            img_cv2 = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2GRAY)
            _, img_cv2 = cv2.threshold(img_cv2, 250, 255, cv2.THRESH_BINARY_INV)

            res = cv2.matchTemplate(img_cv2, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            probs.append([max_val,i])
            loc = np.where(res >= 0.9)
            for pt in zip(*loc[::-1]): 
                wave.append([pt[0],i])
        #print(sorted(probs))
        try:
            if wave != []:
                wave_number = ""
                while wave != []:
                    leftmost = min(wave)
                    wave_number+=str(leftmost[1])
                    wave.remove(leftmost)
                print(f"Wave: {wave_number}")
                return int(wave_number)
        except Exception as e:
            print(f"Error in get wave into int {e}")
        print("No wave found")
        return -1
        
    except Exception as e:
        print(f"Error in get_wave: {e}")   
def read_region(region: tuple[int, int, int, int], whitelist: str, threshold_val: int|None=None) -> str:
    try:
        
        regionArea = region
        screenshot = screenshot_region(region=regionArea) # Get image of num
        screenshot = cv2.resize(screenshot, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC) 
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY) # Grayscale for speed
        if threshold_val is not None:
            _, thresh = cv2.threshold(gray, threshold_val, 255, cv2.THRESH_BINARY) # Threshold 
        else:
            _, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY) # Threshold ) # resize for accuracy
        text = pytesseract.image_to_string(thresh, config=f'--oem 3 --psm 7 -c tessedit_char_whitelist={whitelist}') 
        if not text.strip():
            return None
        return text 
        
    except Exception as e:
        print(f"Error in read_region: {e}")
        

def restart_match(offset: tuple[int,int]):
    '''sybau'''
    pos = [(29, 605), (700, 288), (347, 363), (407, 355), (752, 150)]#[(260, 267), (557, 391)]
    for p in pos:
        click(p[0]+offset[0], p[1]+offset[1], delay=0.1)
        if p ==(347, 363):
            time_out = 20
            while not does_exist("Alert.png",confidence=0.9,grayscale=True,region=(260+offset[0],267+offset[1],557+offset[0],391+offset[1])):
                time.sleep(0.5)
                time_out -=1
                
        time.sleep(1)

def wait_for_wave(num: int,offset: tuple[int,int]):
    while get_wave(offset=offset) > num+5 or get_wave(offset=offset) < num:
        if does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
            break
        time.sleep(2)
    print("found wave")

def print_arg(arg):
    print(arg)

def wait(amount):
    time.sleep(amount)
    
def place_unit(unit: int, pos : tuple[int,int], offset: tuple[int,int], priority: int | None = None, no_cancel: bool | None=None, upg: str | None = None):
    '''
    Places a unit found in Winter\\UNIT_hb.png, at location given in pos. 
    '''
    pydirectinput.press(str(unit))
    while not pyautogui.pixel(305+offset[0], 233+offset[1]) == (255,255,255):
        if load_state()["running"] == False:
            while not load_state()["running"]:
                time.sleep(0.5)
        if does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
            break
        click(pos[0]+offset[0], pos[1]+offset[1], delay=float(load_settings()["Unit_Settings"]["Placement_Delay"]))
        time.sleep(0.1)
        if no_cancel is not None and no_cancel:
            pass
        else:
            keyboard.press_and_release('q')
        time.sleep(0.5)
        click(pos[0]+offset[0], pos[1]+offset[1], delay=0.1)
        time.sleep(1)
        if does_exist("Uma\\Uma.png", confidence=0.8, grayscale=True):
            print("Found Uma")
            Uma_Selection = load_settings()["Uma_Unit"]
            if Uma_Selection.lower() == "speed":
                click(173+offset[0], 454+offset[1], delay=0.1)
            elif Uma_Selection.lower() == "damage":
                click(327+offset[0], 456+offset[1], delay=0.1)
            elif Uma_Selection.lower() == "crit":
                click(480+offset[0], 454+offset[1], delay=0.1)
            elif Uma_Selection.lower() == "cost":
                click(636+offset[0], 457+offset[1], delay=0.1)
            break
        if pyautogui.pixel(305+offset[0], 233+offset[1]) == (255,255,255):
            break
        if does_exist("Unit_Open.png", confidence=0.8, grayscale=True, region=(100+offset[0],400+offset[1], 153, 416)):
            break
        pydirectinput.press(str(unit))
        time.sleep(0.2)
    if priority is not None:
        for _ in range(priority):
            keyboard.press_and_release('r')
    if upg is not None and upg == "a":
            keyboard.press_and_release('z')
    click(307+offset[0], 230+offset[1], delay=0.2)
    print(f"Placed {unit} at {pos}")
    
def upgrade_unit(upgrade: str, pos : tuple[int,int], offset: tuple[int,int]):
    selected = select_unit(pos, offset)
    if not selected:
        return False
    can_upgrade_color = (0, 228, 27)
    try:
        if upgrade.lower() !="max" and upgrade.lower() != "auto":
            upgrade = int(upgrade)
            upgrades = 0
            while upgrades < upgrade:
                if not pyautogui.pixel(305+offset[0], 233+offset[1]) == (255,255,255) and not does_exist("Unit_Open.png", confidence=0.8, grayscale=True, region=(100+offset[0],400+offset[1], 153, 416)):
                    selec = select_unit(pos, offset)
                    if not selec:
                        return False
                if does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
                    break
                if does_exist("Unit_Max.png", confidence=0.8, grayscale=True, region=(100+offset[0],400+offset[1], 153, 416)):
                    print("Unit is max level")
                    break
                if pyautogui.pixelMatchesColor(157+offset[0],403+offset[1], can_upgrade_color,tolerance=20):
                    pydirectinput.press('t')
                    upgrades += 1
                    print(f"Upgraded {upgrades} times")
                time.sleep(0.5)
        elif upgrade.lower() == "max":  
            while not does_exist("Unit_Max.png", confidence=0.8, grayscale=True, region=(100+offset[0],400+offset[1], 153, 416)):
                if does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
                    break
                pydirectinput.press('t')
                time.sleep(0.5)
        elif upgrade.lower() == "auto":
            pydirectinput.press('z')
        print(f"Upgraded unit at {pos}") 
        click(307+offset[0], 230+offset[1], delay=0.2)   
    except Exception as e:
        print(f"Error in upgrade_unit: {e}")
    
  
def sell_unit(pos : tuple[int,int], offset: tuple[int,int]):
    select = select_unit(pos, offset)
    if not select:
        return False
    keyboard.press_and_release('x')
    print(f"Sold unit at {pos}")      
    
def select_unit(unit: tuple[int,int], offset: tuple[int,int]):
    timeout = 28
    while not pyautogui.pixel(305+offset[0], 233+offset[1]) == (255,255,255) and not does_exist("Unit_Open.png", confidence=0.8, grayscale=True, region=(100+offset[0],400+offset[1], 153, 416)):
        if does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
            break
        if does_exist("Unit_Open.png", confidence=0.8, grayscale=True, region=(100+offset[0],400+offset[1], 153, 416)):
            break
        if load_state()["running"] == False:
            while not load_state()["running"]:
                time.sleep(0.5)
        click(unit[0]+offset[0], unit[1]+offset[1], delay=0.67)
        if timeout <= 0:
            print("select unit timeout failure")
            return False
        time.sleep(0.8)
        timeout-=1
    print(f"Selected {unit}")    
    return True

def auto_positioner(positioner: str, offset: tuple[int,int], just_camera: bool | None=None, no_restart: bool | None=None, zoom: bool | None=None):
    print("Starting auto positioner")
    time.sleep(1)
    click(409+offset[0], 309+offset[1])
    pydirectinput.keyDown("i")
    time.sleep(2)
    pydirectinput.keyUp("i")
    ctypes.windll.user32.mouse_event(0x0001, 0, 10000, 0, 0)
    time.sleep(1)
    pydirectinput.keyDown("o")
    time.sleep(2)
    pydirectinput.keyUp("o")
    print("Starting loop")
    if just_camera is not None and just_camera:
        if does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
            click(355+offset[0], 470+offset[1])
            time.sleep(5)
            click(409+offset[0], 309+offset[1])
        return_to_spawn(offset)
        time.sleep(1)
        print("Found Position for map")
        return

    while not does_exist(f"Positioner\\{positioner}.png",confidence=0.85,grayscale=True,region=(0+offset[0], 0+offset[1], 355+offset[0], 288+offset[1])):
        if load_state()["running"] == False:
            while not load_state()["running"]:
                time.sleep(0.5)
        if does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
            click(355+offset[0], 470+offset[1])
            time.sleep(5)
            click(409+offset[0], 309+offset[1])
        if zoom is not None and zoom:
            pydirectinput.keyDown("o")
            time.sleep(1)
            pydirectinput.keyUp("o")
        return_to_spawn(offset=offset)
        time.sleep(2)
    print(f"Found Position for {positioner}")
    if no_restart is not None and no_restart:
        pass
    else:
        start(offset)
        time.sleep(6)
        restart_match(offset)
        time.sleep(1)
        click(412+offset[0], 309+offset[1])

def return_to_spawn(offset: tuple[int,int]):
    click_pos = [(30, 605), (708, 322), (755, 149)]
    for pos in click_pos:
        click(pos[0]+offset[0], pos[1]+offset[1], delay=0.2)
        time.sleep(0.8)
def use_ability(pos: tuple[int,int], ability: str, offset: tuple[int,int]):
    print(f"Using Ability {ability} at {pos}, offset: {offset}")
    if "PRIDEBURN" not in ability.upper().split('_')[0]:
        selected = select_unit(pos, offset)
        if not selected:
            return False
    base_ability = (336, 279)
    second_ability =  (335, 333)
    third_ability = (336, 384)
    if ability.upper().split('_')[0] == "BASE":
        if "AUTO" in ability.upper():
            click(376+offset[0], 280+offset[1])
        else:
            click(base_ability[0]+offset[0], base_ability[1]+offset[1], delay=0.2)
        click(307+offset[0], 230+offset[1], delay=0.2)
        return
    if ability.upper().split('_')[0] == "SECOND":
        click(second_ability[0]+offset[0], second_ability[1]+offset[1], delay=0.2)
        click(307+offset[0], 230+offset[1], delay=0.2)
        return
    if ability.upper().split('_')[0] == "THIRD":
        click(third_ability[0]+offset[0], third_ability[1]+offset[1], delay=0.2)
        click(307+offset[0], 230+offset[1], delay=0.2)
        return
    
    if ability.upper().split('_')[0] == "MAGE":
        while not pyautogui.pixelMatchesColor(694+offset[0],165+offset[1],(255,255,255),tolerance=40):
            click(base_ability[0]+offset[0], base_ability[1]+offset[1], delay=0.2)
            time.sleep(1)
        alert = (409, 358)
        match ability.upper().split('_')[1]:
            case "1":
                while not does_exist("Alert.png",confidence=0.95,grayscale=True,region=(245+offset[0], 253+offset[1], 569+offset[0], 391+offset[1])):
                    if not pyautogui.pixelMatchesColor(694+offset[0],165+offset[1],(255,255,255),tolerance=40):
                        select_unit(pos,offset)
                        while not pyautogui.pixelMatchesColor(694+offset[0],165+offset[1],(255,255,255),tolerance=40):
                            click(base_ability[0]+offset[0], base_ability[1]+offset[1], delay=0.2)
                            time.sleep(1)
                    if does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
                        break
                    if load_state()["running"] == False:
                        while not load_state()["running"]:
                            time.sleep(0.5)
                    click(212+offset[0],462+offset[1],delay=0.2)
                    time.sleep(1)
                click(alert[0]+offset[0],alert[1]+offset[1])
                time.sleep(0.5)
            case "2":
                while not does_exist("Alert.png",confidence=0.95,grayscale=True,region=(245+offset[0], 253+offset[1], 569+offset[0], 391+offset[1])):
                    if not pyautogui.pixelMatchesColor(694+offset[0],165+offset[1],(255,255,255),tolerance=40):
                        select_unit(pos,offset)
                        while not pyautogui.pixelMatchesColor(694+offset[0],165+offset[1],(255,255,255),tolerance=40):
                            click(base_ability[0]+offset[0], base_ability[1]+offset[1], delay=0.2)
                            time.sleep(1)
                    if does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
                        break
                    if load_state()["running"] == False:
                        while not load_state()["running"]:
                            time.sleep(0.5)
                    click(410+offset[0],461+offset[1],delay=0.2)
                    time.sleep(1)
                click(alert[0]+offset[0],alert[1]+offset[1])
                time.sleep(0.5)
            case "3":
                while not does_exist("Alert.png",confidence=0.95,grayscale=True,region=(245+offset[0], 253+offset[1], 569+offset[0], 391+offset[1])):
                    if not pyautogui.pixelMatchesColor(694+offset[0],165+offset[1],(255,255,255),tolerance=40):
                        select_unit(pos,offset)
                        while not pyautogui.pixelMatchesColor(694+offset[0],165+offset[1],(255,255,255),tolerance=40):
                            click(base_ability[0]+offset[0], base_ability[1]+offset[1], delay=0.2)
                            time.sleep(1)
                    if does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
                        break
                    if load_state()["running"] == False:
                        while not load_state()["running"]:
                            time.sleep(0.5)
                    click(603+offset[0],462+offset[1],delay=0.2)
                    time.sleep(1)
                click(alert[0]+offset[0],alert[1]+offset[1])
                time.sleep(0.5)
        
        click(696+offset[0],165+offset[1],delay=0.2)
        click(307+offset[0], 230+offset[1], delay=0.2)
        return
    
    if ability.upper().split('_')[0] == "VSJW":
        VSJW_NUKES = [(403, 327), (444, 325), (404, 365)]
        if ability.upper().split('_')[1] == "NUKE":
            Nuke_Num = int(ability.upper().split('_')[2])-1
            click(base_ability[0]+offset[0], base_ability[1]+offset[1], delay=0.2)
            time.sleep(1)
            click(424+offset[0],281+offset[1],delay=0.2)
            time.sleep(1)
            click(VSJW_NUKES[Nuke_Num][0]+offset[0],VSJW_NUKES[Nuke_Num][1]+offset[1],delay=0.2)
            click(base_ability[0]+offset[0], base_ability[1]+offset[1], delay=0.2)
            return
        if ability.upper().split('_')[1] == "SHADOW":
            click(base_ability[0]+offset[0], base_ability[1]+offset[1], delay=0.2)
            time.sleep(1)
            click(380+offset[0], 281+offset[1])
            time.sleep(1)
            mouse = Controller()
            arise = (210, 455)
            bear = [(442, 240), (468, 239), (497, 239), (523, 239)]
            steel = [(106, 240), (134, 239), (161, 239), (188, 239)]
            healer = [(369, 239), (398, 239), (427, 238), (454, 240)]
            belu = [(635, 238), (663, 240), (692, 241), (719, 242)]
            if ability.upper().split('_')[2] == "A1":
                click(arise[0]+offset[0]+arise[1]+offset[1])
            for prioity in ability.split('_')[3:]:
                match prioity[0].upper():
                    case "B":
                        click(424+offset[0], 333+offset[1])
                        mouse.scroll(0,10)
                        click(bear[int(prioity[1])-1][0]+offset[0],bear[int(prioity[1])-1][1]+offset[1])   
                    case "S":
                        click(424+offset[0], 333+offset[1])
                        mouse.scroll(0,10)
                        time.sleep(0.1)
                        mouse.scroll(0,-6)
                        click(steel[int(prioity[1])-1][0]+offset[0],steel[int(prioity[1])-1][1]+offset[1]) 
                    case "H":
                        click(424+offset[0], 333+offset[1])
                        mouse.scroll(0,10)
                        time.sleep(0.1)
                        mouse.scroll(0,-6)
                        click(healer[int(prioity[1])-1][0]+offset[0],healer[int(prioity[1])-1][1]+offset[1]) 
                    case "E":
                        click(424+offset[0], 333+offset[1])
                        mouse.scroll(0,10)
                        time.sleep(0.1)
                        mouse.scroll(0,-6)
                        click(belu[int(prioity[1])-1][0]+offset[0],belu[int(prioity[1])-1][1]+offset[1]) 
            click(720+offset[0], 164+offset[1],delay=0.1)
            click(base_ability[0]+offset[0], base_ability[1]+offset[1], delay=0.2)
            click(307+offset[0], 230+offset[1], delay=0.2)
            return 
        click(307+offset[0], 230+offset[1], delay=0.2)
        return
    
    if "PRIDEBURN" in ability.upper().split('_')[0]:
        escanor_slot = ability.split("_")[1]
        Slots = [(272, 570), (327, 568), (382, 573), (437, 573), (491, 572), (547, 573)]
        click(403+offset[0], 459+offset[1], delay=0.2)
        for i,slot in enumerate(Slots):
            if i == int(escanor_slot)-1:
                continue
            else:
                click(slot[0]+offset[0],slot[1]+offset[1],delay=0.2)
        click(403+offset[0], 459+offset[1], delay=0.2)
        return
    
    if "VALENTINE" in ability.upper().split('_')[0]:
        click(base_ability[0]+offset[0], base_ability[1]+offset[1], delay=0.2)
        time.sleep(0.5)
        for placement in ability.upper().split('_')[1:]:
            keyboard.press("shift")
            x,y = int(placement.split(',')[0]), int(placement.split(',')[1])
            click(x+offset[0], y+offset[1], delay=0.1)
            time.sleep(0.2)
        keyboard.release("shift")
        time.sleep(1)
        pydirectinput.press('q')
        return

    if "LAW" in ability.upper().split('_')[0]:
        click(base_ability[0]+offset[0], base_ability[1]+offset[1], delay=0.2)
        time.sleep(1)
        match ability.upper().split('_')[1]:
            case "ONE":
                click(212+offset[0], 461+offset[1], delay=0.2)
            case "TWO":
                click(408+offset[0], 459+offset[1], delay=0.2)
            case "THREE":
                click(605+offset[0], 458+offset[1], delay=0.2)
            case _:
                pass
        click(695+offset[0], 166+offset[1], delay=0.1)
        click(307+offset[0], 230+offset[1], delay=0.2)
        return
    if "BROOK" in ability.upper().split('_')[0]:
        buff = False
        click(base_ability[0]+offset[0], base_ability[1]+offset[1], delay=0.2)
        time.sleep(0.5)
        def spam():
            while not buff:
                if load_state()["running"] == False:
                    while not load_state()["running"]:
                        time.sleep(0.5)
                Thread(target=pydirectinput.press, args=('a',),daemon=True).start()
                Thread(target=pydirectinput.press, args=('s',),daemon=True).start()
                Thread(target=pydirectinput.press, args=('d',),daemon=True).start()
                Thread(target=pydirectinput.press, args=('f',),daemon=True).start()
                Thread(target=pydirectinput.press, args=('g',),daemon=True).start()
                time.sleep(0.1)
        Thread(target=spam, daemon=True).start()
        c = 60
        while not buff: #[(566, 497), (620, 552)
            click(409+offset[0], 309+offset[1],delay=0.1)
            if does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
                break
            if load_state()["running"] == False:
                while not load_state()["running"]:
                    time.sleep(0.5)
            if c <= 0:
                print("Buff failed to proc in time")
                buff = True
                break
            num = read_region((566+offset[0], 497+offset[1], 620+offset[0], 552+offset[1]), whitelist="0123456789",threshold_val=70)
            if num and int(num) >= 40 and int(num) < 60:
                buff = True
                print("Brook buff on")
            c-=1
            time.sleep(1)
        time.sleep(1)
        click(620+offset[0], 202+offset[1])
        click(307+offset[0], 230+offset[1], delay=0.2)
        return
    
    if "UMA_RACING" in ability.upper():
        speed = (368, 309)
        damage = (520, 309)
        crit = (524, 391)
        cost = (365, 394)
        rest = (281, 421)
        mood_region = (280+offset[0], 228+offset[1], 388+offset[0], 247+offset[1])
        action_region = (435+offset[0], 230+offset[1], 534+offset[0], 250+offset[1])
        uma_upgrades = [False, False, False,False]
        actions = int(read_region(action_region,whitelist="01234"))
        while not all(uma_upgrades):
            if does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
                break
            if load_state()["running"] == False:
                while not load_state()["running"]:
                    time.sleep(0.5)
            try:
                actions = int(read_region(action_region,whitelist="01234"))
                if actions == 0:
                    click(320+offset[0], 466+offset[1], delay=0.1)
                    time.sleep(0.5)
                if read_region(mood_region,whitelist="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ").replace("Mood","").strip() != "Great":
                    if actions > 0:
                        click(rest[0]+offset[0], rest[1]+offset[1], delay=0.1)
                        if does_exist("Alert.png", confidence=0.95, grayscale=True):
                                click(409+offset[0], 355+offset[1])
                else:
                    if uma_upgrades[0] == False:
                        if actions > 0:
                            upg_region = (280+offset[0], 230+offset[1], 332+offset[0], 326+offset[1])
                            if does_exist("Uma\\Uma_Max.png", confidence=0.95, grayscale=True, region=upg_region):
                                uma_upgrades[0] = True
                            click(speed[0]+offset[0], speed[1]+offset[1], delay=0.1)
                            time.sleep(0.5)
                            if does_exist("Alert.png", confidence=0.95, grayscale=True):
                                click(409+offset[0], 355+offset[1])
                    elif uma_upgrades[1] == False:
                        if actions > 0:
                            upg_region = (442+offset[0], 288+offset[1], 487+offset[0], 329+offset[1])
                            if does_exist("Uma\\Uma_Max.png", confidence=0.95, grayscale=True, region=upg_region):
                                uma_upgrades[1] = True
                            click(damage[0]+offset[0], damage[1]+offset[1], delay=0.1)
                            time.sleep(0.5)
                            if does_exist("Alert.png", confidence=0.95, grayscale=True):
                                click(409+offset[0], 355+offset[1])
                    elif uma_upgrades[2] == False:
                        if actions > 0:
                            upg_region = (285+offset[0], 362+offset[1], 332+offset[0], 408+offset[1])
                            if does_exist("Uma\\Uma_Max.png", confidence=0.95, grayscale=True, region=upg_region):
                                uma_upgrades[2] = True
                            click(cost[0]+offset[0], cost[1]+offset[1], delay=0.1)
                            time.sleep(0.5)
                            if does_exist("Alert.png", confidence=0.95, grayscale=True):
                                click(409+offset[0], 355+offset[1])
                    elif uma_upgrades[3] == False:
                        if actions > 0:
                            upg_region = (444+offset[0], 364+offset[1], 485+offset[0], 410+offset[1])
                            if does_exist("Uma\\Uma_Max.png", confidence=0.95, grayscale=True, region=upg_region):
                                uma_upgrades[3] = True
                            click(crit[0]+offset[0], crit[1]+offset[1], delay=0.1)
                            time.sleep(0.5)
                            if does_exist("Alert.png", confidence=0.95, grayscale=True):
                                click(409+offset[0], 355+offset[1])
                time.sleep(1)
            except Exception as e:
                print(f"Error in uma loop: {e}")
        click(307+offset[0], 230+offset[1], delay=0.2)
        return
        
    if "AINZ" in ability.upper().split('_')[0]:
        if ability.upper() == "AINZ_NUKE":
            click(base_ability[0]+offset[0], base_ability[1]+offset[1], delay=0.2)
        elif "AINZ_SPELLS" in ability.upper():
            click(second_ability[0]+offset[0], second_ability[1]+offset[1], delay=0.2)
            # back: (228, 245)
            #(429, 278), (429, 317) 1 and 2
            ainz_pngs = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Resources", "Ainz")
            time.sleep(0.8)
            for element in ability.split("_")[2:]:
                Element = "".join(c for c in element if not c.isdigit())
                spell_num = "".join(c for c in element if c.isdigit())
                if "fire" in Element.lower():
                    if does_exist(f"{ainz_pngs}\\Fire.png", confidence=0.8, grayscale=True):
                        click_image(f"{ainz_pngs}\\Fire.png", confidence=0.8, grayscale=True, offset=[0,0])
                        time.sleep(0.5)
                        for num in spell_num:
                            if num == "1":
                                click(429+offset[0], 278+offset[1], delay=0.1)
                            elif num == "2":
                                click(429+offset[0], 317+offset[1], delay=0.1)
                            time.sleep(0.5)
                elif "water" in Element.lower():
                    if does_exist(f"{ainz_pngs}\\Water.png", confidence=0.8, grayscale=True):
                        click_image(f"{ainz_pngs}\\Water.png", confidence=0.8, grayscale=True, offset=[0,0])
                        time.sleep(0.5)
                        for num in spell_num:
                            if num == "1":
                                click(429+offset[0], 278+offset[1], delay=0.1)
                            elif num == "2":
                                click(429+offset[0], 317+offset[1], delay=0.1)
                            time.sleep(0.5)
                elif "cosmic" in Element.lower():
                    if does_exist(f"{ainz_pngs}\\Cosmic.png", confidence=0.8, grayscale=True):
                        click_image(f"{ainz_pngs}\\Cosmic.png", confidence=0.8, grayscale=True, offset=[0,0])
                        time.sleep(0.5)
                        for num in spell_num:
                            if num == "1":
                                click(429+offset[0], 278+offset[1], delay=0.1)
                            elif num == "2":
                                click(429+offset[0], 317+offset[1], delay=0.1)
                            time.sleep(0.5)
                elif "holy" in Element.lower():
                    if does_exist(f"{ainz_pngs}\\Holy.png", confidence=0.8, grayscale=True):
                        click_image(f"{ainz_pngs}\\Holy.png", confidence=0.8, grayscale=True, offset=[0,0])
                        time.sleep(0.5)
                        for num in spell_num:
                            if num == "1":
                                click(429+offset[0], 278+offset[1], delay=0.1)
                            elif num == "2":
                                click(429+offset[0], 317+offset[1], delay=0.1)
                            time.sleep(0.5)
                elif "elementless" in Element.lower():
                    if does_exist(f"{ainz_pngs}\\Elementless.png", confidence=0.8, grayscale=True):
                        click_image(f"{ainz_pngs}\\Elementless.png", confidence=0.8, grayscale=True, offset=[0,0])
                        time.sleep(0.5)
                        for num in spell_num:
                            if num == "1":
                                click(429+offset[0], 278+offset[1], delay=0.1)
                            elif num == "2":
                                click(429+offset[0], 317+offset[1], delay=0.1)
                            time.sleep(0.5)
                elif "unbound" in Element.lower():
                    if does_exist(f"{ainz_pngs}\\Unbound.png", confidence=0.8, grayscale=True):
                        click_image(f"{ainz_pngs}\\Unbound.png", confidence=0.8, grayscale=True, offset=[0,0])
                        time.sleep(0.5)
                        for num in spell_num:
                            if num == "1":
                                click(429+offset[0], 278+offset[1], delay=0.1)
                            elif num == "2":
                                click(429+offset[0], 317+offset[1], delay=0.1)
                            time.sleep(0.5)
                elif "nature" in Element.lower():
                    if does_exist(f"{ainz_pngs}\\Nature.png", confidence=0.8, grayscale=True):
                        click_image(f"{ainz_pngs}\\Nature.png", confidence=0.8, grayscale=True, offset=[0,0])
                        time.sleep(0.5)
                        for num in spell_num:
                            if num == "1":
                                click(429+offset[0], 278+offset[1], delay=0.1)
                            elif num == "2":
                                click(429+offset[0], 317+offset[1], delay=0.1)
                            time.sleep(0.5)
                elif "curse" in Element.lower():
                    if does_exist(f"{ainz_pngs}\\Curse.png", confidence=0.8, grayscale=True):
                        click_image(f"{ainz_pngs}\\Curse.png", confidence=0.8, grayscale=True, offset=[0,0])
                        time.sleep(0.5)
                        for num in spell_num:
                            if num == "1":
                                click(429+offset[0], 278+offset[1], delay=0.1)
                            elif num == "2":
                                click(429+offset[0], 317+offset[1], delay=0.1)
                            time.sleep(0.5)
                elif "blast" in Element.lower():
                    if does_exist(f"{ainz_pngs}\\Blast.png", confidence=0.8, grayscale=True):
                        click_image(f"{ainz_pngs}\\Blast.png", confidence=0.8, grayscale=True, offset=[0,0])
                        time.sleep(0.5)
                        for num in spell_num:
                            if num == "1":
                                click(429+offset[0], 278+offset[1], delay=0.1)
                            elif num == "2":
                                click(429+offset[0], 317+offset[1], delay=0.1)
                            time.sleep(0.5)
                elif "spark" in Element.lower():
                    if does_exist(f"{ainz_pngs}\\Spark.png", confidence=0.8, grayscale=True):
                        click_image(f"{ainz_pngs}\\Spark.png", confidence=0.8, grayscale=True, offset=[0,0])
                        time.sleep(0.5)
                        for num in spell_num:
                            if num == "1":
                                click(429+offset[0], 278+offset[1], delay=0.1)
                            elif num == "2":
                                click(429+offset[0], 317+offset[1], delay=0.1)
                            time.sleep(0.5)
                elif "passion" in Element.lower():
                    if does_exist(f"{ainz_pngs}\\Passion.png", confidence=0.8, grayscale=True):
                        click_image(f"{ainz_pngs}\\Passion.png", confidence=0.8, grayscale=True, offset=[0,0])
                        time.sleep(0.5)
                        for num in spell_num:
                            if num == "1":
                                click(429+offset[0], 278+offset[1], delay=0.1)
                            elif num == "2":
                                click(429+offset[0], 329+offset[1], delay=0.1)
                            time.sleep(0.5)
                click(228+offset[0], 245+offset[1], delay=0.1)
                time.sleep(0.5)
            click(567+offset[0], 428+offset[1], delay=0.1)
            time.sleep(0.5)
            click(410+offset[0], 366+offset[1])
            click(307+offset[0], 230+offset[1], delay=0.2)
            return
        elif "AINZ_WORLDITEM" in ability.upper():
            click(third_ability[0]+offset[0], third_ability[1]+offset[1], delay=0.2)
            time.sleep(0.8)

            if "AINZ_WORLDITEM_SCROLL" in ability.upper():
                c = 1
                r = 0
                click(363+(c*270)+offset[0], (277+(r*85))+offset[1])
                time.sleep(0.5)
                other_pos = [int(ability.split("_")[3]),int(ability.split("_")[4])]
                click(other_pos[0]+offset[0], other_pos[1]+offset[1], delay=0.1)
            elif "AINZ_WORLDITEM_SAVIOR" in ability.upper():
                c = 0
                r = 0
                click(363+(c*270)+offset[0], (277+(r*85))+offset[1])
                click(666+offset[0], 182+offset[1], delay=0.1)
            elif "AINZ_WORLDITEM_BRANCH" in ability.upper():
                c = 0
                r = 1
                click(363+(c*270)+offset[0], (277+(r*85))+offset[1])
                click(666+offset[0], 182+offset[1], delay=0.1)
            elif "AINZ_WORLDITEM_ELEMENTS" in ability.upper():
                c = 1
                r = 1
                click(363+(c*270)+offset[0], (277+(r*85))+offset[1])
                click(666+offset[0], 182+offset[1], delay=0.1)
            elif "AINZ_WORLDITEM_OUROBOUROS" in ability.upper():
                c = 1
                r = 2
                click(363+(c*270)+offset[0], (277+(r*85))+offset[1])
                time.sleep(0.5)
                num = (ability.split("_")[4])
                option = (ability.split("_")[5])
                #(408, 288)
                click(408+offset[0], 288+offset[1], delay=0.1)
                keyboard.write(num)
                time.sleep(0.5)
                if option.lower() == "hp":
                    click(404+offset[0], 344+offset[1], delay=0.1)
                elif option.lower() == "wave":
                    click(407+offset[0], 385+offset[1], delay=0.1)
                elif option.lower() == "cost":
                    click(407+offset[0], 430+offset[1], delay=0.1)
                click(666+offset[0], 182+offset[1], delay=0.1)
            elif "AINZ_WORLDITEM_CALORIC" in ability.upper():
                c = 0
                r = 2
                ainz_unit = ability.split("_")[3]
                ainz_unit_pos = [int(ability.split("_")[4]), int(ability.split("_")[5])]
                #[(212, 231), (215, 284), (314, 335)]
                click(363+(c*270)+offset[0], (277+(r*85))+offset[1])
                time.sleep(1)
                for pos in [(212, 231), (215, 284), (314, 335)]:
                    click(pos[0]+offset[0], pos[1]+offset[1], delay=0.1)
                    if pos == (212,231):
                        keyboard.write(ainz_unit)
                    time.sleep(0.8)
                place_unit(0,ainz_unit_pos, offset=offset, no_cancel=True)
        click(307+offset[0], 230+offset[1], delay=0.2)
        return
    if "DIO" in ability.upper().split('_')[0]:
        time.sleep(0.8)
        c = 0
        r = 0
        dio_ability = ability.split("_")[1]
        print(dio_ability)
        if dio_ability.upper() != "TIMESTOP":
            click(base_ability[0]+offset[0], base_ability[1]+offset[1], delay=0.2)
            if dio_ability.upper() == "STUN":
                c,r = 1,2
            elif dio_ability.upper() == "BURN":
                c,r = 0,0
            elif dio_ability.upper() == "SCORCHED":
                c,r = 0,1
            elif dio_ability.upper() == "BUBLED":
                c,r = 0,2
            elif dio_ability.upper() == "BLEED":
                c,r = 1,0
            elif dio_ability.upper() == "RUPTURE":
                c,r = 1,1
            elif dio_ability.upper() == "SLOW":
                c,r = 2,0
            elif dio_ability.upper() == "FREEZE":
                c,r = 2,1
            elif dio_ability.upper() == "WOUNDED":
                c,r = 2,2
            click((250+(r*175))+offset[0], (291+(c*78))+offset[1])
            click(666+offset[0], 182+offset[1], delay=0.1)
        else:
            click(second_ability[0]+offset[0], second_ability[1]+offset[1], delay=0.2)
            time.sleep(0.8)
            selected = select_unit(pos, offset)
            if not selected:
                return False
            if dio_ability.upper() == "TIMESTOP":
                click(378+offset[0], 283+offset[1], delay=0.1)
        click(307+offset[0], 230+offset[1], delay=0.2)
        return
            

def reconnect():
    print("Reconnecting")
    psapi = ctypes.WinDLL("Psapi.dll")
    kernel32 = ctypes.WinDLL("kernel32.dll")
    EnumProcesses = psapi.EnumProcesses
    EnumProcesses.argtypes = [ctypes.POINTER(ctypes.wintypes.DWORD), ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.wintypes.DWORD)]
    EnumProcesses.restype = ctypes.wintypes.BOOL
    OpenProcess = kernel32.OpenProcess
    OpenProcess.argtypes = [ctypes.wintypes.DWORD, ctypes.wintypes.BOOL, ctypes.wintypes.DWORD]
    OpenProcess.restype = ctypes.wintypes.HANDLE
    QueryFullProcessImageNameW = kernel32.QueryFullProcessImageNameW
    QueryFullProcessImageNameW.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD, ctypes.wintypes.LPWSTR, ctypes.POINTER(ctypes.wintypes.DWORD)]
    QueryFullProcessImageNameW.restype = ctypes.wintypes.BOOL
    CloseHandle = kernel32.CloseHandle
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    def get_exe_path(pid):
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        buf = ctypes.create_unicode_buffer(260)
        size = ctypes.wintypes.DWORD(len(buf))
        path = ctypes.windll.kernel32.QueryFullProcessImageNameW(handle,0,buf,ctypes.byref(size))
        CloseHandle(handle)
        return buf.value if path else None
    def find_roblox_pid():
        arr = (ctypes.wintypes.DWORD*4096)()
        needed = ctypes.wintypes.DWORD()
        if not EnumProcesses(arr,ctypes.sizeof(arr),ctypes.byref(needed)):
            return []
        count = needed.value // ctypes.sizeof(ctypes.wintypes.DWORD)
        pids = arr[:count]
        match = []
        for pid in pids:
            path = get_exe_path(pid)
            if not path:
                continue
            exe = os.path.basename(path).lower()
            if exe == "robloxplayerbeta.exe":
                match.append(pid)
        return match
    pid = find_roblox_pid()
    roblox_exe = get_exe_path(pid=pid[0])
    subprocess.Popen([roblox_exe, f"roblox://placeId={16146832113}&linkCode={load_settings()["Settings"]["Private_Server_Code"]}/"])
    time.sleep(10)
    offset = [0,0]
    try:
        window = None
        while window is None:
            find_title = next(filter(lambda p: "Roblox" in p, gw.getAllTitles()))
            window = gw.getWindowsWithTitle(find_title)[0]
            time.sleep(2)
        #<Win32Window left="200", top="161", width="1100", height="800", title="Roblox">
        window.width=816
        window.height=638
        offset[0] = window.left
        offset[1] = window.top
        
    except Exception as e:
        print(f"error when resize: {e}")
    while not does_exist("AreaIcon.png",confidence=0.8,grayscale=False):
        #(654, 187)
        if pyautogui.pixelMatchesColor(654+offset[0],187+offset[1],(255,255,255),tolerance=5):  
            click(654+offset[0],187+offset[1],delay=0.1)
        time.sleep(1)
    time.sleep(5)
    if pyautogui.pixelMatchesColor(654+offset[0],187+offset[1],(255,255,255),tolerance=5):  
            click(654+offset[0],187+offset[1],delay=0.1)

def return_to_lobby(offset: tuple[int,int]):
    clicks = [(30, 607), (434, 317), (352, 363)]
    for pos in clicks:
        click(pos[0]+offset[0],pos[1]+offset[1])
        time.sleep(1)
                
        
def click(x,y, delay: int | None=None, right_click: bool | None = None, dont_move: bool | None = None) -> None:
    if delay is not None:
        delay=delay
    else:
        delay = 0.65
    if dont_move is None:
        pyautogui.moveTo(x,y)
    ctypes.windll.user32.mouse_event(0x0001, 0, 1, 0, 0)
    time.sleep(delay)
    ctypes.windll.user32.mouse_event(0x0001, 0, -1, 0, 0)
    if right_click:
        pyautogui.rightClick()
    else:
        pyautogui.click()
    

def start(offset: tuple[int,int]):
    click(472+offset[0],122+offset[1],delay=0.2)    
def wait_for_spawn(offset: tuple[int,int], case: int):
    region = (442+offset[0], 109+offset[1], 506+offset[0], 143+offset[1])
    if case == 1:
        while does_exist("VoteStart.png",confidence=0.9,grayscale=True,region=region):
            time.sleep(0.5)
        return
    if case == 0:
        timeout_wfs = int(load_settings()["Settings"]["Wait_Start_Timeout"])
        t=0
        while not does_exist("VoteStart.png",confidence=0.9,grayscale=True,region=region):
            if does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
                break
            if does_exist("Odyssey\\Autoplay.png", confidence=0.9, grayscale=True,region=(631+offset[0], 366+offset[1], 805+offset[0], 472+offset[1])):
                if not does_exist("VoteStart.png",confidence=0.9,grayscale=True,region=region):
                    restart_match(offset)
                    time.sleep(1)
            if t==timeout_wfs*2:
                restart_match(offset)
                t=0
                time.sleep(1)
            t+=1
            time.sleep(0.5)
        return
def wait_for_cards(offset: tuple[int,int]):
    region = (51+offset[0], 208+offset[1], 778+offset[0], 237+offset[1])
    timeout_wfs = int(load_settings()["Settings"]["Wait_Start_Timeout"])
    t=0
    while not does_exist("Challenge\\ModifierShow.png",confidence=0.9,grayscale=True,region=region):
        if does_exist("Challenge\\ModifierShow.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
            break
        if t==timeout_wfs:
            click(412+offset[0], 309+offset[1])
            start(offset)
            restart_match(offset)
            t=0
            time.sleep(1)
        t+=1
        time.sleep(0.5)
    return#(537, 312)
def check_for_cards(offset):
    if does_exist("Challenge\\ModifierShow.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
        return True
    return False
def challenge_cards(card:str, offset: tuple[int,int]):#(51, 208), (778, 237)
    card = f"Challenge\\{card}.png"
    region = (44+offset[0], 202+offset[1], 790+offset[0], 352+offset[1])
    click(537+offset[0],312+offset[1])
    mouse = Controller()
    selected = False
    direction = False
    while not selected:
        if does_exist(card, confidence=0.9, grayscale=True,region=region):
            click_image(card, confidence=0.9, grayscale=True,region=region,offset=(0,0))
            selected = True
        else:
            if direction:
                direction = not direction
                mouse.scroll(0,10)
            else:
                direction = not direction
                mouse.scroll(0,-10)
        time.sleep(2)
    return

def press(key: str, delay: float):
    pydirectinput.keyDown(key)
    time.sleep(delay)
    pydirectinput.keyUp(key)
    
def lobby_path(area: str, stage: int, act: int):
    '''
    Area: like story, dungeon, etc
    stage: what stage lol
    act: which act
    '''
    print(f"pathing to lobby: {area, stage, act}")
    start_match = [(447, 476),(405, 363)]
    create_match = (82, 288)
    find_title = next(filter(lambda p: "Roblox" in p, gw.getAllTitles()))
    rb_window = gw.getWindowsWithTitle(find_title)[0]
    offset = (rb_window.left, rb_window.top)
    print(f"Window pos: {offset}")
    while not does_exist("AreaIcon.png",confidence=0.7,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.top+rb_window.height)): # just wait for lobby
        if pyautogui.pixelMatchesColor(654+offset[0],187+offset[1],(255,255,255),tolerance=5): #incase pop up close
            click(654+offset[0],187+offset[1],delay=0.1)
        print("Finding area icon")
        time.sleep(1)
    print("Found area icon")
    time.sleep(1) # Delay for loaded in
    if pyautogui.pixelMatchesColor(654+offset[0],187+offset[1],(255,255,255),tolerance=5): #incase pop up close
        click(654+offset[0],187+offset[1],delay=0.1)
    click_image("AreaIcon.png",confidence=0.7,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.top+rb_window.height),offset=(0,0))
    print("Pressed area icon")
    areas = {
        "Towers": (89,400),
        "Story": (714, 408),
        "Legend": (714, 408),
        "Raids": (340,400),
        "Challenges": (466,400),
        "Dungeons": (588,400),
        "Boss": (92,525),
        "Odyssey": (218,525),
        "Worldlines": (337, 524),
        "Winter": (342,525),
        "WorldDestroyer": (110, 249),
        "Rift": (465, 520)
    }

    stages = {
        1: (190,222),
        2: (190,272),
        3: (190, 325),
        4: (190, 373),
        5: (190, 422),
        6: (165, 447)
    }
    acts = {
        1: (311,216),
        2: (314,266),
        3: (314,315),
        4: (314,364),
        5: (314,412),
    }
    # Key pathing
    
    mouse = Controller()
    match area:
        case "Winter": # hi
            click_image("AreaIcon.png",confidence=0.9,grayscale=True,region=(10+offset[0], 125+offset[1], 207+offset[0], 499+offset[1]),offset=(0,0))
            time.sleep(2)
            click(591+offset[0],522+offset[1])# [(591, 522)]
            time.sleep(2)
            pydirectinput.keyDown("s")
            time.sleep(5.7)
            pydirectinput.keyUp("s")
            pydirectinput.press('e')
            winter_start =  [(181, 469), (350, 328), (405, 363), (80, 454)]
            for pos_c in winter_start:
                click(pos_c[0]+offset[0],pos_c[1]+offset[1])
                time.sleep(1)
        case "Odyssey":
            click_image("AreaIcon.png",confidence=0.9,grayscale=True,region=(10+offset[0], 125+offset[1], 207+offset[0], 499+offset[1]),offset=(0,0))
            time.sleep(2)
            click(areas.get(area)[0]+offset[0],areas.get(area)[1]+offset[1])
            time.sleep(2)
            pydirectinput.keyDown("w")
            time.sleep(0.2)
            pydirectinput.keyDown("shift")
            time.sleep(4)
            pydirectinput.keyUp("shift")
            pydirectinput.keyUp("w")
            
            # start
            pydirectinput.press("e")
            time.sleep(1)
            pydirectinput.press("q")
            time.sleep(1)
            pydirectinput.press("q")
            time.sleep(2)
            click(182+offset[0], 447+offset[1])
        case "Boss":
            #(201, 409)
            click_image("AreaIcon.png",confidence=0.9,grayscale=True,region=(10+offset[0], 125+offset[1], 207+offset[0], 499+offset[1]),offset=(0,0))
            time.sleep(2)
            click(areas.get(area)[0]+offset[0],areas.get(area)[1]+offset[1])
            time.sleep(2)
            pydirectinput.keyDown("w")
            time.sleep(1.8) # TRAVEL TIME
            pydirectinput.keyUp("w")
            pydirectinput.press('e')
            time.sleep(2)
            click(201+offset[0], 409+offset[1])
            time.sleep(2)
            click(70+offset[0], 487+offset[1])
        case "Rift":
            #(201, 409)
            click_image("AreaIcon.png",confidence=0.9,grayscale=True,region=(10+offset[0], 125+offset[1], 207+offset[0], 499+offset[1]),offset=(0,0))
            time.sleep(2)
            click(areas.get(area)[0]+offset[0],areas.get(area)[1]+offset[1])
            time.sleep(2)
            pydirectinput.keyDown("w")
            time.sleep(3) # TRAVEL TIME
            pydirectinput.keyUp("w")
            pydirectinput.keyDown("a")
            time.sleep(2)
            pydirectinput.keyUp("a")
            pydirectinput.keyDown("w")
            time.sleep(0.8) # TRAVEL TIME
            pydirectinput.keyUp("w")
            pydirectinput.keyDown("a")
            time.sleep(2)
            pydirectinput.keyUp("a")
            while not does_exist("PlayRift.png",confidence=0.9,grayscale=True,region=(offset[0],offset[1],offset[0]+816,offset[1]+638)):  
                pydirectinput.press('e')
                time.sleep(1)
            time.sleep(3)
            click_image("PlayRift.png",confidence=0.9,grayscale=True,offset=(0,0),region=(offset[0],offset[1],offset[0]+816,offset[1]+638))
        case "Story":
            # bc of sandobx
            act+=1
            area_click = areas.get(area)
            click_image("AreaIcon.png",confidence=0.9,grayscale=True,region=(10+offset[0], 125+offset[1], 207+offset[0], 499+offset[1]),offset=(0,0))
            time.sleep(2)
            click(area_click[0]+offset[0],area_click[1]+offset[1])
            time.sleep(2)
            pydirectinput.keyDown("d")
            time.sleep(0.2)
            pydirectinput.keyDown("shift")
            time.sleep(4)
            pydirectinput.keyUp("shift")
            pydirectinput.keyUp("d")
            click(create_match[0]+offset[0],create_match[1]+offset[1])
            if stage > 6:
                click(stages.get(1)[0]+offset[0],stages.get(1)[1]+offset[1])
                mouse.scroll(0,-10)
                stage-=6
            time.sleep(0.5)
            print(stage)
            click(stages.get(stage)[0]+offset[0],stages.get(stage)[1]+offset[1])
            if act > 3:
                click(acts.get(1)[0]+offset[0],acts.get(1)[1]+offset[1])
                mouse.scroll(0,-10)
                act-=3
            time.sleep(0.5)
            print(act)
            click(acts.get(act)[0]+offset[0],acts.get(act)[1]+offset[1])    
            time.sleep(1)
            for c in start_match:
                click(c[0]+offset[0],c[1]+offset[1])
                time.sleep(0.8)
            click_image("StartButton.png",confidence=0.9,grayscale=True,offset=(0,0))
        case "Legend":
            area_click = areas.get(area)
            click_image("AreaIcon.png",confidence=0.9,grayscale=True,region=(10+offset[0], 125+offset[1], 207+offset[0], 499+offset[1]),offset=(0,0))
            time.sleep(2)
            click(area_click[0]+offset[0],area_click[1]+offset[1])
            time.sleep(2)
            pydirectinput.keyDown("d")
            time.sleep(0.2)
            pydirectinput.keyDown("shift")
            time.sleep(4)
            pydirectinput.keyUp("shift")
            pydirectinput.keyUp("d")
            click(create_match[0]+offset[0],create_match[1]+offset[1])
            time.sleep(2)
            click(505+offset[0], 538+offset[1])
            time.sleep(1)
            if stage > 5:
                click(stages.get(1)[0]+offset[0],stages.get(1)[1]+offset[1])
                mouse.scroll(0,-10)
                stage-=5
            time.sleep(0.5)
            click(stages.get(stage)[0]+offset[0],stages.get(stage)[1]+offset[1]) 
            time.sleep(1)
            click(acts.get(act)[0]+offset[0],acts.get(act)[1]+offset[1])    
            time.sleep(1)
            for c in start_match:
                click(c[0]+offset[0],c[1]+offset[1])
                time.sleep(0.8)
            click_image("StartButton.png",confidence=0.9,grayscale=True,offset=(0,0))
            
        case "Raids":
            area_click = areas.get(area)
            click_image("AreaIcon.png",confidence=0.9,grayscale=True,region=(10+offset[0], 125+offset[1], 207+offset[0], 499+offset[1]),offset=(0,0))
            time.sleep(2)
            click(area_click[0]+offset[0],area_click[1]+offset[1])
            time.sleep(2)
            pydirectinput.keyDown("w")
            time.sleep(3)
            pydirectinput.keyUp("w")
            pydirectinput.keyDown("d")
            time.sleep(0.1)
            pydirectinput.keyDown("shift")
            time.sleep(3)
            pydirectinput.keyUp("d")
            pydirectinput.keyUp("shift")
            
            click(create_match[0]+offset[0],create_match[1]+offset[1])
            time.sleep(1)
            if stage > 5:
                click(stages.get(1)[0]+offset[0],stages.get(1)[1]+offset[1])
                mouse.scroll(0,-10)
                stage-=5
            time.sleep(0.5)
            click(stages.get(stage)[0]+offset[0],stages.get(stage)[1]+offset[1]) 
            time.sleep(1)
            print(act)
            click(acts.get(act)[0]+offset[0],acts.get(act)[1]+offset[1])    
            time.sleep(1)
            for c in start_match:
                click(c[0]+offset[0],c[1]+offset[1])
                time.sleep(0.8)
            click_image("StartButton.png",confidence=0.9,grayscale=True,offset=(0,0))
        case "Dungeons":
            area_click = areas.get(area)
            click_image("AreaIcon.png",confidence=0.9,grayscale=True,region=(10+offset[0], 125+offset[1], 207+offset[0], 499+offset[1]),offset=(0,0))
            time.sleep(2)
            click(area_click[0]+offset[0],area_click[1]+offset[1])
            time.sleep(2)
            pydirectinput.keyDown("w")
            pydirectinput.keyDown("d")
            time.sleep(0.1)
            pydirectinput.keyDown("shift")
            time.sleep(4)
            pydirectinput.keyUp("d")
            pydirectinput.keyUp("w")
            pydirectinput.keyUp("shift")
            
            click(create_match[0]+offset[0],create_match[1]+offset[1])
            time.sleep(1)
            if stage > 5:
                click(stages.get(1)[0]+offset[0],stages.get(1)[1]+offset[1])
                mouse.scroll(0,-10)
                stage-=5
            time.sleep(0.5)
            click(stages.get(stage)[0]+offset[0],stages.get(stage)[1]+offset[1]) 
            time.sleep(1)
            click(acts.get(act)[0]+offset[0],acts.get(act)[1]+offset[1])    
            time.sleep(1)
            for c in start_match:
                click(c[0]+offset[0],c[1]+offset[1])
                time.sleep(0.8)
            click_image("StartButton.png",confidence=0.9,grayscale=True,offset=(0,0))
        case "Worldlines":
            area_click = areas.get(area)
            click_image("AreaIcon.png",confidence=0.9,grayscale=True,region=(10+offset[0], 125+offset[1], 207+offset[0], 499+offset[1]),offset=(0,0))
            time.sleep(2)
            click(area_click[0]+offset[0],area_click[1]+offset[1])
            time.sleep(2)
            pydirectinput.keyDown("w")
            time.sleep(0.3)
            pydirectinput.keyUp("w")
            pydirectinput.press("e")
            time.sleep(2)
            click(627+offset[0], 466+offset[1])
        case "Towers":
            area_click = areas.get(area)
            click_image("AreaIcon.png",confidence=0.9,grayscale=True,region=(10+offset[0], 125+offset[1], 207+offset[0], 499+offset[1]),offset=(0,0))
            time.sleep(2)
            click(area_click[0]+offset[0],area_click[1]+offset[1])
            pydirectinput.keyDown("w")
            pydirectinput.keyDown("a")
            time.sleep(0.1)
            pydirectinput.keyDown("shift")
            time.sleep(4)
            pydirectinput.keyUp("d")
            pydirectinput.keyUp("a")
            pydirectinput.keyUp("shift")
            time.sleep(1)
            click(create_match[0]+offset[0],create_match[1]+offset[1])
            time.sleep(1)
            if stage > 5:
                click(stages.get(1)[0]+offset[0],stages.get(1)[1]+offset[1])
                mouse.scroll(0,-10)
                stage-=5
            time.sleep(0.5)
            click(stages.get(stage)[0]+offset[0],stages.get(stage)[1]+offset[1]) 
            click(acts.get(1)[0]+offset[0],acts.get(1)[1]+offset[1])    
            time.sleep(1)
            count = 0
            off = 0
            while act > 5:
                act-=4
                mouse.scroll(0,-2)  
                count+=1
                if count >3:
                    count = 0
                    off+=18
            click(acts.get(act)[0]+offset[0],acts.get(act)[1]+offset[1]-off)    
            time.sleep(1)
            for c in start_match:
                click(c[0]+offset[0],c[1]+offset[1])
                time.sleep(0.8)
            click_image("StartButton.png",confidence=0.9,grayscale=True,offset=(0,0))
            
            
        case "Challenges":
            modes = {
                1: (223,259),
                2: (226,328),
                3: (223,392)
            }
            types = {
                1: (637,293),
                2: (637,379),
                3: (637, 463)
            }
            scroll_offset = 0
            
            area_click = areas.get(area)
            click_image("AreaIcon.png",confidence=0.9,grayscale=True,region=(10+offset[0], 125+offset[1], 207+offset[0], 499+offset[1]),offset=(0,0))
            time.sleep(2)
            click(area_click[0]+offset[0],area_click[1]+offset[1])
            pydirectinput.keyDown("w")
            time.sleep(1.2)
            pydirectinput.keyUp("w")
            pydirectinput.keyDown("a")
            time.sleep(0.1)
            pydirectinput.keyDown("shift")
            time.sleep(3)
            pydirectinput.keyUp("a")
            pydirectinput.keyUp("shift")
            click(create_match[0]+offset[0],create_match[1]+offset[1])
            time.sleep(2)
            click(modes.get(stage)[0]+offset[0],modes.get(stage)[1]+offset[1])
            print("press")
            time.sleep(1)
            click(types.get(1)[0]-50+offset[0],types.get(1)[1]+offset[1])
            if act > 3:
                mouse.scroll(0,-3)
                scroll_offset = 40
                act-=3
            click(types.get(act)[0]+offset[0],types.get(act)[1]+offset[1]-scroll_offset)
            
            
        case "WorldDestroyer":
            click_image("AreaIcon.png",confidence=0.9,grayscale=True,region=(10+offset[0], 125+offset[1], 207+offset[0], 499+offset[1]),offset=(0,0))
            time.sleep(2)
            click(areas.get(area)[0]+offset[0],areas.get(area)[1]+offset[1])
            time.sleep(2)
            pydirectinput.keyDown("a")
            time.sleep(1)
            pydirectinput.keyUp("a")
            pydirectinput.keyDown("w")
            time.sleep(0.2)
            pydirectinput.keyDown("shift")
            time.sleep(1)
            pydirectinput.keyUp("shift")
            pydirectinput.keyUp("w")
            pydirectinput.press('e')
            time.sleep(1)
            pydirectinput.press("q")
            time.sleep(1)
            pydirectinput.press("q")
            time.sleep(2)
         
function_registry = {
    "press": {
        "type": [str, float],
        "func": press  
    },
    "get_wave": {
      "type": [[int,int]],
      "func": get_wave  
    },
    "does_exist": {
        "type": [str,float,bool,([int,int,int,int], type(None))],
        "func": does_exist  
    },
    "click_image": {
        "type": [str,float,bool,[int,int],([int,int,int,int], type(None))],
        "func": click_image  
    },
    "get_image_center": {
        "type": [str,float,bool,[int,int],([int,int,int,int], type(None))],
        "func": get_wave  
    },
    "print": {
        "type": [None],
        "func": print_arg        
    },
    "read_region": {
        "type": [[int,int,int,int],str,(int,type(None))],
        "func": read_region        
    },
    "return_to_lobby": {
        "type": [[int,int]],
        "func": return_to_lobby        
    },
    "wait_for_wave": {
        "type": [int, [int,int]],
        "func": wait_for_wave
    },
    "wait": {
        "type": [float],
        "func": wait        
    },
    "click": { 
        "type": [int,int,(int,type(None)),(bool,type(None)),(bool,type(None))],
        "func": click        
    },
    "ability":{
        "type": [[int,int],str,[int,int]],
        "func": use_ability
    },
    "rts":{
        "type": [[int,int]],
        "func": return_to_spawn
    },
    "place_unit":{
        "type": [int, [int,int], [int,int],(bool,type(None))],
        "func": place_unit
    },
    "select_unit":{
        "type": [[int,int], [int,int]],
        "func": select_unit
    },
    "sell_unit":{
        "type": [[int,int], [int,int]],
        "func": select_unit
    },
    "upg_unit":{
        "type": [str, [int,int], [int,int]],
        "func": upgrade_unit
    },
    
}

