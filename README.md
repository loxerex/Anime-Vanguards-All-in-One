
# **Anime‑Vanguards All‑in‑One (AIO) Macro**

All‑in‑one macro tool for Anime Vanguards.  
Too lazy to write a full essay, so watch the YouTube tutorial if you want the full walkthrough:  
https://www.youtube.com/@macroLoxer

This repo **does NOT** include:
- the simple launcher  
- the portable Python distribution  
- pytesseract  

The launcher is literally a 3‑line batch script that runs the Python files using the Python interpreter inside the Python dist.

# **Config Creator**
---

## **Default Hotkeys (VK → Actual Key)**  
These are the default shortcuts the macro listens for.  
Each number is a **Virtual‑Key (VK) code**, translated below into the real keyboard key.

| Action | VK Code | Actual Key |
|-------|---------|------------|
| Load Previous Config | **36** | **Home** |
| Position Right‑Bottom | **112** | **F1** |
| Run Config | **114** | **F3** |
| Stop Macro | **115** | **F4** |
| Auto‑Position | **116** | **F5** |
| Kill Macro | **117** | **F6** |
| Set Map | **118** | **F7** |
| Export Config | **119** | **F8** |
| Import Config | **120** | **F9** |
| Add Order | **45** | **Insert** |
| Log Mouse Position | **190** | **. (Period)** |
| Stop Logging Mouse Position | **78** | **N** |

---

## **Mouse Position Logging **  
To record mouse positions for placements, you must:

1. Click **“Log Mouse Positions”** in the UI  
2. Press the **Log Mouse Position key** (`.` by default) to save each coordinate  
3. Press the **Stop Logging key** (`N` by default) to finish  

If you don’t click the button first, the hotkeys won’t do anything.

---

## **Config Creator**
The Config Creator lets you build configs visually instead of editing JSON manually.

### What you can do:
- Add placements, upgrades, abilities, delays, and logic  
- Set map + auto‑position  
- Use the AI assistant in the **Help** tab to explain fields or fix errors  
- you MUST provide your own api key.

### Required step:
**You must export a config before running it.**  
The macro runs the last exported config in CurrentConfig.json, so make sure to export before running it

### Basic workflow:
1. Open the AIO tool  
2. Go to **Config Creator**  
3. Add your orders  
4. Set map + auto‑position  
5. Export the config (**F8**)  
6. Run it (**F3**)  

---

If you want, I can also generate a polished full README with badges, screenshots, and a feature list.
