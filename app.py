import streamlit as st
import pandas as pd
import requests
import openai
import os
from dotenv import load_dotenv
from io import BytesIO

# .envからAPIキーを読み込み
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key  # v1系ではこの方法が正解

st.title("🔍 フィッシングサイト診断ツール（ChatGPT API）")
uploaded_file = st.file_uploader("📤 URL一覧のExcelファイルをアップロードしてください", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    if "URL" not in df.columns:
        st.error("⚠️ 'URL'という列が必要です。")
    else:
        results = []
        progress = st.progress(0)
        for i, url in enumerate(df["URL"]):
            try:
                html = requests.get(url, timeout=10).text[:3000]
            except:
                html = "取得失敗"

            prompt = f"""
このURLとHTMLはフィッシングサイトの可能性がありますか？

URL: {url}
HTML（一部）: {html}

以下の形式で日本語で答えてください：

フィッシングスコア: 数字（0〜100）
理由: 300文字以内で簡潔に
"""

            try:
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                result_text = response.choices[0].message["content"].strip()
            except Exception as e:
                result_text = f"エラー: {e}"

            results.append(result_text)
            progress.progress((i + 1) / len(df))

        df["診断結果"] = results
        st.success("✅ 診断完了！")
        st.dataframe(df)

        output = BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        st.download_button("📥 結果をExcelでダウンロード", output.getvalue(), file_name="output.xlsx")
