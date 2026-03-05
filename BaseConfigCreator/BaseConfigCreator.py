from customtkinter import CTkFrame, CTk, CTkTabview, CTkImage, CTkLabel, CTkButton, CTkScrollableFrame, CTkTextbox, CTkFont, CTkComboBox
from threading import Thread
from threading import Event
import keyboard
from datetime import datetime
import os
import sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Tools import winTools as wt
from Tools import Function_Dictionary as fd
import json
import tkinter as tk
import requests
import difflib
import time
import pyautogui
from pynput import keyboard as pyboard
import ast
import subprocess
import pydirectinput


global OrderArray, UnitInfo, UnitVisible
OrderArray = []
UnitInfo = {}
UnitVisible = [False,False,False,False,False,False,False]

def test_upd(data, path):
    json_path = path
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)
def load_json(json_path):
    print(json_path)
    with open(json_path, "r") as file:
        return json.load(file)
def load_settings():
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"BCC_Settings.json")
    with open(json_path, "r") as file:
        return json.load(file)
def update_settings(data):
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"BCC_Settings.json")
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)
def Movement_Handler(index,operation):
    if index > len(OrderArray)-1 or index == 0 and operation == -1:
        return
    a_order = OrderArray[index]
    b_order = OrderArray[index+operation]
    OrderArray[index+operation] = a_order
    OrderArray[index] = b_order
    for i in range(len(OrderArray)):
        Order_obj = OrderArray[i]
        Order_obj.main_frame.grid(row=i,column=0,padx=2,pady=5,sticky='w')
        Order_obj.row = i

def delete_obj(index):
    if index < len(OrderArray):
        obj = OrderArray[index]
        OrderArray.pop(index)
        obj.main_frame.destroy()
        del obj
        for i in range(len(OrderArray)):
            Order_obj = OrderArray[i]
            Order_obj.main_frame.grid(row=i,column=0,padx=2,pady=5,sticky='w')
            Order_obj.row = i
        
class Hotkey():
    def __init__(self):
        self.listener = pyboard.Listener(on_press=self.hotkey_check)
        self.listener.daemon = False
        self.listener.start()
        self.hotkeys = {}
    def hotkey_check(self, key):
        try:
            if not hasattr(key, "vk"):
                key = self.listener.canonical(key)
            self.hotkeys[key.vk]()
        except Exception:
            pass
    def add_hotkey(self, key, callback):
        self.hotkeys[key] = callback
    def remove_hotkey(self,hotkey):
        print(self.hotkeys.pop(hotkey,None))



global h_keys
h_keys = Hotkey()        
        
class OrderStatement():
    def __init__(self, master, row, key):
        self.master = master
        self.row = row
        self.key = key
        order_template = CTkFrame(self.master,width=390,height=37,fg_color="#241515")
        self.main_frame = order_template
        self.order_key = CTkTextbox(order_template,text_color="#EEEEEE", width=70,font=(CTkFont(size=15,family="Consolas")) ,height=26, fg_color="#573F3F",corner_radius=3)
        self.order_key.insert("0.0", text=self.key[0])
        self.order_key.place(x=5,y=4)
        self.order_arg1 = CTkTextbox(order_template,text_color="#EEEEEE", width=90,font=(CTkFont(size=15,family="Consolas")) ,height=26, fg_color="#573F3F",corner_radius=3)
        self.order_arg2 = CTkTextbox(order_template,text_color="#EEEEEE", width=90,font=(CTkFont(size=15,family="Consolas")) ,height=26, fg_color="#573F3F",corner_radius=3)
        self.order_arg1.insert("0.0", text=self.key[1])
        self.order_arg2.insert("0.0", text=self.key[2])
        self.order_arg1.place(x=80,y=4)
        self.order_arg2.place(x=85+90,y=4)
        order_down = CTkButton(master=order_template,width=30,height=28,text="↓",text_color="#EEEEEE",font=(CTkFont(size=15)),command=lambda: Movement_Handler(self.row,1),corner_radius=3,fg_color="#8E1616",hover_color="#7E1414")
        order_down.place(x=85+90+10+90,y=4)
        order_up = CTkButton(master=order_template,width=30,command=lambda: Movement_Handler(self.row,-1),height=28,text="↑",text_color="#EEEEEE",font=(CTkFont(size=15)),corner_radius=3,fg_color="#8E1616",hover_color="#7E1414")
        order_up.place(x=85+90+10+90+20+20,y=4)
        order_delete = CTkButton(master=order_template,width=30,command=lambda: delete_obj(self.row),height=28,text="X",text_color="#EEEEEE",font=(CTkFont(size=15)),corner_radius=3,fg_color="#8E1616",hover_color="#7E1414")
        order_delete.place(x=85+90+10+90+30+20+30,y=4)
        order_template.grid(row=self.row,column=0,padx=2,pady=5,sticky='w')
    def get_key(self):
        return [self.order_key.get("0.0", "end-1c"),self.order_arg1.get("0.0", "end-1c"),self.order_arg2.get("0.0", "end-1c")]
class MainWindow():
    def __init__(self):
        # this is just the base settings for the ui
        self.app = CTk(fg_color="#1A1A1A")
        self.app._set_appearance_mode("dark")
        self.app.geometry("1633x780")
        self.app.configure(fg_color="#1D1616")
        self.app.title("Base Config Creator")
        self.app.resizable(False,False)
        self.app.iconbitmap(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'Resources\\temp_logo.ico'))
        self.tabs = CTkTabview(self.app, width=1633,height=770,fg_color="#1D1616",text_color="#EEEEEE",bg_color="#1D1616",segmented_button_fg_color="#291E1E",segmented_button_selected_color="#8E1616",segmented_button_selected_hover_color="#891515")
        self.tabs.pack(fill="both", expand=True, padx=20, pady=20)
        self.tabs.place(x=0, y=-10)
        
        # other
        self.running = False
        self.map = ""
        self.export_showing = False
        self.process = None
        
        # main views, macro view is the main view, key dict is for info
        # help is the assistant thing you can do
        # settings is api key n etc
        self.tabs.add('Macro View') 
        self.tabs.add('Key Dictionary') 
        self.tabs.add('Help') 
        self.tabs.add('Settings') 
        
        self.tabs.set('Settings')
        
        #Settings
        settings = load_settings()
        
        Settings_Tab = self.tabs.tab('Settings')
        def save_setting(key, value):
            if key != "API_KEY":
                value = ast.literal_eval(value)
            print(key,value)
            settings[key] = value
            print(settings.get(key))
            update_settings(settings)
            
        aio_settings = CTkLabel(master=Settings_Tab,text_color="#EEEEEE", text="Base Config Creator Settings (VK DECIMAL KEY CODES)",font=CTkFont(size=20))
        aio_settings.place(x=10,y=10)
        
        setting_container = CTkScrollableFrame(master=Settings_Tab,width=1605,height=650,bg_color="#2A2121")
        setting_container.place(x=5,y=35)
        setting_container.grid_columnconfigure(0, weight=1)
        setting_container.grid_columnconfigure(1, weight=1)
        setting_container.grid_columnconfigure(2, weight=1)
        setting_container.grid_columnconfigure(3, weight=1)


        SCC = 0
        SRR = 0
        for key in settings.keys():   
            if key != "Name":
                if type(settings[key]) is not dict:
                    templ = CTkFrame(master=setting_container,height=150,width=475,corner_radius=2,fg_color="#262626")
                    templ.grid_columnconfigure(0, weight=1)
                    label = CTkLabel(master=templ,text=key,anchor='w',font=CTkFont(size=18),text_color="white",fg_color="#191919", corner_radius=5,width=200,height=28)
                    label.grid(row=0, column=0, padx=0, pady=0, sticky="ew")
                    test = CTkTextbox(master=templ,width=180,height=50,corner_radius=5,font=CTkFont(family="Consolas",size=13))
                    if key != "API_KEY":
                        test.insert("0.0", str(settings[key]))
                    else:
                        test.insert("0.0", "API_KEY HIDDEN")
                    test.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
                    test2 = CTkButton(master=templ,text="Set",command=lambda key=key, textbox=test: save_setting(key, textbox.get("0.0", "end-1c")),height=28,corner_radius=5,font=CTkFont(size=13),fg_color="#8E1616",hover_color="#841414")
                    test2.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")
                    
                    templ.grid(row=SCC, column=SRR, padx=10, pady=10, sticky="ew")
                    if SRR < 3:
                        SRR+=1
                    elif SRR == 3:
                        SCC+=1
                        SRR = 0 
        
        #Help
    
        self.help_tab = CTkTextbox(master=self.tabs.tab('Help'),width=1609,height=650,fg_color="#2E2222",text_color="#EEEEEE",font=CTkFont(size=15))
        self.help_tab.configure(state="disabled")
        self.help_tab.place(x=6,y=5)
        self.help_input = CTkTextbox(master=self.tabs.tab('Help'),width=1400,height=60,fg_color="#2E2222",text_color="#EEEEEE",font=CTkFont(size=20))
        self.help_input.place(x=6+22+10,y=670)
        help_button = CTkButton(master=self.tabs.tab('Help'),height=60,width=120,text="Ask",command=lambda:send_help_req(self.help_input.get("0.0","end-1c")),fg_color="#2C2929",hover_color="#373333",font=CTkFont(size=20))
        help_button.place(x=1430+22+10,y=670)
        def send_help_req(describe_config):
            prompt_system_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"AiAssistant","prompt.txt")
            api_key = settings["API_KEY"]
            prompt = ""
            user_info = {}
            for unit in UnitInfo.keys():
                Boxes = UnitInfo.get(unit)
                placements = Boxes[0]
                upgrades = Boxes[1]
                abilities = Boxes[2]
                user_info[unit] = f"Placements: {placements.get("0.0","end-1c").strip()}, Upgrades: {upgrades.get("0.0","end-1c").strip()}, abilties: {abilities.get("0.0","end-1c").strip()}"
            
            with open(prompt_system_path, "r", encoding="utf-8") as file:
                prompt = file.read()
            prompt+=f" -- USER EXISTING POS/UPG/ABILITIES, REFERENCE: {str(user_info)} "
            if True:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                    "Content-Type": "application/json" 
                }

                data = {
                    "model": "openai/gpt-4.1",
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": describe_config}
                        
                        ]
                }

                t = requests.post("https://models.github.ai/inference/chat/completions",headers=headers,json=data)
                content = t.content
                data = json.loads(content)
                print(data["choices"][0]["message"]["content"])
                self.help_tab.configure(state="normal")
                self.help_tab.delete("0.0",'end')
                self.help_tab.insert("0.0",data["choices"][0]["message"]["content"])
                self.help_tab.configure(state="disabled")
            
        
        
        #Key Dict
        KeyDictionary = CTkTabview(self.tabs.tab('Key Dictionary'),width=800,height=710,anchor='w',fg_color="#2E2222",bg_color="#1D1616",segmented_button_fg_color="#291E1E",segmented_button_selected_color="#8E1616",segmented_button_selected_hover_color="#891515")
        KeyDictionary.place(x=5, y=5)
        
        KeyView = CTkFrame(self.tabs.tab('Key Dictionary'),width=800,height=692,fg_color="#2E2222",corner_radius=5)
        KeyView.place(x=816, y=5+18)
        self.key_title = CTkLabel(master=KeyView,width=780,corner_radius=5,height=60,fg_color="#271C1C",anchor='w',text="Key",font=CTkFont(size=35))
        self.key_title.place(x=10,y=10)
        self.info_box = CTkTextbox(master=KeyView,fg_color="#271C1C",width=780,height=590,text_color="#EEEEEE",font=CTkFont(size=20))
        self.info_box.place(x=10,y=80)
        self.info_box.configure(state="disabled")
        KeyDictionary.add("Units")
        KeyDictionary.add("Order")
        KeyDictionary.add("Unit Abilities")
        KeyDictionary.add("Other")
        
        Dictionary_Json = load_json(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Info", "Dictionary.json"))
        def change_infobox(section,key):
            self.key_title.configure(text=key)
            self.info_box.configure(state="normal")
            self.info_box.delete("0.0",'end')
            self.info_box.insert("0.0",Dictionary_Json[section][key])
            self.info_box.configure(state="disabled")
        for section in Dictionary_Json.keys():
            master = CTkScrollableFrame(master=KeyDictionary.tab(section),width=800,height=710,fg_color="#2E2222")
            master.place(x=0,y=0)
            row = 0
            for key in Dictionary_Json[section].keys():
                print(key)#2C2929
                key_label = CTkLabel(master=master,height=35,width=780,text=key,font=CTkFont(size=15),fg_color="#2C2929",anchor='w',corner_radius=5,text_color="#EEEEEE")
                key_info = CTkButton(master=key_label,height=29,width=30,text="?",fg_color="#2C2929",hover_color="#2C2929", command=lambda x=section, y=key:change_infobox(x,y))
                key_info.place(x=740,y=3)
                key_label.grid(row=row, column=0, padx=0, pady=10, sticky="ew")
                row+=1
                
        # Macro view tab thingy
        transparent_color = "#000001"
        self.app.wm_attributes("-transparentcolor", transparent_color)
        self.app.wm_attributes("-topmost",True)
        self.roblox_cut_out = CTkFrame(master=self.tabs.tab('Macro View'),width=790,height=590,fg_color=transparent_color)
        self.roblox_cut_out.place(x=15+400,y=10) 
        
        self.OrderContainer = CTkFrame(self.tabs.tab('Macro View'), width=400, height=700, fg_color="#291E1E")
        self.OrderContainer.place(x=790+400+26,y=10)
        Order_label= CTkLabel(self.OrderContainer, text='Order',text_color="#EEEEEE", width=400,font=(CTkFont(size=20)) ,height=28, fg_color="#8E1616",corner_radius=3)
        Order_label.place(x=0, y=0)
        
        self.OrderBox = CTkScrollableFrame(self.OrderContainer,width=400,height=662, fg_color="#291E1E",corner_radius=3)
        self.OrderBox.place(x=0,y=28)
        
        # unit info:
        self.unit_Tabs = CTkTabview(self.tabs.tab('Macro View'), width=400,height=700,fg_color="#291E1E",text_color="#EEEEEE",bg_color="#1D1616",segmented_button_fg_color="#291E1E",segmented_button_selected_color="#8E1616",segmented_button_selected_hover_color="#891515")
        self.unit_Tabs.place(x=5,y=-10)
        for i in range (1,8):
            self.unit_Tabs.add(f"Unit {i}")#352626
            placement_box = CTkTextbox(self.unit_Tabs.tab(f"Unit {i}"),font=CTkFont(family="Consolas",size=17),width=390,height=190, fg_color="#352626",corner_radius=3)
            placement_label = CTkLabel(self.unit_Tabs.tab(f"Unit {i}"),text="Placements",font=CTkFont(family="Consolas",size=17),width=390,height=25,fg_color="#291E1E",anchor="w")
            placement_label.place(x=1,y=0)
            placement_box.place(x=1,y=25)
            
            upgrade_box = CTkTextbox(self.unit_Tabs.tab(f"Unit {i}"),font=CTkFont(family="Consolas",size=17),width=390,height=190, fg_color="#352626",corner_radius=3)
            upgrade_label = CTkLabel(self.unit_Tabs.tab(f"Unit {i}"),text="Upgrades",font=CTkFont(family="Consolas",size=17),width=390,height=25,fg_color="#291E1E",anchor="w")
            upgrade_label.place(x=1,y=190+25)
            upgrade_box.place(x=1,y=190+10+25+12)
            
            ability_box = CTkTextbox(self.unit_Tabs.tab(f"Unit {i}"),font=CTkFont(family="Consolas",size=17),width=390,height=190, fg_color="#352626",corner_radius=3)
            ability_label = CTkLabel(self.unit_Tabs.tab(f"Unit {i}"),text="Abilities",font=CTkFont(family="Consolas",size=17),width=390,height=25,fg_color="#291E1E",anchor="w")
            ability_label.place(x=1,y=190+25+190+26)
            ability_box.place(x=1,y=380+20+25+26+4)
            
            

            global UnitInfo
            UnitInfo.setdefault(i, [placement_box,upgrade_box,ability_box])
        def change_visible():
            p=None
            c_tab = self.unit_Tabs.get()
            p=int(c_tab.split(" ")[1])
            global UnitVisible
            UnitVisible[p-1] = not UnitVisible[p-1]
            print(f"Unit {p}: {UnitVisible[p-1]}")
        toggle_visible = CTkButton(self.unit_Tabs,text="Toggle Overlay",command=change_visible,text_color="#EEEEEE",width=70,height=25,fg_color="#8E1616",hover_color="#841414")
        toggle_visible.place(x=295,y=37)
        print(UnitInfo)
        self.unit_Tabs._segmented_button.grid(sticky="w")
        #self.unit_Tabs.set()
        
        self.mouse_log_event = Event()
        self.mouse_log = False
        def mouse_log_start():
            if self.mouse_log_event.is_set():
                self.mouse_log_event.clear()
            self.log_mouse_pos()

        export_button = CTkButton(self.tabs.tab('Macro View'),text="Export Config",command=self.export_config,text_color="#EEEEEE",width=190,height=25,fg_color="#8E1616",hover_color="#841414")
        export_button.place(x=5,y=695)
        import_button = CTkButton(self.tabs.tab('Macro View'),text="Import Config",command=self.import_config,text_color="#EEEEEE",width=190,height=25,fg_color="#8E1616",hover_color="#841414")
        import_button.place(x=215,y=695)


        log_mouse = CTkButton(self.tabs.tab('Macro View'),text="Take Mouse Positions",command=mouse_log_start,text_color="#EEEEEE",width=70,height=25,fg_color="#8E1616",hover_color="#841414")
        log_mouse.place(x=415,y=590+30)
        
        self.mouse_positions = CTkTextbox(self.tabs.tab('Macro View'),font=CTkFont(family="Consolas",size=17),width=790,height=190, fg_color="#352626",corner_radius=3)
        self.mouse_positions.place(x=415,y=590+30+30)
        self.mouse_positions.configure(state="disabled")
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        #keybinds
        def add_order():
            global OrderArray
            Order_Obj = OrderStatement(master=self.OrderBox,row=len(OrderArray),key=["keyhere","arg1","arg2"])
            OrderArray.append(Order_Obj)
            print(OrderArray)
            
        def load_previous_config():
            try:
                    config = load_json(os.path.join(os.path.dirname(os.path.abspath(__file__)),"CurrentConfig.json"))
                    print(config)
                    Units = config["Units"]
                    Order = config["Order"]
                    for i in Units.keys():
                        Boxes = UnitInfo.get(int(i))
                        placements = Boxes[0]
                        upgrades = Boxes[1]
                        abilities = Boxes[2]
                        placements.delete("0.0",'end')
                        upgrades.delete("0.0",'end')
                        abilities.delete("0.0",'end')
                        for ind,placement in enumerate(Units[i]["placements"]):
                            print(len((Units[i]["placements"])))
                            if ind < len((Units[i]["placements"]))-1:
                                placements.insert("end",f"{placement},")
                            else:
                                placements.insert("end",f"{placement}")
                        for ind,upgrade in enumerate(Units[i]["upgrades"]):
                            print(len((Units[i]["upgrades"])))
                            if ind < len((Units[i]["upgrades"]))-1:
                                upgrades.insert("end",f"{upgrade},")
                            else:
                                upgrades.insert("end",f"{upgrade}")
                        for ind,ability in enumerate(Units[i]["abilities"]):
                            print(len((Units[i]["abilities"])))
                            if ind < len((Units[i]["abilities"]))-1:
                                abilities.insert("end",f"{ability},")
                            else:
                                abilities.insert("end",f"{ability}")
                    while len(OrderArray) > 0:
                        delete_obj(0)
                    for g in Order:
                        Order_Obj = OrderStatement(master=self.OrderBox,row=len(OrderArray),key=g)
                        OrderArray.append(Order_Obj)
            except Exception:
                pass
        h_keys.add_hotkey(settings["pos_rb"], self.pos_rb)
        h_keys.add_hotkey(settings["run_config"], lambda: self.run_config())
        h_keys.add_hotkey(settings["stop_macro"], lambda: self.stop_macro())
        h_keys.add_hotkey(settings["auto_position"], lambda: self.auto_position())
        h_keys.add_hotkey(settings["kill_macro"], lambda: self.kill_macro())
        h_keys.add_hotkey(settings["set_map"], lambda: self.set_map())
        h_keys.add_hotkey(settings["export_config"], lambda: self.export_config())
        h_keys.add_hotkey(settings["import_config"], lambda: self.import_config())
        h_keys.add_hotkey(settings["add_order"],add_order)
        h_keys.add_hotkey(settings["log_mouse_position"],lambda: None)
        h_keys.add_hotkey(settings["stop_logging_mouse_position"],lambda: None)
        h_keys.add_hotkey(settings["load_previous_config"],lambda: load_previous_config())#load_previous_config

        for i in range (0,7):
            h_keys.add_hotkey(97+i,lambda i=i: self.unit_Tabs.set(f"Unit {i+1}"))
        Thread(target=self.update_order).start()
        Thread(target=self.overlay_debug).start()
    def log_mouse_pos(self):
        if not self.mouse_log:
            mouse_just_pos = []
            window = wt.get_window("Roblox")
            offset = (window.left,window.top)
            cur_overlay = None
            self.mouse_log_event.clear()
            def add_mouse():
                cords = pyautogui.position()
                print("Adding")
                cords = cords.x-offset[0], cords.y-offset[1]
                mouse_just_pos.append((cords[0],cords[1]))
            def close():
                print("Closing")
                print(mouse_just_pos)
                self.mouse_log = False
                self.mouse_positions.configure(state="normal")
                self.mouse_positions.delete("0.0",'end')
                self.mouse_positions.insert("0.0",str(mouse_just_pos)[1:len(str(mouse_just_pos))-1].replace("(","[").replace(")","]").strip())
                self.mouse_positions.configure(state="disabled")
                print(h_keys.listener.is_alive())
                nonlocal cur_overlay
                cur_overlay.destroy()
                cur_overlay = None
            h_keys.add_hotkey(190,add_mouse)
            h_keys.add_hotkey(78,close)
            def debug():
                self.mouse_log = True
                print("entered")
                overlay = tk.Toplevel()
                nonlocal cur_overlay
                cur_overlay = overlay
                overlay.attributes("-topmost", True)
                overlay.attributes("-transparentcolor", "black")
                overlay.overrideredirect(True)
                canvas = tk.Canvas(overlay, bg="black", highlightthickness=0)
                canvas.pack(fill="both", expand=True)
                overlay.geometry(
                    f"{overlay.winfo_screenwidth()}x{overlay.winfo_screenheight()}+0+0"
                )
                def update_overlay():
                    while self.mouse_log:
                        window = wt.get_window("Roblox")
                        offset = (window.left,window.top)
                        if True:
                            canvas.delete("all")
                            for i, box in enumerate(mouse_just_pos):
                                canvas.create_text(
                                    box[0]+offset[0], box[1]+offset[1]-16, 
                                    text=f"P{i+1}", 
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
                            
                        time.sleep(0.5)
                t= Thread(target=update_overlay, daemon=True)
                t.start()
                t.join()
                h_keys.add_hotkey(190,lambda: None)
                h_keys.add_hotkey(78,lambda: None)
            
            t = Thread(target=debug,daemon=True)
            t.start()
            print("ended")
    def update_order(self):
        p_order = None
        p_pos = 0
        while True:
            if p_order != OrderArray:
                print("hello")
                for ind,obj in enumerate(OrderArray):
                    if not ind < p_pos:
                        print(f"added {obj}")
                p_pos=len(OrderArray)
                p_order = OrderArray.copy()
            if p_order is None:
                print("is none")
                p_order = OrderArray()
                p_pos=len(OrderArray)
            time.sleep(1)
    def pos_rb(self):
        window = wt.get_window("Roblox") # Get roblox window
        roblox_window = window
        print(roblox_window)
        wt.resize_window(roblox_window, 816, 638)  # Resize window
        wt.move_window(roblox_window, self.roblox_cut_out.winfo_rootx()-15, self.roblox_cut_out.winfo_rooty()-32)
        wt.activate_window(window=window)
        time.sleep(0.5)
    def start_app(self):
        self.app.mainloop() 
        
    def stop_macro(self):
        state = load_json(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"Info", "state.json"))
        state["running"] = False
        test_upd(state,os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"Info", "state.json"))
    def kill_macro(self):
        if self.process is not None:
            self.process.terminate()
            self.running = False
        state = load_json(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"Info", "state.json"))
        state["running"] = False
        test_upd(state,os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"Info", "state.json"))
    def auto_position(self):
        if self.map != "":
            state = load_json(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"Info", "state.json"))
            state["running"] = True
            test_upd(state,os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"Info", "state.json"))
            print(self.map)
            rb_window = wt.get_window("Roblox")
            offset = (rb_window.left, rb_window.top)
            Positioner_Folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Resources", "Positioner")
            print(Positioner_Folder)
            CTM_POSITIONS_AUTO = {
                "Ant_Island": [[169,533,6],[409,309,0]],
                "Kuinshi_Palace": [[45,242,1]],
                "Sand_Village": [[695,482,1]],
                "AOT": [[802,274,1],[729,285,3]],
                "Shibuya_Aftermath": [[29,454,1],[177,419,4]],
                "Saber": [[67,90,1]],
                "Shining_Castle": [[411,510,1]],
                "Edge_Of_Heaven": [[410,619,1],[344,495,4]],
                "Spirit_Society": [[340,79,1],[70,110,5]]
            }
            CTM_POSITIONS_NO_AUTO = {
                "Frozen_Volcano": [[382,623,1],[382,623,4],[643,619,2]],
                "Lebero_Raid": [[785,591,1],[239,620,4],[418,619,4]],
                "Igris": [[412,49,2]],
                "Golden_Castle": [[411,76,1]],
                "Martial_Island": [[28,398,1]]
            }
            if self.map == "Ruined_City":
                fd.auto_positioner("SBR",offset,just_camera=True)
                time.sleep(1)
                top_down_unit = 5
                fd.start(offset)
                print("placing", top_down_unit)
                fd.place_unit(top_down_unit,pos=(161,187),offset=offset)
                pydirectinput.press('f')
                inputs =  [(619, 193), (156, 247), (333, 537), (405, 609),(305, 232)] 
                for c in inputs:
                    fd.click(c[0]+offset[0],c[1]+offset[1],delay=0.1)
                    if c == (333,537):
                        time.sleep(1)
                    else:
                        time.sleep(0.2)
                pydirectinput.press('f')
                pydirectinput.keyDown('o')
                time.sleep(0.8)
                pydirectinput.keyUp('o')
                fd.click(417+offset[0], 520+offset[1],right_click=True)
                fd.restart_match(offset)
                
                return
            if os.path.exists(os.path.join(Positioner_Folder, f"{self.map}.png")):
                print(f"Exists {os.path.join(Positioner_Folder,self.map)}")
                fd.auto_positioner(f"{self.map}",offset=offset,no_restart=True)
                if CTM_POSITIONS_AUTO.get(self.map) is not None:
                    for j in CTM_POSITIONS_AUTO.get(self.map):
                        fd.click(j[0]+offset[0],j[1]+offset[1],right_click=True)
                        time.sleep(j[3])
            else:
                print("Doesnt exist")
                print(os.path.join(Positioner_Folder, f"{self.map}.png"))
                fd.auto_positioner(f"{self.map}",offset=offset,just_camera=True)
                if CTM_POSITIONS_NO_AUTO.get(self.map) is not None:
                    for j in CTM_POSITIONS_NO_AUTO.get(self.map):
                        fd.click(j[0]+offset[0],j[1]+offset[1],right_click=True)
                        time.sleep(j[3])
            state = load_json(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"Info", "state.json"))
            state["running"] = False
            test_upd(state,os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"Info", "state.json"))
    def set_map(self):
        if not self.export_showing:
            self.export_showing = True
            frame_show = CTkFrame(master=self.app,width=500,height=300,fg_color="#1D1616",corner_radius=5,border_width=1,border_color="#D84040")
            frame_show.place(relx=0.5,rely=0.5,anchor="center")    
            frame_show.lift()
            
            def close():
                self.export_showing = False
                frame_show.destroy()
                
            frame_label = CTkLabel(master=frame_show,height=70,width=490,text="Set map",font=CTkFont(size=30),fg_color="#8E1616",anchor='w',corner_radius=5,text_color="#EEEEEE")
            frame_label.place(x=5,y=5)
                
            frame_close = CTkButton(master=frame_show,width=30,height=30,text="X",text_color="#EEEEEE",font=(CTkFont(size=20)),command=close,corner_radius=0,fg_color="#8E1616",hover_color="#7E1414")
            frame_close.place(x=460,y=10)
            
    
                
        
            Gamemode_Label = CTkLabel(master=frame_show,text="Gamemode:",anchor='w',font=CTkFont(size=18),text_color="white",fg_color="#1D1616", corner_radius=5,width=200,height=28)
            Gamemode = CTkTextbox(master=frame_show,width=250,height=25,corner_radius=5,font=CTkFont(family="Consolas",size=13))
            Gamemode.place(x=20,y=120)
            Gamemode_Label.place(x=15,y=90)
            
            Stage_label = CTkLabel(master=frame_show,text="Stage:",anchor='w',font=CTkFont(size=18),text_color="white",fg_color="#1D1616", corner_radius=5,width=200,height=28)
            Stage = CTkTextbox(master=frame_show,width=250,height=25,corner_radius=5,font=CTkFont(family="Consolas",size=13))
            Stage.place(x=20,y=120+80)
            Stage_label.place(x=15,y=90+80)
            
            
            def import_config():
                Settings_Folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"Settings")
                Gamemode_Input = Gamemode.get("0.0", "end-1c")
                Stage_Input = Stage.get("0.0", "end-1c")
                if True:
                    Gamemodes = [gamemode for gamemode in os.listdir(Settings_Folder)]
                    gamemode_match = difflib.get_close_matches(Gamemode_Input.capitalize(),Gamemodes,cutoff=0.6)
                    gamemode_prob = max([( difflib.SequenceMatcher(None, Gamemode_Input,match).quick_ratio(), match) for match in gamemode_match])
                    Stages = [stage.replace(".json","") for stage in os.listdir(os.path.join(Settings_Folder,gamemode_prob[1]))]
                    stage_match = difflib.get_close_matches(Stage_Input.capitalize().replace(" ","_"),Stages,cutoff=0.6)
                    stage_prob = max([( difflib.SequenceMatcher(None, Stage_Input.replace(" ","_"),stage).quick_ratio(), stage) for stage in stage_match])
                    if len(stage_prob) != 0 and len(gamemode_prob) !=0:
                        found_path = os.path.join(Settings_Folder, gamemode_prob[1], stage_prob[1]+".json")
                        if os.path.exists(found_path):
                            self.map = stage_prob[1]
                            print(self.map)
                            popup = CTkFrame(master=frame_show,width=200,height=100,fg_color="#1D1616",corner_radius=5,border_width=1,border_color="#D84040")
                            popup.place(relx=0.5,rely=0.5,anchor="center")    
                            popup.lift()
                            
                            def popup_closef():
                                popup.destroy()
                                
                            popup_label = CTkLabel(master=popup,height=70,width=190,text="Map Set!",font=CTkFont(size=25),fg_color="#8E1616",anchor='w',corner_radius=5,text_color="#EEEEEE")
                            popup_label.place(x=5,y=5)
                                
                            popup_close = CTkButton(master=popup,width=30,height=30,text="X",text_color="#EEEEEE",font=(CTkFont(size=20)),command=popup_closef,corner_radius=0,fg_color="#8E1616",hover_color="#7E1414")
                            popup_close.place(x=160,y=10)
            Config_Import = CTkButton(master=frame_show,text="Set Map",command=lambda: import_config() ,text_color="#EEEEEE",width=175,height=28,fg_color="#8E1616",hover_color="#841414")
            Config_Import.place(x=20,y=90+80+80)
    def export_config(self):
        if not self.export_showing:
            self.export_showing = True
            frame_show = CTkFrame(master=self.app,width=700,height=400,fg_color="#1D1616",corner_radius=5,border_width=1,border_color="#D84040")
            frame_show.place(relx=0.5,rely=0.5,anchor="center")    
            frame_show.lift()
            
            def close():
                self.export_showing = False
                frame_show.destroy()
                print("closed")
                        
            frame_label = CTkLabel(master=frame_show,height=70,width=690,text="Config Exporter",font=CTkFont(size=30),fg_color="#8E1616",anchor='w',corner_radius=5,text_color="#EEEEEE")
            frame_label.place(x=5,y=5)
                
                    
            frame_close = CTkButton(master=frame_show,width=30,height=30,text="X",text_color="#EEEEEE",font=(CTkFont(size=20)),command=close,corner_radius=0,fg_color="#8E1616",hover_color="#7E1414")
            frame_close.place(x=660,y=10)
                    
            setting_container = CTkFrame(master=frame_show,width=660,height=300,bg_color="#2A2121")
            setting_container.place(x=20,y=85)
            
            AP_Label = CTkLabel(master=setting_container,corner_radius=5,height=25,width=180,text=" Auto Pos:",font=CTkFont(size=20),fg_color="#8E1616",anchor='w',text_color="#EEEEEE")
            Auto_Pos = CTkTextbox(master=setting_container,corner_radius=5,width=180,height=30,font=CTkFont(family="Consolas",size=13))
            Auto_Pos.place(x=20+5,y=25+10)
            AP_Label.place(x=20+5,y=13)
            
            Caloric_Unit_Label = CTkLabel(master=setting_container,height=25,width=180,text="Caloric Unit:",font=CTkFont(size=20),fg_color="#8E1616",anchor='w',corner_radius=5,text_color="#EEEEEE")
            Caloric_Unit_Label.place(x=10+200+30,y=13)
            Caloric_Unit = CTkTextbox(master=setting_container,width=180,height=30,corner_radius=5,font=CTkFont(family="Consolas",size=13))
            Caloric_Unit.place(x=10+200+30,y=25+10)
            
            def on_export():
                self.export(Auto_Pos.get("0.0","end-1c"),Caloric_Unit.get("0.0","end-1c"))
                Exported_Config.insert("0.0",f"{load_json(os.path.join(os.path.dirname(os.path.abspath(__file__)), "CurrentConfig.json"))}")
            Export =CTkButton(setting_container,text="Export Config",font=CTkFont(size=25),command=on_export,text_color="#EEEEEE",width=180,height=52,fg_color="#8E1616",hover_color="#841414")
            Export.place(x=455,y=13)

            Exported_Config = CTkTextbox(master=setting_container,width=610,height=200,corner_radius=5,font=CTkFont(family="Consolas",size=13))
            Exported_Config.place(x=25,y=80)
    def import_config(self):
        if not self.export_showing:
            self.export_showing = True
            frame_show = CTkFrame(master=self.app,width=700,height=400,fg_color="#1D1616",corner_radius=5,border_width=1,border_color="#D84040")
            frame_show.place(relx=0.5,rely=0.5,anchor="center")    
            frame_show.lift()
            
            def close():
                self.export_showing = False
                frame_show.destroy()
                print("closed")
                        
            frame_label = CTkLabel(master=frame_show,height=70,width=690,text="Config Importer",font=CTkFont(size=30),fg_color="#8E1616",anchor='w',corner_radius=5,text_color="#EEEEEE")
            frame_label.place(x=5,y=5)
                
                    
            frame_close = CTkButton(master=frame_show,width=30,height=30,text="X",text_color="#EEEEEE",font=(CTkFont(size=20)),command=close,corner_radius=0,fg_color="#8E1616",hover_color="#7E1414")
            frame_close.place(x=660,y=10)
                    
            setting_container = CTkFrame(master=frame_show,width=660,height=300,bg_color="#2A2121")
            setting_container.place(x=20,y=85)
            
            AP_Label = CTkLabel(master=setting_container,corner_radius=5,height=25,width=610,text="Config:",font=CTkFont(size=20),fg_color="#8E1616",anchor='w',text_color="#EEEEEE")

            AP_Label.place(x=20+5,y=13)
            
            Imported_Config = CTkTextbox(master=setting_container,width=610,height=200,corner_radius=5,font=CTkFont(family="Consolas",size=13))
            Imported_Config.place(x=25,y=38)
            
            def on_export():
                try:
                    config = json.loads(Imported_Config.get("0.0","end-1c"))
                    print(config)
                    Units = config["Units"]
                    Order = config["Order"]
                    for i in Units.keys():
                        Boxes = UnitInfo.get(int(i))
                        placements = Boxes[0]
                        upgrades = Boxes[1]
                        abilities = Boxes[2]
                        placements.delete("0.0",'end')
                        upgrades.delete("0.0",'end')
                        abilities.delete("0.0",'end')
                        for ind,placement in enumerate(Units[i]["placements"]):
                            print(len((Units[i]["placements"])))
                            if ind < len((Units[i]["placements"]))-1:
                                placements.insert("end",f"{placement},")
                            else:
                                placements.insert("end",f"{placement}")
                        for ind,upgrade in enumerate(Units[i]["upgrades"]):
                            print(len((Units[i]["upgrades"])))
                            if ind < len((Units[i]["upgrades"]))-1:
                                upgrades.insert("end",f"{upgrade},")
                            else:
                                upgrades.insert("end",f"{upgrade}")
                        for ind,ability in enumerate(Units[i]["abilities"]):
                            print(len((Units[i]["abilities"])))
                            if ind < len((Units[i]["abilities"]))-1:
                                abilities.insert("end",f"{ability},")
                            else:
                                abilities.insert("end",f"{ability}")
                    while len(OrderArray) > 0:
                        delete_obj(0)
                    for g in Order:
                        Order_Obj = OrderStatement(master=self.OrderBox,row=len(OrderArray),key=g)
                        OrderArray.append(Order_Obj)

        
                except Exception as e:
                    print(e)
            Import =CTkButton(setting_container,text="Import Config",font=CTkFont(size=25),command=on_export,text_color="#EEEEEE",width=180,height=40,fg_color="#8E1616",hover_color="#841414")
            Import.place(x=240,y=249)

            
    def export(self, auto_pos, caloric_unit):
        try:
                print("called")
                print(auto_pos,caloric_unit)
                print("------")
                def eval_from_string(args,capitalized: bool | None=None, no: bool | None=None) -> any:
                    total = []
                    if type(args) is str:
                        for arg in args.split('],'):
                            reformed = []
                            #print(arg)
                            for part in arg.replace('[',"").replace("]","").replace("\"","").replace("\'", "").split(","):
                                part = part.strip()
                                if part.lower() == -1 or part.lower() == "none" or part.lower() == "null":
                                    reformed.append(None)
                                    continue
                                if part.lower() == "false":
                                    reformed.append(False)
                                    continue
                                if part.lower() == "true":
                                    reformed.append(True)
                                    continue
                                try:
                                    reformed.append(ast.literal_eval(part))
                                except Exception:
                                    if capitalized is not None and capitalized:
                                        part = part.upper()
                                    reformed.append(part)
                                    
                            i = 0
                            while i < len(reformed):
                                if type(reformed[i]) is str:
                                    if '(' in reformed[i]:
                                        new_arg = [ast.literal_eval(reformed[i].replace("(","")),ast.literal_eval(reformed[i+1].replace(")",""))]
                                        reformed.pop(i+1)
                                        reformed.pop(i)
                                        reformed.insert(i,new_arg)
                                        
                                        i+=2
                                        continue
                                i+=1    
                            if no is None and not no:
                                total.append(reformed)
                            else:
                                total = reformed
                    print(total)
                    return total
                
                Exported_Config = {}
                Exported_Config["Units"] = {
                    "1": {
                        "placements": 
                            eval_from_string(UnitInfo[1][0].get("0.0","end-1c"),True)
                        ,
                        "upgrades": 
                            eval_from_string(UnitInfo[1][1].get("0.0","end-1c"),True)
                        ,
                        "abilities": 
                            eval_from_string(UnitInfo[1][2].get("0.0","end-1c"),True)
                        ,
                    },

                    "2": {
                        "placements": 
                            eval_from_string(UnitInfo[2][0].get("0.0","end-1c"),True)
                        ,
                        "upgrades": 
                            eval_from_string(UnitInfo[2][1].get("0.0","end-1c"),True)
                        ,
                        "abilities": 
                            eval_from_string(UnitInfo[2][2].get("0.0","end-1c"),True)
                        ,
                    },

                    "3": {
                        "placements": 
                            eval_from_string(UnitInfo[3][0].get("0.0","end-1c"),True)
                        ,
                        "upgrades": 
                            eval_from_string(UnitInfo[3][1].get("0.0","end-1c"),True)
                        ,
                        "abilities": 
                            eval_from_string(UnitInfo[3][2].get("0.0","end-1c"),True)
                        ,
                    },

                    "4": {
                        "placements": 
                            eval_from_string(UnitInfo[4][0].get("0.0","end-1c"),True)
                        ,
                        "upgrades": 
                            eval_from_string(UnitInfo[4][1].get("0.0","end-1c"),True)
                        ,
                        "abilities": 
                            eval_from_string(UnitInfo[4][2].get("0.0","end-1c"),True)
                        ,
                    },

                    "5": {
                        "placements": 
                            eval_from_string(UnitInfo[5][0].get("0.0","end-1c"),True)
                        ,
                        "upgrades": 
                            eval_from_string(UnitInfo[5][1].get("0.0","end-1c"),True)
                        ,
                        "abilities": 
                            eval_from_string(UnitInfo[5][2].get("0.0","end-1c"),True)
                        ,
                    },

                    "6": {
                        "placements": 
                            eval_from_string(UnitInfo[6][0].get("0.0","end-1c"),True)
                        ,
                        "upgrades": 
                            eval_from_string(UnitInfo[6][1].get("0.0","end-1c"),True)
                        ,
                        "abilities": 
                            eval_from_string(UnitInfo[6][2].get("0.0","end-1c"),True)
                        ,
                    },

                    "7": {
                        "placements": 
                            eval_from_string(UnitInfo[7][0].get("0.0","end-1c"),True)
                        ,
                        "upgrades": 
                            eval_from_string(UnitInfo[7][1].get("0.0","end-1c"),True)
                        ,
                        "abilities": 
                            eval_from_string(UnitInfo[7][2].get("0.0","end-1c"),True)
                        ,
                    },

                                }  
                Exported_Config["Order"] = [eval_from_string(f"{statement.get_key()}",no=True) for statement in OrderArray]
                Exported_Config["Caloric_Unit"] = eval_from_string(f"[{caloric_unit}]",no=True)[0]
                Exported_Config["Auto_Pos"] =  eval_from_string(f"[{auto_pos}]",no=True)[0]
                print(Exported_Config)
                test_upd(Exported_Config,os.path.join(os.path.dirname(os.path.abspath(__file__)), "CurrentConfig.json"))
        except Exception as e:
            print(f"error export: {e}")
    def overlay_debug(self):
        overlay = tk.Tk()
        overlay.attributes("-topmost", True)
        overlay.attributes("-transparentcolor", "black")
        overlay.overrideredirect(True)
        canvas = tk.Canvas(overlay, bg="black", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        overlay.geometry(f"{overlay.winfo_screenwidth()}x{overlay.winfo_screenheight()}+0+0")
        p_box = {}
        p_UnitVisible = [False,False,False,False,False,False,False]
        def update_overlay():
            while True:
                window = wt.get_window("Roblox")
                offset = (window.left,window.top)
                for i, b in enumerate(UnitVisible):
                    if b:
                        try:
                            unit = UnitInfo.get(i+1)
                            placements = unit[0].get("0.0", "end-1c")
                            literal = ast.literal_eval(f"[{placements}]")
                            if literal != p_box.get(i) or not p_UnitVisible[i]:
                                p_UnitVisible[i] = True
                                canvas.delete(f"unit{i}")
                                for box in literal:
                                    canvas.create_text(
                                            box[0]+offset[0], box[1]+offset[1]-16, 
                                            text=f"Unit-{i+1}", 
                                            fill="red", 
                                            font=("Consolas", 12),
                                            tags=(f"unit{i}")
                                        )
                                    print("h")
                                    canvas.create_rectangle(
                                            box[0] + offset[0] - 8,
                                            box[1] + offset[1] - 8,
                                            box[0] + offset[0] + 8,
                                            box[1] + offset[1] + 8,
                                            outline="red",
                                            width=2,
                                            tags=(f"unit{i}")
                                            )     
                                if p_box.get(i) is None:
                                    p_box.setdefault(i, literal)  
                                else:
                                    p_box[i] = literal
                        except Exception as e:
                            print(e)
                    else:
                        p_UnitVisible[i] = False
                        canvas.delete(f"unit{i}")
                    overlay.update()
                time.sleep(1)
        Thread(target=update_overlay, daemon=True).start()
        overlay.mainloop()
    def run_config(self):
        if not self.running:
            self.running = True
            print("hi")
            state = load_json(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"Info", "state.json"))
            state["running"] = True
            test_upd(state,os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"Info", "state.json"))
            process = subprocess.Popen([sys.executable,os.path.join(os.path.dirname(os.path.abspath(__file__)),"RunConfig.py")])
            self.process = process
Window = MainWindow()
Window.start_app()



