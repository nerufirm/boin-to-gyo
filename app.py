"""ジョイマン風 韻踏みフレーズ生成アプリ

入力単語の母音パターン（a/i/u/e/o + ん=n）を解析し、
同じパターンを持つ辞書内の単語を探してテンポよく並べる。

実行: streamlit run app.py
"""

import os
import random

import pykakasi
import streamlit as st

# ─────────────────────────────────────────────
# ステップ1: 単語の母音抽出
# ─────────────────────────────────────────────
# ヘボン式ローマ字を後処理すると「な行の子音 n」を「ん」と誤判定するため、
# ローマ字ではなく "ひらがなのモーラ" から母音を取り出す。
#
#   は ん き ょ う      な ま え
#   a  n  →  o  u      a  a  e      ← な の n は拾わない（正しい）
#
# 拗音（ゃゅょ）は直前の母音を上書き、促音（っ）は無音、
# 長音（ー）は直前の母音を繰り返す。

_SMALL_YOUON = {
    "ゃ": "a", "ゅ": "u", "ょ": "o",
    "ぁ": "a", "ぃ": "i", "ぅ": "u", "ぇ": "e", "ぉ": "o",
}

# 各ひらがな → 母音 の対応表を組み立てる
_BASE_VOWEL = {}
for _vowel, _chars in {
    "a": "あかさたなはまやらわがざだばぱ",
    "i": "いきしちにひみりぎじぢびぴ",
    "u": "うくすつぬふむゆるぐずづぶぷ",
    "e": "えけせてねへめれげぜでべぺ",
    "o": "おこそとのほもよろをごぞどぼぽ",
}.items():
    for _c in _chars:
        _BASE_VOWEL[_c] = _vowel


@st.cache_resource
def _get_kakasi():
    """pykakasi 変換器は生成コストが高いので使い回す。"""
    return pykakasi.kakasi()


def to_hiragana(word: str) -> str:
    """漢字・カタカナ混じりの文字列をひらがな読みに変換する。"""
    kks = _get_kakasi()
    return "".join(item["hira"] for item in kks.convert(word))


def get_vowel_pattern(word: str) -> str:
    """単語の母音パターン（例: バズる → 'auu'）を返す。"""
    vowels: list[str] = []
    for ch in to_hiragana(word):
        if ch in _SMALL_YOUON:            # 拗音: 直前モーラの母音を上書き
            if vowels:
                vowels[-1] = _SMALL_YOUON[ch]
            else:
                vowels.append(_SMALL_YOUON[ch])
        elif ch == "ん":                  # 撥音: n として1拍
            vowels.append("n")
        elif ch == "っ":                  # 促音: 母音なし
            continue
        elif ch == "ー":                  # 長音: 直前の母音を繰り返す
            if vowels:
                vowels.append(vowels[-1])
        elif ch in _BASE_VOWEL:
            vowels.append(_BASE_VOWEL[ch])
        # それ以外（記号・空白など）は無視
    return "".join(vowels)


# ─────────────────────────────────────────────
# 辞書: wordfreq 由来の実在語 約12,000語（build_dict.py で生成）
# words.txt を同梱しておけば実行時に wordfreq は不要。
# ─────────────────────────────────────────────
_DICT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "words.txt")


@st.cache_data
def load_dictionary() -> list[str]:
    """words.txt から単語リストを読み込む。無ければ最小フォールバック。"""
    if os.path.exists(_DICT_PATH):
        with open(_DICT_PATH, encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return ["担ぐ", "隠す", "東京", "情報", "反響", "感動", "心", "男", "子供"]


@st.cache_data
def build_pattern_index() -> dict[str, str]:
    """辞書の各単語について母音パターンを事前計算する。"""
    return {w: get_vowel_pattern(w) for w in load_dictionary()}


# ─────────────────────────────────────────────
# ステップ2 & 3: 検索してフレーズを組む
# ─────────────────────────────────────────────
def find_rhymes(word: str, pattern: str, index: dict[str, str]) -> list[str]:
    """母音パターンが一致する単語を辞書から探す（入力語自身は除く）。"""
    return [w for w, p in index.items() if p == pattern and w != word]


def generate_phrase(word: str, matches: list[str]) -> str:
    """一致語から1〜2語をランダムに選び「A、B、入力語」の形に整える。"""
    n = min(len(matches), random.choice([1, 2]))
    chosen = random.sample(matches, n)
    return "、".join(chosen + [word])


# ─────────────────────────────────────────────
# Streamlit UI
# ─────────────────────────────────────────────
st.set_page_config(page_title="母音と行", page_icon="🎤")
st.title("🎤 母音と行")
st.caption("入力した単語と母音がそろう言葉を辞書から探して、テンポよく並べます。")

word = st.text_input("韻を踏みたい単語を入力", placeholder="例: バズる")

if st.button("韻を踏む", type="primary"):
    target = word.strip()
    if not target:
        st.warning("単語を入力してね。")
    else:
        index = build_pattern_index()
        pattern = get_vowel_pattern(target)
        matches = find_rhymes(target, pattern, index)

        if matches:
            st.success(generate_phrase(target, matches))
            st.caption(f"母音パターン: `{pattern or '(なし)'}`／一致した候補: {'、'.join(matches)}")
        else:
            st.error(f"ごめん、{target}で踏める韻が見つからなかった…")
            st.caption(f"母音パターン: `{pattern or '(なし)'}`")

_dictionary = load_dictionary()
st.caption(f"収録語数: {len(_dictionary):,} 語（wordfreq 頻度上位より）")
with st.expander("収録単語をのぞく（先頭300語）"):
    st.write("、".join(_dictionary[:300]))
