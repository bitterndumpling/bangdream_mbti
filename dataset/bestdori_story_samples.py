import json
import re
import urllib.request
from pathlib import Path
from typing import List


SERVER = "cn"
LANG_INDEX = 3  # Simplified Chinese in Bestdori language arrays
USER_AGENT = "Mozilla/5.0 Codex"
OUTPUT_DIR = Path(__file__).resolve().parent / "story_samples"


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def fetch_json(url: str):
    return json.loads(fetch_text(url))


def fetch_asset(url: str):
    text = fetch_text(url)
    if not text.lstrip().startswith("{"):
        raise ValueError(f"Asset response is not JSON: {url}")
    return json.loads(text)["Base"]


def zh(value, default=""):
    if isinstance(value, list) and len(value) > LANG_INDEX and value[LANG_INDEX]:
        return value[LANG_INDEX]
    if isinstance(value, list):
        for item in value:
            if item:
                return item
    if isinstance(value, str):
        return value
    return default


def clean_text(text: str) -> str:
    if not text:
        return ""
    return text.replace("\r\n", "\n").replace("\r", "\n").replace("{{userName}}", "玩家").strip()


def split_dialogue(text: str):
    text = clean_text(text)
    if not text:
        return []

    parts = []
    for block in text.split("\n"):
        block = block.strip()
        if not block:
            continue

        start = 0
        for match in re.finditer(r"[。！？!?](?=[^」』”\"]|$)", block):
            end = match.end()
            piece = block[start:end].strip()
            if piece:
                parts.append(piece)
            start = end

        tail = block[start:].strip()
        if tail:
            parts.append(tail)

    return parts


def build_character_name_map():
    characters = fetch_json("https://bestdori.com/api/characters/all.5.json")
    name_map = {}
    for char_id, data in characters.items():
        display_name = zh(data.get("firstName")) or zh(data.get("characterName")) or zh(data.get("nickname"))
        if not display_name:
            display_name = str(char_id)
        name_map[int(char_id)] = display_name
    return name_map


def speaker_name(talk, name_map):
    display_name = clean_text(talk.get("windowDisplayName", ""))
    if display_name:
        return display_name

    talk_characters = talk.get("talkCharacters") or []
    names = []
    for item in talk_characters:
        character_id = item.get("characterId")
        if character_id in name_map:
            names.append(name_map[character_id])

    if names:
        return "/".join(dict.fromkeys(names))
    return "旁白"


def extract_lines(asset, name_map):
    lines = []
    snippets = asset.get("snippets", [])
    talk_data = asset.get("talkData", [])
    special_effect_data = asset.get("specialEffectData", [])

    for snippet in snippets:
        action_type = snippet.get("actionType")
        reference_index = snippet.get("referenceIndex")

        if action_type == 1 and reference_index is not None and reference_index < len(talk_data):
            talk = talk_data[reference_index]
            speaker = speaker_name(talk, name_map)
            for piece in split_dialogue(talk.get("body", "")):
                lines.append(f"{speaker}：{piece}")
        elif action_type == 6 and reference_index is not None and reference_index < len(special_effect_data):
            effect = special_effect_data[reference_index]
            if effect.get("effectType") == 8:
                location = clean_text(effect.get("stringVal", ""))
                if location:
                    lines.append(f"[场景] {location}")

    return lines


def write_sample(path: Path, title: str, metadata: List[str], lines: List[str]):
    body = [f"# {title}", ""]
    body.extend([f"- {item}" for item in metadata])
    body.append("")
    body.extend(lines)
    path.write_text("\n".join(body) + "\n", encoding="utf-8")


def generate_main_story_sample(name_map):
    stories = fetch_json("https://bestdori.com/api/misc/mainstories.5.json")
    story = stories["1"]
    scenario_id = story["scenarioId"]
    asset_url = f"https://bestdori.com/assets/{SERVER}/scenario/main_rip/Scenario{scenario_id}.asset"
    asset = fetch_asset(asset_url)
    title = f"{zh(story['caption'])}：{zh(story['title'])}"
    metadata = [
        "分类：主线故事",
        f"故事ID：1",
        f"Scenario ID：{scenario_id}",
        f"服务器：{SERVER}",
        f"来源：{asset_url}",
    ]
    output = OUTPUT_DIR / "sample_main_story_001.md"
    write_sample(output, title, metadata, extract_lines(asset, name_map))
    return output


def generate_band_story_sample(name_map):
    bands = fetch_json("https://bestdori.com/api/misc/bandstories.5.json")
    band_story = bands["1"]
    episode = band_story["stories"]["1"]
    scenario_id = episode["scenarioId"]
    band_id = int(band_story["bandId"])
    asset_url = (
        f"https://bestdori.com/assets/{SERVER}/scenario/band/{band_id:03d}_rip/Scenario{scenario_id}.asset"
    )
    asset = fetch_asset(asset_url)
    title = f"{zh(band_story['mainTitle'])} {zh(band_story['subTitle'])} / {zh(episode['caption'])}：{zh(episode['title'])}"
    metadata = [
        "分类：乐团故事",
        f"乐团ID：{band_id}",
        "故事组ID：1",
        "章节ID：1",
        f"Scenario ID：{scenario_id}",
        f"服务器：{SERVER}",
        f"来源：{asset_url}",
    ]
    output = OUTPUT_DIR / "sample_band_story_001_001.md"
    write_sample(output, title, metadata, extract_lines(asset, name_map))
    return output


def generate_card_story_sample(name_map):
    card = fetch_json("https://bestdori.com/api/cards/1.json")
    episode = card["episodes"]["entries"][0]
    scenario_id = episode["scenarioId"]
    resource_set_name = card["resourceSetName"]
    asset_url = (
        f"https://bestdori.com/assets/{SERVER}/characters/resourceset/{resource_set_name}_rip/Scenario{scenario_id}.asset"
    )
    asset = fetch_asset(asset_url)
    character_name = name_map.get(int(card["characterId"]), str(card["characterId"]))
    title = f"{character_name} / {zh(card['prefix'])} / {zh(episode['title'])}"
    metadata = [
        "分类：卡牌故事",
        "卡牌ID：1",
        "Episode 序号：1",
        f"Scenario ID：{scenario_id}",
        f"资源包：{resource_set_name}",
        f"服务器：{SERVER}",
        f"来源：{asset_url}",
    ]
    output = OUTPUT_DIR / "sample_card_story_0001_ep01.md"
    write_sample(output, title, metadata, extract_lines(asset, name_map))
    return output


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    name_map = build_character_name_map()
    outputs = [
        generate_main_story_sample(name_map),
        generate_band_story_sample(name_map),
        generate_card_story_sample(name_map),
    ]
    for output in outputs:
        print(output)


if __name__ == "__main__":
    main()
