from __future__ import annotations

import re
import time
from pathlib import Path

from deep_translator import GoogleTranslator
from googletrans import Translator


DATASET_ROOT = Path(__file__).resolve().parent
DOSSIER_ROOT = DATASET_ROOT / "character_dossiers"
REVIEW_PATH = DATASET_ROOT / "personality_descriptions_review.md"


NAME_MAP = {
    "char_ako_ako": {"cn": "宇田川亚子", "en": "Ako Udagawa", "ja": "宇田川 あこ", "short_en": "Ako", "short_ja": "あこ"},
    "char_anon_anon": {"cn": "千早爱音", "en": "Anon Chihaya", "ja": "千早 愛音", "short_en": "Anon", "short_ja": "愛音"},
    "char_arisa_arisa": {"cn": "市谷有咲", "en": "Arisa Ichigaya", "ja": "市ヶ谷 有咲", "short_en": "Arisa", "short_ja": "有咲"},
    "char_asuka_asuka": {"cn": "户山明日香", "en": "Asuka Toyama", "ja": "戸山 明日香", "short_en": "Asuka", "short_ja": "明日香"},
    "char_aya_aya": {"cn": "丸山彩", "en": "Aya Maruyama", "ja": "丸山 彩", "short_en": "Aya", "short_ja": "彩"},
    "char_chisato_chisato": {"cn": "白鹭千圣", "en": "Chisato Shirasagi", "ja": "白鷺 千聖", "short_en": "Chisato", "short_ja": "千聖"},
    "char_chiyu_chiyu": {"cn": "珠手知由", "en": "Chiyu Tamade", "ja": "珠手 ちゆ", "short_en": "Chiyu", "short_ja": "ちゆ"},
    "char_eve_eve": {"cn": "若宫伊芙", "en": "Eve Wakamiya", "ja": "若宮 イヴ", "short_en": "Eve", "short_ja": "イヴ"},
    "char_hagumi_hagumi": {"cn": "北泽育美", "en": "Hagumi Kitazawa", "ja": "北沢 はぐみ", "short_en": "Hagumi", "short_ja": "はぐみ"},
    "char_himari_himari": {"cn": "上原绯玛丽", "en": "Himari Uehara", "ja": "上原 ひまり", "short_en": "Himari", "short_ja": "ひまり"},
    "char_hina_hina": {"cn": "冰川日菜", "en": "Hina Hikawa", "ja": "氷川 日菜", "short_en": "Hina", "short_ja": "日菜"},
    "char_kanon_kanon": {"cn": "松原花音", "en": "Kanon Matsubara", "ja": "松原 花音", "short_en": "Kanon", "short_ja": "花音"},
    "char_kaoru_kaoru": {"cn": "濑田薰", "en": "Kaoru Seta", "ja": "瀬田 薫", "short_en": "Kaoru", "short_ja": "薫"},
    "char_kasumi_kasumi": {"cn": "户山香澄", "en": "Kasumi Toyama", "ja": "戸山 香澄", "short_en": "Kasumi", "short_ja": "香澄"},
    "char_kokoro_kokoro": {"cn": "弦卷心", "en": "Kokoro Tsurumaki", "ja": "弦巻 こころ", "short_en": "Kokoro", "short_ja": "こころ"},
    "char_lisa_lisa": {"cn": "今井莉莎", "en": "Lisa Imai", "ja": "今井 リサ", "short_en": "Lisa", "short_ja": "リサ"},
    "char_mana_mana": {"cn": "纯田真奈", "en": "Mana Sumita", "ja": "純田 まな", "short_en": "Mana", "short_ja": "まな"},
    "char_marina_marina": {"cn": "月岛麻里奈", "en": "Marina Tsukishima", "ja": "月島 まりな", "short_en": "Marina", "short_ja": "まりな"},
    "char_mashiro_mashiro": {"cn": "仓田真白", "en": "Mashiro Kurata", "ja": "倉田 ましろ", "short_en": "Mashiro", "short_ja": "ましろ"},
    "char_masuki_masuki": {"cn": "佐藤益木", "en": "Masuki Sato", "ja": "佐藤 ますき", "short_en": "Masuki", "short_ja": "ますき"},
    "char_maya_maya": {"cn": "大和麻弥", "en": "Maya Yamato", "ja": "大和 麻弥", "short_en": "Maya", "short_ja": "麻弥"},
    "char_misaki_misaki": {"cn": "奥泽美咲", "en": "Misaki Okusawa", "ja": "奥沢 美咲", "short_en": "Misaki", "short_ja": "美咲"},
    "char_moca_moca": {"cn": "青叶摩卡", "en": "Moca Aoba", "ja": "青葉 モカ", "short_en": "Moca", "short_ja": "モカ"},
    "char_mutsumi_mutsumi": {"cn": "若叶睦", "en": "Mutsumi Wakaba", "ja": "若葉 睦", "short_en": "Mutsumi", "short_ja": "睦"},
    "char_nanami_nanami": {"cn": "广町七深", "en": "Nanami Hiromachi", "ja": "広町 七深", "short_en": "Nanami", "short_ja": "七深"},
    "char_nyamu_nyamu": {"cn": "祐天寺若麦", "en": "Nyamu Yutenji", "ja": "祐天寺 にゃむ", "short_en": "Nyamu", "short_ja": "にゃむ"},
    "char_owner_livehouse": {"cn": "都筑诗船", "en": "Shifune Tsuzuki", "ja": "都築 詩船", "short_en": "Shifune", "short_ja": "詩船"},
    "char_ran_ran": {"cn": "美竹兰", "en": "Ran Mitake", "ja": "美竹 蘭", "short_en": "Ran", "short_ja": "蘭"},
    "char_rana_rana": {"cn": "要乐奈", "en": "Rana Kaname", "ja": "要 楽奈", "short_en": "Rana", "short_ja": "楽奈"},
    "char_rei_rei": {"cn": "和奏瑞依", "en": "Rei Wakana", "ja": "和奏 レイ", "short_en": "Rei", "short_ja": "レイ"},
    "char_reona_reona": {"cn": "鳰原令王那", "en": "Reona Nyubara", "ja": "鳰原 れおな", "short_en": "Reona", "short_ja": "れおな"},
    "char_rimi_rimi": {"cn": "牛込里美", "en": "Rimi Ushigome", "ja": "牛込 りみ", "short_en": "Rimi", "short_ja": "りみ"},
    "char_rinko_rinko": {"cn": "白金燐子", "en": "Rinko Shirokane", "ja": "白金 燐子", "short_en": "Rinko", "short_ja": "燐子"},
    "char_rokka_rokka": {"cn": "朝日六花", "en": "Rokka Asahi", "ja": "朝日 六花", "short_en": "Rokka", "short_ja": "六花"},
    "char_rui_rui": {"cn": "八潮瑠唯", "en": "Rui Yashio", "ja": "八潮 瑠唯", "short_en": "Rui", "short_ja": "瑠唯"},
    "char_saaya_saaya": {"cn": "山吹沙绫", "en": "Saaya Yamabuki", "ja": "山吹 沙綾", "short_en": "Saaya", "short_ja": "沙綾"},
    "char_sakiko_sakiko": {"cn": "丰川祥子", "en": "Sakiko Togawa", "ja": "豊川 祥子", "short_en": "Sakiko", "short_ja": "祥子"},
    "char_sayo_sayo": {"cn": "冰川纱夜", "en": "Sayo Hikawa", "ja": "氷川 紗夜", "short_en": "Sayo", "short_ja": "紗夜"},
    "char_soyo_soyo": {"cn": "长崎爽世", "en": "Soyo Nagasaki", "ja": "長崎 そよ", "short_en": "Soyo", "short_ja": "そよ"},
    "char_tae_tae": {"cn": "花园多惠", "en": "Tae Hanazono", "ja": "花園 たえ", "short_en": "Tae", "short_ja": "たえ"},
    "char_taki_taki": {"cn": "椎名立希", "en": "Taki Shiina", "ja": "椎名 立希", "short_en": "Taki", "short_ja": "立希"},
    "char_tomoe_tomoe": {"cn": "宇田川巴", "en": "Tomoe Udagawa", "ja": "宇田川 巴", "short_en": "Tomoe", "short_ja": "巴"},
    "char_tomori_tomori": {"cn": "高松灯", "en": "Tomori Takamatsu", "ja": "高松 燈", "short_en": "Tomori", "short_ja": "燈"},
    "char_touko_touko": {"cn": "桐谷透子", "en": "Toko Kirigaya", "ja": "桐ヶ谷 透子", "short_en": "Toko", "short_ja": "透子"},
    "char_tsugumi_tsugumi": {"cn": "羽泽鸫", "en": "Tsugumi Hazawa", "ja": "羽沢 つぐみ", "short_en": "Tsugumi", "short_ja": "つぐみ"},
    "char_tsukushi_tsukushi": {"cn": "二叶筑紫", "en": "Tsukushi Futaba", "ja": "二葉 つくし", "short_en": "Tsukushi", "short_ja": "つくし"},
    "char_uika_uika": {"cn": "三角初华", "en": "Uika Misumi", "ja": "三角 初華", "short_en": "Uika", "short_ja": "初華"},
    "char_umiri_umiri": {"cn": "八幡海铃", "en": "Umiri Yahata", "ja": "八幡 海鈴", "short_en": "Umiri", "short_ja": "海鈴"},
    "char_yukina_yukina": {"cn": "凑友希那", "en": "Yukina Minato", "ja": "湊 友希那", "short_en": "Yukina", "short_ja": "友希那"},
}


PRONOUN_FIXES = {
    r"\bhe\b": "she",
    r"\bHe\b": "She",
    r"\bhim\b": "her",
    r"\bHim\b": "Her",
    r"\bhis\b": "her",
    r"\bHis\b": "Her",
    r"\bhimself\b": "herself",
    r"\bHimself\b": "Herself",
}

FULL_NAME_TOKEN = "ZXFULLNAMETOKEN"
SHORT_NAME_TOKEN = "ZXSHORTNAMETOKEN"


def split_description_body(text: str) -> str:
    multi_match = re.search(r"^## 中文\s*$([\s\S]*?)(?=^##\s+|\Z)", text, re.M)
    if multi_match:
        return multi_match.group(1).strip()

    lines = text.splitlines()
    if len(lines) >= 3:
        return "\n".join(lines[2:]).strip()
    return text.strip()


def load_review_descriptions() -> dict[str, str]:
    if not REVIEW_PATH.exists():
        return {}
    text = REVIEW_PATH.read_text(encoding="utf-8")
    matches = re.findall(r"^##\s+(.+?)\s*$([\s\S]*?)(?=^##\s+|\Z)", text, re.M)
    result: dict[str, str] = {}
    for title, body in matches:
        cleaned = body.strip()
        if cleaned:
            result[title.strip()] = cleaned
    return result


def load_short_names() -> dict[str, str]:
    result: dict[str, str] = {}
    for folder in DOSSIER_ROOT.iterdir():
        if not folder.is_dir() or folder.name not in NAME_MAP:
            continue
        path = folder / "personality_description.md"
        if not path.exists():
            continue
        title_line = path.read_text(encoding="utf-8").splitlines()[0]
        result[folder.name] = title_line.replace("#", "").replace("性格描述", "").strip()
    return result


def build_global_name_tokens(short_name_map: dict[str, str]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    seen: set[str] = set()
    for folder_name, names in NAME_MAP.items():
        candidates = [names["cn"]]
        short_cn = short_name_map.get(folder_name, "")
        if len(short_cn) >= 2:
            candidates.append(short_cn)
        for source in candidates:
            if not source or source in seen:
                continue
            token = f"ZXN{len(entries)}TOKEN"
            entries.append({"source": source, "token": token, "en": names["short_en"] if source == short_cn else names["en"], "ja": names["short_ja"] if source == short_cn else names["ja"]})
            seen.add(source)
    entries.sort(key=lambda item: len(item["source"]), reverse=True)
    return entries


def apply_global_name_tokens(text: str, token_entries: list[dict[str, str]]) -> str:
    result = text
    for item in token_entries:
        result = result.replace(item["source"], item["token"])
    return result


def replace_meta_line(lines: list[str], prefix: str, value: str, insert_after: str | None = None) -> list[str]:
    target = f"{prefix}{value}"
    for idx, line in enumerate(lines):
        if line.startswith(prefix):
            lines[idx] = target
            return lines
    if insert_after is not None:
        for idx, line in enumerate(lines):
            if line.startswith(insert_after):
                lines.insert(idx + 1, target)
                return lines
    lines.append(target)
    return lines


def postprocess_translation(
    text: str,
    names: dict[str, str],
    short_cn: str,
    lang: str,
    token_entries: list[dict[str, str]],
) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace("Pastel＊Palettes", "Pastel*Palettes")
    text = text.replace("AveMujica", "Ave Mujica")
    text = text.replace("MyGO! ! ! ! !", "MyGO!!!!!")
    text = text.replace("MyGO!!!!!", "MyGO!!!!!")
    if lang == "en":
        for item in token_entries:
            text = text.replace(item["token"], item["en"])
        text = text.replace(FULL_NAME_TOKEN, names["en"])
        text = text.replace(SHORT_NAME_TOKEN, names["short_en"])
        text = text.replace(names["cn"], names["en"])
        text = text.replace(short_cn, names["short_en"])
        parts = names["en"].split()
        if len(parts) == 2:
            text = text.replace(f"{parts[1]} {parts[0]}", names["en"])
        for pattern, replacement in PRONOUN_FIXES.items():
            text = re.sub(pattern, replacement, text)
        text = re.sub(r"([.!?;:])([A-Za-z\"'])", r"\1 \2", text)
        text = text.replace("  ", " ")
        if text:
            text = text[0].upper() + text[1:]
    else:
        for item in token_entries:
            text = text.replace(item["token"], item["ja"])
        text = text.replace(FULL_NAME_TOKEN, names["ja"])
        text = text.replace(SHORT_NAME_TOKEN, names["short_ja"])
        text = text.replace(names["cn"], names["ja"])
        text = text.replace(short_cn, names["short_ja"])
        text = re.sub(r"(?<!彼)彼(?!女)", "彼女", text)
        text = text.replace("彼女女", "彼女")
    return text.strip()


def translate_text(translator: Translator, text: str, dest: str) -> str:
    last_error: Exception | None = None
    for _ in range(4):
        try:
            return translator.translate(text, src="zh-cn", dest=dest).text
        except Exception as exc:  # pragma: no cover - network retry
            last_error = exc
            time.sleep(1.2)
    if last_error is not None:
        try:
            return GoogleTranslator(source="zh-CN", target=dest).translate(text)
        except Exception:
            sentences = [item for item in re.split(r"(?<=[。！？])", text) if item.strip()]
            translated_parts = []
            for sentence in sentences:
                piece = GoogleTranslator(source="zh-CN", target=dest).translate(sentence.strip())
                translated_parts.append(piece)
                time.sleep(0.15)
            return "".join(translated_parts)
    raise RuntimeError("translation failed")


def update_portrait(folder: Path, names: dict[str, str]) -> None:
    path = folder / "portrait.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    lines = replace_meta_line(lines, "- 角色名：", names["cn"])
    lines = replace_meta_line(lines, "- 英文名：", names["en"], insert_after="- 角色名：")
    lines = replace_meta_line(lines, "- 日文名：", names["ja"], insert_after="- 英文名：")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_description(
    folder: Path,
    names: dict[str, str],
    translator: Translator,
    review_map: dict[str, str],
    token_entries: list[dict[str, str]],
) -> None:
    path = folder / "personality_description.md"
    original = path.read_text(encoding="utf-8")
    title_line = original.splitlines()[0]
    short_cn = title_line.replace("#", "").replace("性格描述", "").strip()
    body_cn = review_map.get(short_cn, split_description_body(original))
    source_cn = body_cn.replace(names["cn"], FULL_NAME_TOKEN).replace(short_cn, SHORT_NAME_TOKEN)
    source_cn = apply_global_name_tokens(source_cn, token_entries)

    body_en = postprocess_translation(translate_text(translator, source_cn, "en"), names, short_cn, "en", token_entries)
    time.sleep(0.2)
    body_ja = postprocess_translation(translate_text(translator, source_cn, "ja"), names, short_cn, "ja", token_entries)
    time.sleep(0.2)

    content = "\n".join(
        [
            title_line,
            "",
            f"- 中文名：{names['cn']}",
            f"- English Name: {names['en']}",
            f"- 日本語名：{names['ja']}",
            "",
            "## 中文",
            body_cn,
            "",
            "## English",
            body_en,
            "",
            "## 日本語",
            body_ja,
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")


def main() -> None:
    translator = Translator()
    review_map = load_review_descriptions()
    short_name_map = load_short_names()
    token_entries = build_global_name_tokens(short_name_map)
    for folder in sorted(DOSSIER_ROOT.iterdir()):
        if not folder.is_dir() or folder.name not in NAME_MAP:
            continue
        portrait = folder / "portrait.md"
        personality = folder / "personality_description.md"
        if not portrait.exists() or not personality.exists():
            continue
        names = NAME_MAP[folder.name]
        update_portrait(folder, names)
        update_description(folder, names, translator, review_map, token_entries)


if __name__ == "__main__":
    main()
