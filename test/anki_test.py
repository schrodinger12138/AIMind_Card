import os
import json
import requests

ANKI_CONNECT_URL = "http://localhost:8765"
ANKI_CONNECT_VERSION = 6

def invoke(action, params=None):
    payload = {
        "action": action,
        "version": ANKI_CONNECT_VERSION,
        "params": params or {}
    }
    r = requests.post(ANKI_CONNECT_URL, json=payload)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data["result"]

def find_json_file():
    """在当前目录及子目录下查找 JSON 文件"""
    for root, _, files in os.walk("."):
        for f in files:
            if f.lower() == "card.json":
                return os.path.join(root, f)
        for f in files:
            if f.lower().endswith(".json"):
                return os.path.join(root, f)
    return None

def create_deck(deck_name):
    try:
        invoke("createDeck", {"deck": deck_name})
    except Exception as e:
        print(f"创建牌组时出错：{e}")

def add_note(deck_name, front, back, tags=None):
    note = {
        "deckName": deck_name,
        "modelName": "Basic",
        "fields": {"Front": front, "Back": back},
        "options": {"allowDuplicate": False},
        "tags": tags or []
    }
    return invoke("addNote", {"note": note})

def sanitize_tag(s):
    return "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in str(s))[:50]

def main():
    json_path = find_json_file()
    if not json_path:
        print("❌ 未找到任何 JSON 文件，请将 card.json 放在当前目录或子目录下。")
        return

    print(f"✅ 找到 JSON 文件：{json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cards = data.get("cards", [])
    if not cards:
        print("❌ JSON 文件中未找到 'cards' 列表。")
        return

    deck_name = "card_json_import"
    create_deck(deck_name)

    added, skipped, errors = 0, 0, 0

    for c in cards:
        title = c.get("title", "")
        q = c.get("question", "")
        a = c.get("answer", "")
        front = f"<b>{title}</b><br><br>{q}" if title else q
        back = a
        tags = ["imported_json"]
        if c.get("id"):
            tags.append(f"id_{c['id']}")
        tags.append(sanitize_tag(title))

        try:
            note_id = add_note(deck_name, front, back, tags)
            print(f"✅ 已添加卡片：{title} (note_id={note_id})")
            added += 1
        except Exception as e:
            msg = str(e).lower()
            if "duplicate" in msg:
                print(f"⚠️ 跳过重复卡片：{title}")
                skipped += 1
            else:
                print(f"❌ 添加失败：{title} -> {e}")
                errors += 1

    print(f"\n📊 导入完成：共 {len(cards)} 张 | 成功 {added} | 跳过 {skipped} | 错误 {errors}")

if __name__ == "__main__":
    main()
