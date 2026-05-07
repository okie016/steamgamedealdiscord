import requests
import json
import os

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
            "title": f"🎮 {game['name']}",
            "url": game["url"],
            "color": 0x1b2838,
            "fields": [
                {"name": "ส่วนลด",  "value": f"**{game['discount']}% OFF**",                              "inline": True},
                {"name": "ราคา",    "value": f"~~฿{game['original_price']:.0f}~~ → **฿{game['final_price']:.0f}**", "inline": True},
            ],
            "thumbnail": {"url": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{game['id']}/header.jpg"},
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

def main():
    notified    = load_notified()
    deals       = get_steam_deals()
    new_notified = list(notified)

    sent = 0
    for game in deals:
        if game["id"] in notified:
            print(f"Skip (already sent): {game['name']}")
            continue
        send_discord(game)
        new_notified.append(game["id"])
        print(f"✅ Sent: {game['name']} -{game['discount']}%")
        sent += 1

    save_notified(new_notified)
    print(f"\nDone — {sent} new deal(s) sent out of {len(deals)} found.")

if __name__ == "__main__":
    main()
