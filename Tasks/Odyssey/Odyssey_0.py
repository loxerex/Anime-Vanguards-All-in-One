import os
import sys
import time
import pydirectinput
import pyautogui
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Tools import Function_Dictionary as fd
from Tools import winTools as wt
from threading import Thread
rb_window = wt.get_window("Roblox")
offset = (rb_window.left, rb_window.top)

skip_wave = (300,465)
auto_play = (739,456)
return_to_lobby = (184, 470)
def load_state():
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"Info", "state.json")
    with open(json_path, 'r') as file:
        return json.load(file)
def update_state(data):
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"Info", "state.json")
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)

def load_aio_settings():
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"Settings", "AIO_Settings.json")
    with open(json_path, 'r') as file:
        return json.load(file)
def oddysey_path():
    is_pathed = False
    while not is_pathed:
        while not fd.does_exist("IsInGame.png",confidence=0.9,grayscale=True,region=(15+offset[0],133+offset[1],204+offset[0],590+offset[1])):
            while not load_state()["running"]:
                        time.sleep(0.5)
            if pyautogui.pixelMatchesColor(654+offset[0],187+offset[1],(255,255,255),tolerance=5): #incase pop up close
                fd.click(654+offset[0],187+offset[1],delay=0.1)
            time.sleep(0.5)
        time.sleep(5) # Delay for loaded in
        while not fd.does_exist("AreaIcon.png",confidence=0.9,grayscale=True,region=(15+offset[0],133+offset[1],204+offset[0],590+offset[1])): # just wait for lobby
            if pyautogui.pixelMatchesColor(654+offset[0],187+offset[1],(255,255,255),tolerance=5): #incase pop up close
                fd.click(654+offset[0],187+offset[1],delay=0.1)
            time.sleep(0.5)
        if pyautogui.pixelMatchesColor(654+offset[0],187+offset[1],(255,255,255),tolerance=5): #incase pop up close
            fd.click(654+offset[0],187+offset[1],delay=0.1)
        fd.click_image("AreaIcon.png",confidence=0.9,grayscale=True,region=(10+offset[0], 125+offset[1], 207+offset[0], 499+offset[1]),offset=(0,0))
        time.sleep(0.5)
        if pyautogui.pixelMatchesColor(654+offset[0],187+offset[1],(255,255,255),tolerance=5): #incase pop up close
            fd.click(654+offset[0],187+offset[1],delay=0.1)
        fd.click(222+offset[0], 523+offset[1],delay=0.2)
        if pyautogui.pixelMatchesColor(654+offset[0],187+offset[1],(255,255,255),tolerance=5): #incase pop up close
            fd.click(654+offset[0],187+offset[1],delay=0.1)
        while not load_state()["running"]:
                        time.sleep(0.5)
        time.sleep(0.5)
        pydirectinput.keyDown('w')
        time.sleep(0.5)
        pydirectinput.keyDown("shift")
        time.sleep(3)
        pydirectinput.keyUp('w')
        pydirectinput.keyUp("shift")
        pydirectinput.press('e')
        pydirectinput.press('q')
        pydirectinput.press('q')
        pydirectinput.press('q')
        time.sleep(2)
        if fd.does_exist("Odyssey\\OdysseyMenu.png",confidence=0.9,grayscale=True,region=(157+offset[0],108+offset[1],360+offset[0],192+offset[1])): 
            print("Pathed")
            fd.click(307+offset[0], 454+offset[1],delay=0.2)
            return
        else:
            print("retrying path")
            fd.click(767+offset[0], 112+offset[1],delay=0.2)
        time.sleep(2)

def wait_for_spawn(offset: tuple[int,int]):
    region = (442+offset[0], 109+offset[1], 506+offset[0], 143+offset[1])
    while not fd.does_exist("VoteStart.png",confidence=0.9,grayscale=True,region=region):
        if fd.does_exist("Odyssey\\Autoplay.png", confidence=0.9, grayscale=True,region=(631+offset[0], 366+offset[1], 805+offset[0], 472+offset[1]))or fd.does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or fd.does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])):
            break
        time.sleep(0.5)
        
    return
def main():
    print("Starting odyssey")
    while True:
        if any([fd.does_exist("Leaderboard_Check.png",confidence=0.8,grayscale=True,region=(543+offset[0], 87+offset[1], 797+offset[0], 191+offset[1])), fd.does_exist("LB_Check2.png",confidence=0.8,grayscale=True,region=(543+offset[0], 87+offset[1], 797+offset[0], 191+offset[1]))]):
            pydirectinput.press("tab")
        oddysey_path()
        
        wait_for_spawn(offset)
        if load_aio_settings()["Click_Chat"]:
            if not load_aio_settings()["VC_CHAT"]:
                fd.click(145+rb_window.left, 64+rb_window.top,delay=0.4)
                fd.click(145+rb_window.left, 64+rb_window.top,delay=0.4)
            else:
                fd.click(202+rb_window.left, 64+rb_window.top,delay=0.4)
                fd.click(202+rb_window.left, 64+rb_window.top,delay=0.4)
        if any([fd.does_exist("Leaderboard_Check.png",confidence=0.8,grayscale=True,region=(543+offset[0], 87+offset[1], 797+offset[0], 191+offset[1])), fd.does_exist("LB_Check2.png",confidence=0.8,grayscale=True,region=(543+offset[0], 87+offset[1], 797+offset[0], 191+offset[1]))]):
            pydirectinput.press("tab")
        for match in range(4):
            auto_play_pressed = False
            print(f"Starting match {match+1}")
            while not load_state()["running"]:
                time.sleep(0.5)
            wait_for_spawn(offset)
            region = (442+offset[0], 109+offset[1], 506+offset[0], 143+offset[1])
            while fd.does_exist("VoteStart.png",confidence=0.9,grayscale=True,region=region):
                fd.start(offset)
                time.sleep(0.3)
            fd.click(auto_play[0]+offset[0],auto_play[1]+offset[1])
            while fd.get_wave(offset) < 15:
                while not load_state()["running"]:
                    time.sleep(0.5)
                if fd.does_exist("VoteStart.png",confidence=0.9,grayscale=True,region=region):
                    fd.start(offset)
                    time.sleep(0.3)
                if fd.does_exist("Odyssey\\Intensity.png",confidence=0.9,grayscale=True,region=(613+offset[0], 213+offset[1], 782+offset[0], 348+offset[1])):
                    break
                for _ in range(15):
                    time.sleep(0.05)
                    Thread(target=fd.click, args=[skip_wave[0]+offset[0],skip_wave[1]+offset[1]], kwargs={"delay": 0.05}).start()
                time.sleep(0.5)
            print("Waiting for intensity card")
            while not fd.does_exist("Odyssey\\Intensity.png",confidence=0.9,grayscale=True,region=(613+offset[0], 213+offset[1], 782+offset[0], 348+offset[1])):
                if fd.does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or pyautogui.pixelMatchesColor(x=394+offset[0],y=157+offset[1],expectedRGBColor=(255,19,23)):
                    break
                time.sleep(0.2)
            fd.click(695+offset[0], 304+offset[1],delay=0.5)
            while not fd.does_exist("Victory.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or any([pyautogui.pixelMatchesColor(x=427+offset[0],y=471+offset[1],expectedRGBColor=(15,253,60),tolerance=5)],[pyautogui.pixelMatchesColor(x=427+offset[0],y=471+offset[1],expectedRGBColor=(12,198,47),tolerance=5)]):
                if fd.does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or pyautogui.pixelMatchesColor(x=394+offset[0],y=157+offset[1],expectedRGBColor=(255,19,23)):
                    break
                while not load_state()["running"]:
                    time.sleep(0.5)
                time.sleep(0.3)
            print("Going to next match")
            sent_win = False
            if fd.does_exist("Failed.png",confidence=0.9,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or pyautogui.pixelMatchesColor(x=394+offset[0],y=157+offset[1],expectedRGBColor=(255,19,23)):
                sent_win = True
                add_data =  load_state()
                add_data["num_runs"]+=1
                add_data["losses"]+=1
                update_state(add_data)
                time.sleep(1)
                fd.click(return_to_lobby[0]+offset[0],return_to_lobby[1]+offset[1],delay=0.2)
                break
            if not sent_win:    
                while fd.does_exist("Victory.png",confidence=0.75,grayscale=True,region=(147+offset[0], 150+offset[1], 226+offset[0], 175+offset[1])) or any([pyautogui.pixelMatchesColor(x=427+offset[0],y=471+offset[1],expectedRGBColor=(15,253,60),tolerance=5)],[pyautogui.pixelMatchesColor(x=427+offset[0],y=471+offset[1],expectedRGBColor=(12,198,47),tolerance=5)]):
                    while not load_state()["running"]:
                        time.sleep(0.5)
                    if match < 3:
                        fd.click(371+offset[0], 472+offset[1],delay=0.2)
                    else:
                        if not sent_win:
                            sent_win = True
                            add_data =  load_state()
                            add_data["num_runs"]+=1
                            add_data["wins"]+=1
                            update_state(add_data)
                            time.sleep(1)
                        fd.click(return_to_lobby[0]+offset[0],return_to_lobby[1]+offset[1],delay=0.2)
                    time.sleep(0.5)
        time.sleep(0.1)
main()
