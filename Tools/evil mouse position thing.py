import pyautogui
import keyboard
import pygetwindow as gw
import time
import tkinter as tk
from threading import Thread

save_mouse_location = '.'
stop_key = 'n'
mouse_info2 = {}
mouse_just_pos = []
#Togglables
BotOn = True
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
    
window = get_window("Roblox")
offset = (window.left,window.top)
def debug():
    overlay = tk.Tk()
    overlay.attributes("-topmost", True)
    overlay.attributes("-transparentcolor", "black")
    overlay.overrideredirect(True)
    canvas = tk.Canvas(overlay, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    overlay.geometry(
        f"{overlay.winfo_screenwidth()}x{overlay.winfo_screenheight()}+0+0"
    )
    def update_overlay():
        p_box = None
        while True:
            if p_box is None:
                p_box = mouse_just_pos.copy()
            if mouse_just_pos != p_box:
                print("added")
                canvas.delete("all")
                for i, box in enumerate(mouse_just_pos):
                    print(box)
                    print("created")
                    canvas.create_text(
                        box[0]+offset[0], box[1]+offset[1]-16, 
                        text=f"C{i}", 
                        fill="red", 
                        font=("Consolas", 12)
                    )
                    canvas.create_rectangle(
                        box[0] + offset[0] - 8,
                        box[1] + offset[1] - 8,
                        box[0] + offset[0] + 8,
                        box[1] + offset[1] + 8,
                        outline="red",
                        width=2,
                    )
                overlay.update()
                p_box = mouse_just_pos.copy()
            time.sleep(0.5)
    Thread(target=update_overlay, daemon=True).start()
    overlay.mainloop()
Thread(target=debug,daemon=True).start()

def add_cords(cords):
    print(cords)
    color = pyautogui.pixel(cords[0],cords[1])
    cords = cords.x-window.left, cords.y-window.top
    print(cords)
    pos_info = {(cords[0], cords[1]): color}
    mouse_info2.update(pos_info)
    mouse_just_pos.append((cords[0],cords[1]))

def bot_toggle():
    global BotOn
    BotOn = not BotOn
    
    
print(window)

keyboard.add_hotkey(save_mouse_location, lambda: add_cords(pyautogui.position()))
keyboard.add_hotkey(stop_key, bot_toggle)

while BotOn:
    time.sleep(0.1)

#print(f"Mouse position with color {mouse_info2}")
print(f"Just mouse cordinates: {mouse_just_pos}")
