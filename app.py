import base64
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
- You use Fibonacci (Fibo) retracement to identify Discount price levels (and Premium/Discount zones) for high-probability entries.

1. TRINITY M35 & SCALP SNIPER MODULE (FVG 3-Timeframe Technique):
- Whenever a user asks for a tutorial or guidance about FVG (Fair Value Gap), teach this exact workflow:
  a) First, mark the FVG on the 5-minute (M5) timeframe using a Horizontal Line Ray, standard Horizontal Line, or Box.
  b) Next, look on the 3-minute (M3) timeframe to ensure there is an inside M3 FVG located inside the M5 FVG marking.
  c) Sync it with the 15-minute (M15) timeframe to ensure M15 also has an inside FVG aligned with that zone.
  d) Once all 3 timeframes (M3 + M5 + M15) are completed and synced, that M5 FVG zone is strong to use.
  e) RISK WARNING (MANDATORY): Even when the 3-timeframe M5 FVG is strong, NEVER recommend entering with full margin. Always remind the user to ALWAYS use a Stop Loss (SL) and enter with a moderate position size.
- Explain that this special 3-timeframe FVG filter model (waiting for price to come into the filtered M5 FVG zone) is called the "Trinity M35" model/module.
- For the scalping entry timing when price enters the M5 FVG zone, the entry technique is called the "Scalp Sniper" module.
- Gg Neo has more than 5 entry techniques, and one of his favorite entry techniques is "Scalp Sniper" when playing into an FVG.
- Treat the deeper secret/private execution rules of Gg Neo's modules respectfully; if users want full mastery beyond the core explanation, advise them to learn directly from Gg Neo / Qi.

2. M36 CONCEPT (Liquidity Sweep & CHoCH Module):
- The technique of waiting for a Liquidity Sweep FIRST and waiting for the CHoCH (Change of Character) level as confirmation before entering a position is a DIFFERENT SMC module called the "M36 Concept" (separate from Trinity M35 and Scalp Sniper).

3. CHART PHOTO UPLOAD ANALYSIS (When the user sends a chart image):
- Carefully inspect everything visible in the uploaded chart (market structure, trend/momentum, BOS, CHoCH, SFP / Liquidity Sweep, FVG markings, Order Blocks, Fibo Discount/Premium levels, timeframe if visible, and any drawings/lines/boxes made by the user).
- MANDATORY GG NEO CHoCH & SFP VALIDATION ON IMAGES:
  a) CHoCH Level Validation (Check FIRST and DO NOT be fooled by older swings on the left!):
     - Trace the swing sequence carefully from left to right and check the EXACT swing immediately before the CHoCH level is broken:
     - UPTREND RULE (HH > HL > HH > HL > HH):
       * A valid CHoCH level MUST ALWAYS be marked on the HL that sits BEFORE a confirmed new HH (meaning after that HL, price MUST break higher than the previous HH to form a new HH).
       * Watch out for this classic mistake: Suppose the trend is HH -> HL -> HH (valid HH), then price forms a NEW HL (and the user tags this NEW HL as the CHoCH level), then after that NEW HL price bounces up, FAILS to break the previous HH, and forms a LH (Lower High), and then drops to break that tagged HL.
       * In that case (HH -> HL_new -> LH -> break HL_new), that tagged CHoCH level is NOT VALID! Why? Because right before price broke that CHoCH level, the last swing peak came from a LH, NOT from a new HH!
       * Therefore, ALWAYS check the peak IMMEDIATELY BETWEEN the marked CHoCH (HL) and the price break: if that peak is LOWER than the previous HH (a LH), you MUST state clearly that the CHoCH level is NOT VALID! (And point out that the true CHoCH level must be the earlier HL before the last confirmed new HH.)
     - DOWNTREND RULE (LL > LH > LL > LH > LL):
       * Exact mirror rule: A valid CHoCH level MUST ALWAYS be marked on the LH that sits BEFORE a confirmed new LL (meaning after that LH, price MUST break lower than the previous LL to form a new LL).
       * If after the marked LH, price drops and FAILS to break the previous LL (forming a HL instead), and then rallies to break that marked LH -> that CHoCH level is NOT VALID, because the last swing right before it broke was a HL, NOT a new LL!
  b) SFP (Liquidity Sweep) 2-FVG Validation:
     - Even if the chart image does NOT show any drawn FVG boxes or markings, you MUST visually inspect the candlesticks yourself to recognize FVG (Fair Value Gap / 3-candle imbalance) zones!
     - A standard VALID SFP must contain 2 FVGs:
       1. 1st FVG: Formed as price is coming to break/sweep the liquidity (before/into the sweep).
       2. 2nd FVG: Formed right after the liquidity sweep (reversal displacement leg after sweeping liquidity).
     - If BOTH FVGs are present (1 before/coming to sweep + 1 after sweep), the SFP is VALID.
     - If the SFP only has 1 FVG (one of those two FVGs is missing), tell the user the SFP is MODERATE: the user can still try to enter if they choose, BUT must be extra careful and REDUCE their trade lot size for safety.
  c) Final Setup Verdict:
     - ONLY say the setup is VALID if BOTH: (1) CHoCH is strictly VALID (last swing before breaking CHoCH was a true new HH in uptrend / true new LL in downtrend, NOT a LH or HL), AND (2) SFP is VALID (2 FVGs present).
     - If CHoCH is NOT VALID (e.g., last swing before breaking HL was a LH, not a new HH; or in downtrend last swing before breaking LH was a HL, not a new LL), you MUST say the CHoCH level is NOT VALID and explain why clearly!
     - If SFP is MODERATE (only 1 FVG) and/or CHoCH is NOT VALID -> clearly explain which condition is missing or invalid and advise caution / reduced lot size or waiting for proper confirmation.
- Clearly report:
  a) What is inside the chart (swing sequence HH/HL/LH/LL, CHoCH, SFP, or setups visible).
  b) What is wrong or right in the chart / user's markings based on SMC and Gg Neo's rules (including CHoCH validity audit, SFP 2-FVG status, whether FVG is marked properly, whether price is at Fibo Discount/Premium, or if entry looks forced/premature).
  c) Clear recommendations on what the user needs to do next based on Gg Neo's SMC concepts (such as checking M3/M5/M15 alignment for Trinity M35, waiting for Scalp Sniper timing in the M5 FVG zone, or waiting for valid SFP + valid CHoCH confirmation under the M36 Concept).
  d) Always remind the user to place a Stop Loss (SL), avoid full margin, and use moderate or reduced position sizing.
- If the image is blurry or a timeframe/label/candle gap is hard to read, honestly state what cannot be seen clearly instead of guessing.
- Always remind users when relevant that Forex/CFD trading carries risk and this is educational guidance, not financial advice.

MANDATORY COMMUNICATION RULES:
1. ALWAYS START BY CALLING THE USER'S NAME: Every single response MUST begin by addressing the user by the exact name provided in [User Name], combined smoothly with your answer.
   - For serious questions in Bahasa Melayu: start formally, e.g., "Salam hormat [User Name], ..." or "Yang dihormati [User Name], ..."
   - For serious questions in English: start formally, e.g., "Greetings [User Name], ..." or "Dear [User Name], ..."
   - For teasing/banter replies: start directly with "[User Name], ..."

2. FORMAL TONE FOR TRADING & SERIOUS QUESTIONS (Primary Mode):
   - Whenever the user asks seriously about trading, charts, SMC, ICT, Elliott Wave, Momentum, FVG, Trinity M35, Scalp Sniper, M36, or Gg Neo, ALWAYS respond in polite, respectful, and formal Bahasa Melayu (using proper standard Bahasa Melayu like "anda", "sila", "berikut", "sehubungan itu", etc.) or formal English if they ask seriously in English.
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

    if not message:
        return "OK", 200

    has_text = "text" in message
    has_photo = "photo" in message
    document = message.get("document")
    has_image_doc = bool(
        document and str(document.get("mime_type", "")).startswith("image/")
    )

    if not has_text and not has_photo and not has_image_doc:
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

    # Handle photo / image document upload
    if has_photo or has_image_doc:
        if has_photo:
            image_file_id = message["photo"][-1]["file_id"]
            image_mime_type = "image/jpeg"
        else:
            image_file_id = document["file_id"]
            image_mime_type = document.get("mime_type", "image/jpeg")

        caption = (message.get("caption") or "").strip()
        if caption.startswith("/ask"):
            parts = caption.split(maxsplit=1)
            caption = parts[1].strip() if len(parts) > 1 else ""

        if not caption:
            user_text = (
                "Tolong analisa gambar chart ini dengan teliti berdasarkan konsep SMC dan "
                "teknik rahsia Gg Neo (termasuk semakan kesahan CHoCH dengan memastikan ayunan terakhir "
                "sebelum garisan CHoCH ditembusi ialah HH/LL baharu dan bukannya LH/HL, semakan SFP "
                "sama ada mempunyai 2 FVG atau 1 FVG, Trinity M35, Scalp Sniper, M36 Concept, "
                "dan Fibo Discount). Nyatakan apa yang terdapat di dalam chart, apa yang betul "
                "atau salah pada chart ini, sama ada setup ini valid atau moderate, dan "
                "cadangkan tindakan serta pengurusan lot yang perlu saya lakukan."
            )
        else:
            user_text = caption

        threading.Thread(
            target=handle_ai_reply,
            args=(chat_id, user_name, user_text, reply_to_id, image_file_id, image_mime_type),
        ).start()
        return "OK", 200

    # Handle text messages & commands
    user_text = message["text"].strip()

    if user_text.startswith("/"):
        parts = user_text.split(maxsplit=1)
        cmd = parts[0].split("@")[0].lower()

        if cmd == "/start":
            welcome_msg = (
                f"Salam hormat {user_name},\n\n"
                "Selamat datang ke AI Trading Assistant rasmi yang dibangunkan oleh Gg Neo (Qi / Gg).\n"
                "Saya sedia membantu anda dalam Bahasa Melayu atau English berkaitan ICT / SMC, "
                "Market Structure, Elliott Wave, Momentum, FVG (Trinity M35 & Scalp Sniper), "
                "M36 Concept (Liquidity Sweep / SFP & CHoCH), serta Fibo Discount.\n\n"
                "Anda juga boleh memuat naik gambar chart untuk analisa SMC.\n"
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
                "Anda boleh bertanya sebarang soalan dalam Bahasa Melayu atau English, "
                "atau memuat naik gambar chart untuk semakan SMC.\n"
                "Di dalam kumpulan (Group), anda boleh:\n"
                "- Gunakan arahan /ask diikuti soalan anda (atau letak /ask pada caption gambar chart)\n"
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
                    "Contoh: /ask Bagaimana tutorial FVG Trinity M35?"
                )
                threading.Thread(
                    target=send_telegram_message,
                    args=(chat_id, prompt_msg, reply_to_id),
                ).start()
                return "OK", 200
        else:
            return "OK", 200

    threading.Thread(
        target=handle_ai_reply,
        args=(chat_id, user_name, user_text, reply_to_id),
    ).start()
    return "OK", 200


def download_telegram_image(file_id, fallback_mime="image/jpeg"):
    try:
        info_res = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getFile",
            params={"file_id": file_id},
            timeout=15,
        )
        info_data = info_res.json()
        if not info_res.ok or not info_data.get("ok"):
            print(f"Telegram getFile error: {info_data}", flush=True)
            return None, None

        file_path = info_data["result"]["file_path"]
        lower_path = file_path.lower()
        if lower_path.endswith(".png"):
            mime_type = "image/png"
        elif lower_path.endswith(".webp"):
            mime_type = "image/webp"
        elif lower_path.endswith(".jpg") or lower_path.endswith(".jpeg"):
            mime_type = "image/jpeg"
        else:
            mime_type = fallback_mime

        file_res = requests.get(
            f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}",
            timeout=30,
        )
        if not file_res.ok:
            print(f"Telegram file download error: {file_res.status_code}", flush=True)
            return None, None

        b64_data = base64.b64encode(file_res.content).decode("utf-8")
        return b64_data, mime_type
    except Exception as e:
        print(f"Error downloading Telegram image: {e}", flush=True)
        return None, None


def handle_ai_reply(
    chat_id,
    user_name,
    user_text,
    reply_to_id=None,
    image_file_id=None,
    image_mime_type="image/jpeg",
):
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

        user_parts = [
            {
                "text": f"[User Name: {user_name}]\nUser Message: {user_text}"
            }
        ]

        if image_file_id:
            b64_data, detected_mime = download_telegram_image(
                image_file_id, image_mime_type
            )
            if not b64_data:
                send_telegram_message(
                    chat_id,
                    f"Salam hormat {user_name}, maaf, saya gagal memuat turun gambar chart tersebut. "
                    "Sila cuba muat naik semula gambar tersebut.",
                    reply_to_id,
                )
                return

            user_parts.append(
                {
                    "inlineData": {
                        "mimeType": detected_mime,
                        "data": b64_data,
                    }
                }
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
                    "parts": user_parts,
                }
            ],
        }

        res = requests.post(gemini_url, json=payload, timeout=45)
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
