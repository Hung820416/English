import streamlit as st
from groq import Groq

# 設定網頁標題
st.set_page_config(page_title="My Speak AI", page_icon="🗣️", layout="centered")

st.title("🗣️ 專屬 AI 英文口語教練")
st.caption("電腦、手機皆可使用！支援語音輸入與 20 個基礎情境課程。")

# 1. 檢查並讀取隱藏的金鑰
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("找不到 API Key，請檢查 .streamlit/secrets.toml 設定！")
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

# 如果使用者切換了課程，就重設聊天歷史
if "current_lesson" not in st.session_state or st.session_state.current_lesson != selected_lesson:
    st.session_state.current_lesson = selected_lesson
    # 建立系統規則（System Prompt）
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                f"你是一位專門教導『0基礎華人』的英文老師，名字叫 Lily。\n"
                f"目前的情境是：【{selected_lesson}】。\n"
                f"規則：\n"
                f"1. 請用極其簡單、短小的英文與學生對話（每次不超過 2 句話，單字要簡單）。\n"
                f"2. 每一句英文後面，必須括號附上【中文翻譯】。\n"
                f"3. 如果發現學生的英文有語法錯誤，請在對話最後用中文溫柔地糾正，並給出正確說法。\n"
                f"4. 請主動開啟與該情境相關的對話，引導學生回答。"
            )
        },
        {
            "role": "assistant",
            "content": f"Hello! Let's practice {selected_lesson}. I will start! \n（你好！讓我們來練習這堂課。我先開始囉！）"
        }
    ]

# 3. 顯示歷史對話紀錄
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# 4. 語音與文字輸入區
st.write("---")
st.subheader("請選擇『說話』或『打字』來回答老師：")

user_message = None

# 【語音輸入功能】
audio_file = st.audio_input("🎤 點擊麥克風開始錄音（講完再點一次停止）")
if audio_file:
    with st.spinner("正在把你的聲音轉成文字..."):
        try:
            # 將語音檔案傳給 Groq Whisper API 進行轉錄
            transcription = client.audio.transcriptions.create(
                file=(audio_file.name, audio_file.read()),
                model="whisper-large-v3",
                language="en" # 強制指定辨識英文
            )
            user_message = transcription.text
            st.success(f"🗣️ 語音辨識成功！你說了：{user_message}")
        except Exception as e:
            st.error(f"語音辨識出錯了：{str(e)}")

# 【打字輸入功能】
user_text = st.chat_input("或者是用打字回答 Lily 老師...")
if user_text:
    user_message = user_text

# 5. 當收到使用者的訊息（不論是說話還是打字）
if user_message:
    # 顯示使用者的話
    with st.chat_message("user"):
        st.write(user_message)
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    # 呼叫 Groq Llama 3 生成老師的回答
    with st.chat_message("assistant"):
        with st.spinner("Lily 老師正在思考如何回應你..."):
            try:
                chat_completion = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.1-8b-instant",  # 改成這個
                temperature=0.7,
                )
                response = chat_completion.choices[0].message.content
                st.write(response)
                # 紀錄老師的回答
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"連線錯誤: {str(e)}")