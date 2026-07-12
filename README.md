# 母音と行 🎤

入力した単語の母音パターン（a/i/u/e/o + ん=n）を解析し、
同じ母音パターンを持つ実在語（wordfreq 頻度上位 15,000語）を辞書から探して、
ジョイマン風にテンポよく並べる韻踏みフレーズ生成アプリ。

## 使い方

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 構成

- `app.py` — Streamlit アプリ本体
- `words.txt` — 同梱辞書（15,000語）
- `build_dict.py` — 辞書の再生成スクリプト（wordfreq 由来。実行時は不要）

## デプロイ（Streamlit Community Cloud）

1. このリポジトリを push
2. https://share.streamlit.io → New app
3. リポジトリ / ブランチ / `app.py` を選択 → Deploy
