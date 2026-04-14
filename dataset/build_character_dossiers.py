import json
import re
from collections import Counter, defaultdict
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parent / "bestdori_cn_markdown"
OUTPUT_ROOT = Path(__file__).resolve().parent / "character_dossiers"


def ascii_slug(text, fallback):
    text = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return text or fallback


def safe_text(text):
    return (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()


def shorten(text, limit=22):
    text = safe_text(text)
    text = re.sub(r"\s+", "", text)
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


def dedupe(items):
    result = []
    seen = set()
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def dedupe_roster_items(items):
    result = []
    seen = set()
    for item in items:
        if not item:
            continue
        key = item["key"]
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def make_roster():
    roster = [
        {"key": "kasumi", "display": "香澄", "full": "户山香澄", "band": "Poppin'Party", "ids": [1], "aliases": ["香澄", "户山香澄"]},
        {"key": "tae", "display": "多惠", "full": "花园多惠", "band": "Poppin'Party", "ids": [2], "aliases": ["多惠", "花园多惠", "惠惠"]},
        {"key": "rimi", "display": "里美", "full": "牛込里美", "band": "Poppin'Party", "ids": [3], "aliases": ["里美", "牛込里美"]},
        {"key": "saaya", "display": "沙绫", "full": "山吹沙绫", "band": "Poppin'Party", "ids": [4], "aliases": ["沙绫", "山吹沙绫"]},
        {"key": "arisa", "display": "有咲", "full": "市谷有咲", "band": "Poppin'Party", "ids": [5], "aliases": ["有咲", "市谷有咲"]},
        {"key": "ran", "display": "兰", "full": "美竹兰", "band": "Afterglow", "ids": [6], "aliases": ["兰", "美竹兰"]},
        {"key": "moca", "display": "摩卡", "full": "青叶摩卡", "band": "Afterglow", "ids": [7], "aliases": ["摩卡", "青叶摩卡"]},
        {"key": "himari", "display": "绯玛丽", "full": "上原绯玛丽", "band": "Afterglow", "ids": [8], "aliases": ["绯玛丽", "上原绯玛丽"]},
        {"key": "tomoe", "display": "巴", "full": "宇田川巴", "band": "Afterglow", "ids": [9], "aliases": ["巴", "宇田川巴"]},
        {"key": "tsugumi", "display": "鸫", "full": "羽泽鸫", "band": "Afterglow", "ids": [10], "aliases": ["鸫", "羽泽鸫"]},
        {"key": "kokoro", "display": "心", "full": "弦卷心", "band": "Hello, Happy World!", "ids": [11], "aliases": ["心", "弦卷心"]},
        {"key": "kaoru", "display": "薰", "full": "濑田薰", "band": "Hello, Happy World!", "ids": [12], "aliases": ["薰", "濑田薰"]},
        {"key": "hagumi", "display": "育美", "full": "北泽育美", "band": "Hello, Happy World!", "ids": [13], "aliases": ["育美", "北泽育美"]},
        {"key": "kanon", "display": "花音", "full": "松原花音", "band": "Hello, Happy World!", "ids": [14], "aliases": ["花音", "松原花音"]},
        {"key": "misaki", "display": "美咲", "full": "奥泽美咲", "band": "Hello, Happy World!", "ids": [15, 601], "aliases": ["美咲", "奥泽美咲", "米歇尔", "Michelle"]},
        {"key": "aya", "display": "彩", "full": "丸山彩", "band": "Pastel*Palettes", "ids": [16], "aliases": ["彩", "丸山彩"]},
        {"key": "hina", "display": "日菜", "full": "冰川日菜", "band": "Pastel*Palettes", "ids": [17], "aliases": ["日菜", "冰川日菜"]},
        {"key": "chisato", "display": "千圣", "full": "白鹭千圣", "band": "Pastel*Palettes", "ids": [18], "aliases": ["千圣", "白鹭千圣"]},
        {"key": "maya", "display": "麻弥", "full": "大和麻弥", "band": "Pastel*Palettes", "ids": [19], "aliases": ["麻弥", "大和麻弥"]},
        {"key": "eve", "display": "伊芙", "full": "若宫伊芙", "band": "Pastel*Palettes", "ids": [20], "aliases": ["伊芙", "若宫伊芙"]},
        {"key": "yukina", "display": "友希那", "full": "凑友希那", "band": "Roselia", "ids": [21], "aliases": ["友希那", "凑友希那"]},
        {"key": "sayo", "display": "纱夜", "full": "冰川纱夜", "band": "Roselia", "ids": [22], "aliases": ["纱夜", "冰川纱夜"]},
        {"key": "lisa", "display": "莉莎", "full": "今井莉莎", "band": "Roselia", "ids": [23], "aliases": ["莉莎", "今井莉莎"]},
        {"key": "ako", "display": "亚子", "full": "宇田川亚子", "band": "Roselia", "ids": [24], "aliases": ["亚子", "宇田川亚子"]},
        {"key": "rinko", "display": "燐子", "full": "白金燐子", "band": "Roselia", "ids": [25], "aliases": ["燐子", "白金燐子"]},
        {"key": "mashiro", "display": "真白", "full": "仓田真白", "band": "Morfonica", "ids": [26], "aliases": ["真白", "仓田真白"]},
        {"key": "touko", "display": "透子", "full": "桐谷透子", "band": "Morfonica", "ids": [27], "aliases": ["透子", "桐谷透子"]},
        {"key": "nanami", "display": "七深", "full": "广町七深", "band": "Morfonica", "ids": [28], "aliases": ["七深", "广町七深"]},
        {"key": "tsukushi", "display": "筑紫", "full": "二叶筑紫", "band": "Morfonica", "ids": [29], "aliases": ["筑紫", "二叶筑紫"]},
        {"key": "rui", "display": "瑠唯", "full": "八潮瑠唯", "band": "Morfonica", "ids": [30], "aliases": ["瑠唯", "八潮瑠唯"]},
        {"key": "rei", "display": "瑞依", "full": "和奏瑞依", "band": "RAISE A SUILEN", "ids": [31], "aliases": ["瑞依", "和奏瑞依", "LAYER"]},
        {"key": "rokka", "display": "六花", "full": "朝日六花", "band": "RAISE A SUILEN", "ids": [32], "aliases": ["六花", "朝日六花", "LOCK"]},
        {"key": "masuki", "display": "益木", "full": "佐藤益木", "band": "RAISE A SUILEN", "ids": [33], "aliases": ["益木", "佐藤益木", "MASKING"]},
        {"key": "reona", "display": "令王那", "full": "鳰原令王那", "band": "RAISE A SUILEN", "ids": [34], "aliases": ["令王那", "鳰原令王那", "PAREO"]},
        {"key": "chiyu", "display": "知由", "full": "珠手知由", "band": "RAISE A SUILEN", "ids": [35], "aliases": ["知由", "珠手知由", "CHU²", "CHU2"]},
        {"key": "tomori", "display": "灯", "full": "高松灯", "band": "MyGO!!!!!", "ids": [36], "aliases": ["灯", "高松灯"]},
        {"key": "anon", "display": "爱音", "full": "千早爱音", "band": "MyGO!!!!!", "ids": [37], "aliases": ["爱音", "千早爱音"]},
        {"key": "rana", "display": "乐奈", "full": "要乐奈", "band": "MyGO!!!!!", "ids": [38], "aliases": ["乐奈", "要乐奈"]},
        {"key": "soyo", "display": "爽世", "full": "长崎爽世", "band": "MyGO!!!!!", "ids": [39], "aliases": ["爽世", "长崎爽世"]},
        {"key": "taki", "display": "立希", "full": "椎名立希", "band": "MyGO!!!!!", "ids": [40], "aliases": ["立希", "椎名立希"]},
        {"key": "sakiko", "display": "祥子", "full": "丰川祥子", "band": "重要其他角色", "ids": [], "aliases": ["祥子", "丰川祥子"]},
        {"key": "uika", "display": "初华", "full": "三角初华", "band": "重要其他角色", "ids": [], "aliases": ["初华", "三角初华"]},
        {"key": "mutsumi", "display": "睦", "full": "若叶睦", "band": "重要其他角色", "ids": [], "aliases": ["睦", "若叶睦"]},
        {"key": "umiri", "display": "海铃", "full": "八幡海铃", "band": "重要其他角色", "ids": [], "aliases": ["海铃", "八幡海铃"]},
        {"key": "nyamu", "display": "若麦", "full": "祐天寺若麦", "band": "重要其他角色", "ids": [], "aliases": ["若麦", "祐天寺若麦"]},
        {"key": "asuka", "display": "明日香", "full": "户山明日香", "band": "重要其他角色", "ids": [], "aliases": ["明日香", "户山明日香"]},
        {"key": "mana", "display": "真奈", "full": "鹈泽真奈", "band": "重要其他角色", "ids": [], "aliases": ["真奈", "鹈泽真奈"]},
        {"key": "marina", "display": "麻里奈", "full": "月岛麻里奈", "band": "重要其他角色", "ids": [201], "aliases": ["麻里奈", "月岛麻里奈"]},
        {"key": "owner", "display": "店长", "full": "LiveHouse 店长", "band": "重要其他角色", "ids": [], "aliases": ["店长", "老板"]},
    ]

    for item in roster:
        item["folder"] = "char_%s_%s" % (item["key"], ascii_slug(item["full"], item["key"]))
        item["speaker_aliases"] = set(item["aliases"])
        item["mention_aliases"] = set(alias for alias in item["aliases"] if len(alias) >= 2)
    return roster


ROSTER = make_roster()
ROSTER_BY_KEY = {item["key"]: item for item in ROSTER}
ROSTER_BY_ID = {}
for item in ROSTER:
    for character_id in item["ids"]:
        ROSTER_BY_ID[character_id] = item


TRAIT_RULES = {
    "积极主动": ["一起", "快点", "加油", "出发", "想", "一定", "太好了", "好耶", "期待", "试试看"],
    "认真克制": ["必须", "应该", "先", "练习", "冷静", "计划", "规则", "准备", "认真", "确认"],
    "温柔体贴": ["谢谢", "没关系", "抱歉", "辛苦", "帮助", "担心", "照顾", "请多关照", "不要紧"],
    "敏感细腻": ["有点", "那个", "可是", "害怕", "担心", "紧张", "不安", "心情", "难过"],
    "直率吐槽": ["真是的", "吵死了", "笨蛋", "受不了", "你这家伙", "到底", "干嘛", "少来"],
    "浪漫感性": ["星星", "闪闪发光", "心跳", "梦想", "喜欢", "开心", "美丽", "光芒"],
    "自信强势": ["交给我", "当然", "我来", "没问题", "听好了", "绝对", "赢", "不会输"],
}

TOPIC_RULES = {
    "乐队活动": ["乐队", "LIVE", "演唱会", "练习", "歌曲", "吉他", "贝斯", "鼓", "键盘", "主唱", "舞台"],
    "校园日常": ["学校", "教室", "上学", "放学", "同学", "社团", "老师", "考试", "午休"],
    "同伴关系": ["大家", "一起", "同伴", "朋友", "拜托", "支持", "约定", "帮忙"],
    "情绪成长": ["喜欢", "害怕", "担心", "努力", "梦想", "勇气", "开心", "烦恼", "改变"],
    "店铺工作": ["LiveHouse", "客人", "活动", "工作", "老板", "店里", "营业", "打扫"],
}


def split_markdown_sections(text):
    sections = {}
    current = None
    buffer = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(buffer).strip()
            current = line[3:].strip()
            buffer = []
        elif current is not None:
            buffer.append(line)

    if current is not None:
        sections[current] = "\n".join(buffer).strip()

    return sections


def load_existing_portrait_supplements():
    supplements = {}

    for character in ROSTER:
        path = OUTPUT_ROOT / character["folder"] / "portrait.md"
        if not path.exists():
            continue

        sections = split_markdown_sections(path.read_text(encoding="utf-8"))
        setting = sections.get("外部设定基础") or sections.get("外部补充设定") or ""
        story = sections.get("外部剧情基础") or sections.get("外部剧情补充") or ""
        sources = sections.get("参考来源") or ""
        supplements[character["key"]] = {
            "setting": setting.strip(),
            "story": story.strip(),
            "sources": [line.rstrip() for line in sources.splitlines() if line.strip()],
        }

    return supplements


def first_sentences(text, limit=2):
    text = safe_text(text)
    if not text:
        return ""
    cleaned_lines = []
    for line in text.splitlines():
        cleaned = re.sub(r"^\s*-\s*", "", line.strip())
        if cleaned:
            cleaned_lines.append(cleaned)
    text = "".join(cleaned_lines)
    parts = re.split(r"(?<=[。！？])", text)
    parts = [part.strip() for part in parts if part.strip()]
    return "".join(parts[:limit])


def top_relationships(entries, character):
    counts = Counter()
    for entry in entries:
        for participant in entry.get("participants", []):
            if participant != character["display"]:
                counts[participant] += 1
    return counts


def format_counter_items(counter, limit=5, fallback="暂无明显集中对象"):
    items = ["%s（%s）" % (name, count) for name, count in counter.most_common(limit)]
    return "、".join(items) if items else fallback


def story_scope_text(entries):
    category_counts = Counter(entry["source_category"] for entry in entries)
    main_count = sum(count for category, count in category_counts.items() if "主线" in category)
    band_count = sum(count for category, count in category_counts.items() if "乐团" in category)

    if main_count and band_count:
        return "同时覆盖主线推进（%s）和乐队内部关系（%s）两条线" % (main_count, band_count)
    if main_count:
        return "目前更集中在主线推进相关剧情（%s）" % main_count
    if band_count:
        return "目前更集中在乐队内部与团内关系剧情（%s）" % band_count
    return "目前主要以零散剧情片段被收录"


def card_scope_text(entries):
    if not entries:
        return "当前没有卡牌侧补充。"

    episode_counts = Counter(entry["episode_type"] or "other" for entry in entries)
    memorial_count = episode_counts.get("memorial", 0)
    normal_count = len(entries) - memorial_count

    if memorial_count and normal_count:
        return "卡牌侧同时包含日常补完（%s）和回忆/特训向内容（%s）。" % (normal_count, memorial_count)
    if memorial_count:
        return "卡牌侧目前以回忆/特训向内容（%s）为主。" % memorial_count
    return "卡牌侧目前以日常补完内容（%s）为主。" % len(entries)


def normalized_card_type_label(value):
    if value == "memorial":
        return "回忆/特训"
    if value in {"normal", "other", "", "standard"}:
        return "日常/通常"
    return value or "未标明"


def inferred_topics(text, limit=2):
    scores = topic_scores(text)
    topics = [name for name, score in scores.most_common(limit) if score > 0]
    return topics or ["人物关系", "情绪推进"]


def entry_summary(character, participants, dialogues, scene=None, episode_type=None, mode="story"):
    joined = "\n".join("%s：%s" % (dialogue["speaker"], dialogue["text"]) for dialogue in dialogues)
    topics = "、".join(inferred_topics(joined, limit=2))
    others = [name for name in participants if name != character["display"]]

    if others:
        relation = "与%s的互动" % ("、".join(others[:2]) + ("等人" if len(others) > 2 else ""))
    else:
        relation = "个人状态与自我表达"

    if mode == "story":
        if scene and scene != "未标明":
            return "这段切片主要呈现%s在%s这一场景里%s，重点落在%s，也补充了她/他在这一阶段的剧情位置。" % (
                character["display"],
                scene,
                relation,
                topics,
            )
        return "这段切片主要呈现%s的%s，重点落在%s，也补充了她/他在这一阶段的剧情位置。" % (
            character["display"],
            relation,
            topics,
        )

    card_label = normalized_card_type_label(episode_type)
    focus = "%s%s" % (character["display"], relation) if others else "%s的%s" % (character["display"], relation)
    return "这则%s卡牌剧情主要围绕%s展开，重点补充了%s，适合用来观察角色在主线之外的稳定表现。" % (
        card_label,
        focus,
        topics,
    )


def story_analysis_lines(character, entries):
    if not entries:
        return [
            "当前没有从主线或乐团故事中切到与该角色直接相关的剧情片段，因此这一部分暂时无法作为稳定印证来源。",
            "",
            "- 剧情分布：暂无",
            "- 高频同场角色：暂无",
            "- 高频来源标题：暂无",
        ]

    relation_counts = top_relationships(entries, character)
    title_counts = Counter(entry["source_title"] for entry in entries)
    category_counts = Counter(entry["source_category"] for entry in entries)

    paragraph = (
        "在已整理的 %s 条主线/乐团剧情切片里，%s%s。"
        "这说明这个角色在本地语料中的位置，不应该只从单句台词去读，而要放回到持续出现的关系链和章节位置里看。"
    ) % (len(entries), character["display"], story_scope_text(entries))

    category_text = "、".join("%s（%s）" % (name, count) for name, count in category_counts.most_common()) or "暂无"
    title_text = "、".join("%s（%s）" % (name, count) for name, count in title_counts.most_common(3)) or "暂无"

    return [
        paragraph,
        "",
        "- 剧情分布：%s" % category_text,
        "- 高频同场角色：%s" % format_counter_items(relation_counts, limit=5),
        "- 高频来源标题：%s" % title_text,
    ]


def card_analysis_lines(character, entries):
    if not entries:
        return [
            "当前没有归到该角色名下的卡牌剧情，因此暂时无法从私人篇章、节庆篇章或回忆篇章里继续补正人物侧面。",
            "",
            "- 卡牌类型分布：暂无",
            "- 高频同场角色：暂无",
        ]

    relation_counts = Counter()
    type_counts = Counter()
    for entry in entries:
        type_counts[entry["episode_type"] or "other"] += 1
        for participant in entry["participants"]:
            if participant != character["display"]:
                relation_counts[participant] += 1

    type_labels = []
    for name, count in type_counts.most_common():
        label = normalized_card_type_label(name)
        type_labels.append("%s（%s）" % (label, count))

    paragraph = (
        "在 %s 条卡牌剧情里，%s 的个人篇章补完%s"
        "这部分更适合用来观察角色的私下状态、非主线场合下的关系重心，以及主线之外的稳定人格表现。"
    ) % (
        len(entries),
        character["display"],
        "相对丰富；" if len(entries) >= 20 else "已经有一定覆盖；",
    )

    return [
        paragraph,
        "",
        "- 卡牌类型分布：%s" % ("、".join(type_labels) if type_labels else "暂无"),
        "- 高频同场角色：%s" % format_counter_items(relation_counts, limit=5),
    ]


def overall_analysis_text(character, story_entries, card_entries, supplement):
    external_anchor = first_sentences(supplement.get("setting", ""), 2) or first_sentences(supplement.get("story", ""), 2)

    story_relations = top_relationships(story_entries, character)
    relation_text = format_counter_items(story_relations, limit=3, fallback="暂无明显集中对象")
    story_scope = story_scope_text(story_entries) if story_entries else "本地主线/乐团切片暂时不足"
    card_scope = card_scope_text(card_entries)

    if external_anchor:
        opening = "从外部设定与已整理剧情综合来看，%s的角色框架可以先理解为：%s" % (character["display"], external_anchor)
    else:
        opening = "从已整理剧情综合来看，%s的人物分析更适合放在章节位置、关系分布和卡牌篇章中整体理解。" % character["display"]

    return (
        "%s\n\n"
        "结合本地剧情来看，%s在已整理语料中的位置%s，且最常与 %s 同场。%s"
        "整体而言，这个角色的理解重点更落在长期剧情功能、关系位置，以及公开场合与私人场合之间的呈现差异。"
    ) % (opening, character["display"], story_scope, relation_text, card_scope)


def story_document_overview(character, entries, supplement):
    anchor = (first_sentences(supplement.get("story", ""), 1) or first_sentences(supplement.get("setting", ""), 1)).rstrip("。！？")
    lines = ["## 切片总览", ""]

    if entries:
        relation_counts = top_relationships(entries, character)
        title_counts = Counter(entry["source_title"] for entry in entries)
        intro = "从主线故事和乐团故事的切片分布来看，%s%s。" % (
            character["display"],
            ("的剧情位置与外部资料描述基本一致，" + anchor) if anchor else "在本地语料里有比较清晰的叙事重心",
        )
        lines.extend(
            [
                intro,
                "",
                "- 剧情范围：%s" % story_scope_text(entries),
                "- 高频同场角色：%s" % format_counter_items(relation_counts, limit=5),
                "- 高频来源标题：%s" % ("、".join("%s（%s）" % (name, count) for name, count in title_counts.most_common(3)) or "暂无"),
                "",
            ]
        )
    else:
        lines.extend(
            [
                "当前没有切到与该角色直接相关的主线/乐团故事片段，因此这一份文档暂时无法进一步展开。",
                "",
            ]
        )

    return lines


def card_document_overview(character, entries, supplement):
    anchor = first_sentences(supplement.get("setting", ""), 1)
    lines = ["## 卡牌总览", ""]

    if entries:
        relation_counts = Counter()
        type_counts = Counter()
        for entry in entries:
            type_counts[entry["episode_type"] or "other"] += 1
            for participant in entry["participants"]:
                if participant != character["display"]:
                    relation_counts[participant] += 1

        intro = "从卡牌剧情的个人篇章来看，%s%s。" % (
            character["display"],
            ("在更私人、日常的场景里延续了外部设定中的人物底色" if anchor else "在主线之外同样维持了稳定的人物呈现"),
        )
        lines.extend(
            [
                intro,
                "",
                "- 卡牌覆盖：%s" % card_scope_text(entries),
                "- 卡牌类型分布：%s" % ("、".join("%s（%s）" % (normalized_card_type_label(name), count) for name, count in type_counts.most_common()) or "暂无"),
                "- 高频同场角色：%s" % format_counter_items(relation_counts, limit=5),
                "",
            ]
        )
    else:
        lines.extend(
            [
                "当前没有归到该角色名下的卡牌剧情，因此这一份文档暂时没有可继续展开的个人篇章材料。",
                "",
            ]
        )

    return lines


def parse_story_markdown(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    title = ""
    metadata = {}
    content = []
    in_content = False

    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            continue
        if not in_content and not line.strip():
            continue
        if not in_content and line.startswith("- "):
            payload = line[2:]
            if "：" in payload:
                key, value = payload.split("：", 1)
                metadata[key.strip()] = value.strip()
            continue
        in_content = True
        content.append(line.rstrip())

    return {"path": path, "title": title, "metadata": metadata, "content": content}


def parse_content_lines(content_lines):
    scene = None
    dialogues = []

    for line in content_lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("[场景] "):
            yield {"type": "scene", "scene": line[5:].strip()}
            continue
        if "：" in line:
            speaker, text = line.split("：", 1)
            yield {"type": "dialogue", "speaker": speaker.strip(), "text": text.strip()}
            continue
        if dialogues:
            yield {"type": "dialogue", "speaker": "旁白", "text": line}


def slice_story(parsed_story, max_dialogues=18):
    slices = []
    current_scene = None
    current_dialogues = []

    def flush():
        if current_dialogues:
            slices.append({"scene": current_scene, "dialogues": list(current_dialogues)})
            current_dialogues[:] = []

    for item in parse_content_lines(parsed_story["content"]):
        if item["type"] == "scene":
            flush()
            current_scene = item["scene"]
        elif item["type"] == "dialogue":
            current_dialogues.append({"speaker": item["speaker"], "text": item["text"]})
            if len(current_dialogues) >= max_dialogues:
                flush()

    flush()
    return slices


def match_roster_members(text, speaker_names):
    matched = []
    full_text = safe_text(text)
    speaker_set = set(speaker_names)

    for item in ROSTER:
        if speaker_set & item["speaker_aliases"]:
            matched.append(item)
            continue
        for alias in item["mention_aliases"]:
            if alias in full_text:
                matched.append(item)
                break
    return dedupe_roster_items(matched)


def summarize_dialogue_block(scene, participants, dialogues):
    speaker_names = [dialogue["speaker"] for dialogue in dialogues if dialogue["speaker"] != "旁白"]
    speaker_names = dedupe(speaker_names)
    focus = [shorten(dialogue["text"], 18) for dialogue in dialogues[:3] if dialogue["text"]]
    focus = [item for item in focus if item]
    who = "、".join(participants[:4] or speaker_names[:4] or ["相关角色"])
    place = ("在%s" % scene) if scene else "在这一段剧情里"
    if focus:
        return "%s，%s围绕“%s”展开交流，推动了这一段人物关系与情绪变化。" % (
            place,
            who,
            " / ".join(focus[:2]),
        )
    return "%s，%s展开了一段对话，补充了角色当下的状态与互动。" % (place, who)


def summarize_card_block(owner_name, participants, dialogues, episode_type):
    focus = [shorten(dialogue["text"], 18) for dialogue in dialogues[:3] if dialogue["text"]]
    focus = [item for item in focus if item]
    cast = "、".join(participants[:4] or [owner_name])
    label = "回忆向" if episode_type == "memorial" else "日常补充"
    if focus:
        return "这则%s卡牌剧情以%s为中心，%s围绕“%s”展开互动，内容主要补充了该角色更私人、更具体的一面。" % (
            label,
            owner_name,
            cast,
            " / ".join(focus[:2]),
        )
    return "这则%s卡牌剧情以%s为中心，补充了角色在单独篇章中的表现与情绪。" % (label, owner_name)


def collect_story_slices():
    results = defaultdict(list)
    story_files = list((SOURCE_ROOT / "main_story").rglob("*.md")) + list((SOURCE_ROOT / "band_story").rglob("*.md"))

    for path in sorted(story_files):
        parsed = parse_story_markdown(path)
        source_category = parsed["metadata"].get("分类", "")
        for index, block in enumerate(slice_story(parsed), 1):
            dialogues = block["dialogues"]
            speaker_names = dedupe([dialogue["speaker"] for dialogue in dialogues])
            joined_text = "\n".join(
                ["[场景] %s" % block["scene"]] * (1 if block["scene"] else 0)
                + ["%s：%s" % (dialogue["speaker"], dialogue["text"]) for dialogue in dialogues]
            )
            matched = match_roster_members(joined_text, speaker_names)
            if not matched:
                continue

            participant_names = [item["display"] for item in matched]
            entry = {
                "source_path": str(path.relative_to(SOURCE_ROOT)).replace("\\", "/"),
                "source_category": source_category,
                "source_title": parsed["title"],
                "scene": block["scene"] or "未标明",
                "participants": participant_names,
                "summary": summarize_dialogue_block(block["scene"], participant_names, dialogues),
                "dialogues": dialogues,
                "slice_index": index,
            }

            for item in matched:
                results[item["key"]].append(entry)

    return results


def collect_card_stories():
    results = defaultdict(list)
    for path in sorted((SOURCE_ROOT / "card_story").rglob("*.md")):
        parsed = parse_story_markdown(path)
        metadata = parsed["metadata"]
        owner_id = metadata.get("角色ID", "").strip()
        owner = None
        if owner_id.isdigit():
            owner = ROSTER_BY_ID.get(int(owner_id))

        if owner is None:
            continue

        dialogues = []
        for item in parse_content_lines(parsed["content"]):
            if item["type"] == "dialogue":
                dialogues.append({"speaker": item["speaker"], "text": item["text"]})

        participant_names = dedupe([dialogue["speaker"] for dialogue in dialogues if dialogue["speaker"] != "旁白"])
        entry = {
            "source_path": str(path.relative_to(SOURCE_ROOT)).replace("\\", "/"),
            "card_id": metadata.get("卡牌ID", ""),
            "episode_index": metadata.get("Episode 序号", ""),
            "episode_type": metadata.get("Episode 类型", ""),
            "title": parsed["title"],
            "summary": summarize_card_block(owner["display"], participant_names, dialogues, metadata.get("Episode 类型", "")),
            "participants": participant_names,
            "dialogues": dialogues,
        }
        results[owner["key"]].append(entry)

    return results


def trait_scores(text):
    scores = Counter()
    for label, keywords in TRAIT_RULES.items():
        for keyword in keywords:
            scores[label] += text.count(keyword)
    return scores


def topic_scores(text):
    scores = Counter()
    for label, keywords in TOPIC_RULES.items():
        for keyword in keywords:
            scores[label] += text.count(keyword)
    return scores


def portrait_text(character, story_entries, card_entries, supplement):
    setting_text = supplement.get("setting", "").strip()
    story_text = supplement.get("story", "").strip()
    source_lines = supplement.get("sources", [])

    lines = [
        "# %s 人物画像" % character["display"],
        "",
        "- 角色名：%s" % character["full"],
        "- 所属分类：%s" % character["band"],
        "- 主线/乐团剧情切片数：%s" % len(story_entries),
        "- 卡牌剧情数：%s" % len(card_entries),
        "",
        "## 总体画像",
        "",
        overall_analysis_text(character, story_entries, card_entries, supplement),
        "",
        "## 外部设定基础",
        "",
        setting_text or "当前尚未补入该角色的外部设定补充，因此这里只能更多依赖本地剧情切片与卡牌剧情来做保守整理。",
        "",
        "## 外部剧情基础",
        "",
        story_text or "当前尚未补入该角色的外部剧情补充，因此这一部分暂时留空。",
        "",
    ]
    lines.extend(["## 主线/乐团切片印证", ""])
    lines.extend(story_analysis_lines(character, story_entries))
    lines.extend(["", "## 卡牌剧情印证", ""])
    lines.extend(card_analysis_lines(character, card_entries))
    lines.extend(["", "## 参考来源", ""])
    if source_lines:
        lines.extend(source_lines)
    else:
        lines.append("- 暂无额外外部来源，当前主要依赖本地抓取剧情整理。")
    lines.append("")
    return "\n".join(lines)


def story_slices_text(character, entries, supplement):
    lines = [
        "# %s 剧情切片" % character["display"],
        "",
        "- 收录范围：主线故事 + 乐团故事",
        "- 切片数量：%s" % len(entries),
        "",
    ]
    lines.extend(story_document_overview(character, entries, supplement))

    if not entries:
        return "\n".join(lines)

    for index, entry in enumerate(entries, 1):
        lines.extend(
            [
                "## 切片 %03d" % index,
                "",
                "- 来源分类：%s" % entry["source_category"],
                "- 来源标题：%s" % entry["source_title"],
                "- 来源文件：%s" % entry["source_path"],
                "- 场景：%s" % entry["scene"],
                "- 参与角色：%s" % "、".join(entry["participants"]),
                "- 剧情概要：%s" % entry_summary(character, entry["participants"], entry["dialogues"], scene=entry["scene"], mode="story"),
                "",
                "### 对话",
                "",
            ]
        )
        for dialogue in entry["dialogues"]:
            lines.append("%s：%s" % (dialogue["speaker"], dialogue["text"]))
        lines.append("")

    return "\n".join(lines)


def card_stories_text(character, entries, supplement):
    lines = [
        "# %s 卡牌剧情" % character["display"],
        "",
        "- 收录范围：该角色名下已导出的卡牌剧情",
        "- 条目数量：%s" % len(entries),
        "",
    ]
    lines.extend(card_document_overview(character, entries, supplement))

    if not entries:
        return "\n".join(lines)

    for index, entry in enumerate(entries, 1):
        lines.extend(
            [
                "## 卡牌剧情 %03d" % index,
                "",
                "- 卡牌ID：%s" % entry["card_id"],
                "- Episode 序号：%s" % entry["episode_index"],
                "- Episode 类型：%s" % entry["episode_type"],
                "- 标题：%s" % entry["title"],
                "- 来源文件：%s" % entry["source_path"],
                "- 参与角色：%s" % ("、".join(entry["participants"]) if entry["participants"] else character["display"]),
                "- 剧情概要：%s" % entry_summary(character, entry["participants"], entry["dialogues"], episode_type=entry["episode_type"], mode="card"),
                "",
                "### 对话",
                "",
            ]
        )
        for dialogue in entry["dialogues"]:
            lines.append("%s：%s" % (dialogue["speaker"], dialogue["text"]))
        lines.append("")

    return "\n".join(lines)


def build_dossiers():
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    story_map = collect_story_slices()
    card_map = collect_card_stories()
    supplement_map = load_existing_portrait_supplements()

    summary_lines = [
        "# 角色归档总览",
        "",
        "- 来源目录：`bestdori_cn_markdown/`",
        "- 输出目录：`character_dossiers/`",
        "- 角色总数：%s" % len(ROSTER),
        "",
    ]

    for character in ROSTER:
        folder = OUTPUT_ROOT / character["folder"]
        folder.mkdir(parents=True, exist_ok=True)

        story_entries = story_map.get(character["key"], [])
        card_entries = card_map.get(character["key"], [])

        story_entries = sorted(story_entries, key=lambda item: (item["source_path"], item["slice_index"]))
        card_entries = sorted(
            card_entries,
            key=lambda item: (
                int(item["card_id"] or 0),
                int(item["episode_index"] or 0),
            ),
        )

        supplement = supplement_map.get(character["key"], {"setting": "", "story": "", "sources": []})

        (folder / "portrait.md").write_text(portrait_text(character, story_entries, card_entries, supplement), encoding="utf-8")
        (folder / "story_slices.md").write_text(story_slices_text(character, story_entries, supplement), encoding="utf-8")
        (folder / "card_stories.md").write_text(card_stories_text(character, card_entries, supplement), encoding="utf-8")

        summary_lines.extend(
            [
                "## %s" % character["display"],
                "",
                "- 文件夹：`%s/`" % character["folder"],
                "- 主线/乐团切片：%s" % len(story_entries),
                "- 卡牌剧情：%s" % len(card_entries),
                "",
            ]
        )

    (OUTPUT_ROOT / "README.md").write_text("\n".join(summary_lines), encoding="utf-8")


if __name__ == "__main__":
    build_dossiers()
