from customtkinter import CTkFrame, CTk, CTkTabview, CTkImage, CTkLabel, CTkButton, CTkScrollableFrame, CTkTextbox, CTkFont, CTkComboBox
from threading import Thread
from threading import Event
import keyboard
from datetime import datetime
import os
import json
from Tools import ProcessHandler as Handler
import time
from Tools import winTools as wt
from Tools import Webhook
from PIL import Image
import psutil
import ast
import sys
import atexit
import logging
import webbrowser
import io
import tkinter as tk
import requests
import difflib
print_buffer = io.StringIO()
class Logger:
    def __init__(self, level):
        self.level = level
    def write(self, msg):
        msg = msg.strip()
        if msg:
            self.level(msg)
    def flush(self):
        pass
logging.basicConfig(
    filename=f"RunLogs\\AVAIOBETA_{str(datetime.now()).split(".")[0].replace("-","_").replace(":","_").replace(" ","_")}_log.txt",
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s - %(filename)s - %(funcName)s - : %(message)s",
    filemode="a"
)
handler = logging.StreamHandler(print_buffer)

log_obj = logging.getLogger()
log_obj.addHandler(handler)
sys.stdout = Logger(log_obj.info)
sys.stderr = Logger(log_obj.error)


def load_state():
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"Info", "state.json")
    with open(json_path, 'r') as file:
        return json.load(file)
def update_state(data):
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"Info", "state.json")
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)
        
def load_settings():
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Settings", "AIO_Settings.json")
    with open(json_path, 'r') as file:
        return json.load(file)       
def update_settings(data, path):
    json_path = path
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)

def load_json(json_path):
    with open(json_path, "r") as file:
        return json.load(file)
def write_json(json_path, data):
    with open(json_path, "w") as file:
        json.dump(data, file, indent=4)
def load_pid():
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Info", "processpid.json")
    with open(json_path, 'r') as file:
        return json.load(file)
def update_pid(data):
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Info", "processpid.json")
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)
    

@atexit.register
def kill_pids():
    print("called")
    pids = psutil.pids()
    for pid in pids:
        try:
            if pid != os.getpid():
                process = psutil.Process(pid)
                if process.name().lower() == "python.exe" or process.name().lower() == "pythonw.exe" :
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
def closing(root):
    kill_pids()
    print("Closing")
    root.destroy()
    os._exit(0)
last_pos = 0

class MainWindow():
    def __init__(self):
        self.run_event = Event()
        self.app = CTk(fg_color="#1A1A1A")
        self.app._set_appearance_mode("dark")
        self.app.geometry("1100x700")
        self.app.configure(fg_color="#1D1616")
        self.app.title("AIO")
        self.app.resizable(False,False)
        self.app.iconbitmap('Resources\\temp_logo.ico') 
        
        # Variables
        self.task = ""
        self.path_to_task = ""
        self.task_running = False
        self.task_process = None
        self.is_open_ds = False
        self.config_path = ""
        self.show_debug = False
        self.tabs = CTkTabview(self.app, width=1100,height=710,fg_color="#1D1616",text_color="#EEEEEE",bg_color="#1D1616",segmented_button_fg_color="#291E1E",segmented_button_selected_color="#8E1616",segmented_button_selected_hover_color="#891515")
        self.tabs.pack(fill="both", expand=True, padx=20, pady=20)
        self.tabs.place(x=0, y=-10)
        
        
        self.tabs.add('Player') 
        self.tabs.add('Tasks') 
        self.tabs.add('Settings') 
        
        self.tabs.set('Player') 
        
        

            
        self.app.protocol("WM_DELETE_WINDOW", lambda: closing(self.app))
        
        
        
        #Tasks
        #self.tabs.tab('Tasks')
        Task_Tabs = CTkTabview(self.tabs.tab('Tasks'),width=1078,height=710,anchor='w',fg_color="#2E2222",bg_color="#1D1616",segmented_button_fg_color="#291E1E",segmented_button_selected_color="#8E1616",segmented_button_selected_hover_color="#891515")
        Task_Tabs.place(x=5, y=0)
        
        #Config Importer
        Config_Import = CTkButton(master=self.tabs.tab('Tasks'),text="Import Config",command=self.import_config,text_color="#EEEEEE",width=175,height=28,fg_color="#8E1616",hover_color="#841414")
        Config_Import.place(x=20,y=600)
        
        Task_Path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tasks")
        Task_Tabs.add('Story') 
        Task_Tabs.add('Legend_Stages') 
        Task_Tabs.add('Raid') 
        Task_Tabs.add('Dungeons')
        Task_Tabs.add('Boss_Rush') 
        Task_Tabs.add('Event') 
        Task_Tabs.add('Challenges')
        Task_Tabs.add('Rift')
        Task_Tabs.add('Odyssey')
        Task_Tabs.add('Worldlines')
        Task_Tabs.add('Custom')
        tabs = ["Story", "Legend_Stages", "Event","Worldlines","Raid", "Rift", "Challenges", "Dungeons","Boss_Rush","Odyssey", "Custom"]
        # tabs
        
        for tab in tabs:
            Task_Folder = os.path.join(Task_Path, tab)
            SC = 0 
            SR = 0
            task_added = []
            for file in os.listdir(Task_Folder):
                file_name = file
                if file_name not in task_added:
                    task_added.append(file_name)
                    
                    gear_icon = CTkImage( light_image=Image.open("Resources\\gearicon.png"), dark_image=Image.open("Resources\\gearicon.png"), size=(18, 18) )
                    Template = CTkFrame(master=Task_Tabs.tab(f"{tab}"),fg_color="#1D1616",height=140,width=195)
                    Template.grid(row=SC,column=SR,padx=5,pady=5)
                    
                    Template_Label = CTkLabel(master=Template,width=Template.winfo_width()-10,text_color="#EEEEEE", height=Template.winfo_height()/4, text="".join([step for step in file if not f"{step}".isdigit()]).replace("_", " ").replace(".py",""),font=CTkFont(size=17))
                    Template_Label.place(x=10,y=5)
                    
                    Template_BoxLabel = CTkLabel(master=Template,width=Template.winfo_width()-10,height=Template.winfo_height()/4, text="Selected Config: ",font=CTkFont(size=15))
                    Template_BoxLabel.place(x=10,y=35)
                    
                    Template_ComboBox = CTkComboBox(master=Template,width=175,height=28, text_color="#EEEEEE", values=[file for file in os.listdir(Task_Folder) if file_name in file],command=self.set_task,fg_color="#1D1616")
                    Template_ComboBox.place(x=10,y=63)

                    Template_SetTask = CTkButton(master=Template,text="Set as task",text_color="#EEEEEE",width=175,height=28, command=lambda cb=Template_ComboBox: self.set_task(cb.get()),fg_color="#8E1616",hover_color="#841414")
                    Template_SetTask.place(x=10,y=91+10)
                    
                    Template_Config = CTkButton(master=Template,text="",width=15,height=15,fg_color="transparent",image=gear_icon, command=lambda cb=Template_ComboBox: self.show_base_settings(cb.get()),hover_color="#1D1616")
                    Template_Config.place(x=155,y=5)
                    if SR < 4:
                        SR+=1
                    elif SR == 4:
                        SC+=1
                        SR = 0

            

        
        # Settings Screen
        settings = load_settings()
        
        Settings_Tab = self.tabs.tab('Settings')
        settings_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Settings", "AIO_Settings.json")
        def save_setting(key, value):
            if any(a for a in key if a == "Wait_Start_Timeout" or a=="FV_Card_Priority" or a=="AI_Card_Priority"):
                value = ast.literal_eval(value)
            if type(key) is type([]):
                settings[key[0]][key[1]] =value
                print()
            else:
                print(key,value)
                settings[key] = value
                print(settings.get(key))
            update_settings(settings, settings_json_path)
            
        aio_settings = CTkLabel(master=Settings_Tab,text_color="#EEEEEE", text="AIO Main Settings",font=CTkFont(size=20))
        aio_settings.place(x=10,y=10)
        
        setting_container = CTkScrollableFrame(master=Settings_Tab,width=1055,height=495,bg_color="#2A2121")
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
                    test.insert("0.0", str(settings[key]))
                    test.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
                    test2 = CTkButton(master=templ,text="Set",command=lambda key=key, textbox=test: save_setting(key, textbox.get("0.0", "end-1c")),height=28,corner_radius=5,font=CTkFont(size=13),fg_color="#8E1616",hover_color="#841414")
                    test2.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")
                    
                    templ.grid(row=SCC, column=SRR, padx=10, pady=10, sticky="ew")
                    if SRR < 3:
                        SRR+=1
                    elif SRR == 3:
                        SCC+=1
                        SRR = 0
                else:
                    for s_key in settings[key].keys():
                        templ = CTkFrame(master=setting_container,height=150,width=475,corner_radius=2,fg_color="#262626")
                        templ.grid_columnconfigure(0, weight=1)
                        label = CTkLabel(master=templ,text=s_key,anchor='w',font=CTkFont(size=18),text_color="white",fg_color="#191919", corner_radius=5,width=200,height=28)
                        label.grid(row=0, column=0, padx=0, pady=0, sticky="ew")
                        test = CTkTextbox(master=templ,width=180,height=50,corner_radius=5,font=CTkFont(family="Consolas",size=13))
                        test.insert("0.0", str(settings[key][s_key]))
                        test.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
                        test2 = CTkButton(master=templ,text="Set",command=lambda key=[key,s_key], textbox=test: save_setting(key, textbox.get("0.0", "end-1c")),height=28,corner_radius=5,font=CTkFont(size=13),fg_color="#8E1616",hover_color="#841414")
                        test2.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")
                        
                        templ.grid(row=SCC, column=SRR, padx=10, pady=10, sticky="ew")
                        if SRR < 3:
                            SRR+=1
                        elif SRR == 3:
                            SCC+=1
                            SRR = 0
        
        # Player Screen
        transparent_color = "#000001"
        self.app.wm_attributes("-transparentcolor", transparent_color)
        self.app.wm_attributes("-topmost",True)
        
        self.roblox_cut_out = CTkFrame(master=self.tabs.tab('Player'),width=790,height=590,fg_color=transparent_color)
        self.roblox_cut_out.place(x=15,y=15) 
        
        
        # Info
        self.Info_Frame_One = CTkFrame(master=self.tabs.tab('Player'), width=305, height=195,fg_color="#291E1E")
        self.Info_Frame_One.place(x=820, y=15)
        
        # Task name
        self.task_name_player = CTkLabel(master=self.Info_Frame_One,text=f'Task: {self.task}',text_color="#EEEEEE",fg_color="#8E1616",anchor='w',corner_radius=5,width=250,height=28)
        self.task_name_player.grid(row=0,column=0,columnspan=2,sticky="w",padx=5,pady=5,)


        # Wins
        self.wins = CTkLabel(master=self.Info_Frame_One,text='Wins: 0',fg_color="#8E1616", text_color="#EEEEEE",anchor='w',corner_radius=5,width=120,height=28)
        self.wins.grid(row=1,column=0,sticky="w",padx=5,pady=5)

        # Losses
        self.losses = CTkLabel(master=self.Info_Frame_One,text='Losses: 0',fg_color="#8E1616",text_color="#EEEEEE",anchor='w',corner_radius=5,width=120,height=28)
        self.losses.grid(row=1,column=1,sticky="",padx=5,pady=5)
        # Run time
        self.runtime = CTkLabel(master=self.Info_Frame_One,text='Runtime: 0:00:00',fg_color="#8E1616",text_color="#EEEEEE",anchor='w',corner_radius=5,width=250,height=28)
        self.runtime.grid(row=2,column=0,sticky="",columnspan=2,padx=5,pady=5)
        
        # Output
        self.Code_Container = CTkFrame(self.tabs.tab('Player'), width=260, height=455, fg_color="#291E1E")
        self.Code_Container.place(x=820, y=150)
        
        code_output_label =CTkLabel(self.Code_Container, text='Output',text_color="#FFFFFF", width=40, height=28, fg_color='transparent')
        code_output_label.place(x=10, y=0)
        
        self.code_output = CTkTextbox(self.Code_Container, width=250, text_color="#FFFFFF", height=417,fg_color="#1D1616",font=CTkFont(family="Consolas",size=13))
        self.code_output.place(x=5,y=32)
        
        if settings.get("Kill_Task") == None:
            settings.setdefault("Kill_Task", "f6")
            update_settings(settings,settings_json_path)
        
        position_rb = CTkButton(self.tabs.tab('Player'),command=lambda: self.pos_rb("hi"), text=f'{settings["Position_Key"]}: Position Roblox', text_color="#EEEEEE",hover_color="#841414",width=125, height=28, fg_color='#8E1616',corner_radius=5)
        position_rb.place(x=15,y=620)
        start_rb = CTkButton(self.tabs.tab('Player'),command=lambda: self.start_macro("hi"), text=f'{settings["Start_Key"]}: Run Task', width=100,text_color="#EEEEEE",hover_color="#841414", height=28, fg_color='#8E1616',corner_radius=5)
        start_rb.place(x=150,y=620)
        stop_rb = CTkButton(self.tabs.tab('Player'),command=lambda: self.stop_macro("hi"), text=f'{settings["Stop_Key"]}: Stop Task', width=100,text_color="#EEEEEE", hover_color="#841414",height=28, fg_color='#8E1616',corner_radius=5)
        stop_rb.place(x=261,y=620)
        debug_rb = CTkButton(self.tabs.tab('Player'),command=lambda: self.show_position_debug("hi"), text=f'{settings["Debug_Key"]}: Position Debug', width=100,text_color="#EEEEEE",hover_color="#841414", height=28, fg_color='#8E1616',corner_radius=5)
        debug_rb.place(x=372,y=620)
        kill_rb = CTkButton(self.tabs.tab('Player'), command=lambda: self.kill_macro("hi"),text=f'{settings["Kill_Task"]}: Kill Task', width=100,text_color="#EEEEEE",hover_color="#841414", height=28, fg_color='#8E1616',corner_radius=5)
        kill_rb.place(x=497,y=620)
        donate = CTkButton(self.tabs.tab('Player'), text="Support Me!", width=260,text_color="#EEEEEE", height=28, fg_color='#8E1616',hover_color="#841414",corner_radius=5,command=lambda: webbrowser.open(url="https://linktr.ee/loxerex",new=0,autoraise=True))
        donate.place(x=820,y=620)
        # hotkeys
        keyboard.on_press_key(settings["Position_Key"], self.pos_rb)
        keyboard.on_press_key(settings["Start_Key"], self.start_macro)
        keyboard.on_press_key(settings["Stop_Key"], self.stop_macro)
        keyboard.on_press_key(settings["Debug_Key"], self.show_position_debug)
        keyboard.on_press_key(settings["Kill_Task"], self.kill_macro)
        Thread(target=self.runtime_counter, daemon=True).start()
        Thread(target=self.upd_count, daemon=True).start()
        Thread(target=self.print_output, daemon=True).start()
        
    def import_config(self):
        if not self.is_open_ds:
            self.is_open_ds = True
            frame_show = CTkFrame(master=self.app,width=500,height=400,fg_color="#1D1616",corner_radius=5,border_width=1,border_color="#D84040")
            frame_show.place(relx=0.5,rely=0.5,anchor="center")    
            frame_show.lift()
            
            def close():
                self.is_open_ds = False
                frame_show.destroy()
                
            frame_label = CTkLabel(master=frame_show,height=70,width=490,text="Config Importer",font=CTkFont(size=30),fg_color="#8E1616",anchor='w',corner_radius=5,text_color="#EEEEEE")
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
            
            Pastebin_Code_Label = CTkLabel(master=frame_show,text="Pastebin Code:",anchor='w',font=CTkFont(size=18),text_color="white",fg_color="#1D1616", corner_radius=5,width=200,height=28)
            Pastebin_Code = CTkTextbox(master=frame_show,width=250,height=25,corner_radius=5,font=CTkFont(family="Consolas",size=13))
            Pastebin_Code.place(x=20,y=120+160)
            Pastebin_Code_Label.place(x=15,y=90+160)
            
            def import_config(code):
                Settings_Folder = os.path.join(os.path.dirname(os.path.abspath(__file__)),"Settings")
                pastebin_url = f"https://pastebin.com/raw/{code}"
                Gamemode_Input = Gamemode.get("0.0", "end-1c")
                Stage_Input = Stage.get("0.0", "end-1c")
                json_data = None
                try:
                    with requests.get(pastebin_url, stream=True) as req:
                        req.raise_for_status() 
                        json_data = json.loads(req.text)
                except Exception as e:
                    if json_data is None:
                        print(f"Error when importing config with code: {code}, error: {e}")
                if json_data is not None:
                    Gamemodes = [gamemode for gamemode in os.listdir(Settings_Folder)]
                    gamemode_match = difflib.get_close_matches(Gamemode_Input.capitalize(),Gamemodes,cutoff=0.6)
                    gamemode_prob = max([( difflib.SequenceMatcher(None, Gamemode_Input,match).quick_ratio(), match) for match in gamemode_match])
                    Stages = [stage.replace(".json","") for stage in os.listdir(os.path.join(Settings_Folder,gamemode_prob[1]))]
                    stage_match = difflib.get_close_matches(Stage_Input.capitalize().replace(" ","_"),Stages,cutoff=0.6)
                    stage_prob = max([( difflib.SequenceMatcher(None, Stage_Input.replace(" ","_"),stage).quick_ratio(), stage) for stage in stage_match])
                    if len(stage_prob) != 0 and len(gamemode_prob) !=0:
                        found_path = os.path.join(Settings_Folder, gamemode_prob[1], stage_prob[1]+".json")
                        if os.path.exists(found_path):
                            data = load_json(found_path)
                            next_config = str(int(list(data["configs"].keys())[-1])+1)
                            data["configs"].setdefault(next_config, json_data)
                            data["selected"] = next_config
                            write_json(found_path, data)
                            popup = CTkFrame(master=frame_show,width=200,height=100,fg_color="#1D1616",corner_radius=5,border_width=1,border_color="#D84040")
                            popup.place(relx=0.5,rely=0.5,anchor="center")    
                            popup.lift()
                            
                            def popup_closef():
                                popup.destroy()
                                
                            popup_label = CTkLabel(master=popup,height=70,width=190,text="Config Imported!",font=CTkFont(size=30),fg_color="#8E1616",anchor='w',corner_radius=5,text_color="#EEEEEE")
                            popup_label.place(x=5,y=5)
                                
                            popup_close = CTkButton(master=popup,width=30,height=30,text="X",text_color="#EEEEEE",font=(CTkFont(size=20)),command=popup_closef,corner_radius=0,fg_color="#8E1616",hover_color="#7E1414")
                            popup_close.place(x=160,y=10)
            Config_Import = CTkButton(master=frame_show,text="Import Config",command=lambda: import_config(Pastebin_Code.get("0.0", "end-1c")) ,text_color="#EEEEEE",width=175,height=28,fg_color="#8E1616",hover_color="#841414")
            Config_Import.place(x=20,y=120+220)
    def show_base_settings(self,task):
        if ".py" in task:
            #print((f"{self.task.replace(" ", "_").replace("__","_")}0.py"))
            if not self.is_open_ds and self.task != "" and task == f"{self.task.replace(" ", "_").replace("__","_")}0.py":
                
                frame_show = CTkFrame(master=self.app,width=700,height=600,fg_color="#1D1616",corner_radius=5,border_width=1,border_color="#D84040")
                frame_show.place(relx=0.5,rely=0.5,anchor="center")    
                frame_show.lift()
        
                def close():
                    self.is_open_ds = False
                    frame_show.destroy()
                    
                frame_label = CTkLabel(master=frame_show,height=70,width=690,text=task,font=CTkFont(size=30),fg_color="#8E1616",anchor='w',corner_radius=5,text_color="#EEEEEE")
                frame_label.place(x=5,y=5)
            
                
                frame_close = CTkButton(master=frame_show,width=30,height=30,text="X",text_color="#EEEEEE",font=(CTkFont(size=20)),command=close,corner_radius=0,fg_color="#8E1616",hover_color="#7E1414")
                frame_close.place(x=660,y=10)
                
                setting_container = CTkScrollableFrame(master=frame_show,width=660,height=495,bg_color="#2A2121")
                setting_container.place(x=9,y=85)
                
                setting_json = None
                json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Settings", self.path_to_task.split("\\")[::-1][1], self.path_to_task.split("\\")[::-1][0].replace("_0.py", ".json"))

                if os.path.exists(json_path):
                    print("path exists")
                    setting_json = load_json(json_path)
                    def save_setting(key, value):
                        try:
                            
                            print(f"{type(value)}: {value}")
                            if key != "selected" or key != "Down_Time_Task" or key!= "USE_AINZ_UNIT":
                                value = ast.literal_eval(value)
                            print(f"{type(value)}: {value}")
                            print(key,value)
                            setting_json[key] = value
                            print(setting_json.get(key))
                            update_settings(setting_json, json_path)
                        except Exception as e:
                            print(f"error {e}")
                    SCC = 0
                    SRR = 0
                    for key in setting_json.keys():   
                        if key != "Name":
                            setting_container.grid_columnconfigure(SRR, weight=1)
                            templ = CTkFrame(master=setting_container,height=200,width=300,corner_radius=2,fg_color="#262626")
                            templ.grid_columnconfigure(0, weight=1)
                            label = CTkLabel(master=templ,text=key,anchor='w',font=CTkFont(size=18),text_color="white",fg_color="#191919", corner_radius=5,width=200,height=28)
                            label.grid(row=0, column=0, padx=0, pady=0, sticky="ew")
                            test = CTkTextbox(master=templ,width=180,height=50,corner_radius=5,font=CTkFont(family="Consolas",size=13))
                            test.insert("0.0", str(setting_json[key]))
                            test.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
                            test2 = CTkButton(master=templ,text="Set",command=lambda key=key, textbox=test: save_setting(key, textbox.get("0.0", "end-1c")),height=28,corner_radius=5,font=CTkFont(size=13),fg_color="#8E1616",hover_color="#841414")
                            test2.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")
                            templ.grid(row=SCC, column=SRR, padx=5, pady=5, sticky="ew")
                            if SRR < 1:
                                SRR+=1
                            elif SRR == 1:
                                SCC+=1
                                SRR = 0
                else:
                    print("error")
                self.is_open_ds = True

    def upd_count(self):
        p_wins = 0
        p_losses = 0
        while True:
            while self.task_process is None:
                time.sleep(1)
            cur_state = load_state()         
            wins = cur_state["wins"]
            losses = cur_state["losses"]
            try:
                if wins > p_wins:
                    p_wins = wins
                    Webhook.send_webhook(self.runtime.cget("text").replace("Runtime: ", ""), wins, losses, task_name=self.task, img=wt.screen_shot_memory())
                elif losses > p_losses:
                    p_losses = losses
                    Webhook.send_webhook(self.runtime.cget("text"), wins, losses, task_name=self.task, img=wt.screen_shot_memory())
            except Exception as e:
                print(e)
            self.wins.configure(text=f"Wins: {wins}")
            self.losses.configure(text=f"Losses: {losses}")
            time.sleep(2)
            

    def print_output(self):
        while True:
            cur_line = self.get_logs()
            if "STREAM b" not in cur_line:
                self.code_output.configure(state="normal")
                self.code_output.insert("end", cur_line)
                self.code_output.see("end")
                self.code_output.configure(state="disabled")
            if self.task_process is not None:
                for line in self.task_process.stdout:
                    print(line.strip())
                    self.code_output.configure(state="normal")
                    self.code_output.insert("end", line)
                    self.code_output.see("end")
                    self.code_output.configure(state="disabled")
            time.sleep(1)
    def get_logs(self):
        global last_pos
        print_buffer.seek(last_pos)
        new_info = print_buffer.read()
        last_pos = print_buffer.tell()
        print_buffer.seek(0, io.SEEK_END)
        return new_info
    def set_task(self, task):
        j = load_state()
        j["num_runs"] = 0
        j["wins"] = 0
        j["losses"] = 0
        update_state(j)
        if self.task_process is not None or len(load_pid()["pid"]) > 0:
            try:
                self.task_process.terminate()
            except Exception as e:
                print(e)
            kill_pids()
            self.task_running = False
        self.task = "".join([step for step in task if not f"{step}".isdigit()]).replace("_"," ").replace(".py", " ")
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"Tasks")
        find = False
        for folder in os.listdir(self.config_path):
            if find:
                break
            for file in os.listdir(os.path.join(self.config_path, folder)):
                if file == task:
                    self.path_to_task = os.path.join(self.config_path, folder, file)
                    find = True
                    break
        print(self.path_to_task)
        print(self.path_to_task.split("\\")[::-1][0])
        self.task_name_player.configure(text=f"Task: {self.task}")
        print(f"Set Task to {self.task}")
        
    def runtime_counter(self):
        start = None
        while True:
            while self.task_running:
                if start is None:
                    start = datetime.now()
                runtime = datetime.now()-start
                self.runtime.configure(text=f"Runtime: {str(runtime).split('.')[0]}")
                while self.run_event.is_set():
                    if start is not None:
                        start = None
                    time.sleep(0.5)
                time.sleep(1)
            time.sleep(0.5)
        
        
    def start_macro(self, x):
        if self.task != "":
            self.run_event.clear()
            j = load_state()
            j['running'] = True
            j['task_path'] = self.path_to_task
            print(j['task_path'])
            if not self.task_running or len(load_pid()["pid"]) == 0:
                kill_pids()
                self.task_running = True
                self.task_process = Handler.run_task(self.path_to_task)
            update_state(j)
    
    def stop_macro(self, x):
        self.run_event.set()
        j = load_state()
        j['running'] = False
        j['task_path'] = ""
        update_state(j)
    def kill_macro(self,x):
        self.run_event.set()
        j = load_state()
        j['running'] = False
        j['task_path'] = ""
        try:
            self.task_process.terminate()
        except Exception:
            pass
        self.task_process = None
        kill_pids()
        update_state(j)    
    def pos_rb(self, x):
        try:
            window = wt.get_window("Roblox") # Get roblox window
            roblox_window = window
            print(roblox_window)
            wt.resize_window(roblox_window, 816, 638)  # Resize window
            wt.move_window(roblox_window, self.roblox_cut_out.winfo_rootx()-15, self.roblox_cut_out.winfo_rooty()-32)
            wt.activate_window(window=window)
            time.sleep(0.5)
        except Exception as e:
            print(e)
    def show_position_debug(self,x):
        print("debug")
        if self.config_path != "":
            self.show_debug = not self.show_debug
            if self.show_debug:
                window = wt.get_window("Roblox")
                offset = (window.left,window.top)
                json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Settings", self.path_to_task.split("\\")[::-1][1], self.path_to_task.split("\\")[::-1][0].replace("_0.py", ".json"))
                if not os.path.exists(json_path):
                    return
                if json_path.split("\\")[-1] == "Winter.json":
                    loaded_config = load_json(json_path)
                    Units = []
                    for unit in loaded_config["Unit_Positions"][0].keys():
                        Units+=[loaded_config["Unit_Positions"][0][unit]]
                else:
                    loaded_config = load_json(json_path)
                    selection = loaded_config["configs"][loaded_config["selected"]]
                    Units = []
                    for unit in selection["Units"].keys():
                        Units+=[selection["Units"][unit]["placements"]]
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
                        canvas.delete("all")
                        for i, b in enumerate(Units):
                            for j, box in enumerate(b):
                                if type(box) is type([]) and len(box)>=2:
                                    canvas.create_text(
                                                box[0]+offset[0], box[1]+offset[1]-16, 
                                                text=f"Unit-{i+1}", 
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
                        while self.show_debug:
                            time.sleep(0.5)
                        overlay.destroy()
                        return
                    Thread(target=update_overlay, daemon=True).start()
                    overlay.mainloop()
                Thread(target=debug,daemon=True).start()
    
    def start_app(self):
        self.app.mainloop()   
Window = MainWindow()
Window.start_app()





