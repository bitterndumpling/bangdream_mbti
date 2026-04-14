import argparse
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional


SERVER = "cn"
LANG_INDEX = 3
USER_AGENT = "Mozilla/5.0 Codex"
ROOT_DIR = Path(__file__).resolve().parent / "bestdori_cn_markdown"
REPORTS_DIR = ROOT_DIR / "_reports"


def zh(value, default=""):
    if isinstance(value, list):
        if len(value) > LANG_INDEX and value[LANG_INDEX]:
            return value[LANG_INDEX]
        for item in value:
            if item:
                return item
        return default
    if isinstance(value, str):
        return value
    return default


def clean_text(text):
    if not text:
        return ""
    return (
        text.replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("{{userName}}", "玩家")
        .strip()
    )


def split_dialogue(text):
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


def ascii_slug(text, fallback):
    text = clean_text(text)
    text = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return text or fallback


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)
    return path


class ThrottledClient(object):
    def __init__(self, delay, retries):
        self.delay = delay
        self.retries = retries
        self.last_request_at = 0.0

    def _wait(self):
        elapsed = time.time() - self.last_request_at
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

    def fetch_text(self, url):
        last_error = None
        for attempt in range(1, self.retries + 1):
            self._wait()
            self.last_request_at = time.time()
            try:
                request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(request, timeout=30) as response:
                    return response.read().decode("utf-8")
            except Exception as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(self.delay * attempt * 2)
        raise last_error

    def fetch_json(self, url):
        return json.loads(self.fetch_text(url))

    def fetch_asset(self, url):
        text = self.fetch_text(url)
        if not text.lstrip().startswith("{"):
            raise ValueError("Asset response is not JSON: %s" % url)
        return json.loads(text)["Base"]


class CrawlContext(object):
    def __init__(self, client):
        self.client = client
        self.errors = []
        self.character_map = {}
        self.band_map = {}
        self.card_meta_map = {}

    def record_error(self, category, item_id, message, url):
        self.errors.append(
            {
                "category": category,
                "item_id": str(item_id),
                "message": str(message),
                "url": url,
            }
        )

    def save_errors(self):
        ensure_dir(REPORTS_DIR)
        path = REPORTS_DIR / "errors.json"
        path.write_text(json.dumps(self.errors, ensure_ascii=False, indent=2), encoding="utf-8")


def write_markdown(path, title, metadata, lines):
    body = ["# %s" % title, ""]
    for line in metadata:
        body.append("- %s" % line)
    body.append("")
    if lines:
        body.extend(lines)
    else:
        body.append("[未提取到对白]")
    path.write_text("\n".join(body) + "\n", encoding="utf-8")


def extract_lines(asset, character_map):
    lines = []
    snippets = asset.get("snippets", [])
    talk_data = asset.get("talkData", [])
    special_effect_data = asset.get("specialEffectData", [])

    for snippet in snippets:
        action_type = snippet.get("actionType")
        reference_index = snippet.get("referenceIndex")

        if action_type == 1 and reference_index is not None and reference_index < len(talk_data):
            talk = talk_data[reference_index]
            name = clean_text(talk.get("windowDisplayName", ""))
            if not name:
                names = []
                for talk_character in talk.get("talkCharacters") or []:
                    character_id = talk_character.get("characterId")
                    if character_id in character_map:
                        names.append(character_map[character_id]["display_name"])
                if names:
                    name = "/".join(list(dict.fromkeys(names)))
                else:
                    name = "旁白"

            for sentence in split_dialogue(talk.get("body", "")):
                lines.append("%s：%s" % (name, sentence))

        elif action_type == 6 and reference_index is not None and reference_index < len(special_effect_data):
            effect = special_effect_data[reference_index]
            if effect.get("effectType") == 8:
                location = clean_text(effect.get("stringVal", ""))
                if location:
                    lines.append("[场景] %s" % location)

    return lines


def load_reference_data(ctx):
    characters = ctx.client.fetch_json("https://bestdori.com/api/characters/all.5.json")
    bands = ctx.client.fetch_json("https://bestdori.com/api/bands/main.1.json")
    cards = ctx.client.fetch_json("https://bestdori.com/api/cards/all.5.json")

    band_map = {}
    for band_id, band in bands.items():
        band_id_int = int(band_id)
        band_name_zh = zh(band.get("bandName"), "乐团%s" % band_id)
        band_name_list = band.get("bandName") or []
        band_name_en = band_name_list[1] if isinstance(band_name_list, list) and len(band_name_list) > 1 and band_name_list[1] else "band_%s" % band_id
        band_map[band_id_int] = {
            "id": band_id_int,
            "display_name": band_name_zh,
            "slug": "band_%03d_%s" % (band_id_int, ascii_slug(band_name_en, "band_%s" % band_id)),
        }

    character_map = {}
    for character_id, character in characters.items():
        character_id_int = int(character_id)
        display_name = zh(character.get("firstName")) or zh(character.get("characterName")) or "角色%s" % character_id
        first_name_list = character.get("firstName") or []
        english_name = first_name_list[1] if isinstance(first_name_list, list) and len(first_name_list) > 1 and first_name_list[1] else "char_%s" % character_id
        band_id = int(character.get("bandId") or 0)
        character_map[character_id_int] = {
            "id": character_id_int,
            "display_name": display_name,
            "band_id": band_id,
            "slug": "char_%03d_%s" % (character_id_int, ascii_slug(english_name, "char_%s" % character_id)),
        }

    card_meta_map = {}
    for card_id, card in cards.items():
        card_meta_map[int(card_id)] = card

    ctx.character_map = character_map
    ctx.band_map = band_map
    ctx.card_meta_map = card_meta_map


def band_directory(ctx, band_id):
    band = ctx.band_map.get(band_id)
    if band:
        return ROOT_DIR / "band_story" / band["slug"]
    return ROOT_DIR / "band_story" / ("band_%03d_other" % band_id)


def card_band_directory(ctx, band_id):
    band = ctx.band_map.get(band_id)
    if band:
        return ROOT_DIR / "card_story" / band["slug"]
    return ROOT_DIR / "card_story" / ("band_%03d_other" % band_id)


def main_story_path(story_id):
    return ROOT_DIR / "main_story" / ("main_%04d.md" % story_id)


def write_main_story(ctx):
    ensure_dir(ROOT_DIR / "main_story")
    stories = ctx.client.fetch_json("https://bestdori.com/api/misc/mainstories.5.json")
    story_ids = sorted(int(key) for key in stories.keys())
    processed = 0

    for story_id in story_ids:
        story = stories[str(story_id)]
        published_at = story.get("publishedAt") or []
        if len(published_at) <= LANG_INDEX or not published_at[LANG_INDEX]:
            continue

        scenario_id = story.get("scenarioId")
        asset_url = "https://bestdori.com/assets/%s/scenario/main_rip/Scenario%s.asset" % (SERVER, scenario_id)
        output_path = main_story_path(story_id)

        if output_path.exists():
            processed += 1
            continue

        try:
            asset = ctx.client.fetch_asset(asset_url)
            title = "%s：%s" % (zh(story.get("caption")), zh(story.get("title")))
            metadata = [
                "分类：主线故事",
                "故事ID：%s" % story_id,
                "Scenario ID：%s" % scenario_id,
                "服务器：%s" % SERVER,
                "来源：%s" % asset_url,
            ]
            write_markdown(output_path, title, metadata, extract_lines(asset, ctx.character_map))
            processed += 1
        except Exception as exc:
            ctx.record_error("main_story", story_id, exc, asset_url)

    print("main_story_done=%s" % processed)


def write_band_story(ctx):
    ensure_dir(ROOT_DIR / "band_story")
    stories = ctx.client.fetch_json("https://bestdori.com/api/misc/bandstories.5.json")
    group_ids = sorted(int(key) for key in stories.keys())
    processed = 0

    for group_id in group_ids:
        group = stories[str(group_id)]
        band_id = int(group.get("bandId") or 0)
        chapter_number = int(group.get("chapterNumber") or 0)
        chapter_dir = ensure_dir(band_directory(ctx, band_id) / ("chapter_%02d" % chapter_number))
        story_ids = sorted(int(key) for key in group.get("stories", {}).keys())

        for story_id in story_ids:
            story = group["stories"][str(story_id)]
            published_at = story.get("publishedAt") or []
            if len(published_at) <= LANG_INDEX or not published_at[LANG_INDEX]:
                continue

            scenario_id = story.get("scenarioId")
            asset_url = "https://bestdori.com/assets/%s/scenario/band/%03d_rip/Scenario%s.asset" % (
                SERVER,
                band_id,
                scenario_id,
            )
            output_path = chapter_dir / ("story_%03d.md" % story_id)

            if output_path.exists():
                processed += 1
                continue

            try:
                asset = ctx.client.fetch_asset(asset_url)
                group_title = "%s %s" % (zh(group.get("mainTitle")), zh(group.get("subTitle")))
                title = "%s / %s：%s" % (group_title, zh(story.get("caption")), zh(story.get("title")))
                metadata = [
                    "分类：乐团故事",
                    "故事组ID：%s" % group_id,
                    "乐团ID：%s" % band_id,
                    "章节：%s" % chapter_number,
                    "章节内故事ID：%s" % story_id,
                    "Scenario ID：%s" % scenario_id,
                    "服务器：%s" % SERVER,
                    "来源：%s" % asset_url,
                ]
                write_markdown(output_path, title, metadata, extract_lines(asset, ctx.character_map))
                processed += 1
            except Exception as exc:
                ctx.record_error("band_story", "%s-%s" % (group_id, story_id), exc, asset_url)

    print("band_story_done=%s" % processed)


def card_story_candidate_ids(ctx, start_id, end_id):
    ids = sorted(ctx.card_meta_map.keys())
    result = []
    for card_id in ids:
        if start_id and card_id < start_id:
            continue
        if end_id and card_id > end_id:
            continue

        card = ctx.card_meta_map[card_id]
        released_at = card.get("releasedAt") or []
        if len(released_at) <= LANG_INDEX or not released_at[LANG_INDEX]:
            continue
        if not card.get("resourceSetName"):
            continue
        result.append(card_id)
    return result


def write_card_story(ctx, start_id=None, end_id=None):
    ensure_dir(ROOT_DIR / "card_story")
    candidate_ids = card_story_candidate_ids(ctx, start_id, end_id)
    total = len(candidate_ids)
    processed_files = 0

    for index, card_id in enumerate(candidate_ids, 1):
        meta = ctx.card_meta_map[card_id]
        detail_url = "https://bestdori.com/api/cards/%s.json" % card_id

        try:
            detail = ctx.client.fetch_json(detail_url)
        except Exception as exc:
            ctx.record_error("card_story_meta", card_id, exc, detail_url)
            continue

        character_id = int(detail.get("characterId") or meta.get("characterId") or 0)
        character = ctx.character_map.get(character_id, {})
        band_id = int(character.get("band_id") or 0)
        character_dir = ensure_dir(card_band_directory(ctx, band_id) / character.get("slug", "char_%03d" % character_id))

        episodes = (((detail.get("episodes") or {}).get("entries")) or [])
        if not episodes:
            continue

        resource_set_name = detail.get("resourceSetName") or meta.get("resourceSetName")
        prefix_text = zh(detail.get("prefix") or meta.get("prefix"), "卡牌%s" % card_id)

        for episode_index, episode in enumerate(episodes, 1):
            scenario_id = episode.get("scenarioId")
            if not scenario_id:
                continue

            asset_url = "https://bestdori.com/assets/%s/characters/resourceset/%s_rip/Scenario%s.asset" % (
                SERVER,
                resource_set_name,
                scenario_id,
            )
            output_path = character_dir / ("card_%06d_episode_%02d.md" % (card_id, episode_index))

            if output_path.exists():
                processed_files += 1
                continue

            try:
                asset = ctx.client.fetch_asset(asset_url)
                title = "%s / %s / %s" % (
                    character.get("display_name", "角色%s" % character_id),
                    prefix_text,
                    zh(episode.get("title"), "Episode %02d" % episode_index),
                )
                metadata = [
                    "分类：卡牌故事",
                    "卡牌ID：%s" % card_id,
                    "角色ID：%s" % character_id,
                    "Episode 序号：%s" % episode_index,
                    "Episode 类型：%s" % episode.get("episodeType", ""),
                    "Scenario ID：%s" % scenario_id,
                    "资源包：%s" % resource_set_name,
                    "服务器：%s" % SERVER,
                    "来源：%s" % asset_url,
                ]
                write_markdown(output_path, title, metadata, extract_lines(asset, ctx.character_map))
                processed_files += 1
            except Exception as exc:
                ctx.record_error("card_story_asset", "%s-%s" % (card_id, episode_index), exc, asset_url)

        if index % 25 == 0 or index == total:
            print("card_progress=%s/%s files=%s" % (index, total, processed_files))

    print("card_story_done=%s" % processed_files)


def count_markdown_files(path):
    if not path.exists():
        return 0
    return len(list(path.rglob("*.md")))


def write_index_files(ctx):
    ensure_dir(ROOT_DIR)
    ensure_dir(REPORTS_DIR)

    main_count = count_markdown_files(ROOT_DIR / "main_story")
    band_count = count_markdown_files(ROOT_DIR / "band_story")
    card_count = count_markdown_files(ROOT_DIR / "card_story")

    band_summary = []
    card_summary = []
    for band_id, band in sorted(ctx.band_map.items()):
        band_story_dir = ROOT_DIR / "band_story" / band["slug"]
        card_story_dir = ROOT_DIR / "card_story" / band["slug"]
        band_story_count = count_markdown_files(band_story_dir)
        card_story_count = count_markdown_files(card_story_dir)
        if band_story_count:
            band_summary.append("- %s：%s 个文件" % (band["display_name"], band_story_count))
        if card_story_count:
            card_summary.append("- %s：%s 个文件" % (band["display_name"], card_story_count))

    readme_lines = [
        "# Bestdori 中文剧情导出",
        "",
        "- 服务器：%s" % SERVER,
        "- 主线故事文件数：%s" % main_count,
        "- 乐团故事文件数：%s" % band_count,
        "- 卡牌故事文件数：%s" % card_count,
        "- 输出格式：Markdown",
        "",
        "## 目录结构",
        "",
        "- `main_story/`：主线故事",
        "- `band_story/`：按乐团、章节分类的乐团故事",
        "- `card_story/`：按乐团、角色分类的卡牌故事",
        "- `_reports/errors.json`：抓取失败记录",
        "",
        "## 乐团故事统计",
        "",
    ]
    readme_lines.extend(band_summary or ["- 暂无"])
    readme_lines.extend(["", "## 卡牌故事统计", ""])
    readme_lines.extend(card_summary or ["- 暂无"])
    readme_lines.append("")
    (ROOT_DIR / "README.md").write_text("\n".join(readme_lines) + "\n", encoding="utf-8")

    summary = {
        "server": SERVER,
        "main_story_files": main_count,
        "band_story_files": band_count,
        "card_story_files": card_count,
        "error_count": len(ctx.errors),
    }
    (REPORTS_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    ctx.save_errors()
    print("finalize_done=1")


def parse_args():
    parser = argparse.ArgumentParser(description="Crawl Bestdori CN stories into Markdown.")
    parser.add_argument(
        "--category",
        choices=["all", "main", "band", "card", "finalize"],
        default="all",
    )
    parser.add_argument("--card-start", type=int, default=0)
    parser.add_argument("--card-end", type=int, default=0)
    parser.add_argument("--delay", type=float, default=0.18)
    parser.add_argument("--retries", type=int, default=3)
    return parser.parse_args()


def main():
    args = parse_args()
    ensure_dir(ROOT_DIR)
    ensure_dir(REPORTS_DIR)

    client = ThrottledClient(delay=args.delay, retries=args.retries)
    ctx = CrawlContext(client)
    load_reference_data(ctx)

    if args.category in ("all", "main"):
        write_main_story(ctx)
    if args.category in ("all", "band"):
        write_band_story(ctx)
    if args.category in ("all", "card"):
        write_card_story(ctx, start_id=args.card_start or None, end_id=args.card_end or None)
    if args.category in ("all", "finalize"):
        write_index_files(ctx)


if __name__ == "__main__":
    main()
