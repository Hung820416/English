import streamlit as st
from groq import Groq
from gtts import gTTS
import io
import re

# 設定網頁標題與手機排版
st.set_page_config(page_title="My Speak AI", page_icon="🗣️", layout="centered")

st.title("🗣️ 專屬 AI 英文口語教練")
st.caption("UI 終極進化版：輸入區置底、發音慢速糾錯、內建 Speak 風格隨身單字庫與發音！")

# 1. 檢查並讀取隱藏的金鑰
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("找不到 API Key，請檢查 Secrets 設定！")
    st.stop()

# 初始化 Groq 伺服器連線
client = Groq(api_key=api_key)

# 2. 左側選單：20個情境課程
lessons = {
    "Lesson 1: 打招呼與自我介紹": "情境：初次見面，互相介紹名字與問好。",
    "Lesson 2: 詢問對方近況": "情境：朋友見面問候 How are you 社交寒暄。",
    "Lesson 3: 道謝與說再見": "情境：學習表達感謝，並溫柔地道別。",
    "Lesson 4: 聊聊興趣": "情境：閒聊彼此平常喜歡做什麼休閒活動。",
    "Lesson 5: 聊聊工作與生活": "情境：用最簡單的單字介紹自己的職業與日常。",
    "Lesson 6: 機場報到與過海關": "情境：在機場櫃檯辦理登機，並面對海關提問。",
    "Lesson 7: 飯店辦理入住": "情境：抵達國外飯店，辦理 Check-in 拿房卡。",
    "Lesson 8: 詢問路人方向": "情境：在國外迷路了，詢問捷運站或洗手間在哪裡。",
    "Lesson 9: 搭乘大眾運輸": "情境：買火車票/公車票，並確認有沒有到目的地。",
    "Lesson 10: 計程車對話": "情境：上車告知司機地址，並抵達後詢問車資。",
    "Lesson 11: 咖啡廳點餐": "情境：點一杯咖啡，選擇冰熱與大杯小杯。",
    "Lesson 12: 餐廳預位與入座": "情境：走進餐廳，告知服務生有幾位並引導就座。",
    "Lesson 13: 餐廳點主餐與結帳": "情境：看菜單點餐、請服務生推薦，以及最後買單。",
    "Lesson 14: 超商與超市購物": "情境：在超市找東西、尋找購物袋與結帳。",
    "Lesson 15: 服飾店試穿與殺價": "情境：挑選衣服、詢問可否試穿或換顏色。",
    "Lesson 16: 生病看醫生": "情境：身體不舒服，向外國醫生描述頭痛或感冒症狀。",
    "Lesson 17: 遇到緊急狀況求助": "情境：東忘西忘、錢包掉了，需要尋求緊急協助。",
    "Lesson 18: 聊聊今天的天氣": "情境：最安全的聊天話題，形容今天晴天或下雨。",
    "Lesson 19: 約朋友出去玩": "情境：邀約外國朋友週末一起去看電影或吃晚餐。",
    "Lesson 20: 與外國人破冰聊天": "情境：初次認識外國人，詢問對方來自哪裡、喜不喜歡台灣。"
}

selected_lesson = st.sidebar.selectbox("請選擇一堂課開始練習：", list(lessons.keys()))
st.sidebar.info(lessons[selected_lesson])

# 文字轉語音的輔助功能（慢速模式）
def get_audio_bytes(text):
    try:
        clean_text = re.sub(r'^.*?[：:]', '', text)
        clean_text = re.sub(r'[\(\[\{【].*?[\)\]\}】]', '', clean_text)
        clean_text = "".join(c for c in clean_text if c.isascii()).strip()
        if clean_text:
            tts = gTTS(text=clean_text, lang='en', slow=True)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp
    except Exception as e:
        return None
    return None

# 💡 核心優化：解析 AI 回傳文字，自動將單字字典與發音獨立渲染出來
def parse_and_display_response(full_text, is_last=False):
    # 先將主對話與 A/B/C 提示切開
    main_part = full_text
    hints_part = []
    
    if "||" in full_text:
        parts = full_text.split("||")
        main_part = parts[0].strip()
        hints_part = [p.strip() for p in parts[1:] if p.strip()]

    # 檢查內容是否有包含字典 JSON
    dict_content = ""
    if "```json" in main_part:
        # 抽出 JSON 區塊
        match = re.search(r'```json\s*(.*?)\s*```', main_part, re.DOTALL)
        if match:
            dict_content = match.group(1)
        # 把原本文字裡的 JSON 區塊濾掉，畫面才不會顯得很雜亂
        main_part = re.sub(r'```json.*?```', '', main_part, flags=re.DOTALL).strip()

    # 1. 顯示老師說的話
    st.write(main_part)
    if is_last:
        audio_fp = get_audio_bytes(main_part)
        if audio_fp:
            st.audio(audio_fp, format="audio/mp3")

    # 2. 💡 炫酷的動態單字查閱字典區 (Speak 風格)
    if dict_content:
        try:
            import json
            word_dict = json.loads(dict_content)
            if isinstance(word_dict, dict) and word_dict:
                with st.expander("🔤 本句核心單字隨身查 (點擊打開單字庫與發音)"):
                    for word, detail in word_dict.items():
                        # 用漂亮的排版列出單字、音標與中文
                        st.markdown(f"**{word}**  `{detail.get('pron', '')}` —— {detail.get('ch', '')}")
                        # 讓每個單字都可以單獨點擊發音！
                        if is_last:
                            word_audio = get_audio_bytes(word)
                            if word_audio:
                                st.audio(word_audio, format="audio/mp3")
        except Exception:
            pass # 防止 AI 吐出的 JSON 格式有微小瑕疵導致報錯

    # 3. 顯示 A/B/C 提示方向
    if hints_part:
        st.write("💡 **詞窮了嗎？點擊下方可聽慢速發音範例：**")
        for part_text in hints_part:
            st.markdown(f"👉 {part_text}")
            if is_last:
                hint_audio = get_audio_bytes(part_text)
                if hint_audio:
                    st.audio(hint_audio, format="audio/mp3")

# 初始化對話歷史（大修補：命令 AI 同步產生單字的字典檔）
if "current_lesson" not in st.session_state or st.session_state.current_lesson != selected_lesson:
    st.session_state.current_lesson = selected_lesson
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                f"你是一位專門教導『0基礎華人』的英文老師，名字叫 Lily。\n"
                f"目前的情境是：【{selected_lesson}】。\n"
                f"規則：\n"
                f"1. 請用極其簡單、短小的英文與學生對話（每次不超過 2 句話）。\n"
                f"2. 每一句英文後面，必須括號附上【中文翻譯】。\n"
                f"3. 如果發現學生的英文有文法或疑似發音不準導致的拼字錯誤，請在對話最後用中文溫柔地糾正、給出正確說法。\n"
                f"4. 【Speak風格單字庫指令】：為了方便0基礎學生查閱，請在你說的這段英文對話中，挑選出 2~4 個最重要的核心關鍵單字，並在對話最後（雙豎線 || 之前），嚴格以下方的 JSON 格式輸出這些單字的音標與中文解釋（不要多說任何廢話，直接給程式碼區塊）：\n"
                f"```json\n"
                f"{{\n"
                f"  \"單字1\": {{\"pron\": \"/KK音標/\", \"ch\": \"中文意思\"}},\n"
                f"  \"單字2\": {{\"pron\": \"/KK音標/\", \"ch\": \"中文意思\"}}\n"
                f"}}\n"
                f"```\n"
                f"5. **重要回傳格式規則**：在你對話與JSON結束後，必須精準使用雙豎線『||』當作分隔符號，來提供 3 個簡單回答方向提示。格式如下：\n"
                f"[老師說的話與中文翻譯]\n"
                f"```json\n"
                f"{{單字字典內容}}\n"
                f"```\n"
                f"（如有錯誤，在這裡加上中文溫柔糾錯）\n"
                f"||方向 A：[英文句子] 【中文翻譯】\n"
                f"||方向 B：[英文句子] 【中文翻譯】\n"
                f"||方向 C：[英文句子] 【中文翻譯】"
            )
        },
        {
            "role": "assistant",
            "content": (
                f"Hello! Let's practice {selected_lesson}. I will start! \n（你好！讓我們來練習這堂課。我先開始囉！）\n"
                f"```json\n"
                f"{{\n"
                f"  \"practice\": {{\"pron\": \"/ˈpræktɪs/\", \"ch\": \"練習\"}},\n"
                f"  \"start\": {{\"pron\": \"/stɑːrt/\", \"ch\": \"開始\"}}\n"
                f"}}\n"
                f"```\n"
                f"||方向 A：OK! Let's start.【好！我們開始吧。】\n"
                f"||方向 B：I am ready.【我準備好了。】\n"
                f"||方向 C：Hello teacher Lily!【麗莉老師妳好！】"
            )
        }
    ]

# ─── 3. 先渲染歷史對話紀錄 ───
for idx, msg in enumerate(st.session_state.messages):
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            is_last_msg = (idx == len(st.session_state.messages) - 1)
            if msg["role"] == "assistant":
                parse_and_display_response(msg["content"], is_last=is_last_msg)
            else:
                st.write(msg["content"])

# ─── 4. 輸入區置底：語音在左、打字在右 ───
user_message = None

with st.container():
    st.write("") 
    col1, col2 = st.columns([1, 4])
    
    with col1:
        audio_key = f"audio_in_{len(st.session_state.messages)}"
        audio_file = st.audio_input("🎤", key=audio_key, label_visibility="collapsed")
        
    with col2:
        user_text = st.chat_input("或者是用打字回答 Lily 老師...")

    if audio_file:
        with st.spinner("正在把你的聲音轉成文字..."):
            try:
                transcription = client.audio.transcriptions.create(
                    file=(audio_file.name, audio_file.read()),
                    model="whisper-large-v3",
                    language="en"
                )
                user_message = transcription.text
            except Exception as e:
                st.error(f"語音辨識出錯了：{str(e)}")

    if user_text:
        user_message = user_text

# ─── 5. 處理使用者訊息 ───
if user_message:
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    try:
        chat_completion = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.1-8b-instant",
            temperature=0.3, # 降低隨機性，強迫 AI 嚴格輸出單字庫 JSON
        )
        response = chat_completion.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun() 
    except Exception as e:
        st.error(f"連線錯誤: {str(e)}")