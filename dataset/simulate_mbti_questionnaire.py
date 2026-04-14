from __future__ import annotations

import hashlib
import json
import math
import random
import re
from collections import Counter
from pathlib import Path

import requests


DATASET_ROOT = Path(__file__).resolve().parent
DOSSIER_ROOT = DATASET_ROOT / "character_dossiers"
QUESTION_BANK_PATH = DATASET_ROOT / "ojts_question_bank_v2_1.json"
SUMMARY_PATH = DATASET_ROOT / "mbti_questionnaire_summary.md"
METHOD_PATH = DATASET_ROOT / "mbti_questionnaire_method.md"
COMMUNITY_CALIBRATION_PATH = DATASET_ROOT / "community_mbti_calibration.json"
SIMULATION_RUNS = 10
REFERENCE_TYPE_WEIGHT = 0.50
PORTRAIT_WEIGHT = 0.25
CARD_WEIGHT = 0.15
SLICE_WEIGHT = 0.10

QUESTION_BANK_SOURCE = "https://openpsychometrics.org/tests/OJTS/"
QUESTION_BANK_LICENSE = "CC BY-NC-SA 4.0"
QUESTION_BANK_NAME = "Open Jungian Type Scales (OJTS v2.1)"

OPPOSITE = {
    "E": "I",
    "I": "E",
    "S": "N",
    "N": "S",
    "F": "T",
    "T": "F",
    "J": "P",
    "P": "J",
}

RADAR_ORDER = ["E", "S", "T", "J", "I", "N", "F", "P"]

POLE_KEYWORDS = {
    "E": ["主动", "带动", "热闹", "社交", "群体", "公开", "舞台", "表达", "现场", "感染力", "活跃", "外出", "表演"],
    "I": ["独处", "沉默", "内化", "保留", "安静", "私下", "反思", "观察", "独自", "寡言", "内心", "克制"],
    "S": ["具体", "现实", "细节", "经验", "实际", "事实", "当下", "步骤", "现成", "操作", "落地", "务实"],
    "N": ["抽象", "意义", "可能性", "理想", "未来", "象征", "概念", "愿景", "世界观", "方向", "想象", "整体"],
    "F": ["情感", "在意", "价值", "心意", "共感", "同情", "温柔", "照顾", "忠诚", "感受", "理解", "关心", "真心"],
    "T": ["逻辑", "效率", "标准", "规则", "分析", "结果", "结构", "判断", "合理", "推理", "目标", "客观", "专业"],
    "J": ["计划", "秩序", "整理", "安排", "提前", "规则", "约束", "收束", "承诺", "组织", "有条理", "负责"],
    "P": ["即兴", "灵活", "自由", "随性", "变化", "保留选择", "玩乐", "开放", "临场", "探索", "随机", "适应"],
}

TYPE_ONE_LINERS = {
    "ENFJ": "更偏外向连接、抽象理解、价值驱动和结构推进。",
    "ENFP": "更偏外向连接、抽象探索、价值驱动和开放弹性。",
    "ENTJ": "更偏外向推进、抽象规划、逻辑判断和组织掌控。",
    "ENTP": "更偏外向探索、抽象发散、逻辑拆解和临场变化。",
    "ESFJ": "更偏外向关系、现实执行、情感照料和稳定组织。",
    "ESFP": "更偏外向体验、现实感受、情感表达和即兴行动。",
    "ESTJ": "更偏外向管理、现实导向、逻辑标准和秩序推进。",
    "ESTP": "更偏外向行动、现实反应、逻辑处理和即兴应对。",
    "INFJ": "更偏内在思考、抽象理解、价值判断和稳定收束。",
    "INFP": "更偏内在感受、抽象意义、价值驱动和开放探索。",
    "INTJ": "更偏内在规划、抽象结构、逻辑判断和长期控制。",
    "INTP": "更偏内在分析、抽象模型、逻辑拆解和开放推演。",
    "ISFJ": "更偏内在克制、现实关注、情感责任和秩序维持。",
    "ISFP": "更偏内在体验、现实感受、情感判断和自由保留。",
    "ISTJ": "更偏内在稳态、现实执行、逻辑标准和规则落实。",
    "ISTP": "更偏内在观察、现实处理、逻辑反应和灵活应变。",
}

AXIS_REASON = {
    "E": "更常通过主动互动、公开表达或带动现场来处理问题。",
    "I": "更常先在内部消化，再选择性地向外表达立场。",
    "S": "更常依赖现实条件、具体细节和当下经验来判断局面。",
    "N": "更常从意义、可能性、方向感和隐含主题去理解问题。",
    "F": "更常把感受、关系、价值和对人的回应放在判断前列。",
    "T": "更常把逻辑、结构、效率和标准一致性放在判断前列。",
    "J": "更常用计划、收束、安排和责任结构去降低混乱。",
    "P": "更常保留空间，依靠灵活调整和临场变化推进事情。",
}

BACKUP_REASON = {
    "E": "虽然也存在保留和内化的一面，但资料里更常出现主动带动关系与公开表达的处理方式。",
    "I": "虽然也会参与群体互动，但资料里更常表现为先内化、后表达的节奏。",
    "S": "虽然也会谈到意义和理想，但资料里更常落到现实条件、细节和可执行层面。",
    "N": "虽然也会处理具体事务，但资料里更常从主题、方向和抽象意义去组织理解。",
    "F": "虽然也会讲原则与方法，但最终更常回到价值、关系和感受后果来判断。",
    "T": "虽然也在意关系影响，但最终更常回到逻辑、标准和方法正确性来判断。",
    "J": "虽然并非没有弹性，但整体仍更偏向提前安排、收束局面和稳定结构。",
    "P": "虽然并非完全无计划，但整体仍更偏向保留余地、即兴调整和开放推进。",
}

DIRECT_META = {
    1: {"poles": ["I"], "hints": ["低调", "不想引人注目", "不抢风头"]},
    2: {"poles": ["I"], "hints": ["不擅活跃气氛", "不想逗别人笑", "怕被要求搞笑"]},
    3: {"poles": ["I"], "hints": ["保留意见", "不轻易表态", "不急着表达"]},
    4: {"poles": ["E"], "hints": ["社交圈大", "认识很多人", "广结交友"]},
    5: {"poles": ["E"], "hints": ["气氛中心", "带动现场", "活跃气氛"]},
    6: {"poles": ["E"], "hints": ["声音大", "吵闹", "动静大"]},
    7: {"poles": ["S"], "hints": ["不爱抽象讨论", "回避哲学", "不爱空谈"]},
    8: {"poles": ["S"], "hints": ["不爱文本分析", "不爱文学解读", "不爱深究象征"]},
    9: {"poles": ["S"], "hints": ["传统方式", "常规路线", "老办法"]},
    10: {"poles": ["N"], "hints": ["喜欢有挑战的内容", "爱思考复杂问题", "爱啃硬内容"]},
    11: {"poles": ["N"], "hints": ["隐藏含义", "深层意思", "言外之意"]},
    12: {"poles": ["N"], "hints": ["什么都好奇", "求知欲强", "探究"]},
    13: {"poles": ["F"], "hints": ["浪漫", "激情", "感情体验"]},
    14: {"poles": ["F"], "hints": ["很共情", "心疼别人", "他人受苦会难过"]},
    15: {"poles": ["F"], "hints": ["感受优先", "跟随心意", "看内心"]},
    16: {"poles": ["T"], "hints": ["逻辑最重要", "理性优先", "重分析"]},
    17: {"poles": ["T"], "hints": ["不理解情绪化", "看不懂感情用事", "讨厌失控"]},
    18: {"poles": ["T"], "hints": ["不求讨喜", "威慑", "尊重胜过喜欢"]},
    19: {"poles": ["J"], "hints": ["喜欢秩序", "有条理", "规整"]},
    20: {"poles": ["J"], "hints": ["按计划做事", "照步骤来", "计划性"]},
    21: {"poles": ["J"], "hints": ["提前准备", "有准备", "未雨绸缪"]},
    22: {"poles": ["P"], "hints": ["临时起意", "最后才计划", "即兴安排"]},
    23: {"poles": ["P"], "hints": ["随性而为", "凭一时兴致", "说做就做"]},
    24: {"poles": ["P"], "hints": ["容易分心", "拖拖拉拉", "被别的事吸走"]},
    25: {"poles": ["N", "J"], "hints": ["自我提升", "持续改进", "精进"]},
    26: {"poles": ["N", "J"], "hints": ["想做重要的事", "要有意义", "要做大事"]},
    27: {"poles": ["N", "P"], "hints": ["世界观特别", "想法奇特", "特异观点"]},
    28: {"poles": ["N", "P"], "hints": ["讨厌例行公事", "不喜欢重复", "要变化"]},
    29: {"poles": ["S", "J"], "hints": ["尽力守规则", "按规矩来", "守序"]},
    30: {"poles": ["S", "J"], "hints": ["尊重权威", "尊重前辈", "服从规范"]},
    31: {"poles": ["S", "P"], "hints": ["想轻松一点", "慢慢来", "图省事"]},
    32: {"poles": ["S", "P"], "hints": ["选轻松的路", "选简单方案", "图方便"]},
    33: {"poles": ["E", "F"], "hints": ["会说秘密", "袒露心事", "对人敞开"]},
    34: {"poles": ["E", "F"], "hints": ["表达友谊", "主动拉近关系", "热情示友"]},
    35: {"poles": ["E", "T"], "hints": ["喜欢挑战", "喜欢竞争", "好胜"]},
    36: {"poles": ["E", "T"], "hints": ["自我评价高", "很有自信", "气场强"]},
    37: {"poles": ["I", "F"], "hints": ["容易害羞", "容易不好意思", "容易尴尬"]},
    38: {"poles": ["I", "F"], "hints": ["容易被事情压垮", "情绪过载", "承压时被淹没"]},
    39: {"poles": ["I", "T"], "hints": ["难表达感情", "不说感受", "情绪表达笨拙"]},
    40: {"poles": ["I", "T"], "hints": ["不轻信别人", "警惕", "戒备"]},
}

BIPOLAR_META = {
    41: {"left_pole": "T", "right_pole": "F", "left_hints": ["怀疑", "存疑", "审慎"], "right_hints": ["愿意相信", "信任", "相信人"]},
    42: {"left_pole": "P", "right_pole": "J", "left_hints": ["混乱", "随性", "散漫"], "right_hints": ["有条理", "组织", "整理"]},
    43: {"left_pole": "N", "right_pole": "S", "left_hints": ["大局", "整体", "方向"], "right_hints": ["细节", "具体", "步骤"]},
    44: {"left_pole": "E", "right_pole": "I", "left_hints": ["精力充沛", "元气", "活力"], "right_hints": ["平静", "温和", "安静"]},
    45: {"left_pole": "F", "right_pole": "T", "left_hints": ["跟随内心", "凭心意", "感受优先"], "right_hints": ["跟随理性", "逻辑优先", "讲道理"]},
    46: {"left_pole": "J", "right_pole": "P", "left_hints": ["提前准备", "预先", "先安排"], "right_hints": ["即兴", "临场", "随机应变"]},
    47: {"left_pole": "S", "right_pole": "N", "left_hints": ["关注当下", "眼前", "现在"], "right_hints": ["关注未来", "以后", "长远"]},
    48: {"left_pole": "I", "right_pole": "E", "left_hints": ["独自工作", "一个人更好", "单独发挥"], "right_hints": ["团队中表现更好", "一起做更强", "协作发挥"]},
}


def safe_text(text):
    return (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()


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


def extract_header_value(lines, prefix):
    for line in lines:
        if line.startswith(prefix):
            return line.split("：", 1)[1].strip()
    return ""


def trim_prefix(text, prefix):
    return text[len(prefix):] if text.startswith(prefix) else text


def trim_suffix(text, suffix):
    return text[:-len(suffix)] if suffix and text.endswith(suffix) else text


def parse_ojts_question_bank():
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}

    index_response = session.get(QUESTION_BANK_SOURCE, headers=headers, timeout=30)
    index_response.raise_for_status()
    index_html = index_response.text

    unqid_match = re.search(r'name="unqid" value="([^"]+)"', index_html)
    seconds_match = re.search(r'name="seconds" value="([^"]+)"', index_html)
    if not unqid_match or not seconds_match:
        raise RuntimeError("无法从 OJTS 首页提取表单参数。")

    question_response = session.post(
        "https://openpsychometrics.org/tests/OJTS/1.php",
        data={"unqid": unqid_match.group(1), "seconds": seconds_match.group(1), "w": "1920", "h": "1080"},
        headers=headers,
        timeout=30,
    )
    question_response.raise_for_status()
    html = question_response.text

    direct_pairs = re.findall(r"'Q(\d+)'\s*:\s*'([^']+)'", html)
    questions = []
    for number, text in direct_pairs:
        qid = int(number)
        meta = DIRECT_META[qid]
        questions.append(
            {
                "id": qid,
                "section": 1,
                "format": "agreement",
                "text": text,
                "poles": meta["poles"],
                "hints": meta["hints"],
            }
        )

    pair_matches = re.findall(
        r'<div style="padding:1em;text-align:right;padding-right:0.3em;">\s*([^<]+?)\s*</div>\s*<div style="padding-top:1em;display:inline-block;">.*?</div>\s*<div style="padding:1em;text-align:left;padding-left:0.3em;">\s*([^<]+?)\s*</div>',
        html,
        re.S,
    )
    pair_matches = pair_matches[-8:]
    for index, pair in enumerate(pair_matches, start=41):
        left_text = re.sub(r"\s+", " ", pair[0]).strip()
        right_text = re.sub(r"\s+", " ", pair[1]).strip()
        meta = BIPOLAR_META[index]
        questions.append(
            {
                "id": index,
                "section": 2,
                "format": "bipolar",
                "left_text": left_text,
                "right_text": right_text,
                "left_pole": meta["left_pole"],
                "right_pole": meta["right_pole"],
                "left_hints": meta["left_hints"],
                "right_hints": meta["right_hints"],
            }
        )

    questions = sorted(questions, key=lambda item: item["id"])
    payload = {
        "name": QUESTION_BANK_NAME,
        "version": "2.1",
        "source": QUESTION_BANK_SOURCE,
        "license": QUESTION_BANK_LICENSE,
        "question_count": len(questions),
        "questions": questions,
    }
    QUESTION_BANK_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def load_community_calibration():
    if COMMUNITY_CALIBRATION_PATH.exists():
        raw = json.loads(COMMUNITY_CALIBRATION_PATH.read_text(encoding="utf-8"))
        normalized = {}
        for key, value in raw.items():
            if isinstance(value, list):
                possible_types = [str(item).strip().upper() for item in value if str(item).strip()]
                normalized[key] = {
                    "possible_types": possible_types,
                    "vote_winner_type": possible_types[0] if possible_types else "",
                    "use_for_calibration": True,
                    "source": "personality-database.com",
                }
                continue
            if isinstance(value, dict):
                entry = dict(value)
                if isinstance(entry.get("possible_types"), list):
                    entry["possible_types"] = [str(item).strip().upper() for item in entry["possible_types"] if str(item).strip()]
                    if entry["possible_types"] and not entry.get("vote_winner_type"):
                        entry["vote_winner_type"] = entry["possible_types"][0]
                normalized[key] = entry
                continue
            normalized[key] = {}
        return normalized
    return {}


def parse_dossier(folder):
    portrait_path = folder / "portrait.md"
    story_path = folder / "story_slices.md"
    card_path = folder / "card_stories.md"

    portrait_text = portrait_path.read_text(encoding="utf-8")
    portrait_lines = portrait_text.splitlines()
    portrait_sections = split_markdown_sections(portrait_text)

    character_name = extract_header_value(portrait_lines, "- 角色名：")
    display_name = trim_suffix(trim_prefix(portrait_lines[0], "# "), " 人物画像").strip() if portrait_lines else folder.name

    story_text = story_path.read_text(encoding="utf-8") if story_path.exists() else ""
    card_text = card_path.read_text(encoding="utf-8") if card_path.exists() else ""

    story_overview = []
    for line in story_text.splitlines():
        if line.startswith("## 切片 001"):
            break
        story_overview.append(line)

    card_overview = []
    for line in card_text.splitlines():
        if line.startswith("## 卡牌剧情 001"):
            break
        card_overview.append(line)

    prefix = "%s：" % display_name
    story_dialogues = [line.split("：", 1)[1].strip() for line in story_text.splitlines() if line.startswith(prefix)]
    card_dialogues = [line.split("：", 1)[1].strip() for line in card_text.splitlines() if line.startswith(prefix)]

    portrait_corpus = [
        {"source": "portrait_core", "weight": 1.0, "text": "\n".join([portrait_sections.get("总体画像", ""), portrait_sections.get("外部设定基础", ""), portrait_sections.get("外部剧情基础", "")])},
    ]
    card_corpus = [
        {"source": "card_validation", "weight": 1.0, "text": portrait_sections.get("卡牌剧情印证", "")},
        {"source": "card_overview", "weight": 0.9, "text": "\n".join(card_overview)},
        {"source": "card_dialogues", "weight": 0.8, "text": "\n".join(card_dialogues[:500])},
    ]
    story_corpus = [
        {"source": "story_validation", "weight": 1.0, "text": portrait_sections.get("主线/乐团切片印证", "")},
        {"source": "story_overview", "weight": 0.8, "text": "\n".join(story_overview)},
        {"source": "story_dialogues", "weight": 0.7, "text": "\n".join(story_dialogues[:500])},
    ]

    weighted_corpus = [
        {"source": "portrait_core", "weight": 5.0, "text": portrait_corpus[0]["text"]},
        {"source": "card_validation", "weight": 3.0, "text": card_corpus[0]["text"]},
        {"source": "card_overview", "weight": 2.6, "text": card_corpus[1]["text"]},
        {"source": "card_dialogues", "weight": 2.2, "text": card_corpus[2]["text"]},
        {"source": "story_validation", "weight": 1.8, "text": story_corpus[0]["text"]},
        {"source": "story_overview", "weight": 1.2, "text": story_corpus[1]["text"]},
        {"source": "story_dialogues", "weight": 1.0, "text": story_corpus[2]["text"]},
    ]

    cognitive_corpus = [
        {"source": "portrait_core", "weight": 4.8, "text": portrait_corpus[0]["text"]},
        {"source": "card_validation", "weight": 2.8, "text": card_corpus[0]["text"]},
        {"source": "card_overview", "weight": 2.6, "text": card_corpus[1]["text"]},
        {"source": "card_dialogues", "weight": 2.0, "text": card_corpus[2]["text"]},
        {"source": "story_validation", "weight": 1.7, "text": story_corpus[0]["text"]},
        {"source": "story_overview", "weight": 1.1, "text": story_corpus[1]["text"]},
        {"source": "story_dialogues", "weight": 0.9, "text": story_corpus[2]["text"]},
    ]

    full_text = safe_text("\n".join([portrait_text, "\n".join(story_overview), "\n".join(card_overview), "\n".join(story_dialogues), "\n".join(card_dialogues)]))

    return {
        "folder": folder,
        "display_name": display_name,
        "character_name": character_name or display_name,
        "portrait_sections": portrait_sections,
        "weighted_corpus": weighted_corpus,
        "cognitive_corpus": cognitive_corpus,
        "source_corpora": {
            "portrait": portrait_corpus,
            "card": card_corpus,
            "story": story_corpus,
        },
        "full_text": full_text,
    }


def build_keyword_idf(dossiers, questions):
    keywords = set()
    for items in POLE_KEYWORDS.values():
        keywords.update(items)
    for question in questions:
        for field in ["hints", "left_hints", "right_hints"]:
            for keyword in question.get(field, []):
                keywords.add(keyword)

    total = max(len(dossiers), 1)
    idf = {}
    for keyword in keywords:
        df = 0
        for dossier in dossiers:
            if keyword and keyword in dossier["full_text"]:
                df += 1
        idf[keyword] = math.log((total + 1.0) / (df + 1.0)) + 1.0
    return idf


def weighted_keyword_count(text, keywords, idf):
    score = 0.0
    for keyword in keywords:
        if keyword:
            score += text.count(keyword) * idf.get(keyword, 1.0)
    return score


def corpus_pole_scores(corpus, idf):
    scores = dict((pole, 1.0) for pole in POLE_KEYWORDS)
    for item in corpus:
        text = safe_text(item["text"])
        if not text:
            continue
        for pole, keywords in POLE_KEYWORDS.items():
            hit = weighted_keyword_count(text, keywords, idf)
            if hit:
                scores[pole] += hit * item["weight"]
    return scores


def pole_baseline_scores(dossier, idf):
    return corpus_pole_scores(dossier.get("cognitive_corpus", dossier["weighted_corpus"]), idf)


def pole_percentages(scores):
    percentages = {}
    for left, right in [("E", "I"), ("S", "N"), ("F", "T"), ("J", "P")]:
        total = scores[left] + scores[right]
        left_pct = int(round(scores[left] / total * 100)) if total else 50
        left_pct = max(1, min(99, left_pct))
        right_pct = 100 - left_pct
        percentages[left] = left_pct
        percentages[right] = right_pct
    return percentages


def support_to_likert(value):
    if value >= 60:
        return 5
    if value >= 22:
        return 4
    if value > -22:
        return 3
    if value > -60:
        return 2
    return 1


def direct_question_support(dossier, question, pole_percent, idf):
    pole_diffs = [pole_percent[pole] - pole_percent[OPPOSITE[pole]] for pole in question["poles"]]
    baseline = sum(pole_diffs) / float(len(pole_diffs))

    hint_score = 0.0
    anti_score = 0.0
    anti_keywords = []
    for pole in question["poles"]:
        anti_keywords.extend(POLE_KEYWORDS[OPPOSITE[pole]][:6])

    for item in dossier.get("cognitive_corpus", dossier["weighted_corpus"]):
        text = safe_text(item["text"])
        if not text:
            continue
        weight = item["weight"]
        hint_score += weighted_keyword_count(text, question.get("hints", []), idf) * weight
        anti_score += weighted_keyword_count(text, anti_keywords, idf) * weight

    specific = ((hint_score - anti_score) / (hint_score + anti_score) * 100.0) if (hint_score + anti_score) else 0.0
    combined = baseline * 0.7 + specific * 0.3
    return combined, baseline, specific


def bipolar_question_support(dossier, question, pole_percent, idf):
    baseline = pole_percent[question["right_pole"]] - pole_percent[question["left_pole"]]
    left_score = 0.0
    right_score = 0.0

    for item in dossier["weighted_corpus"]:
        text = safe_text(item["text"])
        if not text:
            continue
        weight = item["weight"]
        left_score += weighted_keyword_count(text, question.get("left_hints", []), idf) * weight
        right_score += weighted_keyword_count(text, question.get("right_hints", []), idf) * weight

    specific = ((right_score - left_score) / (left_score + right_score) * 100.0) if (left_score + right_score) else 0.0
    combined = baseline * 0.65 + specific * 0.35
    return combined, baseline, specific


def simulate_answers(dossier, questions, pole_percent, idf):
    answers = []
    for question in questions:
        if question["format"] == "agreement":
            combined, baseline, specific = direct_question_support(dossier, question, pole_percent, idf)
            answer = support_to_likert(combined)
            answers.append({"id": question["id"], "section": question["section"], "format": "agreement", "text": question["text"], "answer": answer, "combined": round(combined, 2), "baseline": round(baseline, 2), "specific": round(specific, 2), "poles": question["poles"]})
        else:
            combined, baseline, specific = bipolar_question_support(dossier, question, pole_percent, idf)
            answer = support_to_likert(combined)
            answers.append({"id": question["id"], "section": question["section"], "format": "bipolar", "left_text": question["left_text"], "right_text": question["right_text"], "answer": answer, "combined": round(combined, 2), "baseline": round(baseline, 2), "specific": round(specific, 2), "left_pole": question["left_pole"], "right_pole": question["right_pole"]})
    return answers


def calculate_scores(answers):
    pole_scores = dict((pole, 0) for pole in ["E", "I", "S", "N", "F", "T", "J", "P"])
    for answer in answers:
        if answer["format"] == "agreement":
            support = answer["answer"] - 1
            for pole in answer["poles"]:
                pole_scores[pole] += support
        else:
            pole_scores[answer["left_pole"]] += 5 - answer["answer"]
            pole_scores[answer["right_pole"]] += answer["answer"] - 1

    percentages = {}
    pair_margins = {}
    type_letters = []
    for axis, left, right in [("EI", "E", "I"), ("SN", "S", "N"), ("FT", "F", "T"), ("JP", "J", "P")]:
        total = pole_scores[left] + pole_scores[right]
        left_pct = int(round(pole_scores[left] / float(total) * 100)) if total else 50
        left_pct = max(1, min(99, left_pct))
        right_pct = 100 - left_pct
        percentages[left] = left_pct
        percentages[right] = right_pct
        winner = left if left_pct >= right_pct else right
        loser = right if winner == left else left
        pair_margins[axis] = {"winner": winner, "loser": loser, "margin": abs(left_pct - right_pct), "left": left_pct, "right": right_pct}
        type_letters.append(winner)

    type_code = "".join(type_letters)
    confidence = round(sum(item["margin"] for item in pair_margins.values()) / 4.0, 2)
    return pole_scores, percentages, pair_margins, type_code, confidence


def confidence_label(confidence):
    if confidence >= 30:
        return "高"
    if confidence >= 16:
        return "中"
    return "低"


def backup_type_info(type_code, pair_margins):
    axis_order = [("EI", 0, ("E", "I")), ("SN", 1, ("S", "N")), ("FT", 2, ("F", "T")), ("JP", 3, ("J", "P"))]
    weakest = min(axis_order, key=lambda item: pair_margins[item[0]]["margin"])
    axis, index, pair = weakest
    current_letter = type_code[index]
    backup_letter = pair[1] if current_letter == pair[0] else pair[0]
    backup = list(type_code)
    backup[index] = backup_letter
    return "".join(backup), axis, current_letter, backup_letter, pair_margins[axis]["margin"]


def first_line(text):
    for line in safe_text(text).splitlines():
        cleaned = line.strip().lstrip("-").strip()
        if cleaned:
            return cleaned
    return ""


def section_focus_line(text, preferred_paragraph=1):
    paragraphs = [item.strip() for item in safe_text(text).split("\n\n") if item.strip()]
    if not paragraphs:
        return ""
    index = preferred_paragraph if preferred_paragraph < len(paragraphs) else 0
    return first_line(paragraphs[index])


def evidence_summary(dossier):
    sections = dossier["portrait_sections"]
    return {
        "core": first_line(sections.get("总体画像", "")),
        "cards": first_line(sections.get("卡牌剧情印证", "")),
        "slices": first_line(sections.get("主线/乐团切片印证", "")),
    }


def radar_svg(percentages, title):
    size = 520
    center = size / 2.0
    radius = 180
    levels = [20, 40, 60, 80, 100]

    def point(index, value):
        angle = -math.pi / 2 + index * (2 * math.pi / len(RADAR_ORDER))
        x = center + math.cos(angle) * radius * (value / 100.0)
        y = center + math.sin(angle) * radius * (value / 100.0)
        return x, y

    grid = []
    for level in levels:
        pts = []
        for idx in range(len(RADAR_ORDER)):
            x, y = point(idx, level)
            pts.append("%.2f,%.2f" % (x, y))
        grid.append('<polygon points="%s" fill="none" stroke="#d6d3d1" stroke-width="1" />' % " ".join(pts))

    axis_lines = []
    labels = []
    values = []
    data_points = []
    for idx, pole in enumerate(RADAR_ORDER):
        x, y = point(idx, 100)
        lx, ly = point(idx, 116)
        vx, vy = point(idx, 130)
        dx, dy = point(idx, percentages[pole])
        data_points.append("%.2f,%.2f" % (dx, dy))
        axis_lines.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#e7e5e4" stroke-width="1.2" />' % (center, center, x, y))
        labels.append('<text x="%.2f" y="%.2f" text-anchor="middle" dominant-baseline="middle" font-size="18" fill="#292524" font-family="Microsoft YaHei, PingFang SC, sans-serif">%s</text>' % (lx, ly, pole))
        values.append('<text x="%.2f" y="%.2f" text-anchor="middle" dominant-baseline="middle" font-size="13" fill="#78716c" font-family="Microsoft YaHei, PingFang SC, sans-serif">%s</text>' % (vx, vy, percentages[pole]))

    return """<svg xmlns="http://www.w3.org/2000/svg" width="{0}" height="{1}" viewBox="0 0 {0} {1}">
  <rect width="100%" height="100%" fill="#fcfbf8"/>
  <text x="{2:.2f}" y="34" text-anchor="middle" font-size="22" fill="#1c1917" font-family="Microsoft YaHei, PingFang SC, sans-serif">{3} MBTI 八维图</text>
  <g transform="translate(0,24)">
    {4}
    {5}
    <polygon points="{6}" fill="rgba(14,116,144,0.18)" stroke="#0f766e" stroke-width="3" />
    {7}
    {8}
    <circle cx="{2:.2f}" cy="{2:.2f}" r="4" fill="#0f766e" />
  </g>
</svg>
""".format(size, size + 70, center, title, "".join(grid), "".join(axis_lines), " ".join(data_points), "".join(labels), "".join(values))


def type_explanation_markdown(dossier, result):
    type_code = result["type"]
    backup = result["backup_type"]
    percentages = result["percentages"]
    pair_margins = result["pair_margins"]
    confidence = result["confidence"]
    evidence = evidence_summary(dossier)

    lines = [
        "# %s MBTI 类型解释" % dossier["display_name"],
        "",
        "- 角色名：%s" % dossier["character_name"],
        "- 主类型：%s" % type_code,
        "- 备选类型：%s" % backup,
        "- 置信度：%s（%s）" % (confidence_label(confidence), confidence),
        "- 题库：%s（48 题）" % QUESTION_BANK_NAME,
        "",
        "## 类型概述",
        "",
        "%s 的整体倾向是：%s" % (type_code, TYPE_ONE_LINERS.get(type_code, "更接近该类型的典型四维组合。")),
        "",
    ]

    if evidence["core"]:
        lines.extend(["## 人物核心", "", evidence["core"], ""])

    lines.extend(["## 为什么是这个类型", ""])
    for axis, left, right in [("EI", "E", "I"), ("SN", "S", "N"), ("FT", "F", "T"), ("JP", "J", "P")]:
        winner = pair_margins[axis]["winner"]
        loser = pair_margins[axis]["loser"]
        lines.append("- `%s > %s`（%s : %s）：%s" % (winner, loser, percentages[winner], percentages[loser], AXIS_REASON[winner]))

    lines.extend(["", "## 为什么不是备选类型", ""])
    lines.append("最接近的备选类型是 `%s`。它与主类型 `%s` 的区别主要落在 `%s` 这一轴上。" % (backup, type_code, result["backup_axis"]))
    lines.append("当前结果仍保留 `%s`，因为这一轴虽然不是最强，但仍有 `%s` 点优势。%s" % (result["backup_current"], result["backup_margin"], BACKUP_REASON[result["backup_current"]]))

    lines.extend(["", "## 四维结果", ""])
    for axis, left, right in [("EI", "E", "I"), ("SN", "S", "N"), ("FT", "F", "T"), ("JP", "J", "P")]:
        lines.append("- `%s`：%s %s / %s %s" % (axis, left, percentages[left], right, percentages[right]))

    lines.extend(["", "## 八维数据", ""])
    for pole in ["E", "I", "S", "N", "F", "T", "J", "P"]:
        lines.append("- `%s`：%s" % (pole, percentages[pole]))

    lines.extend(["", "## 图表", "", "![MBTI 八维图](mbti_radar.svg)", "", "## 证据依据", ""])
    lines.append("- 人物概述：%s" % (evidence["core"] or "未提取到明确摘要"))
    lines.append("- 卡牌剧情：%s" % (evidence["cards"] or "暂无明显卡牌印证摘要"))
    lines.append("- 剧情切片：%s" % (evidence["slices"] or "暂无明显切片印证摘要"))

    lines.extend(["", "## 模拟作答概览", "", "| 题号 | 题目/两端描述 | 作答 | 倾向值 |", "| --- | --- | --- | --- |"])
    for answer in result["answers"]:
        label = answer["text"] if answer["format"] == "agreement" else ("%s <-> %s" % (answer["left_text"], answer["right_text"]))
        lines.append("| %s | %s | %s | %.2f |" % (answer["id"], label.replace("|", "/"), answer["answer"], answer["combined"]))

    lines.extend(["", "## 题库来源", "", "- [OJTS 官方题目页](%s)" % QUESTION_BANK_SOURCE, "- 许可证：%s" % QUESTION_BANK_LICENSE, "- [本地题库文件](../ojts_question_bank_v2_1.json)", ""])
    return "\n".join(lines)


def build_summary(results):
    lines = [
        "# MBTI 问卷模拟总览",
        "",
        "- 题库：%s" % QUESTION_BANK_NAME,
        "- 题数：48",
        "- 来源：官方公开题目页（非 API）",
        "- 图表：八维雷达图（E/S/T/J/I/N/F/P）",
        "",
        "| 角色 | 主类型 | 备选类型 | 置信度 | E | I | S | N | F | T | J | P | 文件夹 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in results:
        p = result["percentages"]
        lines.append("| %s | %s | %s | %s (%s) | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (result["display_name"], result["type"], result["backup_type"], confidence_label(result["confidence"]), result["confidence"], p["E"], p["I"], p["S"], p["N"], p["F"], p["T"], p["J"], p["P"], result["folder"]))
    lines.append("")
    return "\n".join(lines)


def build_method_text():
    return "\n".join([
        "# MBTI 题库模拟分析说明",
        "",
        "- 当前采用题库：%s" % QUESTION_BANK_NAME,
        "- 题数：48",
        "- 来源：%s" % QUESTION_BANK_SOURCE,
        "- 许可证：%s" % QUESTION_BANK_LICENSE,
        "",
        "这套分析直接基于 OJTS 官方公开题目页中的原题文本，在本地构建题库并进行角色模拟作答，不再依赖外部 API 的现成结果。",
        "",
        "证据优先级固定为：",
        "1. `portrait.md` 作为人物骨架",
        "2. `card_stories.md` 作为重要验证",
        "3. `story_slices.md` 作为补充验证",
        "",
        "备选类型通过翻转当前结果中差距最小的一条轴得到，用来解释：这个角色最容易与哪个相邻类型混淆，以及为什么最终没有落到那个类型。",
        "",
    ])


AXES = [("EI", "E", "I"), ("SN", "S", "N"), ("FT", "F", "T"), ("JP", "J", "P")]


def clamp(value, low, high):
    return max(low, min(high, value))


def stable_seed(*parts):
    raw = "::".join(str(part) for part in parts)
    return int(hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16], 16)


def population_variance(values):
    if len(values) <= 1:
        return 0.0
    mean = sum(values) / float(len(values))
    return sum((value - mean) ** 2 for value in values) / float(len(values))


def confidence_label_cn(confidence):
    if confidence >= 30:
        return "高"
    if confidence >= 16:
        return "中"
    return "低"


def jitter_pole_percentages(base_percentages, rng):
    percentages = {}
    for _, left, right in AXES:
        left_base = float(base_percentages[left])
        margin = abs(base_percentages[left] - base_percentages[right])
        sigma = 2.5 + (100.0 - margin) * 0.09
        left_pct = round(clamp(left_base + rng.gauss(0.0, sigma), 1.0, 99.0), 2)
        right_pct = round(100.0 - left_pct, 2)
        percentages[left] = left_pct
        percentages[right] = right_pct
    return percentages


def simulate_answers_sampled(dossier, questions, pole_percent, idf, rng):
    answers = []
    for question in questions:
        if question["format"] == "agreement":
            combined, baseline, specific = direct_question_support(dossier, question, pole_percent, idf)
            ambiguity = 1.0 - min(abs(combined), 100.0) / 100.0
            noise_sigma = 4.5 + ambiguity * 10.0
            noise = rng.gauss(0.0, noise_sigma)
            noisy_combined = clamp(combined + noise, -100.0, 100.0)
            answer = support_to_likert(noisy_combined)
            answers.append(
                {
                    "id": question["id"],
                    "section": question["section"],
                    "format": "agreement",
                    "text": question["text"],
                    "answer": answer,
                    "combined": round(noisy_combined, 2),
                    "raw_combined": round(combined, 2),
                    "baseline": round(baseline, 2),
                    "specific": round(specific, 2),
                    "noise": round(noise, 2),
                    "noise_sigma": round(noise_sigma, 2),
                    "poles": question["poles"],
                }
            )
        else:
            combined, baseline, specific = bipolar_question_support(dossier, question, pole_percent, idf)
            ambiguity = 1.0 - min(abs(combined), 100.0) / 100.0
            noise_sigma = 4.5 + ambiguity * 10.0
            noise = rng.gauss(0.0, noise_sigma)
            noisy_combined = clamp(combined + noise, -100.0, 100.0)
            answer = support_to_likert(noisy_combined)
            answers.append(
                {
                    "id": question["id"],
                    "section": question["section"],
                    "format": "bipolar",
                    "left_text": question["left_text"],
                    "right_text": question["right_text"],
                    "answer": answer,
                    "combined": round(noisy_combined, 2),
                    "raw_combined": round(combined, 2),
                    "baseline": round(baseline, 2),
                    "specific": round(specific, 2),
                    "noise": round(noise, 2),
                    "noise_sigma": round(noise_sigma, 2),
                    "left_pole": question["left_pole"],
                    "right_pole": question["right_pole"],
                }
            )
    return answers


def calculate_scores_precise(answers):
    pole_scores = dict((pole, 0) for pole in ["E", "I", "S", "N", "F", "T", "J", "P"])
    for answer in answers:
        if answer["format"] == "agreement":
            support = answer["answer"] - 1
            for pole in answer["poles"]:
                pole_scores[pole] += support
        else:
            pole_scores[answer["left_pole"]] += 5 - answer["answer"]
            pole_scores[answer["right_pole"]] += answer["answer"] - 1

    percentages = {}
    pair_margins = {}
    type_letters = []
    for axis, left, right in AXES:
        total = pole_scores[left] + pole_scores[right]
        left_pct = round(pole_scores[left] / float(total) * 100.0, 2) if total else 50.0
        left_pct = clamp(left_pct, 1.0, 99.0)
        right_pct = round(100.0 - left_pct, 2)
        percentages[left] = left_pct
        percentages[right] = right_pct
        winner = left if left_pct >= right_pct else right
        loser = right if winner == left else left
        pair_margins[axis] = {
            "winner": winner,
            "loser": loser,
            "margin": round(abs(left_pct - right_pct), 2),
            "left": left_pct,
            "right": right_pct,
        }
        type_letters.append(winner)

    type_code = "".join(type_letters)
    confidence = round(sum(item["margin"] for item in pair_margins.values()) / 4.0, 2)
    return pole_scores, percentages, pair_margins, type_code, confidence


def pair_margins_from_percentages(percentages):
    pair_margins = {}
    type_letters = []
    for axis, left, right in AXES:
        left_pct = round(float(percentages[left]), 2)
        right_pct = round(float(percentages[right]), 2)
        winner = left if left_pct >= right_pct else right
        loser = right if winner == left else left
        pair_margins[axis] = {
            "winner": winner,
            "loser": loser,
            "margin": round(abs(left_pct - right_pct), 2),
            "left": left_pct,
            "right": right_pct,
        }
        type_letters.append(winner)
    type_code = "".join(type_letters)
    confidence = round(sum(item["margin"] for item in pair_margins.values()) / 4.0, 2)
    return pair_margins, type_code, confidence


def summarize_answer_runs(questions, run_results):
    summaries = []
    for question in questions:
        matching = []
        for run in run_results:
            for answer in run["answers"]:
                if answer["id"] == question["id"]:
                    matching.append(answer)
                    break

        answer_values = [item["answer"] for item in matching]
        combined_values = [item["combined"] for item in matching]
        raw_values = [item["raw_combined"] for item in matching]
        summary = {
            "id": question["id"],
            "format": question["format"],
            "answer_mean": round(sum(answer_values) / float(len(answer_values)), 2),
            "answer_variance": round(population_variance(answer_values), 4),
            "combined_mean": round(sum(combined_values) / float(len(combined_values)), 2),
            "combined_variance": round(population_variance(combined_values), 4),
            "raw_combined_mean": round(sum(raw_values) / float(len(raw_values)), 2),
            "raw_combined_variance": round(population_variance(raw_values), 4),
        }
        if question["format"] == "agreement":
            summary["text"] = question["text"]
            summary["poles"] = question["poles"]
        else:
            summary["left_text"] = question["left_text"]
            summary["right_text"] = question["right_text"]
            summary["left_pole"] = question["left_pole"]
            summary["right_pole"] = question["right_pole"]
        summaries.append(summary)
    return summaries


def evidence_summary_v2(dossier):
    sections = dossier["portrait_sections"]
    return {
        "core": first_line(sections.get("总体画像", "")),
        "cards": first_line(sections.get("卡牌剧情印证", "")),
        "slices": first_line(sections.get("主线/乐团切片印证", "")),
    }


def percentages_from_type_list(type_list):
    if not type_list:
        return {}
    counts = dict((pole, 0.0) for pole in ["E", "I", "S", "N", "F", "T", "J", "P"])
    for type_code in type_list:
        if len(type_code) != 4:
            continue
        counts[type_code[0]] += 1.0
        counts[type_code[1]] += 1.0
        counts[type_code[2]] += 1.0
        counts[type_code[3]] += 1.0
    total = float(len(type_list))
    percentages = {}
    for _, left, right in AXES:
        left_pct = round(counts[left] / total * 100.0, 2)
        right_pct = round(100.0 - left_pct, 2)
        percentages[left] = left_pct
        percentages[right] = right_pct
    return percentages


def percentages_from_type_code(type_code):
    if len(type_code) != 4:
        return {}
    percentages = {}
    for index, (_, left, right) in enumerate(AXES):
        wanted = type_code[index]
        other = right if wanted == left else left
        percentages[wanted] = 100.0
        percentages[other] = 0.0
    return percentages


def source_pole_percentages(dossier, idf):
    source_percentages = {}
    for source_name, corpus in dossier.get("source_corpora", {}).items():
        if not corpus:
            continue
        source_percentages[source_name] = pole_percentages(corpus_pole_scores(corpus, idf))
    return source_percentages


def blend_percentages(weighted_signals):
    blended = {}
    for _, left, right in AXES:
        left_total = 0.0
        weight_total = 0.0
        for _, weight, signal in weighted_signals:
            if not signal:
                continue
            left_total += float(signal[left]) * weight
            weight_total += weight
        left_pct = round(left_total / weight_total, 2) if weight_total else 50.0
        blended[left] = left_pct
        blended[right] = round(100.0 - left_pct, 2)
    return blended


def enforce_type_anchor(percentages, type_code):
    adjusted = dict(percentages)
    details = []
    if len(type_code) != 4:
        return adjusted, details
    for index, (axis, left, right) in enumerate(AXES):
        wanted = type_code[index]
        other = right if wanted == left else left
        if adjusted[wanted] <= adjusted[other]:
            adjusted[wanted] = 50.5
            adjusted[other] = 49.5
            details.append({"axis": axis, "mode": "anchor", "wanted": wanted})
    return adjusted, details


def build_reference_profile(dossier, calibration_entry, idf):
    calibration_entry = calibration_entry or {}
    possible_types = [str(item).strip().upper() for item in calibration_entry.get("possible_types", []) if str(item).strip()]
    vote_winner_type = calibration_entry.get("vote_winner_type", "").strip().upper()
    if len(vote_winner_type) != 4 and possible_types:
        vote_winner_type = possible_types[0]
    if len(vote_winner_type) != 4:
        return None

    source_percentages = source_pole_percentages(dossier, idf)
    reference_percentages = percentages_from_type_code(vote_winner_type)
    weighted_signals = [
        ("reference", REFERENCE_TYPE_WEIGHT, reference_percentages),
        ("portrait", PORTRAIT_WEIGHT, source_percentages.get("portrait", {})),
        ("card", CARD_WEIGHT, source_percentages.get("card", {})),
        ("story", SLICE_WEIGHT, source_percentages.get("story", {})),
    ]
    blended_percentages = blend_percentages(weighted_signals)
    anchored_percentages, anchor_details = enforce_type_anchor(blended_percentages, vote_winner_type)
    return {
        "applied": calibration_entry.get("use_for_calibration", True),
        "mode": "pdb_anchor",
        "details": anchor_details,
        "possible_types": possible_types or [vote_winner_type],
        "vote_winner_type": vote_winner_type,
        "fixed_final_type": vote_winner_type,
        "source": calibration_entry.get("source", "personality-database.com"),
        "weights": {
            "reference": REFERENCE_TYPE_WEIGHT,
            "portrait": PORTRAIT_WEIGHT,
            "card": CARD_WEIGHT,
            "story": SLICE_WEIGHT,
        },
        "reference_percentages": reference_percentages,
        "source_percentages": source_percentages,
        "blended_percentages": blended_percentages,
        "anchored_percentages": anchored_percentages,
    }


def apply_reference_profile(raw_percentages, reference_profile):
    if not reference_profile or not reference_profile.get("applied"):
        return dict(raw_percentages), {"applied": False, "mode": "none", "details": []}
    return dict(reference_profile["anchored_percentages"]), reference_profile


def aggregate_run_results(dossier, questions, run_results, calibration_entry=None, reference_profile=None):
    raw_percentages = {}
    percentage_variances = {}
    pole_scores = {}
    for pole in RADAR_ORDER:
        values = [run["percentages"][pole] for run in run_results]
        raw_percentages[pole] = round(sum(values) / float(len(values)), 2)
        percentage_variances[pole] = round(population_variance(values), 4)
        score_values = [run["pole_scores"][pole] for run in run_results]
        pole_scores[pole] = round(sum(score_values) / float(len(score_values)), 2)

    raw_pair_margins, raw_type, raw_confidence = pair_margins_from_percentages(raw_percentages)
    raw_backup_type, raw_backup_axis, raw_backup_current, raw_backup_alt, raw_backup_margin = backup_type_info(raw_type, raw_pair_margins)
    percentages, calibration = apply_reference_profile(raw_percentages, reference_profile)
    pair_margins, type_code, confidence = pair_margins_from_percentages(percentages)
    backup_type, backup_axis, backup_current, backup_alt, backup_margin = backup_type_info(type_code, pair_margins)
    confidence_values = [run["confidence"] for run in run_results]

    axis_stats = {}
    for axis, left, right in AXES:
        margins = [abs(run["percentages"][left] - run["percentages"][right]) for run in run_results]
        axis_stats[axis] = {
            "winner": pair_margins[axis]["winner"],
            "loser": pair_margins[axis]["loser"],
            "left_mean": percentages[left],
            "right_mean": percentages[right],
            "mean_margin": round(sum(margins) / float(len(margins)), 2),
            "margin_variance": round(population_variance(margins), 4),
        }

    type_counter = Counter(run["type"] for run in run_results)
    backup_counter = Counter(run["backup_type"] for run in run_results)
    type_frequency = [
        {"type": code, "count": count, "ratio": round(count / float(len(run_results)) * 100.0, 2)}
        for code, count in sorted(type_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    backup_frequency = [
        {"type": code, "count": count, "ratio": round(count / float(len(run_results)) * 100.0, 2)}
        for code, count in sorted(backup_counter.items(), key=lambda item: (-item[1], item[0]))
    ]

    average_variance = round(sum(percentage_variances[pole] for pole in RADAR_ORDER) / float(len(RADAR_ORDER)), 4)

    return {
        "folder": dossier["folder"].name,
        "display_name": dossier["display_name"],
        "character_name": dossier["character_name"],
        "run_count": len(run_results),
        "raw_type": raw_type,
        "raw_backup_type": raw_backup_type,
        "raw_backup_axis": raw_backup_axis,
        "raw_backup_current": raw_backup_current,
        "raw_backup_alt": raw_backup_alt,
        "raw_backup_margin": raw_backup_margin,
        "raw_confidence": raw_confidence,
        "raw_percentages": raw_percentages,
        "raw_pair_margins": raw_pair_margins,
        "type": type_code,
        "backup_type": backup_type,
        "backup_axis": backup_axis,
        "backup_current": backup_current,
        "backup_alt": backup_alt,
        "backup_margin": backup_margin,
        "calibration": calibration,
        "confidence": confidence,
        "confidence_variance": round(population_variance(confidence_values), 4),
        "type_stability_count": type_counter[type_code],
        "type_stability_ratio": round(type_counter[type_code] / float(len(run_results)) * 100.0, 2),
        "raw_type_stability_count": type_counter[raw_type],
        "raw_type_stability_ratio": round(type_counter[raw_type] / float(len(run_results)) * 100.0, 2),
        "backup_stability_count": backup_counter[backup_type],
        "backup_stability_ratio": round(backup_counter[backup_type] / float(len(run_results)) * 100.0, 2),
        "pole_scores": pole_scores,
        "percentages": percentages,
        "percentage_variances": percentage_variances,
        "average_percentage_variance": average_variance,
        "pair_margins": pair_margins,
        "axis_stats": axis_stats,
        "type_frequency": type_frequency,
        "backup_frequency": backup_frequency,
        "answers": summarize_answer_runs(questions, run_results),
        "runs": run_results,
    }


def type_explanation_markdown_v2(dossier, result):
    type_code = result["type"]
    backup = result["backup_type"]
    percentages = result["percentages"]
    pair_margins = result["pair_margins"]
    confidence = result["confidence"]
    evidence = evidence_summary_v2(dossier)
    calibration = result["calibration"]

    lines = [
        "# %s MBTI 类型解释" % dossier["display_name"],
        "",
        "- 角色名：%s" % dossier["character_name"],
        "- 最终类型：%s" % type_code,
        "- 备选类型：%s" % backup,
        "- 原始聚合类型：%s" % result["raw_type"],
        "- 采样轮次：%s" % result["run_count"],
        "- 主类型稳定度：%s/%s（%s%%）" % (result["type_stability_count"], result["run_count"], result["type_stability_ratio"]),
        "- 原始聚合稳定度：%s/%s（%s%%）" % (result["raw_type_stability_count"], result["run_count"], result["raw_type_stability_ratio"]),
        "- 置信度：%s（%s）" % (confidence_label_cn(confidence), confidence),
        "- 置信度方差：%s" % result["confidence_variance"],
        "- 题库：%s（48 题）" % QUESTION_BANK_NAME,
        "",
        "## 类型概述",
        "",
        "%s 的整体倾向是：%s" % (type_code, TYPE_ONE_LINERS.get(type_code, "更接近该类型的典型四维组合。")),
        "",
    ]

    if evidence["core"]:
        lines.extend(["## 人物核心", "", evidence["core"], ""])

    lines.extend(["## PDB 校核", ""])
    if calibration.get("applied"):
        lines.append("- 已应用 PDB 主参考：来源 `%s`。" % (calibration.get("source") or "personality-database.com"))
        if calibration.get("weights"):
            weights = calibration["weights"]
            lines.append(
                "- 权重分配：PDB %.0f%% / 人设概要 %.0f%% / 卡牌剧情 %.0f%% / 剧情切片 %.0f%%。"
                % (weights["reference"] * 100, weights["portrait"] * 100, weights["card"] * 100, weights["story"] * 100)
            )
        if calibration.get("possible_types"):
            lines.append("- PDB 类型排序：`%s`" % " / ".join(calibration["possible_types"]))
        if calibration.get("vote_winner_type"):
            lines.append("- 最终类型先按 PDB 最高票定锚：`%s`" % calibration["vote_winner_type"])
        if calibration.get("fixed_final_type"):
            lines.append("- 指定锁定类型：`%s`" % calibration["fixed_final_type"])
        if result["raw_type"] != type_code:
            lines.append("- 原始问卷聚合结果为 `%s`，按主参考回写后最终结果为 `%s`。" % (result["raw_type"], type_code))
    else:
        lines.append("- 当前角色未应用 PDB 校核，最终结果完全来自资料模拟。")

    lines.extend(["## 为什么是这个类型", ""])
    for axis, left, right in AXES:
        winner = pair_margins[axis]["winner"]
        loser = pair_margins[axis]["loser"]
        axis_info = result["axis_stats"][axis]
        lines.append(
            "- `%s > %s`（%.2f : %.2f，平均轴差 %.2f，方差 %.4f）：%s"
            % (
                winner,
                loser,
                percentages[winner],
                percentages[loser],
                axis_info["mean_margin"],
                axis_info["margin_variance"],
                AXIS_REASON[winner],
            )
        )

    lines.extend(["", "## 为什么不是备选类型", ""])
    lines.append("最接近的备选类型是 `%s`。它与主类型 `%s` 的差别主要落在 `%s` 这一轴上。" % (backup, type_code, result["backup_axis"]))
    lines.append(
        "最终仍保留 `%s`，因为该轴平均优势还有 `%.2f`，虽然会波动，但整体没有被 `%s` 反超。%s"
        % (result["backup_current"], result["backup_margin"], result["backup_alt"], BACKUP_REASON[result["backup_current"]])
    )

    lines.extend(["", "## 四维结果", ""])
    for axis, left, right in AXES:
        axis_info = result["axis_stats"][axis]
        lines.append(
            "- `%s`：%s %.2f / %s %.2f，轴差方差 %.4f"
            % (axis, left, percentages[left], right, percentages[right], axis_info["margin_variance"])
        )

    lines.extend(["", "## 八维数据", ""])
    for pole in RADAR_ORDER:
        lines.append("- `%s`：均值 %.2f，方差 %.4f" % (pole, percentages[pole], result["percentage_variances"][pole]))

    lines.extend(["", "## 类型稳定性", ""])
    for item in result["type_frequency"]:
        lines.append("- `%s`：%s 次（%s%%）" % (item["type"], item["count"], item["ratio"]))

    lines.extend(["", "## 图表", "", "![MBTI 八维图](mbti_radar.svg)", "", "## 证据依据", ""])
    lines.append("- 人物概述：%s" % (evidence["core"] or "未提取到明确摘要"))
    lines.append("- 卡牌剧情：%s" % (evidence["cards"] or "暂无明显卡牌印证摘要"))
    lines.append("- 剧情切片：%s" % (evidence["slices"] or "暂无明显切片印证摘要"))

    lines.extend(
        [
            "",
            "## 模拟作答概览",
            "",
            "| 题号 | 题目/两端描述 | 平均作答 | 作答方差 | 平均倾向值 | 倾向方差 |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for answer in result["answers"]:
        label = answer["text"] if answer["format"] == "agreement" else ("%s <-> %s" % (answer["left_text"], answer["right_text"]))
        lines.append(
            "| %s | %s | %.2f | %.4f | %.2f | %.4f |"
            % (
                answer["id"],
                label.replace("|", "/"),
                answer["answer_mean"],
                answer["answer_variance"],
                answer["combined_mean"],
                answer["combined_variance"],
            )
        )

    lines.extend(
        [
            "",
            "## 题库来源",
            "",
            "- [OJTS 官方题目页](%s)" % QUESTION_BANK_SOURCE,
            "- 许可证：%s" % QUESTION_BANK_LICENSE,
            "- [本地题库文件](../ojts_question_bank_v2_1.json)",
            "",
        ]
    )
    return "\n".join(lines)


def build_summary_v2(results):
    lines = [
        "# MBTI 问卷模拟总览",
        "",
        "- 题库：%s" % QUESTION_BANK_NAME,
        "- 题数：48",
        "- 来源：官方公开题目页（非 API）",
        "- 采样方式：每个角色重复模拟 %s 轮，先按主参考定锚，再结合资料塑形八维" % SIMULATION_RUNS,
        "- PDB 主参考：最高票类型直接作为主锚点，占最终八维 50%",
        "- 资料权重：人物画像 25% / 卡牌剧情 15% / 剧情切片 10%",
        "- 图表：八维雷达图（E/S/T/J/I/N/F/P）",
        "",
        "| 角色 | 最终类型 | 原始聚合 | 备选类型 | 稳定度 | PDB主参考 | 置信度 | EI | SN | FT | JP | 文件夹 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in results:
        p = result["percentages"]
        lines.append(
            "| %s | %s | %s | %s | %s/%s (%s%%) | %s | %s (%s) | E %.2f / I %.2f | S %.2f / N %.2f | F %.2f / T %.2f | J %.2f / P %.2f | %s |"
            % (
                result["display_name"],
                result["type"],
                result["raw_type"],
                result["backup_type"],
                result["type_stability_count"],
                result["run_count"],
                result["type_stability_ratio"],
                "是" if result["calibration"].get("applied") else "否",
                confidence_label_cn(result["confidence"]),
                result["confidence"],
                p["E"],
                p["I"],
                p["S"],
                p["N"],
                p["F"],
                p["T"],
                p["J"],
                p["P"],
                result["folder"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def build_method_text_v2():
    return "\n".join(
        [
            "# MBTI 题库模拟分析说明",
            "",
            "- 当前采用题库：%s" % QUESTION_BANK_NAME,
            "- 题数：48",
            "- 来源：%s" % QUESTION_BANK_SOURCE,
            "- 许可证：%s" % QUESTION_BANK_LICENSE,
            "- 重复采样轮次：%s" % SIMULATION_RUNS,
            "",
            "这套分析直接基于 OJTS 官方公开题目页中的原题文本，在本地构建题库并进行角色模拟作答，不依赖外部 API 的现成结果。",
            "",
            "当前解释框架采用“PDB 主类型定锚 + 题库模拟细化八维”的双层结构：",
            "1. 先区分角色的核心人格（长期动机、稳定价值、亲密关系中的自然反应）与人格面具（公开场合、职责位置、剧情防御姿态）",
            "2. 如果角色同时显露看似矛盾的功能特征，优先判断哪些属于面具/压力表现，而不是直接把矛盾行为当成混型",
            "3. 最终类型先由 PDB 最高票四字母定锚，再用资料证据决定每一轴到底有多强",
            "",
            "证据优先级与占比固定为：",
            "1. `community_mbti_calibration.json` 中的 PDB 最高票类型占 50%，直接决定最终四字母的大方向",
            "2. `portrait.md` 中的总体画像与外部设定占 25%，用于确定人物核心动机和稳定人格骨架",
            "3. `card_stories.md` 占 15%，用于修正角色在私下、低压力和亲密关系里的自然表现",
            "4. `story_slices.md` 占 10%，用于补充主线位置、冲突状态和高压情境下的面具反应",
            "",
            "PDB 参考规则：",
            "1. 只使用 `community_mbti_calibration.json` 中保留的最高票类型作为主参考",
            "2. 该主参考占 50%，并锁定最终四字母方向；其他资料只负责调整各轴强弱与八维形状",
            "3. 如果资料证据与 PDB 方向冲突，最终类型仍以 PDB 主参考为准，但会在轴强度上保留拉扯痕迹",
            "",
            "为了避免单次结果过于僵硬，当前版本会对每个角色进行 10 轮可复现采样：",
            "1. 先按 `50% PDB + 25% 人设概要 + 15% 卡牌 + 10% 剧情切片` 合成基础四轴",
            "2. 每轮对基础倾向加入小幅随机扰动",
            "3. 每道题再根据证据强弱加入轻微噪声，模拟不同轮次下的解释波动",
            "4. 把 10 轮结果汇总为原始问卷波动，再回写到已经定锚的最终八维",
            "5. 最终类型固定服从主参考，备选类型则由最接近翻转的一轴决定",
            "",
            "这里的随机数使用角色标识与轮次生成稳定种子，因此同一份资料在同一版本脚本下可重复得到相同结果。",
            "",
        ]
    )


def main():
    question_bank = parse_ojts_question_bank()
    questions = question_bank["questions"]
    community_calibration = load_community_calibration()

    dossiers = [parse_dossier(folder) for folder in sorted(DOSSIER_ROOT.iterdir()) if folder.is_dir() and (folder / "portrait.md").exists()]
    idf = build_keyword_idf(dossiers, questions)
    results = []

    for dossier in dossiers:
        base_scores = pole_baseline_scores(dossier, idf)
        fallback_percentages = pole_percentages(base_scores)
        calibration_entry = community_calibration.get(dossier["folder"].name)
        reference_profile = build_reference_profile(dossier, calibration_entry, idf)
        base_percentages = reference_profile["anchored_percentages"] if reference_profile and reference_profile.get("applied") else fallback_percentages
        run_results = []

        for run_index in range(SIMULATION_RUNS):
            rng = random.Random(stable_seed(dossier["folder"].name, run_index + 1))
            run_baseline = jitter_pole_percentages(base_percentages, rng)
            answers = simulate_answers_sampled(dossier, questions, run_baseline, idf, rng)
            pole_scores, percentages, pair_margins, type_code, confidence = calculate_scores_precise(answers)
            backup_type, backup_axis, backup_current, backup_alt, backup_margin = backup_type_info(type_code, pair_margins)
            run_results.append(
                {
                    "run_index": run_index + 1,
                    "baseline_percentages": run_baseline,
                    "pole_scores": pole_scores,
                    "percentages": percentages,
                    "pair_margins": pair_margins,
                    "type": type_code,
                    "backup_type": backup_type,
                    "backup_axis": backup_axis,
                    "backup_current": backup_current,
                    "backup_alt": backup_alt,
                    "backup_margin": backup_margin,
                    "confidence": confidence,
                    "answers": answers,
                }
            )

        result = aggregate_run_results(dossier, questions, run_results, calibration_entry=calibration_entry, reference_profile=reference_profile)

        folder = dossier["folder"]
        (folder / "mbti_answers.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        (folder / "mbti_radar.svg").write_text(radar_svg(result["percentages"], dossier["display_name"]), encoding="utf-8")
        (folder / "mbti_analysis.md").write_text(type_explanation_markdown_v2(dossier, result), encoding="utf-8")
        results.append(result)
        print("%s: %s / %s (%s%%)" % (folder.name, result["type"], result["backup_type"], result["type_stability_ratio"]))

    SUMMARY_PATH.write_text(build_summary_v2(results), encoding="utf-8")
    METHOD_PATH.write_text(build_method_text_v2(), encoding="utf-8")
    print("done=%s" % len(results))


if __name__ == "__main__":
    main()
