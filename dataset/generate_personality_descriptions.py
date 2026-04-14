from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


DATASET_ROOT = Path(__file__).resolve().parent
DOSSIER_ROOT = DATASET_ROOT / "character_dossiers"
REVIEW_PATH = DATASET_ROOT / "personality_descriptions_review.md"


MANUAL_OVERRIDES = {
    "char_kasumi_kasumi": "户山香澄像会自己发光的人，心里一有“好喜欢”“好想试试”的念头，就会立刻拉着别人一起向前。她的热情很有感染力，擅长把模糊的憧憬变成真实的起点；真到要慢下来收束细节时，才会露出一点冒失和不周全。可也正因为她总肯先相信那点心动，身边的人才会一次次被她带着迈出第一步。",
    "char_soyo_soyo": "长崎爽世表面总是温柔得体，很会照顾人，也很懂得把关系维持在体面的样子里。可她越是看重羁绊，越容易把不安和执念藏得更深，于是温柔里常带着一点不肯松手的控制感，让人既想依赖她，又难完全看透她。她习惯把自己放在最能周旋的位置上，所以越是亲近的人，越会察觉她那份体贴里其实藏着防备。",
    "char_sakiko_sakiko": "丰川祥子身上有种近乎苛刻的骄傲与秩序感。她习惯把局面握在自己手里，也习惯把责任揽到自己肩上，像是只允许事情按她认定的方式成立。只是那份强硬并不单是冷漠，更像不愿再失去什么之后，留下的一层锋利外壳。她不愿把脆弱摊给任何人看，于是连求助和退让，常常也说得像命令一样。",
    "char_tomori_tomori": "高松灯安静、迟缓，却并不空白；她对情绪、词句和细小事物有近乎本能的敏感，总会把别人忽略的东西放进心里反复回响。她不擅长顺畅地靠近人，却很认真地渴望被理解，所以越沉默，越能让人感觉到她内里那份柔软而固执的重量。",
    "char_chiyu_chiyu": "CHU²像把自己当天才也当答案的人，聪明、骄傲、好胜，习惯用最直接的方式定义舞台和胜负。她身上那股不肯认输的锋芒很有压迫感，可真要看久了，又会发现那份强势里藏着孩子气的执拗，和其实很怕被否定的心。她总想站在最显眼也最正确的位置上，于是被理解这件事，对她来说反而比赢更难开口。",
    "char_rinko_rinko": "白金燐子安静得像总与人群隔着半步距离，说话轻，情绪也收得很深，却会把重要的人和事默默记得很久。她并不是没有主见，只是比起张扬表达，更习惯把心意放进行动和坚持里，因此越相处，越能感到她温柔背后那份安静而稳定的力量。",
}


TYPE_TRAITS = {
    "ENFJ": ["很懂得照看别人的情绪", "往往会先把人和关系放进心里", "习惯一边顾全别人一边推动事情"],
    "ENFP": ["心里一有喜欢的东西就会往前扑", "总能先看到可能性和亮光", "很容易把自己的热情传给周围的人"],
    "ENTJ": ["习惯把局面握在手里", "说到底更相信判断力和执行力", "一旦认定方向就会毫不犹豫地往前推"],
    "ENTP": ["脑子转得快，也总想把事情再翻一面看看", "很擅长抛出新想法和新问题", "越是复杂和有挑战的局面，越容易激起她的兴致"],
    "ESFJ": ["总会先顾到气氛、关系和分寸", "很会照顾人，也很会维持场面", "常把体贴和稳妥放在最前面"],
    "ESFP": ["活得很有当下感", "表达直接，情绪和行动都来得很快", "总会把存在感和热度带进人群里"],
    "ESTJ": ["做事很讲章法和落实", "更习惯用标准、责任和效率说话", "一到需要有人把事情定下来时就会显出力量"],
    "ESTP": ["反应很快，也很敢冲", "总会先盯住眼前最实际的突破口", "越是变化快的场面，越能看出她的狠劲和手感"],
    "INFJ": ["很少把心事轻易摊开", "总带着比表面更深一层的感受和判断", "很多温柔和执拗都藏在不声张的地方"],
    "INFP": ["很多选择都来自内心很个人的坚持", "对情绪和意义有很深的在意", "表面也许安静，心里却始终守着不愿随便交出去的东西"],
    "INTJ": ["骨子里有很强的秩序感和方向感", "做决定时更看全局和结果", "比起热闹表达，更习惯把判断藏在冷静里"],
    "INTP": ["比起立刻表态，更习惯先观察和拆解", "常把真正的想法留在心里慢慢推演", "很多时候显得疏离，其实只是先在自己的思路里把事情想透"],
    "ISFJ": ["总会默默记住别人没说出口的部分", "安静，却很会把责任往自己身上揽", "温和外表下有很深的在意和忍耐"],
    "ISFP": ["待人柔和，却不会轻易放弃自己的感受", "很多心思不说出来，却都藏在反应里", "比起解释自己，更习惯顺着真实的心意去做选择"],
    "ISTJ": ["做事稳，心里也自有一套分寸", "不太会随便摇摆，更相信经验、责任和判断", "很多可靠感不是说出来的，而是一步一步做出来的"],
    "ISTP": ["总像先退半步看清局面的人", "不爱多说，却很少真的迟钝", "比起解释情绪，更擅长用行动和反应来处理问题"],
}


TYPE_SOFT_TURNS = {
    "ENFJ": ["只是太想把所有人都照顾好时，那份温柔也会慢慢变成自己的负担。", "真到什么都想维系住的时候，她也容易把自己逼得太紧。", "可她越舍不得让别人失望，越容易把压力都悄悄往自己身上收。"],
    "ENFP": ["真到要慢下来收束细节时，才会露出一点冒失和不周全。", "只是热情一旦跑在前面，细节和分寸就难免跟得慢半拍。", "可一旦只顾着往前追那点闪光，她也会把后面的麻烦想得太轻。"],
    "ENTJ": ["只是那股掌控欲一旦太满，就容易让人觉得难以靠近。", "不过她越想把一切握稳，越容易显出不肯退让的锋利。", "真到事情失控的边缘，她往往会先把自己那份强硬拿出来。"],
    "ENTP": ["只是想法一多、节奏一快，也难免让人一时跟不上她。", "不过她一旦太享受变化本身，反而容易把别人的步调甩在身后。", "可她越觉得局面有趣，越不容易老老实实停在原地。"],
    "ESFJ": ["只是越在意关系，越容易把真正的不安也一起藏深。", "可她越想把场面顾圆满，心里的执念就越不容易松开。", "真到最怕失去什么的时候，她那份温柔反而会变得格外用力。"],
    "ESFP": ["只是凭着感觉往前冲的时候，偶尔也会显得有些冒进。", "可一旦太相信当下的热度，后面的麻烦就未必都会提前想到。", "真到情绪和行动一起上来的时候，她也很难真的慢下来。"],
    "ESTJ": ["只是她一旦太想把事情做对，语气和态度就容易显得硬了一些。", "不过标准一高、责任一重，她也难免给人不太好亲近的感觉。", "可越是认定什么该怎么做，她越不容易轻易松口。"],
    "ESTP": ["只是那股敢冲的劲头上来时，往往顾不上给自己留太多余地。", "可她越想当场把问题拿下，越容易显得锋利又强硬。", "真到胜负心被点起来的时候，她的步子通常会比别人更猛一点。"],
    "INFJ": ["只是很多情绪都压在很深的地方，真碰到在意的人和事时，反而会显得格外执拗。", "可她越想把心事藏稳，越容易让那份沉默带上一点距离感。", "真到某些不能退开的时刻，她心里的坚持会比表面露出来得更重。"],
    "INFP": ["只是心里越珍惜什么，越不肯轻易退开，于是敏感和固执也常会一起出现。", "可一旦真的碰到触动内心的事，她往往比表面看起来更难放下。", "真到那些和心意有关的时刻，她向来不会轻轻松松地后退。"],
    "INTJ": ["只是那份冷静一旦太过锋利，也会让她显得比实际更难接近。", "可她越想把一切控制在判断之内，越容易露出不愿妥协的那一面。", "真到局面偏离预想的时候，她先露出来的往往不是慌乱，而是更硬的控制感。"],
    "INTP": ["只是想得太深太久的时候，她和别人的距离也会被无声地拉开。", "可她越沉进自己的思路里，越容易把真正的情绪留在外面。", "真到需要立刻把心里话说出口的时候，她反而常会慢半拍。"],
    "ISFJ": ["只是她太习惯忍耐和承担，所以很多真实想法都不会第一时间说出口。", "可她越想把别人照顾好，越容易忘了自己其实也会累。", "真到情绪被逼近边缘时，她那份安静里才会慢慢露出疲惫。"],
    "ISFP": ["只是心事一旦压得太久，那份温和里也会慢慢生出一点别扭和倔强。", "可她越不愿勉强自己，越会在沉默里把情绪藏得很深。", "真到碰上自己不想退让的地方，她的固执反而会显得很安静。"],
    "ISTJ": ["只是太想把分寸和标准守稳时，也会显得拘谨了一些。", "可她越想把事情放在正确的位置上，越不容易轻易放松下来。", "真到责任压上来的时候，她往往会先把自己收得更紧。"],
    "ISTP": ["只是很多情绪都不说出来时，旁人难免会觉得她有点远。", "可她越习惯自己消化一切，越容易把距离留在身上。", "真到情绪碰上来时，她常常还是先选择不声不响地自己扛。"],
}

TYPE_RELATIONAL = {
    "ENFJ": ["她不是那种会把关心挂在嘴边的人，却总会在别人快要失衡的时候先一步补上那个空缺。"],
    "ENFP": ["和她相处时，很容易被那股先相信、先点亮别人的劲头感染，连原本犹豫的人也会被带着向前。"],
    "ENTJ": ["她给人的压迫感往往不是为了逞强，而是太习惯替局面负责，所以总想把事情握在自己能控制的范围里。"],
    "ENTP": ["她的魅力常常就在那种不停变化的脑回路里，像总能把沉闷局面突然撬开一道新的口子。"],
    "ESFJ": ["她看起来总在照顾气氛，其实更在意的是每个人有没有被好好放进关系里。"],
    "ESFP": ["她很少让场子冷下来，情绪、热度和行动几乎总是同时到场，因此也特别容易把别人一起卷进自己的节奏。"],
    "ESTJ": ["她的可靠不只是能把事情做完，更在于一旦大家开始摇摆，她往往会是先把方向重新拎正的那个人。"],
    "ESTP": ["她身上那种利落感很像临场直觉先一步落地，所以越到需要马上做决定的时候，越能看出她的存在感。"],
    "INFJ": ["她并不急着让人理解自己，可一旦真的认定了谁或什么，心里的分量往往会沉得比表面重很多。"],
    "INFP": ["她不一定总把想法说得很响亮，但很多真正重要的选择，反而都藏在那些安静又不肯让步的地方。"],
    "INTJ": ["她并不依赖热闹来证明自己，很多力量都藏在提前看清方向、然后稳稳站住的位置里。"],
    "INTP": ["她看起来像总和人群隔着一点距离，可真要细看，就会发现她其实一直在用自己的方式理解眼前的一切。"],
    "ISFJ": ["她很少抢着站到最前面，却常常会在别人最容易忽略的地方把事情悄悄接住。"],
    "ISFP": ["她的温和并不等于没有棱角，只是那些坚持很少喊出来，而是安静地落在每一次选择里。"],
    "ISTJ": ["她不太靠夸张表达建立存在感，真正让人记住她的，往往是那种一步一步做出来的稳定。"],
    "ISTP": ["她未必会主动解释自己，但很多判断其实都藏在那种冷静、迅速又不多余的反应里。"],
}


CONTEXT_VARIANTS_STRONG = [
    "放到亲近关系和团体相处里看，这一面通常会更明显。",
    "越是和人长期相处，这种底色越藏不住。",
    "在私下状态和正式场合之间，这种气质其实都很稳定。",
    "真到关系被拉近之后，这一面往往会更清楚。",
]

CONTEXT_VARIANTS_MID = [
    "放到和人的相处里看，这种气质会更鲜明。",
    "一旦进入长期相处的状态，这一面就会慢慢浮出来。",
    "越是在熟人和同伴面前，这种底色越容易被看见。",
]


TYPE_FALLBACKS = {
    "ENFJ": "身上总带着温和又能把人聚拢起来的气质",
    "ENFP": "像会自己发光一样，总能把热情带给身边的人",
    "ENTJ": "身上总带着很强的目标感和压迫感",
    "ENTP": "像总会在下一秒抛出新念头的人",
    "ESFJ": "总让人先感到周到、妥帖和可靠",
    "ESFP": "总让人先注意到她身上的热度和存在感",
    "ESTJ": "身上有种利落、可靠又不太会摇摆的劲",
    "ESTP": "身上总有种说做就做的冲劲",
    "INFJ": "总像把很多话都藏在心里的人",
    "INFP": "身上有种很柔软、也很不肯轻易妥协的底色",
    "INTJ": "身上常有种冷静、清醒又不太好接近的感觉",
    "INTP": "像总和热闹隔着一点距离，却始终在看、在想的人",
    "ISFJ": "总让人先感到温和和可靠",
    "ISFP": "总显得安静柔和，却又自有分寸",
    "ISTJ": "总给人稳当、清楚、讲原则的感觉",
    "ISTP": "像总在沉默里先把局面看清的人",
}

ROLE_HINT_TOKENS = (
    "队长",
    "吉他手",
    "贝斯手",
    "鼓手",
    "键盘手",
    "小提琴手",
    "主唱",
    "歌手",
    "孩子",
    "成员",
    "DJ",
)

META_TOKENS = ("官方", "外部", "资料", "角色页", "角色介绍", "整体叙事", "角色功能", "理解重点", "说明了")

STYLE_TEMPLATES = [
    "她{trait}。",
    "很多时候，她{trait}。",
    "和人相处时，她{trait}。",
    "落到具体相处里，她{trait}。",
]


def stable_index(key: str, size: int) -> int:
    if size <= 0:
        return 0
    value = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)
    return value % size


def extract_section(markdown_text: str, title: str) -> str:
    pattern = re.compile(rf"^## {re.escape(title)}\s*$", re.M)
    match = pattern.search(markdown_text)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+", markdown_text[start:], re.M)
    end = start + next_heading.start() if next_heading else len(markdown_text)
    return markdown_text[start:end].strip()


def first_paragraph(text: str) -> str:
    paragraphs = [item.strip() for item in text.split("\n\n") if item.strip()]
    return paragraphs[0] if paragraphs else ""


def bullet_lines(text: str) -> list[str]:
    return [line[2:].strip() for line in text.splitlines() if line.strip().startswith("- ")]


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？])", text)
    return [item.strip() for item in parts if item.strip()]


def clean_overview_sentence(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"^从外部设定与已整理剧情综合来看，[^：]{0,80}：", "", cleaned)
    cleaned = re.sub(r"^从外部设定与已整理剧情综合来看，", "", cleaned)
    cleaned = re.sub(r"^[^，。]{0,20}在现有本地语料里出场较少，但", "", cleaned)
    cleaned = re.sub(r"^[^：]{0,40}其实给了一个很清晰的定位：", "", cleaned)
    cleaned = re.sub(r"^[^：]{0,40}给了一个很清晰的定位：", "", cleaned)
    replacements = [
        ("官方角色页里的", ""),
        ("官方与外部角色介绍里的", ""),
        ("官方与外部资料里的", ""),
        ("官方资料把", ""),
        ("官方资料里的", ""),
        ("官方资料中，", ""),
        ("官方资料里，", ""),
        ("官方角色介绍里，", ""),
        ("外部角色资料里，", ""),
        ("外部角色资料里的", ""),
        ("外部资料里，", ""),
        ("外部资料里的", ""),
        ("外部角色页里的", ""),
        ("官方角色介绍里，", ""),
        ("角色资料里，", ""),
        ("一直被写成会被", "一直会被"),
        ("常被写成", "常给人"),
        ("通常被塑造成", "是"),
        ("通常被写成", "常给人"),
        ("通常是", "是"),
        ("通常给人", "总给人"),
        ("被明确写成", "是"),
        ("被设定成", "是"),
        ("被定位为", "是"),
        ("通常被定义成", "是"),
        ("被写成", "常给人"),
    ]
    for old, new in replacements:
        cleaned = cleaned.replace(old, new)
    cleaned = re.sub(r"常给人(.+?)的成员", r"常给人\1的印象", cleaned)
    cleaned = cleaned.replace("她/他", "她")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = cleaned.replace("给人的感觉往往是", "给人的感觉是")
    cleaned = re.sub(r"^总给人", "让人觉得", cleaned)
    cleaned = re.sub(r"^常给人", "让人觉得", cleaned)
    sentences = [
        item
        for item in split_sentences(cleaned)
        if not any(flag in item for flag in ["结合本地剧情", "整体而言", "这说明", "当前没有卡牌侧补充", "尚未补入", "这里只能"])
    ]
    if not sentences:
        return ""
    first = sentences[0]
    if len(first) > 86:
        pieces = re.split(r"[，、；]", first)
        built = ""
        for piece in pieces:
            candidate = f"{built}，{piece}" if built else piece
            if len(candidate) > 72:
                break
            built = candidate
        first = (built or first[:70]).rstrip("，、；") + "。"
    return first


def read_meta_line(text: str, prefix: str) -> str:
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.split("：", 1)[1].strip()
    return ""


def soften_overview(text: str, short_name: str, type_code: str) -> str:
    if not text:
        fallback = TYPE_FALLBACKS.get(type_code, "有很鲜明的个人气质")
        return f"{short_name}{fallback}。"
    text = text.replace("《It'sMyGO!!!!!》", "《It's MyGO!!!!!》")
    text = text.replace("AveMujica", "Ave Mujica")
    text = re.sub(r"^(她|他)", short_name, text)
    text = re.sub(r"^([^\s，。]{1,12})写成", r"\1是", text)
    text = text.replace("在设定上天然同时属于", "天然同时属于")
    text = text.replace(f"{short_name}总给人", f"{short_name}让人觉得")
    text = text.replace(f"{short_name}常给人", f"{short_name}让人觉得")
    text = text.replace(f"{short_name}给人的感觉往往是", f"{short_name}给人的感觉是")
    if not text.endswith("。"):
        text += "。"
    return text


def clean_followup_sentence(text: str, short_name: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if not cleaned:
        return ""
    cleaned = cleaned.replace("她/他", short_name)
    cleaned = re.sub(r"^(她|他)", short_name, cleaned)
    cleaned = cleaned.replace("《It'sMyGO!!!!!》", "《It's MyGO!!!!!》")
    cleaned = cleaned.replace("AveMujica", "Ave Mujica")
    cleaned = cleaned.replace("这个设定非常重要，因为它直接说明", "")
    cleaned = cleaned.replace("这个设定说明", "")
    cleaned = cleaned.replace("这个设定决定了", "")
    cleaned = cleaned.replace("的设定看起来像", "看起来像")
    cleaned = cleaned.replace("的设定看起来很", "看起来很")
    cleaned = cleaned.replace("在设定上天然同时属于", "天然同时属于")
    cleaned = cleaned.replace("在整体叙事里的作用", "在整体故事里的位置")
    cleaned = cleaned.replace("角色功能", "位置")
    cleaned = re.sub(r"^\s*这让她", f"{short_name}", cleaned)
    if not cleaned.endswith("。"):
        cleaned += "。"
    return cleaned


def contains_meta_tokens(text: str) -> bool:
    return any(token in text for token in META_TOKENS)


def looks_label_like(text: str) -> bool:
    return len(text) <= 40 and any(token in text for token in ROLE_HINT_TOKENS)


def choose_overview(paragraph: str, short_name: str, type_code: str, key: str) -> str:
    sentences = split_sentences(paragraph)
    primary = soften_overview(
        clean_overview_sentence(sentences[0] if sentences else ""),
        short_name,
        type_code,
    )
    secondary = clean_followup_sentence(sentences[1], short_name) if len(sentences) > 1 else ""

    options: list[str] = []
    if primary and not contains_meta_tokens(primary):
        options.append(primary)
    if secondary and not contains_meta_tokens(secondary):
        options.append(secondary)
    if primary and secondary and not contains_meta_tokens(primary + secondary):
        options.append(primary + secondary)

    ordered: list[str] = []
    if looks_label_like(primary) and secondary:
        ordered.extend([secondary, primary + secondary, primary])
    else:
        ordered.extend([primary + secondary if primary and secondary else "", primary, secondary])

    for candidate in ordered:
        if candidate and candidate not in options and not contains_meta_tokens(candidate):
            options.append(candidate)

    if not options:
        fallback = TYPE_FALLBACKS.get(type_code, "有很鲜明的个人气质")
        return f"{short_name}{fallback}。"

    return options[stable_index(key + ":overview", len(options))]


def choose_detail(portrait_text: str, short_name: str, key: str) -> str:
    candidates: list[str] = []

    overall_sentences = split_sentences(first_paragraph(extract_section(portrait_text, "总体画像")))
    if len(overall_sentences) > 1:
        for sentence in overall_sentences[1:3]:
            cleaned = clean_followup_sentence(sentence, short_name)
            if cleaned and not contains_meta_tokens(cleaned):
                candidates.append(cleaned)

    setting_section = extract_section(portrait_text, "外部设定基础")
    setting_para = first_paragraph(setting_section)
    for sentence in split_sentences(setting_para)[1:3]:
        cleaned = clean_followup_sentence(sentence, short_name)
        if cleaned and not contains_meta_tokens(cleaned):
            candidates.append(cleaned)

    for bullet in bullet_lines(setting_section)[:2]:
        cleaned = clean_followup_sentence(bullet, short_name)
        if cleaned and not contains_meta_tokens(cleaned):
            candidates.append(cleaned)

    plot_section = extract_section(portrait_text, "外部剧情基础")
    for bullet in bullet_lines(plot_section)[:2]:
        cleaned = clean_followup_sentence(bullet, short_name)
        if cleaned and not contains_meta_tokens(cleaned):
            candidates.append(cleaned)

    unique: list[str] = []
    for candidate in candidates:
        if candidate not in unique and len(candidate) >= 18:
            unique.append(candidate)

    if not unique:
        return ""
    return unique[stable_index(key + ":detail", len(unique))]


def style_sentence(type_code: str, key: str) -> str:
    variants = TYPE_TRAITS.get(type_code, [])
    if not variants:
        return ""
    trait = variants[stable_index(key + ":style", len(variants))]
    template = STYLE_TEMPLATES[stable_index(key + ":style_tpl", len(STYLE_TEMPLATES))]
    return template.format(trait=trait)


def weakness_sentence(type_code: str, key: str) -> str:
    variants = TYPE_SOFT_TURNS.get(type_code, [])
    if not variants:
        return ""
    return variants[stable_index(key + ":weak", len(variants))]


def relational_sentence(type_code: str, key: str) -> str:
    variants = TYPE_RELATIONAL.get(type_code, [])
    if not variants:
        return ""
    return variants[stable_index(key + ":rel", len(variants))]


def context_sentence(story_count: int, card_count: int, key: str) -> str:
    if story_count >= 120 and card_count >= 15:
        variants = CONTEXT_VARIANTS_STRONG
    elif story_count >= 60 or card_count >= 10:
        variants = CONTEXT_VARIANTS_MID
    else:
        return ""
    return variants[stable_index(key + ":context", len(variants))]


def join_parts(parts: list[str]) -> str:
    return "".join(part for part in parts if part)


def trim_description(text: str, limit: int = 250) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 2].rstrip("，、；") + "。"


def compose_description(base: str, detail: str, style: str, relational: str, context: str, weakness: str, key: str) -> str:
    patterns = [
        [base, detail, style, relational, weakness],
        [base, detail, relational, context, weakness],
        [base, detail, style, context, weakness],
        [base, style, relational, weakness],
        [base, detail, relational, weakness],
        [base, style, context, weakness],
        [base, relational, weakness],
        [base, weakness],
        [base, detail, relational],
        [base, style, relational],
        [base],
    ]
    rotated = patterns[stable_index(key + ":compose", 4):] + patterns[:stable_index(key + ":compose", 4)]
    candidates: list[str] = []
    for pattern in rotated:
        candidate = join_parts(pattern)
        if candidate and candidate not in candidates:
            candidates.append(candidate)

    in_range = [candidate for candidate in candidates if 100 <= len(candidate) <= 250]
    if in_range:
        return max(in_range, key=len)

    under_limit = [candidate for candidate in candidates if len(candidate) <= 250]
    if under_limit:
        return max(under_limit, key=len)

    return trim_description(candidates[0], 250)


def build_description(folder: Path) -> str:
    if folder.name in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[folder.name]

    portrait_text = (folder / "portrait.md").read_text(encoding="utf-8")
    mbti = json.loads((folder / "mbti_answers.json").read_text(encoding="utf-8"))

    short_name = portrait_text.splitlines()[0].replace("#", "").replace("人物画像", "").strip()
    type_code = mbti.get("type", "")

    overall = extract_section(portrait_text, "总体画像")
    story_count = int(read_meta_line(portrait_text, "- 主线/乐团剧情切片数") or 0)
    card_count = int(read_meta_line(portrait_text, "- 卡牌剧情数") or 0)
    overview = choose_overview(first_paragraph(overall), short_name, type_code, folder.name)
    detail = choose_detail(portrait_text, short_name, folder.name)
    style = style_sentence(type_code, folder.name)
    relational = relational_sentence(type_code, folder.name)
    weakness = weakness_sentence(type_code, folder.name)
    context = context_sentence(story_count, card_count, folder.name)
    return compose_description(overview, detail, style, relational, context, weakness, folder.name)


def main() -> None:
    review_blocks = ["# 性格描述总览", ""]
    for folder in sorted(DOSSIER_ROOT.iterdir()):
        if not folder.is_dir():
            continue
        portrait = folder / "portrait.md"
        answers = folder / "mbti_answers.json"
        if not portrait.exists() or not answers.exists():
            continue
        short_name = portrait.read_text(encoding="utf-8").splitlines()[0].replace("#", "").replace("人物画像", "").strip()
        description = build_description(folder)
        output = "# %s 性格描述\n\n%s\n" % (short_name, description)
        (folder / "personality_description.md").write_text(output, encoding="utf-8")
        review_blocks.extend(["## %s" % short_name, "", description, ""])

    REVIEW_PATH.write_text("\n".join(review_blocks), encoding="utf-8")


if __name__ == "__main__":
    main()
