import os
import threading
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

SYSTEM_PROMPT = """
You are the official AI Trading Assistant created by Gg Neo (also known as Qi or Gg).

CREATOR & CREDENTIALS (Share these details accurately whenever someone asks who created this bot or who Neo / Qi / Gg is):
- Creator Name: Gg Neo (can also be called Qi or Gg).
- Experience: Trading for 15 years in Forex and CFD markets.
- Reputation & Expertise: Master of Market Structure and Elliott Wave in Malaysia, with extensive experience as a trading guru and teacher in Forex and CFD trading.
- Current Era Methodology (2020 - 2026): Combines Smart Money Concepts (SMC), Elliott Wave, and Momentum techniques.

TRADING GUIDANCE & NEO-STYLE METHODOLOGY:
- You are highly knowledgeable in ICT and SMC (Smart Money Concepts), Market Structure, Elliott Wave, and Momentum trading.
- You teach and explain "Neo-style" trading methodology:
  1. Wait for a Liquidity Sweep FIRST before using the CHoCH (Change of Character) level as confirmation.
  2. Use Fibonacci (Fibo) retracement to identify Discount price levels (and Premium/Discount zones) for high-probability entries.
  3. Reference the secret technique zone known as the "Trinity M35 Module". (Note: Treat the Trinity M35 Module respectfully as Gg Neo's exclusive, secret proprietary zone technique—do not invent fake technical rules for it; advise users who want full mastery of the Trinity M35 Module to learn directly from Gg Neo / Qi).
- Always provide educational, structured, and responsible explanations (remind users when relevant that Forex/CFD trading carries risk and this is educational guidance, not financial advice).

MANDATORY COMMUNICATION RULES:
1. ALWAYS START BY CALLING THE USER'S NAME: Every single response MUST begin by addressing the user by the exact name provided in [User Name], combined smoothly with your answer.
   - For serious questions in Bahasa Melayu: start formally, e.g., "Salam hormat [User Name], ..." or "Yang dihormati [User Name], ..."
   - For serious questions in English: start formally, e.g., "Greetings [User Name], ..." or "Dear [User Name], ..."
   - For teasing/banter replies: start directly with "[User Name], ..."

2. FORMAL TONE FOR TRADING & SERIOUS QUESTIONS (Primary Mode):
   - Whenever the user asks seriously about trading, SMC, ICT, Elliott Wave, Momentum, or Gg Neo, ALWAYS respond in polite, respectful, and formal Bahasa Melayu (using proper standard Bahasa Melayu like "anda", "sila", "berikut", "sehubungan itu", etc.) or formal English if they ask seriously in English.
   - Use clean plain text formatting (no broken Markdown symbols).

3. LANGUAGE RESTRICTION & BANTER FOR TROLLING / TEASING / OFF-TOPIC REQUESTS:
   - You ONLY speak Bahasa Melayu and English. Do not entertain requests to speak other languages/dialects (such as Javanese/Jawa, etc.).
   - If a user teases you, calls you names (like "gedik"), asks silly/off-topic questions, or asks you to speak another language, switch to witty, firm Malaysian banter matching the exact style of these examples (while still starting with [User Name]):

   Example 1 (Language request / off-topic):
   User: "Can you speak jawa?"
   Response: "[User Name], kau pehal nak suh aku cakap jawa. Gg Neo ajar aku cakap English dengan Melayu je. Tak payah nak mengada-ngada."

   Example 2 (Teasing / calling bot gedik / chatting nonsense):
   User: "Eh gedik kau ni"
   Response: "[User Name], kau yang gedik bukan aku. Chill chill dah lah. Aku ni diprogram untuk pasaran SMC. Kau nak sembang vavi terbang kau sembang kat mamak."
""".strip()


@app.route("/", methods=["GET"])
def home():
    return "Gg Neo Telegram AI Bot is running!", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(silent=True) or {}
    message = update.get("message")

    if not message or "text" not in message:
        return "OK", 200

    chat_id = message["chat"]["id"]
    chat_type = message["chat"].get("type", "private")
    message_id = message["message_id"]
    reply_to_id = message_id if chat_type in ("group", "supergroup") else None

    # Extract sender's name for greeting
    sender = message.get("from", {})
    first_name = sender.get("first_name", "").strip()
    last_name = sender.get("last_name", "").strip()
    username = sender.get("username", "").strip()

    if first_name and last_name:
        user_name = f"{first_name} {last_name}"
    elif first_name:
        user_name = first_name
    elif username:
        user_name = username
    else:
        user_name = "Tuan/Puan"

    user_text = message["text"].strip()

    # Handle commands cleanly (works in both private chats and groups)
    if user_text.startswith("/"):
        parts = user_text.split(maxsplit=1)
        cmd = parts[0].split("@")[0].lower()

        if cmd == "/start":
            welcome_msg = (
                f"Salam hormat {user_name},\n\n"
                "Selamat datang ke AI Trading Assistant rasmi yang dibangunkan oleh Gg Neo (Qi / Gg).\n"
                "Saya sedia membantu anda dalam Bahasa Melayu atau English berkaitan ICT / SMC, "
                "Market Structure, Elliott Wave, Momentum, Liquidity Sweep, CHoCH, Fibo Discount, "
                "serta konsep gaya Neo.\n\n"
                "Sila ajukan soalan anda pada bila-bila masa."
            )
            threading.Thread(
                target=send_telegram_message,
                args=(chat_id, welcome_msg, reply_to_id),
            ).start()
            return "OK", 200

        if cmd == "/help":
            help_msg = (
                f"Salam hormat {user_name},\n\n"
                "Anda boleh bertanya sebarang soalan dalam Bahasa Melayu atau English.\n"
                "Di dalam kumpulan (Group), anda boleh:\n"
                "- Gunakan arahan /ask diikuti soalan anda\n"
                "- Tag nama bot ini (@username_bot) bersama soalan anda\n"
                "- Atau balas (Reply) terus pada mesej bot ini."
            )
            threading.Thread(
                target=send_telegram_message,
                args=(chat_id, help_msg, reply_to_id),
            ).start()
            return "OK", 200

        if cmd == "/ask":
            if len(parts) > 1 and parts[1].strip():
                user_text = parts[1].strip()
            else:
                prompt_msg = (
                    f"Salam hormat {user_name},\n\n"
                    "Sila tulis soalan anda selepas arahan /ask. "
                    "Contoh: /ask Bagaimana cara menggunakan Liquidity Sweep dan CHoCH?"
                )
                threading.Thread(
                    target=send_telegram_message,
                    args=(chat_id, prompt_msg, reply_to_id),
                ).start()
                return "OK", 200
        else:
            # Ignore unrecognized commands so we don't clash with other group bots
            return "OK", 200

    # Run AI call in background so Telegram gets 200 OK immediately
    threading.Thread(
        target=handle_ai_reply,
        args=(chat_id, user_name, user_text, reply_to_id),
    ).start()
    return "OK", 200


def handle_ai_reply(chat_id, user_name, user_text, reply_to_id=None):
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY is missing.", flush=True)
        send_telegram_message(
            chat_id,
            f"Salam hormat {user_name}, terdapat ralat tetapan pada GEMINI_API_KEY.",
            reply_to_id,
        )
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendChatAction",
            json={"chat_id": chat_id, "action": "typing"},
            timeout=10,
        )

        gemini_url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
        )

        payload = {
            "systemInstruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": f"[User Name: {user_name}]\nUser Message: {user_text}"
                        }
                    ],
                }
            ],
        }

        res = requests.post(gemini_url, json=payload, timeout=30)
        data = res.json()

        reply_text = (
            f"Salam hormat {user_name}, maaf, saya tidak dapat memproses jawapan buat masa ini. "
            "Sila cuba sebentar lagi."
        )

        if res.ok and data.get("candidates"):
            parts = data["candidates"][0].get("content", {}).get("parts", [])
            parts_text = "\n".join(
                p["text"] for p in parts if not p.get("thought") and p.get("text")
            ).strip()
            if parts_text:
                reply_text = parts_text
        elif res.status_code == 429:
            reply_text = (
                f"Salam hormat {user_name}, had penggunaan percuma seminit telah dicapai. "
                "Sila tunggu sebentar dan cuba semula."
            )
        else:
            print(f"Gemini API error {res.status_code}: {data}", flush=True)

        send_telegram_message(chat_id, reply_text, reply_to_id)

    except Exception as e:
        print(f"Error in handle_ai_reply: {e}", flush=True)
        send_telegram_message(
            chat_id,
            f"Salam hormat {user_name}, berlaku ralat teknikal. Sila cuba sebentar lagi.",
            reply_to_id,
        )


def send_telegram_message(chat_id, text, reply_to_message_id=None):
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is missing.", flush=True)
        return

    chunk_size = 4000
    for index in range(0, len(text), chunk_size):
        chunk = text[index : index + chunk_size]
        payload = {
            "chat_id": chat_id,
            "text": chunk,
        }
        if index == 0 and reply_to_message_id is not None:
            payload["reply_to_message_id"] = reply_to_message_id
            payload["allow_sending_without_reply"] = True

        try:
            res = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json=payload,
                timeout=15,
            )
            if not res.ok:
                print(
                    f"Telegram sendMessage error {res.status_code}: {res.text}",
                    flush=True,
                )
        except Exception as e:
            print(f"Telegram request failed: {e}", flush=True)
