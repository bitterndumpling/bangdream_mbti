from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_PATH = ROOT / "ojts_question_bank_v2_1.json"


ZH_TEXT = {
    1: "我不喜欢让自己成为众人关注的焦点。",
    2: "我讨厌别人期待我来活跃气氛或逗大家笑的场合。",
    3: "我会把自己的意见收着，不轻易说出来。",
    4: "我希望拥有非常广泛的社交圈。",
    5: "在聚会里我通常是带动气氛的人。",
    6: "我动静很大。",
    7: "我会回避哲学性的讨论。",
    8: "我不喜欢分析文学作品。",
    9: "我倾向于坚持传统、常规的做法。",
    10: "我喜欢阅读有挑战性的内容。",
    11: "我会在事物中寻找隐藏的含义。",
    12: "我几乎对一切都感到好奇。",
    13: "我想体验炽烈的热情与浪漫。",
    14: "他人的不幸会让我深受触动。",
    15: "在做重要决定时，我会倾听自己的感受。",
    16: "我把逻辑看得高于一切。",
    17: "我不理解那些很容易情绪化的人。",
    18: "与其被喜爱，我宁愿被敬畏。",
    19: "我喜欢秩序。",
    20: "我做事会按照计划来。",
    21: "我总是事先做好准备。",
    22: "我经常到最后一刻才做计划。",
    23: "我有时会在没有明显理由的情况下做事。",
    24: "本该几小时做完的事，我常常因为不断分心而拖上好几天。",
    25: "我一直在努力提升自己。",
    26: "我总觉得自己必须去做某件重要的事。",
    27: "我对这个世界抱有一些与众不同的看法。",
    28: "我不喜欢一成不变的日常和重复。",
    29: "我会尽力遵守规则。",
    30: "我尊重权威。",
    31: "我喜欢轻松一点，不把自己逼得太紧。",
    32: "我会选择更轻松、更省力的做法。",
    33: "我会把自己的秘密告诉别人。",
    34: "我会对别人做出很明显、很热情的友好表示。",
    35: "我享受挑战与竞争。",
    36: "我的自尊心很强，也很看得起自己。",
    37: "我很容易觉得难为情或尴尬。",
    38: "一旦事情接连发生，我很容易被压得喘不过气。",
    39: "我不太擅长表达自己的感受。",
    40: "我不会轻易相信别人。",
}


JA_TEXT = {
    1: "自分が注目の的になるのは好きではない。",
    2: "人から面白いことを求められる状況が嫌いだ。",
    3: "自分の意見をあえて控えることが多い。",
    4: "とても広い交友関係を持ちたい。",
    5: "パーティーでは自分が場を盛り上げる中心になりやすい。",
    6: "私はかなり騒がしいほうだ。",
    7: "哲学的な議論は避ける。",
    8: "文学作品を分析するのは好きではない。",
    9: "従来のやり方や慣習に愛着がある。",
    10: "歯ごたえのある難しい文章を読むのが好きだ。",
    11: "物事の中に隠れた意味を探そうとする。",
    12: "ほとんどあらゆることに好奇心を持つ。",
    13: "情熱的でロマンチックな体験をしてみたい。",
    14: "他人の不幸に深く心を動かされる。",
    15: "重要な決断をするとき、自分の気持ちを重視する。",
    16: "何よりも論理を重んじる。",
    17: "感情的になる人のことが理解しにくい。",
    18: "愛されるより、恐れられるほうがましだ。",
    19: "秩序が好きだ。",
    20: "計画に沿って物事を進める。",
    21: "いつも準備を整えている。",
    22: "ぎりぎりになってから予定を立てることが多い。",
    23: "はっきりした理由もなく行動することがある。",
    24: "数時間で終わるはずのことでも、気が散って何日もかかることがある。",
    25: "自分をより良くするために努力している。",
    26: "いつも何か重要なことをしていなければならない気がする。",
    27: "世界について少し変わった考えを持っている。",
    28: "ルーティンや単調な繰り返しが嫌いだ。",
    29: "できるだけルールに従おうとする。",
    30: "権威を尊重する。",
    31: "気楽にやるのが好きだ。",
    32: "楽なやり方を選ぶ。",
    33: "自分の秘密を他人に話すことがある。",
    34: "人に対して大きく分かりやすい友情表現をする。",
    35: "挑戦や競争を楽しむ。",
    36: "自尊心がかなり高い。",
    37: "恥ずかしくなりやすい。",
    38: "出来事が重なると圧倒されやすい。",
    39: "自分の気持ちを表現するのが苦手だ。",
    40: "他人を簡単には信用しない。",
}


HINTS = {
    1: {"zh": ["低调", "不想引人注目", "不抢风头"], "en": ["low-key", "avoids the spotlight", "does not seek attention"], "ja": ["目立ちたくない", "注目を避ける", "前に出たがらない"]},
    2: {"zh": ["不擅活跃气氛", "不想逗别人笑", "怕被要求搞笑"], "en": ["dislikes being expected to be funny", "avoids entertainer role", "hates forced humor"], "ja": ["笑いを求められるのが苦手", "場を盛り上げ役にされたくない", "無理に面白さを求められるのが嫌"]},
    3: {"zh": ["保留意见", "不轻易表态", "不急着表达"], "en": ["holds back opinions", "reserved in speaking up", "not quick to voice views"], "ja": ["意見を控える", "簡単に表明しない", "すぐには口にしない"]},
    4: {"zh": ["社交圈大", "认识很多人", "广结交友"], "en": ["wants a large social circle", "likes knowing many people", "broadly social"], "ja": ["広い交友関係を望む", "多くの人とつながりたい", "顔が広い"]},
    5: {"zh": ["气氛中心", "带动现场", "活跃气氛"], "en": ["life of the party", "energizes the room", "center of the atmosphere"], "ja": ["場の中心になりやすい", "その場を盛り上げる", "ムードメーカー"]},
    6: {"zh": ["声音大", "吵闹", "动静大"], "en": ["loud", "noisy", "high-energy presence"], "ja": ["声が大きい", "にぎやか", "存在感が大きい"]},
    7: {"zh": ["不爱抽象讨论", "回避哲学", "不爱空谈"], "en": ["avoids abstract discussion", "not into philosophy", "dislikes lofty talk"], "ja": ["抽象的な議論を避ける", "哲学話が苦手", "観念的な話が好きではない"]},
    8: {"zh": ["不爱文本分析", "不爱文学解读", "不爱深究象征"], "en": ["dislikes literary analysis", "not into text interpretation", "avoids symbolism reading"], "ja": ["文学分析が苦手", "作品解釈が好きではない", "象徴を深読みしない"]},
    9: {"zh": ["传统方式", "常规路线", "老办法"], "en": ["conventional methods", "traditional approach", "sticks to standard ways"], "ja": ["従来のやり方", "定番の手順", "昔ながらの方法"]},
    10: {"zh": ["喜欢硬核内容", "爱思考复杂问题", "爱啃难材料"], "en": ["likes challenging material", "enjoys difficult reading", "wants intellectual challenge"], "ja": ["難しい内容が好き", "歯ごたえのある文章を好む", "知的な挑戦を楽しむ"]},
    11: {"zh": ["隐藏含义", "深层意思", "言外之意"], "en": ["looks for hidden meaning", "reads beneath the surface", "searches for subtext"], "ja": ["隠れた意味を探す", "表面の下を読む", "行間を読む"]},
    12: {"zh": ["什么都好奇", "求知欲强", "探究"], "en": ["curious about everything", "strong curiosity", "exploratory"], "ja": ["何にでも好奇心を持つ", "知りたがり", "探究心が強い"]},
    13: {"zh": ["浪漫", "激情", "感情体验"], "en": ["romantic", "passionate", "seeks emotional intensity"], "ja": ["ロマンチック", "情熱的", "強い感情体験を求める"]},
    14: {"zh": ["很共情", "心疼别人", "他人受苦会难过"], "en": ["deeply empathetic", "moved by others suffering", "feels others pain"], "ja": ["強く共感する", "他人の不幸に心を痛める", "人の苦しみに動かされる"]},
    15: {"zh": ["感受优先", "跟随心意", "看内心"], "en": ["follows feelings", "feeling-led decisions", "listens to the heart"], "ja": ["気持ちを優先する", "感情に従って決める", "心の声を聞く"]},
    16: {"zh": ["逻辑最重要", "理性优先", "重分析"], "en": ["logic above all", "reason first", "analysis-oriented"], "ja": ["論理最優先", "理性を重視する", "分析寄り"]},
    17: {"zh": ["不理解情绪化", "看不懂感情用事", "讨厌失控"], "en": ["does not understand emotional reactions", "confused by emotionality", "dislikes emotional loss of control"], "ja": ["感情的な反応が理解しにくい", "感情任せがわからない", "感情の暴走が苦手"]},
    18: {"zh": ["不求讨喜", "威慑", "尊重胜过喜欢"], "en": ["would rather be feared", "values respect over affection", "does not need to be liked"], "ja": ["好かれるより恐れられたい", "好意より敬意を求める", "好かれなくても構わない"]},
    19: {"zh": ["喜欢秩序", "有条理", "规整"], "en": ["likes order", "prefers structure", "orderly"], "ja": ["秩序が好き", "整っていたい", "きちんとしている"]},
    20: {"zh": ["按计划做事", "照步骤来", "计划性"], "en": ["acts according to plan", "step-by-step", "planned approach"], "ja": ["計画通りに進める", "手順を守る", "計画性がある"]},
    21: {"zh": ["提前准备", "有准备", "未雨绸缪"], "en": ["always prepared", "plans ahead", "ready in advance"], "ja": ["事前に備える", "前もって準備する", "抜かりなく整える"]},
    22: {"zh": ["临时起意", "最后才计划", "即兴安排"], "en": ["last-minute planning", "plans late", "spontaneous scheduling"], "ja": ["直前に計画する", "最後に決める", "予定を後回しにする"]},
    23: {"zh": ["随性而为", "凭一时兴致", "说做就做"], "en": ["acts on impulse", "does things without clear reason", "spur-of-the-moment"], "ja": ["気の向くままに動く", "特に理由なく行動する", "思いつきで動く"]},
    24: {"zh": ["容易分心", "拖拖拉拉", "被别的事吸走"], "en": ["easily distracted", "procrastinates", "takes too long due to drifting attention"], "ja": ["気が散りやすい", "先延ばししやすい", "注意がそれて時間がかかる"]},
    25: {"zh": ["自我提升", "持续改进", "精进"], "en": ["self-improvement", "keeps improving", "works on growth"], "ja": ["自己改善", "成長を続ける", "自分を磨く"]},
    26: {"zh": ["想做重要的事", "要有意义", "要做大事"], "en": ["needs to do something important", "seeks significance", "driven toward meaningful action"], "ja": ["重要なことをしたい", "意義を求める", "大事な役割を果たしたい"]},
    27: {"zh": ["世界观特别", "想法奇特", "特异观点"], "en": ["unusual worldview", "atypical beliefs", "eccentric ideas"], "ja": ["独特な世界観", "少し変わった考え", "普通と違う信念"]},
    28: {"zh": ["讨厌例行公事", "不喜欢重复", "要变化"], "en": ["dislikes routine", "hates repetition", "wants variety"], "ja": ["ルーティンが嫌い", "繰り返しが苦手", "変化を求める"]},
    29: {"zh": ["遵守规则", "守规矩", "按规范来"], "en": ["follows rules", "rule-abiding", "stays within guidelines"], "ja": ["ルールを守る", "規範に従う", "決まりを重んじる"]},
    30: {"zh": ["尊重权威", "服从正规体系", "看重正式秩序"], "en": ["respects authority", "accepts hierarchy", "values formal order"], "ja": ["権威を尊重する", "上下関係を受け入れる", "公式な秩序を重んじる"]},
    31: {"zh": ["喜欢轻松", "不想太累", "想悠着来"], "en": ["likes to take it easy", "prefers ease", "does not want to overstrain"], "ja": ["気楽にやりたい", "無理したくない", "ゆったり進めたい"]},
    32: {"zh": ["走轻松路线", "图省力", "选容易的"], "en": ["chooses the easy way", "prefers less effort", "takes the easier route"], "ja": ["楽な道を選ぶ", "省エネ志向", "簡単なやり方を選ぶ"]},
    33: {"zh": ["会说秘密", "对人敞开", "分享私事"], "en": ["shares secrets", "opens up to others", "reveals private matters"], "ja": ["秘密を話す", "人に心を開く", "私事を共有する"]},
    34: {"zh": ["大方示好", "热情表达友谊", "会做大动作"], "en": ["makes big gestures of friendship", "openly shows affection", "demonstrative with people"], "ja": ["友情を大きく示す", "好意を分かりやすく表す", "身振り大きく親しさを見せる"]},
    35: {"zh": ["喜欢挑战", "爱竞争", "好胜"], "en": ["enjoys challenge", "competitive", "likes testing limits"], "ja": ["挑戦が好き", "競争を楽しむ", "負けず嫌い"]},
    36: {"zh": ["自尊高", "自信强", "自我评价高"], "en": ["high self-esteem", "very self-confident", "rates self highly"], "ja": ["自尊心が高い", "自信が強い", "自己評価が高い"]},
    37: {"zh": ["容易害羞", "容易尴尬", "脸皮薄"], "en": ["embarrassed easily", "easily self-conscious", "thin-skinned socially"], "ja": ["恥ずかしがりや", "すぐ照れる", "気まずさを感じやすい"]},
    38: {"zh": ["容易被压垮", "容易不堪重负", "事件多就吃不消"], "en": ["gets overwhelmed easily", "buckles under events", "overloaded by too much happening"], "ja": ["圧倒されやすい", "出来事が重なるときつい", "抱え込みやすい"]},
    39: {"zh": ["不擅表达感受", "感情表达困难", "说不出口"], "en": ["struggles to express feelings", "emotionally inexpressive", "finds feelings hard to voice"], "ja": ["感情表現が苦手", "気持ちを言葉にしにくい", "思いを口にしづらい"]},
    40: {"zh": ["不轻信", "戒备", "难以信任他人"], "en": ["slow to trust", "guarded", "does not trust easily"], "ja": ["簡単には信じない", "警戒心が強い", "人を信用しにくい"]},
}


BIPOLAR = {
    41: {
        "zh_left": "怀疑谨慎",
        "zh_right": "愿意相信",
        "zh_left_hints": ["怀疑", "存疑", "审慎"],
        "zh_right_hints": ["愿意相信", "信任", "相信人"],
        "ja_left": "懐疑的",
        "ja_right": "信じたい",
        "ja_left_hints": ["懐疑的", "疑い深い", "慎重"],
        "ja_right_hints": ["信じたい", "信頼しやすい", "信じる側に寄る"],
        "en_left_hints": ["skeptical", "doubting", "cautious"],
        "en_right_hints": ["wants to believe", "trusting", "ready to believe"],
    },
    42: {
        "zh_left": "混乱随性",
        "zh_right": "有条理",
        "zh_left_hints": ["混乱", "随性", "散漫"],
        "zh_right_hints": ["有条理", "组织", "整理"],
        "ja_left": "混沌としている",
        "ja_right": "整っている",
        "ja_left_hints": ["混乱気味", "行き当たりばったり", "散らかりやすい"],
        "ja_right_hints": ["整理されている", "筋道立っている", "きちんとしている"],
        "en_left_hints": ["chaotic", "messy", "unstructured"],
        "en_right_hints": ["organized", "orderly", "structured"],
    },
    43: {
        "zh_left": "想看整体全貌",
        "zh_right": "想看具体细节",
        "zh_left_hints": ["大局", "整体", "方向"],
        "zh_right_hints": ["细节", "具体", "步骤"],
        "ja_left": "全体像をつかみたい",
        "ja_right": "細部を知りたい",
        "ja_left_hints": ["全体像", "大きな流れ", "方向性"],
        "ja_right_hints": ["細部", "具体性", "手順"],
        "en_left_hints": ["big picture", "overall view", "direction-focused"],
        "en_right_hints": ["details", "specifics", "step-focused"],
    },
    44: {
        "zh_left": "精力充沛",
        "zh_right": "平和温和",
        "zh_left_hints": ["精力充沛", "元气", "活力"],
        "zh_right_hints": ["平静", "温和", "安静"],
        "ja_left": "エネルギッシュ",
        "ja_right": "穏やか",
        "ja_left_hints": ["活力がある", "元気が強い", "勢いがある"],
        "ja_right_hints": ["穏やか", "落ち着いている", "静かめ"],
        "en_left_hints": ["energetic", "high-energy", "lively"],
        "en_right_hints": ["mellow", "calm", "gentle"],
    },
    45: {
        "zh_left": "跟随内心",
        "zh_right": "跟随理性",
        "zh_left_hints": ["跟随内心", "凭心意", "感受优先"],
        "zh_right_hints": ["跟随理性", "逻辑优先", "讲道理"],
        "ja_left": "心に従う",
        "ja_right": "頭で判断する",
        "ja_left_hints": ["心に従う", "感情を優先する", "気持ち重視"],
        "ja_right_hints": ["頭で考える", "論理を優先する", "理屈で判断する"],
        "en_left_hints": ["follows the heart", "feeling-led", "emotion first"],
        "en_right_hints": ["follows the head", "logic-led", "reason first"],
    },
    46: {
        "zh_left": "事先准备",
        "zh_right": "临场发挥",
        "zh_left_hints": ["提前准备", "预先", "先安排"],
        "zh_right_hints": ["即兴", "临场", "随机应变"],
        "ja_left": "準備する",
        "ja_right": "即興でやる",
        "ja_left_hints": ["事前に備える", "前もって整える", "先に段取りする"],
        "ja_right_hints": ["即興で動く", "その場で合わせる", "アドリブ対応"],
        "en_left_hints": ["prepares", "plans ahead", "sets things up first"],
        "en_right_hints": ["improvises", "ad-libs", "makes it up on the spot"],
    },
    47: {
        "zh_left": "专注当下",
        "zh_right": "专注未来",
        "zh_left_hints": ["关注当下", "眼前", "现在"],
        "zh_right_hints": ["关注未来", "以后", "长远"],
        "ja_left": "現在に焦点を当てる",
        "ja_right": "未来に焦点を当てる",
        "ja_left_hints": ["今に集中する", "目の前を見る", "現在志向"],
        "ja_right_hints": ["未来を見る", "先を考える", "長期志向"],
        "en_left_hints": ["focused on the present", "present-oriented", "attends to now"],
        "en_right_hints": ["focused on the future", "future-oriented", "looks ahead"],
    },
    48: {
        "zh_left": "独自工作时状态最好",
        "zh_right": "在团队中工作时状态最好",
        "zh_left_hints": ["独自工作", "一个人更好", "单独发挥"],
        "zh_right_hints": ["团队中表现更好", "一起做更强", "协作发挥"],
        "ja_left": "一人で作業すると最もうまくいく",
        "ja_right": "集団で作業すると最もうまくいく",
        "ja_left_hints": ["一人のほうが力を出せる", "単独作業向き", "自分だけで集中できる"],
        "ja_right_hints": ["チームで力を出せる", "協力すると強い", "集団作業向き"],
        "en_left_hints": ["works best alone", "better solo", "strongest when working independently"],
        "en_right_hints": ["works best in groups", "better in teams", "strongest when collaborating"],
    },
}


def build_bank(lang: str, source_data: dict) -> dict:
    payload = {
        "name": source_data["name"],
        "version": source_data.get("version", "v2.1"),
        "source": source_data["source"],
        "license": source_data["license"],
        "question_count": source_data["question_count"],
        "language": lang,
        "translation_of": "ojts_question_bank_v2_1.json",
        "questions": [],
    }

    for question in source_data["questions"]:
        item = {k: v for k, v in question.items() if k not in ["text", "left_text", "right_text", "hints", "left_hints", "right_hints"]}
        qid = question["id"]
        if question["format"] == "agreement":
            if lang == "en":
                item["text"] = html.unescape(question["text"]).replace("‘", "'").replace("’", "'")
            elif lang == "zh":
                item["text"] = ZH_TEXT[qid]
            else:
                item["text"] = JA_TEXT[qid]
            item["hints"] = HINTS[qid][lang]
        else:
            meta = BIPOLAR[qid]
            if lang == "en":
                item["left_text"] = html.unescape(question["left_text"]).replace("‘", "'").replace("’", "'")
                item["right_text"] = html.unescape(question["right_text"]).replace("‘", "'").replace("’", "'")
                item["left_hints"] = meta["en_left_hints"]
                item["right_hints"] = meta["en_right_hints"]
            elif lang == "zh":
                item["left_text"] = meta["zh_left"]
                item["right_text"] = meta["zh_right"]
                item["left_hints"] = meta["zh_left_hints"]
                item["right_hints"] = meta["zh_right_hints"]
            else:
                item["left_text"] = meta["ja_left"]
                item["right_text"] = meta["ja_right"]
                item["left_hints"] = meta["ja_left_hints"]
                item["right_hints"] = meta["ja_right_hints"]
        payload["questions"].append(item)
    return payload


def main() -> None:
    source_data = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    outputs = {
        "en": ROOT / "ojts_question_bank_v2_1_en.json",
        "zh": ROOT / "ojts_question_bank_v2_1_zh.json",
        "ja": ROOT / "ojts_question_bank_v2_1_ja.json",
    }

    for lang, path in outputs.items():
        payload = build_bank(lang, source_data)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    english_text = outputs["en"].read_text(encoding="utf-8")
    if re.search(r"[\u4e00-\u9fff\u3040-\u30ff]", english_text):
        raise RuntimeError("English bank still contains CJK characters.")


if __name__ == "__main__":
    main()
