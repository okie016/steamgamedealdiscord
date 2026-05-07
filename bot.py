import requests
import json
import os
from datetime import datetime, timezone

DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]
NOTIFIED_FILE   = "notified.json"
MIN_DISCOUNT    = 50  # แจ้งเฉพาะลด >= 50% (แก้ตรงนี้ได้)

def load_notified():
    if os.path.exists(NOTIFIED_FILE):
        with open(NOTIFIED_FILE) as f:
            return json.load(f)
    return []

def save_notified(data):
    with open(NOTIFIED_FILE, "w") as f:
        json.dump(data, f)

def send_discord(game):
    payload = {
        "embeds": [{
            "title": game['name'],                    # ✅ เอา emoji ออก
            "url": game["url"],
            "color": 0x1b2838,
            "timestamp": datetime.now(timezone.utc).isoformat(),  # ✅ แก้ timestamp
            "fields": [
                {"name": "ส่วนลด",  "value": f"**{game['discount']}% OFF**",                                      "inline": True},
                {"name": "ราคา",    "value": f"~~฿{game['original_price']:.0f}~~ → **฿{game['final_price']:.0f}**", "inline": True},
            ],
            "image": {                                # ✅ ย้าย header มาเป็น banner ใหญ่
                "url": f"https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/{game['id']}/header.jpg"
            },
                                                      # ✅ ลบ thumbnail ออกแล้ว
            "footer": {"text": "Steam Sale Alert"}
        }]
    }
    res = requests.post(DISCORD_WEBHOOK, json=payload)
    res.raise_for_status()

def get_steam_deals():
    url = "https://store.steampowered.com/api/featuredcategories/?cc=th&l=thai"
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    data = res.json()

    deals = []
    for item in data.get("specials", {}).get("items", []):
        discount = item.get("discount_percent", 0)
        if discount >= MIN_DISCOUNT:
            deals.append({
                "id":             str(item["id"]),
                "name":           item["name"],
                "discount":       discount,
                "final_price":    item["final_price"] / 100,
                "original_price": item["original_price"] / 100,
                "url":            f"https://store.steampowered.com/app/{item['id']}/",
            })
    return deals

def test_discord():
    send_discord({
        "id": "1245620",
        "name": "Elden Ring",
        "discount": 75,
        "final_price": 374,
        "original_price": 1499,
        "url": "https://store.steampowered.com/app/1245620/",
    })
    print("Test sent!")

if __name__ == "__main__":
    test_discord()   # ← เปลี่ยนชั่วคราว (ปกติคือ main())
