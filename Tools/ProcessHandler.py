import json
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import time
import subprocess
import sys
import pygetwindow as gw
import Function_Dictionary as fd
import ctypes
import pyautogui
import pydirectinput
from threading import Thread
from threading import Event
import cv2
import numpy as np
from PIL import ImageGrab
from pynput.mouse import Controller
from datetime import datetime, timedelta, timezone
import psutil

def get_window(title: str) -> gw.Win32Window:
    '''
    Finds title within a string and returns window
    '''
    try:
        find_title = next(filter(lambda p: title in p, gw.getAllTitles()))
        
        match = gw.getWindowsWithTitle(find_title)[0]
        return match
    except Exception as e:
        print(f"Window not found: {e}")
        return None

def load_state():
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Info", "state.json")
    with open(json_path, 'r') as file:
        return json.load(file)
def load_pid():
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Info", "processpid.json")
    with open(json_path, 'r') as file:
        return json.load(file)
def update_pid(data):
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Info", "processpid.json")
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)
    
def load_aio_settings():
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Settings", "AIO_Settings.json")
    with open(json_path, 'r') as file:
        return json.load(file)
def load_json(json_path):
    with open(json_path, 'r') as file:
        return json.load(file)#processpid
def upd_json(json_path,data):
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)#processpid

global disconnect_checker_flag 
disconnect_checker_flag = Event()

def disconnect_checker(process, process_location, path: tuple[str,int,int] | None=None):
    rb_window = get_window("Roblox")
    while load_state()["running"]:
        if disconnect_checker_flag.is_set():
            return
        if fd.does_exist("Disconnected.png",confidence=0.9,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.top+rb_window.height)):
            print("Found Disconnect")
            try:
                process.terminate() # kill script
            except Exception as e:
                print(f"error {e}")
            print("called")
            pids = psutil.pids()
            for pid in pids:
                try:
                    if pid != os.getpid():
                        process = psutil.Process(pid)
                        if process.name().lower() == "python.exe":
                            print("Found 1")
                            if any(arg for arg in process.cmdline() if sys.executable == arg):
                                    print("found 2")
                                    process.terminate()
                                    print(f"Terminated {pid}")
                except Exception as e:
                    print(f"Error when killing subprocess: {e}")
            pids_j = load_pid()
            pids_j["pid"] = []
            update_pid(pids_j)
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
            subprocess.Popen([roblox_exe, f"roblox://placeId={16146832113}&linkCode={load_aio_settings()["Settings"]["Private_Server_Code"]}/"])
            print("Rejoining Roblox")
            time_out = 60
            while not fd.does_exist("IsInGame.png",confidence=0.9,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.top+rb_window.height)):
                if time_out < 0:
                    time_out = 60
                    if fd.does_exist("Disconnected.png",confidence=0.9,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.top+rb_window.height)):
                        subprocess.Popen([roblox_exe, f"roblox://placeId={16146832113}&linkCode={load_aio_settings()["Settings"]["Private_Server_Code"]}/"])
                time_out-=1
                time.sleep(1)
            time.sleep(15)
            offset = (rb_window.left,rb_window.top)
            if any([fd.does_exist("Leaderboard_Check.png",confidence=0.8,grayscale=True,region=(543+offset[0], 87+offset[1], 797+offset[0], 191+offset[1])), fd.does_exist("LB_Check2.png",confidence=0.8,grayscale=True,region=(543+offset[0], 87+offset[1], 797+offset[0], 191+offset[1]))]):
                pydirectinput.press("tab")
            time.sleep(1)
            fd.click(654+rb_window.left, 188+rb_window.top)
            if path is not None:
                fd.lobby_path(path[0],path[1],path[2])
            p =subprocess.Popen([sys.executable, "-u", process_location]) # restart, cant capture text tho
            pids = load_pid()
            pids["pid"] = []
            pids["pid"]+=[p.pid]
            update_pid(pids)
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
def worldlineshandler():

    rb_window = get_window("Roblox")
    offset = (rb_window.left,rb_window.top)
    img_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Resources")
    task_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Tasks")
    folders = ["Worldlines_Extra","Positioner"]
    if any([fd.does_exist("Leaderboard_Check.png",confidence=0.8,grayscale=True,region=(543+offset[0], 87+offset[1], 797+offset[0], 191+offset[1])), fd.does_exist("LB_Check2.png",confidence=0.8,grayscale=True,region=(543+offset[0], 87+offset[1], 797+offset[0], 191+offset[1]))]):
            pydirectinput.press("tab")
    if fd.does_exist("IsInGame.png",confidence=0.8,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.top+rb_window.height)):
        fd.lobby_path(area="Worldlines",stage=0,act=0)
    
    def return_to_spawn(offset: tuple[int,int]):
        click_pos = [(30, 605), (708, 322), (755, 149)]
        for pos in click_pos:
            click(pos[0]+offset[0], pos[1]+offset[1], delay=0.2)
            time.sleep(0.8)
    def restart_match(offset: tuple[int,int]):
        '''sybau'''
        pos = [(29, 605), (700, 288), (347, 363), (407, 355), (752, 150)]
        for p in pos:
            click(p[0]+offset[0], p[1]+offset[1], delay=0.1)
            if p ==(347, 363):
                time.sleep(2)
            time.sleep(1)
    regionArea = (0+offset[0], 0+offset[1], 355+offset[0], 288+offset[1])
    
    def load_wls():
        json_path =os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Settings", "Worldlines", "Worldlines.json")
        with open(json_path, 'r') as file:
            return json.load(file)   
    print("started worldlines")
    def get_map():
            print("Getting map")
            has_map = False
            while not has_map:
                return_to_spawn(offset)
                time.sleep(3)
                imgs = []
                for folder in folders:
                        for image in os.listdir(os.path.join(img_path, folder)):
                            template = cv2.imread(os.path.join(img_path, folder, image))
                            left, top, bottom, right = regionArea
                            img_o = ImageGrab.grab(bbox=(left, top, bottom,right))
                            img_cv2 = cv2.cvtColor(np.array(img_o),cv2.COLOR_RGB2BGR)
                            img = img_cv2
                            template = cv2.cvtColor(template, cv2.COLOR_RGB2BGR)
                            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                            res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
                            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                            if max_val > 0.7:
                                imgs+=[[max_val,image]]
                map = ""
                if len(imgs) > 1:
                    map = max(imgs)[1]
                    has_map = True
                else:
                    if len(imgs) == 1:
                        map = imgs[0][1]
                        has_map = True
                if has_map:
                    print("Got map")
                    if os.path.exists(os.path.join(img_path, "Worldlines_Extra", map)):
                        map = map.replace(f"_{map.split("_")[-1]}","_0.py")
                    else:
                        map = map.replace(".png","_0.py")
                    return map
                time.sleep(1)

    def get_path_of_pyfile(pyf):
            for folder in os.listdir(task_path):
                if os.path.exists(os.path.join(task_path, folder, pyf)):
                    return os.path.join(task_path, folder, pyf)
    Mouse = Controller()
    def equip_team(team_number):
        pos = [(408, 511), (402, 227), (403, 284)] # open menu
        close = (662, 191)
        for i in pos:
            click(i[0]+offset[0],i[1]+offset[1])
            time.sleep(1)
        match team_number:
            case 1:
                Mouse.scroll(0,-2)
                time.sleep(1)
                click(347+offset[0], 383+offset[1])
                time.sleep(3)# clicked equip team prompt
                click(408+offset[0], 357+offset[1])
                Mouse.scroll(0,10)
            case 2:
                Mouse.scroll(0,-6)
                time.sleep(1)
                click(347+offset[0], 383+offset[1])
                time.sleep(3)# clicked equip team prompt
                click(408+offset[0], 357+offset[1])
                Mouse.scroll(0,10)
            case 3:
                Mouse.scroll(0,-10)
                time.sleep(1)
                click(350+offset[0], 366+offset[1])
                time.sleep(3)# clicked equip team prompt
                click(408+offset[0], 357+offset[1])
                Mouse.scroll(0,10)
            case 4:
                Mouse.scroll(0,-14)
                time.sleep(1)
                click(350+offset[0], 366+offset[1])
                time.sleep(3)# clicked equip team prompt
                click(408+offset[0], 357+offset[1])
                Mouse.scroll(0,10)
            case 5:
                Mouse.scroll(0,-17)
                time.sleep(1)
                click(350+offset[0], 451+offset[1])
                time.sleep(3)# clicked equip team prompt
                click(408+offset[0], 357+offset[1])
                Mouse.scroll(0,10)
            case 6:
                Mouse.scroll(0,-21)
                time.sleep(1)
                click(350+offset[0], 451+offset[1])
                time.sleep(3)# clicked equip team prompt
                click(408+offset[0], 357+offset[1])
                Mouse.scroll(0,10)
            case 7:
                Mouse.scroll(0,-25)
                time.sleep(1)
                click(350+offset[0], 427+offset[1])
                time.sleep(3)# clicked equip team prompt
                click(408+offset[0], 357+offset[1])
                Mouse.scroll(0,10)
            case 8:
                Mouse.scroll(0,30)
                time.sleep(1)
                click(350+offset[0], 427+offset[1])
                time.sleep(3)# clicked equip team prompt
                click(408+offset[0], 357+offset[1])
                Mouse.scroll(0,10)
        time.sleep(1)
        click(close[0]+offset[0],close[1]+offset[1])
        time.sleep(0.5)
        click(close[0]+offset[0]-20,close[1]+offset[1])# clos
    Settings = load_wls()
    Mouse = Controller()
    p_team = Settings["Base_Team"]
    while True:
        while not load_state()["running"]:
            time.sleep(0.5)
        while not fd.does_exist("In_Game.png",grayscale=True,confidence=0.8,region=(643+offset[0], 306+offset[1], 806+offset[0], 375+offset[1])):
            time.sleep(1)
        if any([fd.does_exist("Leaderboard_Check.png",confidence=0.8,grayscale=True,region=(543+offset[0], 87+offset[1], 797+offset[0], 191+offset[1])), fd.does_exist("LB_Check2.png",confidence=0.8,grayscale=True,region=(543+offset[0], 87+offset[1], 797+offset[0], 191+offset[1]))]):
                pydirectinput.press("tab")
        time.sleep(1)
        click(409+offset[0], 309+offset[1])
        if True:
            pydirectinput.keyDown("i")
            time.sleep(2)
            pydirectinput.keyUp("i")
            ctypes.windll.user32.mouse_event(0x0001, 0, 10000, 0, 0)
            time.sleep(1)
            pydirectinput.keyDown("o")
            time.sleep(2)
            pydirectinput.keyUp("o")
        map = get_map()
        path = get_path_of_pyfile(map)
        print(map, path)
        click(475+offset[0], 124+offset[1])
        time.sleep(6)
        restart_match(offset)
        if p_team != Settings["Base_Team"]:
            equip_team(int(Settings["Base_Team"]))
            print("Equiping base team")
        
        for set_teams in Settings["Team_For_Map"].keys():
            if set_teams in map:
                p_team = int(Settings["Team_For_Map"][set_teams])
                equip_team(int(Settings["Team_For_Map"][set_teams]))
                print("Equiping map team")
        pydirectinput.press('c')
        time.sleep(1)
        settings_path = path.replace("Tasks","Settings").replace("_0.py", ".json")
        is_inf = False
        if fd.does_exist("CheckForInf.png",grayscale=True,confidence=0.95,region=(525+offset[0], 94+offset[1], 755+offset[0], 153+offset[1])):
            print("Found inf tsuyik")
            pydirectinput.press('c')
            p_team = Settings["Infinite_Tsukuyomi_Team"]
            equip_team(int(Settings["Infinite_Tsukuyomi_Team"]))
            if os.path.exists(settings_path):
                print("Using offset")
                js = load_json(settings_path)
                num = int(js["selected"])+Settings["Infinite_Tsukuyomi_KeyOffset"]
                js["selected"] = str(num)
                upd_json(settings_path, js)
                is_inf = True
        else:
            pydirectinput.press('c')
        process = subprocess.Popen([sys.executable, "-u", path, "--worldlines"])
        pids = load_pid()
        pids["pid"] = []
        print(pids)
        pids["pid"]+=[process.pid]
        update_pid(pids)
        print("Waiting for stage to complete")
        process.wait()
        print("Stage is done, next stage")
        if is_inf:
            print("undo offset")
            js = load_json(settings_path)
            num = int(js["selected"])-Settings["Infinite_Tsukuyomi_KeyOffset"]
            js["selected"] = str(num)
            upd_json(settings_path, js)
        while fd.does_exist("In_Game.png",grayscale=True,confidence=0.8,region=(643+offset[0], 306+offset[1], 806+offset[0], 375+offset[1])):
            time.sleep(1)
        
def challenge_handler():
    rb_window = get_window("Roblox")
    offset = (rb_window.left,rb_window.top)
    img_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Resources")
    task_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Tasks")
    folders = ["Worldlines_Extra","Positioner"]
    def get_lobby_arg_from_pyfile(pyfile):
        config_path = pyfile.replace("Tasks","Settings").replace("_0.py",".json")
        print(config_path)
        area_dict = {
            "Challenges": "Challenges",
            "Story":"Story",
            "Dungeons": "Dungeons",
            "Event": "Event",
            "Raid": "Raids",
            "Worldlines": "Worldlines",
            "Odyssey": "Odyssey",
            "Boss_Rush": "Boss",
            "Winter": "Winter",
            "WorldDestroyer": "WorldDestroyer" ,
            "Legend_Stages":"Legend"
        }
        stage_dicts = {
            "Story": 
                {
                "Planet_Namek": 1,
                "Sand_Village":2,
                "Double_Dungeon":3,
                "Shibuya_Station":4,
                "Underground_Church":5,
                "Spirit_Society":6,
                "Martial Island":7,
                "Edge_Of_Heaven":8,
                "Lebero_Raid":9,
                "Hill_Of_Swords":10,
                "Frozen_Port":11
                },
            "Legend_Stages":{
                "Sand_Village":1,
                "Double_Dungeon":2,
                "Shibuya_Aftermath":3,
                "Golden_Castle":4,
                "Kuinshi_Palace":5,
                "Land_Of_The_Gods":6,
                "Shining_Castle":7,
                "Crystal_Chapel":8,
                "Burning_Spirit_Tree":9,
                "Imprisoned_Island":10,
            },
            "Dungeons": {
                "Ant_Island": 1,
                "Frozen_Volcano":2
            },
            "Raid":{
                "Spider_Forest":1,
                "SBR_Raid":2,
                "Ruined_City":3,
                "HAPPY_Factory":4
            },
            "Challenges":{
                "Weekly":1,
                "Daily":2,
                "HalfHour":3
            }
            
        }
        area = ""
        stage = 0
        if pyfile.split("\\")[-1] == "Winter_0.py":
            area = "Winter"
            stage = 0
            act = 0 
        else:
            act = int(load_json(config_path)["act"])
            for key in area_dict.keys():
                if key in config_path:
                    area = area_dict[key]
                    print(area)
                    for stage in stage_dicts[key].keys():
                        if stage in config_path:
                            stage = stage_dicts[key][stage]
                            break
            print(stage)
        return (area,stage,act)
    
    def load_challenge():
        json_path =os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Settings", "Challenges", "Challenge.json")
        with open(json_path, 'r') as file:
            return json.load(file)  
    Challenge_Settings = load_challenge()
    p_team = Challenge_Settings["Base_Team"]
    def get_map():
            regionArea = (0+offset[0], 0+offset[1], 355+offset[0], 288+offset[1])
            print("Getting map")
            has_map = False
            while not has_map:
                click(409+offset[0], 309+offset[1])
                fd.return_to_spawn(offset)
                time.sleep(3)
                imgs = []
                for folder in folders:
                        for image in os.listdir(os.path.join(img_path, folder)):
                            template = cv2.imread(os.path.join(img_path, folder, image))
                            left, top, bottom, right = regionArea
                            img_o = ImageGrab.grab(bbox=(left, top, bottom,right))
                            img_cv2 = cv2.cvtColor(np.array(img_o),cv2.COLOR_RGB2BGR)
                            img = img_cv2
                            template = cv2.cvtColor(template, cv2.COLOR_RGB2BGR)
                            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                            res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
                            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                            if max_val > 0.7:
                                imgs+=[[max_val,image]]
                map = ""
                if len(imgs) > 1:
                    map = max(imgs)[1]
                    has_map = True
                else:
                    if len(imgs) == 1:
                        map = imgs[0][1]
                        has_map = True
                if has_map:
                    print("Got map")
                    if os.path.exists(os.path.join(img_path, "Worldlines_Extra", map)):
                        map = map.replace(f"_{map.split("_")[-1]}","_0.py")
                    else:
                        map = map.replace(".png","_0.py")
                    return map
                time.sleep(1)
    def get_path_of_pyfile(pyf):
            for folder in os.listdir(task_path):
                if os.path.exists(os.path.join(task_path, folder, pyf)):
                    return os.path.join(task_path, folder, pyf)
    def equip_team(team_number):
        Mouse = Controller()
        pos = [(408, 511), (402, 227), (403, 284)] # open menu
        close = (662, 191)
        for i in pos:
            click(i[0]+offset[0],i[1]+offset[1])
            time.sleep(1)
        match team_number:
            case 1:
                Mouse.scroll(0,-2)
                time.sleep(1)
                click(347+offset[0], 383+offset[1])
                time.sleep(3)# clicked equip team prompt
                click(408+offset[0], 357+offset[1])
                Mouse.scroll(0,10)
            case 2:
                Mouse.scroll(0,-6)
                time.sleep(1)
                click(347+offset[0], 383+offset[1])
                time.sleep(3)# clicked equip team prompt
                click(408+offset[0], 357+offset[1])
                Mouse.scroll(0,10)
            case 3:
                Mouse.scroll(0,-10)
                time.sleep(1)
                click(350+offset[0], 366+offset[1])
                time.sleep(3)# clicked equip team prompt
                click(408+offset[0], 357+offset[1])
                Mouse.scroll(0,10)
            case 4:
                Mouse.scroll(0,-14)
                time.sleep(1)
                click(350+offset[0], 366+offset[1])
                time.sleep(3)# clicked equip team prompt
                click(408+offset[0], 357+offset[1])
                Mouse.scroll(0,10)
            case 5:
                Mouse.scroll(0,-17)
                time.sleep(1)
                click(350+offset[0], 451+offset[1])
                time.sleep(3)# clicked equip team prompt
                click(408+offset[0], 357+offset[1])
                Mouse.scroll(0,10)
            case 6:
                Mouse.scroll(0,-21)
                time.sleep(1)
                click(350+offset[0], 451+offset[1])
                time.sleep(3)# clicked equip team prompt
                click(408+offset[0], 357+offset[1])
                Mouse.scroll(0,10)
            case 7:
                Mouse.scroll(0,-25)
                time.sleep(1)
                click(350+offset[0], 427+offset[1])
                time.sleep(3)# clicked equip team prompt
                click(408+offset[0], 357+offset[1])
                Mouse.scroll(0,10)
            case 8:
                Mouse.scroll(0,30)
                time.sleep(1)
                click(350+offset[0], 427+offset[1])
                time.sleep(3)# clicked equip team prompt
                click(408+offset[0], 357+offset[1])
                Mouse.scroll(0,10)
        time.sleep(1)
        click(close[0]+offset[0],close[1]+offset[1])
        time.sleep(0.5)
        click(close[0]+offset[0]-20,close[1]+offset[1])# clos
    
    def play_game():
        nonlocal p_team
        while not load_state()["running"]:
            time.sleep(0.5)
        fd.wait_for_spawn(offset,0)
        time.sleep(1)
        click(409+offset[0], 309+offset[1])
        if True:
            pydirectinput.keyDown("i")
            time.sleep(2)
            pydirectinput.keyUp("i")
            ctypes.windll.user32.mouse_event(0x0001, 0, 100000, 0, 0)
            time.sleep(1)
            pydirectinput.keyDown("o")
            time.sleep(2)
            pydirectinput.keyUp("o")
        map = get_map()
        path = get_path_of_pyfile(map)
        print(map, path)
        click(475+offset[0], 124+offset[1])
        time.sleep(6)
        fd.restart_match(offset)
        if p_team != Challenge_Settings["Base_Team"]:
            equip_team(int(Challenge_Settings["Base_Team"]))
            print("Equiping base team")
        
        for set_teams in Challenge_Settings["Team_For_Map"].keys():
            if set_teams in map:
                p_team = int(Challenge_Settings["Team_For_Map"][set_teams])
                equip_team(int(Challenge_Settings["Team_For_Map"][set_teams]))
                print("Equiping map team")
        time.sleep(1)
        process = subprocess.Popen([sys.executable, "-u", path, "--return"])
        pids = load_pid()
        pids["pid"] = []
        print(pids)
        pids["pid"]+=[process.pid]
        update_pid(pids)
        print("Waiting for stage to complete")
        process.wait()
        print("Stage is done, next stage")
    
    Last_Challenge = None
    Last_Daily = None
    Challenge_Threshold = timedelta(minutes=30)  # noqa: F841
    Half_hour_done = False
    Daily_done = False
    Weekly_done = False
    Half_Hour_Index = 0
    time_daily_thresh = timedelta(minutes=30)  # noqa: F841
    game_played = False
    print("Starting challenges")
    while True: # main loop
        
        print("Starting")
        while not fd.does_exist("IsInGame.png",confidence=0.9,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.top+rb_window.height)):
            time.sleep(1)
        time.sleep(8)
        if pyautogui.pixelMatchesColor(654+offset[0],187+offset[1],(255,255,255),tolerance=5): #incase pop up close
            fd.click(654+offset[0],187+offset[1],delay=0.1)

        if not Weekly_done:
            fd.lobby_path("Challenges",1,1)
            time.sleep(3)
            if fd.does_exist("Alert.png",confidence=0.9,grayscale=True,region=(rb_window.left, rb_window.top, rb_window.left+rb_window.width,rb_window.top+rb_window.height)):
                print("Weekly done")
                Weekly_done = True
                pos  = [(408, 366), (407, 134)]
                for i in pos:
                    fd.click(i[0]+offset[0],i[1]+offset[1])
                    time.sleep(0.9)
            else:
                while not fd.does_exist("StartButton.png",confidence=0.9,grayscale=True,region=(rb_window.left, rb_window.top, rb_window.left+rb_window.width,rb_window.top+rb_window.height)):
                    time.sleep(0.5)
                fd.click_image("StartButton.png",confidence=0.9,offset=(0,0),grayscale=True,region=(rb_window.left, rb_window.top, rb_window.left+rb_window.width,rb_window.top+rb_window.height))
                play_game()
                game_played = True
            
        if game_played:
            while not fd.does_exist("IsInGame.png",confidence=0.9,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.top+rb_window.height)):
                time.sleep(1)
            time.sleep(8)
            if pyautogui.pixelMatchesColor(654+offset[0],187+offset[1],(255,255,255),tolerance=5): #incase pop up close
                fd.click(654+offset[0],187+offset[1],delay=0.1)
            game_played = False
        
        if not Daily_done:
            fd.lobby_path("Challenges",2,1)
            time.sleep(3)
            if fd.does_exist("Alert.png",confidence=0.9,grayscale=True,region=(rb_window.left, rb_window.top, rb_window.left+rb_window.width,rb_window.top+rb_window.height)):
                print("Daily done")
                Daily_done = True
                Last_Daily = datetime.now(timezone.utc).strftime("%D")
                for i in pos:
                    fd.click(i[0]+offset[0],i[1]+offset[1])
                    time.sleep(0.9)
            else:
                while not fd.does_exist("StartButton.png",confidence=0.9,grayscale=True,region=(rb_window.left, rb_window.top, rb_window.left+rb_window.width,rb_window.top+rb_window.height)):
                    time.sleep(0.5)
                fd.click_image("StartButton.png",confidence=0.9,grayscale=True,offset=(0,0),region=(rb_window.left, rb_window.top, rb_window.left+rb_window.width,rb_window.top+rb_window.height))
                play_game()
                Last_Daily = datetime.now(timezone.utc).strftime("%D")
                game_played = True
                pass
            
        if game_played:
            while not fd.does_exist("IsInGame.png",confidence=0.9,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.top+rb_window.height)):
                time.sleep(1)
            time.sleep(8)
            if pyautogui.pixelMatchesColor(654+offset[0],187+offset[1],(255,255,255),tolerance=5): #incase pop up close
                fd.click(654+offset[0],187+offset[1],delay=0.1)
            game_played = False
            
        if not Half_hour_done:
            Half_hour_done = True
            fd.lobby_path("Challenges",3, Challenge_Settings["30m_Challenge"][Half_Hour_Index])
            time.sleep(3)
            if fd.does_exist("Alert.png",confidence=0.9,grayscale=True,region=(rb_window.left, rb_window.top, rb_window.left+rb_window.width,rb_window.top+rb_window.height)):
                Half_hour_done = True
                Half_Hour_Index+=1
                for i in pos:
                    fd.click(i[0]+offset[0],i[1]+offset[1])
                    time.sleep(0.9)
                Last_Challenge = int(str(datetime.now()).split(":")[1])
            else:
                while not fd.does_exist("StartButton.png",confidence=0.9,grayscale=True,region=(rb_window.left, rb_window.top, rb_window.left+rb_window.width,rb_window.top+rb_window.height)):
                    time.sleep(0.5)
                fd.click_image("StartButton.png",confidence=0.9,grayscale=True,offset=(0,0),region=(rb_window.left, rb_window.top, rb_window.left+rb_window.width,rb_window.top+rb_window.height))
                play_game()
                Last_Challenge = int(str(datetime.now()).split(":")[1])
                game_played = True
                
        if game_played:
            while not fd.does_exist("IsInGame.png",confidence=0.9,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.top+rb_window.height)):
                time.sleep(1)
            time.sleep(8)
            if pyautogui.pixelMatchesColor(654+offset[0],187+offset[1],(255,255,255),tolerance=5): #incase pop up close
                fd.click(654+offset[0],187+offset[1],delay=0.1)
            game_played = False
        downtime = True
        downtime_task = Challenge_Settings["Down_Time_Task"]
        process_running = None
        if Last_Challenge >= 30:
            t_need = 0
        else:
            t_need = 30
        while downtime:
            if process_running is None:
                pyfile = get_path_of_pyfile(downtime_task+"_0.py")
                print(pyfile)
                args = get_lobby_arg_from_pyfile(pyfile)
                print(args)
                fd.lobby_path(*args)
                fd.wait_for_spawn(offset,0)
                if Challenge_Settings["Down_Time_Team"] != 0:
                    equip_team(Challenge_Settings["Down_Time_Team"])
                    p_team = Challenge_Settings["Down_Time_Team"]
                process = subprocess.Popen([sys.executable, "-u", pyfile],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
                pids = load_pid()
                print(pids)
                pids["pid"]+=[process.pid]
                update_pid(pids)
                process_running = process
            else:
                cur_utc = [int(time) for time in datetime.now(timezone.utc).strftime("%H:%M").split(":")]
                reset_utc = [00,00]
                if (cur_utc[0] == reset_utc[0]):
                    if cur_utc[1] < 20 and Last_Daily != datetime.now(timezone.utc).strftime("%D"):
                        Daily_done = False
                if int(str(datetime.now()).split(":")[1]) == t_need:
                    Half_hour_done = False
                    downtime = False
                    while not fd.does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
                        time.sleep(0.5)
                    process_running.terminate()
                    pids = load_pid()
                    print(pids)
                    pids["pid"] = []
                    update_pid(pids)
                    fd.reconnect()
            time.sleep(3)
        time.sleep(1)

def run_task(pyfile):
    global disconnect_checker_flag
    disconnect_checker_flag.set()
    time.sleep(3)
    disconnect_checker_flag.clear()
    if "Odyssey_0.py" in pyfile:
        process = subprocess.Popen([sys.executable, "-u", pyfile],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        pids = load_pid()
        print(pids)
        pids["pid"]+=[process.pid]
        update_pid(pids)
        Thread(target=disconnect_checker, args=[process, pyfile],daemon=True).start()
        return process
    if "Challenge_0.py" in pyfile:
        Thread(target=challenge_handler).start()
        return
    print(f"Prompted to run task {pyfile}")
    if "Worldlines_0.py" in pyfile:
        Thread(target=worldlineshandler).start()
        return
    rb_window = get_window("Roblox")
    config_path = pyfile.replace("Tasks","Settings").replace("_0.py",".json")
    if "LDouble_Dungeon" in config_path:
        config_path.replace("LDouble_Dungeon","Double_Dungeon") 
    if "LSand_Village" in config_path:
        config_path.replace("LSand_Village", "Sand_Village")
    print(f"{config_path}: {os.path.exists(config_path)}")
    #pathing = fd.lobby_path
    #possible_tasks = ["fuck you"]
    #"C:\Users\Loxer\Documents\LA_AIO\Resources\IsInGame.png"
    area_dict = {
        "Challenges": "Challenges",
        "Story":"Story",
        "Dungeons": "Dungeons",
        "Event": "Event",
        "Raid": "Raids",
        "Worldlines": "Worldlines",
        "Odyssey": "Odyssey",
        "Boss_Rush": "Boss",
        "Winter": "Winter",
        "Whitebeard": "WorldDestroyer" ,
        "Legend_Stages":"Legend",
        "Rift": "Rift"
    }
    stage_dicts = {
        "Story": 
            {
            "Planet_Namek": 1,
            "Sand_Village":2,
            "Double_Dungeon":3,
            "Shibuya_Station":4,
            "Underground_Church":5,
            "Spirit_Society":6,
            "Martial Island":7,
            "Edge_Of_Heaven":8,
            "Lebero_Raid":9,
            "Hill_Of_Swords":10,
            "Frozen_Port":11,
            "Downtown_Tokyo":12
            },
        "Legend_Stages":{
            "Sand_Village":1,
            "Double_Dungeon":2,
            "Shibuya_Aftermath":3,
            "Golden_Castle":4,
            "Kuinshi_Palace":5,
            "Land_Of_The_Gods":6,
            "Shining_Castle":7,
            "Crystal_Chapel":8,
            "Burning_Spirit_Tree":9,
            "Imprisoned_Island":10,
            "Tokyo_Railway":11
        },
        "Dungeons": {
            "Ant_Island": 1,
            "Frozen_Volcano":2
        },
        "Raid":{
            "Spider_Forest":1,
            "SBR_Raid":2,
            "Ruined_City":3,
            "HAPPY_Factory":4
        },
        "Challenges":{
            "Weekly":1,
            "Daily":2,
            "HalfHour":3
        },
        
        
        
    }
    area = ""
    stage = 0
    if pyfile.split("\\")[-1] == "Winter_0.py":
        area = "Winter"
        stage = 0
        act = 0 
    elif pyfile.split("\\")[-1] == "Whitebeard_Event_0.py":
        area = "WorldDestroyer"
        stage = 0
        act = 0 
    else:
        act = int(load_json(config_path)["act"])
        for key in area_dict.keys():
            if key in config_path:
                area = area_dict[key]
                if area != "Boss" and  area!="Rift" :
                    for stage in stage_dicts[key].keys():
                        if stage in config_path:
                            stage = stage_dicts[key][stage]
                            break
                    break
                else:
                    stage = 0
                    act = 0
        print(area,stage,act)
    pathed_lobby = False
    offset = (rb_window.left,rb_window.top)
    if fd.does_exist("Leaderboard_Check.png",confidence=0.8,grayscale=True,region=(633+offset[0], 99+offset[1], 669+offset[0], 123+offset[1])):
        pydirectinput.press("tab")
    if fd.does_exist("IsInGame.png",confidence=0.8,grayscale=True,region=(rb_window.left,rb_window.top,rb_window.left+rb_window.width,rb_window.top+rb_window.height)):
        print("In lobby, pathing.")
        fd.lobby_path(area=area,stage=stage,act=int(act))
        pathed_lobby = True
        print(area, stage, act)
    else:
        print("In game, no lobby path")
    if load_aio_settings()["Click_Chat"]:
        print("Closing chat...")
        fd.wait_for_spawn((rb_window.left,rb_window.top),0)
        if any([fd.does_exist("Leaderboard_Check.png",confidence=0.8,grayscale=True,region=(543+offset[0], 87+offset[1], 797+offset[0], 191+offset[1])), fd.does_exist("LB_Check2.png",confidence=0.8,grayscale=True,region=(543+offset[0], 87+offset[1], 797+offset[0], 191+offset[1]))]):
            pydirectinput.press("tab")
        if not load_aio_settings()["VC_CHAT"]:
            fd.click(145+rb_window.left, 64+rb_window.top,delay=0.4)
            if pathed_lobby:
                fd.click(145+rb_window.left, 64+rb_window.top,delay=0.4)
        else:
            fd.click(202+rb_window.left, 64+rb_window.top,delay=0.4)
            if pathed_lobby:
                fd.click(202+rb_window.left, 64+rb_window.top,delay=0.4)
        process = subprocess.Popen([sys.executable, "-u", pyfile],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
    else:
        fd.wait_for_spawn((rb_window.left,rb_window.top),0)
        if any([fd.does_exist("Leaderboard_Check.png",confidence=0.8,grayscale=True,region=(543+offset[0], 87+offset[1], 797+offset[0], 191+offset[1])), fd.does_exist("LB_Check2.png",confidence=0.8,grayscale=True,region=(543+offset[0], 87+offset[1], 797+offset[0], 191+offset[1]))]):
            pydirectinput.press("tab")
    pids = load_pid()
    print(pids)
    pids["pid"]+=[process.pid]
    update_pid(pids)
    Thread(target=disconnect_checker, args=[process, pyfile,[area,stage,act]],daemon=True).start()
    print("Started process and disconnect checker.")
    return process

