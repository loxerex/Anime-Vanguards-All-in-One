import discord
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DiscordBot import BotStates
from Tools import winTools as wt
from discord import app_commands
import asyncio
import json


import psutil
import subprocess


# DISCORD TOKEN, DO NOT SHARE.
token = ""


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

def load_json(json_path):
    with open(json_path, "r") as file:
        return json.load(file)

id = load_json(os.path.join(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))), "Settings", "AIO_Settings.json"))["Discord_Server"]
GUILD = discord.Object(id=id)

class Client(discord.Client):
    user: discord.ClientUser
    
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.synced = False
    async def setup_hook(self):
        if not self.synced:
            self.tree.copy_global_to(guild=GUILD)
            await self.tree.sync(guild=GUILD)
            self.synced = True
            
        
client = Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot Online: {client.user}')


@client.tree.command()
async def check_macro(inter: discord.Interaction):
    """Sends a screenshot of your macro"""
    await inter.response.defer()
    window = wt.get_window("AIO")
    buffer = wt.screen_shot_memory(window=window)
    file = discord.File(buffer, filename="macro.png")
    await inter.followup.send(file=file)

@client.tree.command()
async def kill_task(inter: discord.Interaction):
    """Kills the current task process"""
    await BotStates.change_variable("kill",True)
    await inter.response.send_message("Killed Task",ephemeral=True)

@client.tree.command()
async def set_task(inter: discord.Interaction, gamemode: str, task:str):
    """Sets task given gamemode and name of task"""
    await BotStates.change_variable("set_task",[True, gamemode,task])
    await inter.response.send_message(content=f"Set task to: {task}",ephemeral=True)

@client.tree.command()
async def rejoin_roblox(inter: discord.Interaction):
    """Rejoins roblox"""
    await inter.response.defer()
    await BotStates.change_variable("kill",True)
    roblox_pid = None
    for process in psutil.process_iter(['pid', 'name']):
        try:
            if "robloxplayerbeta" in process.info['name'].lower():
                print(f"Found process: {process.info['name']}: {process.info['pid']} ")
                roblox_pid = process.info['pid']
                break
        except Exception as error:
            print(error)
    if roblox_pid is None:
        return
    r_process = psutil.Process(roblox_pid)
    subprocess.Popen([r_process.exe(), f"roblox://placeId={16146832113}&linkCode={21768692868330557785126702085399}/"])
    window = wt.get_window("AIO")
    await asyncio.sleep(10)
    buffer = wt.screen_shot_memory(window=window)
    file = discord.File(buffer, filename="macro.png")
    await inter.followup.send(content="Rejoined",file=file)
    
@client.tree.command()
async def run_task(inter: discord.Interaction):
    """Runs the task that was set"""
    await inter.response.send_message(content=f"Running Task",ephemeral=True)
    await BotStates.change_variable("run",True)
    
@client.tree.command()
async def close_aio(inter: discord.Interaction):
    """Closes the AIO"""
    await inter.response.send_message(content=f"Closed",ephemeral=True)
    await BotStates.change_variable("exit",True)




def start():
    client.run(token=token)

