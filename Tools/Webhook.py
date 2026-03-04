
import json
import requests
from datetime import datetime
import os

def load_settings():
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Settings", "AIO_Settings.json")
    with open(json_path, 'r') as file:
        return json.load(file)    

def send_webhook(run_time: str, win:int, lose:int, task_name: str, img):
    webhook_url = load_settings()["Settings"]["Webhook"]
    win_ratio = (win/(lose+win))*100
    if True:
        payload = {
            
    
        "username": "Loxer's Automation",
        "avatar_url": "https://media1.tenor.com/m/mbhL7DZmXEMAAAAC/%D0%B0%D0%B0%D0%B0%D0%B0.gif",
        "embeds": [
            {
            "title": "Loxer's Automation",
            "description": "",
            "color": 3447003,
            "fields": [
                {
                "name": "🕒 Run Time",
                "value": run_time,
                "inline": True
                },
                {
                "name": "⚔️ Wins",
                "value": win,
                "inline": True
                },
                {
                "name": "📈 Success Rate",
                "value": f"{win_ratio:.2f}%",
                "inline": True
                },
                {
                "name": "🔁 Total Runs",
                "value": win+lose,
                "inline": True
                },
                {
                "name": "⚙️ Current Task",
                "value": task_name
                }
            ],
            "image": {
                "url": "attachment://screenshot.png",
            },
            "thumbnail": {
                "url": "https://media1.tenor.com/m/1VbR3kVavicAAAAC/gin.gif",
            },
            "footer": {
                "text": f"Loxer's Automation | Run time: {run_time}",
                "icon_url": "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExcDRlMno0eXBhM2Uyb2hoYzJlYnJ6dW05NWQwdTE0dHd6MW9saXJ3eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/6UL3rqweR5Y2Jcrnqb/giphy.gif"
            },
            "timestamp": datetime.utcnow().isoformat()
            }
        ]
        }
        files = {
            "file": ("screenshot.png", img, "image/png")  # name must match attachment:// name
    
        }
        requests.post(webhook_url, data={"payload_json": json.dumps(payload)}, files=files)
        #print(response.status_code, response.text)
    else:
        print("Error, no wins or losses detected")
