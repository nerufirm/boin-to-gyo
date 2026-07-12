"""wordfreq の日本語頻度辞書から実在語を抽出して words.txt を生成する。

実行時(app.py)には wordfreq を使わせず、生成済みの words.txt を同梱する。
    python3 build_dict.py
"""

import re

import pykakasi
from wordfreq import top_n_list

kks = pykakasi.kakasi()

_SMALL = {"ゃ": "a", "ゅ": "u", "ょ": "o",
          "ぁ": "a", "ぃ": "i", "ぅ": "u", "ぇ": "e", "ぉ": "o"}
_BASE = {}
for _v, _cs in {
    "a": "あかさたなはまやらわがざだばぱ",
    "i": "いきしちにひみりぎじぢびぴ",
    "u": "うくすつぬふむゆるぐずづぶぷ",
    "e": "えけせてねへめれげぜでべぺ",
    "o": "おこそとのほもよろをごぞどぼぽ",
}.items():
    for _c in _cs:
        _BASE[_c] = _v


def vowel_pattern(word: str) -> str:
    hira = "".join(i["hira"] for i in kks.convert(word))
    out: list[str] = []
    for ch in hira:
        if ch in _SMALL:
            if out:
                out[-1] = _SMALL[ch]
            else:
                out.append(_SMALL[ch])
        elif ch == "ん":
            out.append("n")
        elif ch == "っ":
            continue
        elif ch == "ー":
            if out:
                out.append(out[-1])
        elif ch in _BASE:
            out.append(_BASE[ch])
    return "".join(out)


KANJI = re.compile(r"[一-鿿]")
KATAKANA_ONLY = re.compile(r"^[゠-ヿー]+$")
# 漢字/かな以外（英数字・記号）を含む語は除外
DISALLOWED = re.compile(r"[^぀-ヿ一-鿿ー]")

# 明らかな機能語・接尾など、漢字を含んでも韻に向かない語を軽く除外
STOP = {"御", "等", "様", "殿", "頃", "迄", "為", "如", "或", "尚", "但"}


def is_content_word(w: str) -> bool:
    if len(w) < 2 and not KATAKANA_ONLY.match(w):
        return False
    if DISALLOWED.search(w):
        return False
    if w in STOP:
        return False
    # 漢字を含む、またはカタカナのみ（＝名詞・動詞・外来語が中心に残る）
    return bool(KANJI.search(w)) or bool(KATAKANA_ONLY.match(w))


MAX_WORDS = 15000   # 頻度上位に絞る（認知度の高い語ほど韻として面白い）


def main():
    candidates = top_n_list("ja", 60000)
    seen = set()
    kept = []
    for w in candidates:
        if len(kept) >= MAX_WORDS:
            break
        if w in seen or not is_content_word(w):
            continue
        pat = vowel_pattern(w)
        if not (2 <= len(pat) <= 6):   # 2〜6モーラだけ採用
            continue
        seen.add(w)
        kept.append(w)

    # パターンごとの語数を集計して、韻が成立しやすいか確認
    from collections import Counter
    pat_count = Counter(vowel_pattern(w) for w in kept)
    multi = sum(1 for c in pat_count.values() if c >= 2)

    with open("words.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(kept) + "\n")

    print(f"抽出語数: {len(kept)}")
    print(f"ユニーク母音パターン数: {len(pat_count)}（うち2語以上で韻可: {multi}）")
    print("多い塊 上位10:", pat_count.most_common(10))


if __name__ == "__main__":
    main()
