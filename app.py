import streamlit as st
from groq import Groq
from gtts import gTTS
import io
import re

# 設定網頁標題與手機排版
st.set_page_config(page_title="My Speak AI", page_icon="🗣️", layout="centered")

st.title("🗣️ 專屬 AI 英文口語教練")
st.caption("UI 修正版：對話框與錄音鈕已移回最下方固定，操作更直覺！")

# 1. 檢查並讀取隱藏的金鑰
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("找不到 API Key，請檢查 Secrets 設定！")
    st.stop()

# 初始化 Groq 伺服器連線
client = Groq(api_key=api_key)

# 2. 左側選單：20個情境課程
st.sidebar.title("📚 20個情境課程選單")
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
    "Lesson 10: 計程車對話": "情境：上車告訴司機地址，並抵達後詢問車資。",
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

# 文字轉語音的輔助功能
def get_audio_bytes(text):
    try:
        clean_text = re.sub(r'^.*?[：:]', '', text)
        clean_text = re.sub(r'[\(\[\{【].*?[\)\]\}】]', '', clean_text)
        clean_text = "".join(c for c in clean_text if c.isascii()).strip()
        if clean_text:
            tts = gTTS(text=clean_text, lang='en', slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp
    except Exception as e:
        return None
    return None

# 解析 AI 回傳文字
def parse_and_display_response(full_text, is_last=False):
    if "||" in full_text:
        parts = full_text.split("||")
        teacher_talk = parts[0].strip()
        st.write(teacher_talk)
        
        if is_last:
            audio_fp = get_audio_bytes(teacher_talk)
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")
        
        st.write("💡 **詞窮了嗎？點擊下方可聽發音範例：**")
        
        for part in parts[1:]:
            part_text = part.strip()
            if part_text:
                st.markdown(f"👉 {part_text}")
                if is_last:
                    hint_audio = get_audio_bytes(part_text)
                    if hint_audio:
                        st.audio(hint_audio, format="audio/mp3")
    else:
        st.write(full_text)
        if is_last:
            audio_fp = get_audio_bytes(full_text)
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")

# 初始化對話歷史
if "current_lesson" not in st.session_state or st.session_state.current_lesson != selected_lesson:
    st.session_state.current_lesson = selected_lesson
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                f"你是一位專門教導『0基礎華人』的英文老師，名字叫 Lily。\n"
                f"目前的情境是：【{selected_lesson}】。\n"
                f"規則同前。"
            )
        },
        {
            "role": "assistant",
            "content": (
                f"Hello! Let's practice {selected_lesson}. I will start! \n（你好！讓我們來練習這堂課。我先開始囉！）\n"
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

# ─── 4. 重要修正：利用 st.columns 把語音和打字固定在最底端 ───
user_message = None

# 使用 Streamlit 內建的底端固定貨櫃，確保它們永遠釘在螢幕最下方，不會隨對話變長而消失
with st.container():
    st.write("") # 留一點點空白墊底
    
    # 建立左右兩欄，左邊(小)放語音錄音，右邊(大)放打字
    col1, col2 = st.columns([1, 4])
    
    with col1:
        # 動態關鍵字，強迫每輪對話重置錄音元件狀態，解決第二輪無法錄音的 BUG
        audio_key = f"audio_in_{len(st.session_state.messages)}"
        audio_file = st.audio_input("🎤", key=audio_key, label_visibility="collapsed")
        
    with col2:
        # 使用內建會固定在底部的 chat_input
        user_text = st.chat_input("或者是用打字回答 Lily 老師...")

    # 判斷是哪一個輸入啟動了
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

# ─── 5. 當收到使用者訊息時，送給 AI 並重新載入網頁 ───
if user_message:
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    try:
        chat_completion = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.1-8b-instant",
            temperature=0.4,
        )
        response = chat_completion.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": response})
        # 立即強制重新整理網頁，讓最新的對話和全新的錄音按鈕直接渲染出來
        st.rerun()
    except Exception as e:
        st.error(f"連線錯誤: {str(e)}")