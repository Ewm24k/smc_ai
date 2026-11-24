import base64
import math
import os
import threading
import time
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

MARKET_CACHE = {}
CACHE_TTL_SEC = 5


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


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


# ==============================================================================
# HIDDEN GG SMC ENGINE (Matches BigBeluga / GG SMC v6 Logic, up to 5000 bars)
# ==============================================================================

def resample_candles(candles, group_size):
    if group_size <= 1 or len(candles) < group_size:
        return candles
    out = []
    for i in range(0, len(candles) - group_size + 1, group_size):
        chunk = candles[i : i + group_size]
        out.append(
            {
                "time": chunk[0]["time"],
                "open": chunk[0]["open"],
                "high": max(c["high"] for c in chunk),
                "low": min(c["low"] for c in chunk),
                "close": chunk[-1]["close"],
                "volume": sum(c["volume"] for c in chunk),
            }
        )
    return out


def fetch_yahoo_candles(ticker, tf):
    tf_map = {
        "1m": ("1m", "7d", 1),
        "3m": ("1m", "7d", 3),
        "5m": ("5m", "1mo", 1),
        "15m": ("15m", "1mo", 1),
        "1h": ("1h", "6mo", 1),
        "4h": ("1h", "6mo", 4),
        "1d": ("1d", "5y", 1),
    }
    y_int, y_range, resample_n = tf_map.get(tf, ("5m", "1mo", 1))
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(
        url,
        params={"interval": y_int, "range": y_range, "includePrePost": "true"},
        headers=headers,
        timeout=15,
    )
    res.raise_for_status()
    data = res.json()
    result = data["chart"]["result"][0]
    timestamps = result.get("timestamp", [])
    quote = result["indicators"]["quote"][0]
    opens = quote.get("open", [])
    highs = quote.get("high", [])
    lows = quote.get("low", [])
    closes = quote.get("close", [])
    vols = quote.get("volume", [])

    candles = []
    seen_times = set()
    for i, ts in enumerate(timestamps):
        o = opens[i] if i < len(opens) else None
        h = highs[i] if i < len(highs) else None
        l = lows[i] if i < len(lows) else None
        c = closes[i] if i < len(closes) else None
        v = vols[i] if i < len(vols) and vols[i] is not None else 1.0
        if None in (o, h, l, c):
            continue
        t_int = int(ts)
        if t_int in seen_times:
            continue
        seen_times.add(t_int)
        candles.append(
            {
                "time": t_int,
                "open": float(o),
                "high": float(h),
                "low": float(l),
                "close": float(c),
                "volume": float(v) if float(v) > 0 else 1.0,
            }
        )

    candles.sort(key=lambda x: x["time"])
    if resample_n > 1:
        candles = resample_candles(candles, resample_n)
    return candles[-5000:]


def fetch_binance_candles(symbol, tf):
    valid_tf = tf if tf in ("1m", "3m", "5m", "15m", "1h", "4h", "1d") else "5m"
    url = "https://data-api.binance.vision/api/v3/klines"
    res = requests.get(
        url,
        params={"symbol": symbol, "interval": valid_tf, "limit": 1000},
        timeout=12,
    )
    res.raise_for_status()
    rows = res.json()
    candles = []
    seen = set()
    for r in rows:
        t_sec = int(r[0] // 1000)
        if t_sec in seen:
            continue
        seen.add(t_sec)
        candles.append(
            {
                "time": t_sec,
                "open": float(r[1]),
                "high": float(r[2]),
                "low": float(r[3]),
                "close": float(r[4]),
                "volume": float(r[5]) if float(r[5]) > 0 else 1.0,
            }
        )
    candles.sort(key=lambda x: x["time"])
    return candles


def get_market_candles(symbol, tf):
    key = f"{symbol}_{tf}"
    now = time.time()
    cached = MARKET_CACHE.get(key)
    if cached and (now - cached["ts"] < CACHE_TTL_SEC):
        return cached["candles"], cached["source"]

    symbol_upper = symbol.upper()
    candles = []
    source = ""

    if symbol_upper == "XAUUSD":
        try:
            candles = fetch_yahoo_candles("GC=F", tf)
            source = "Gold Futures (GC=F)"
        except Exception as e:
            print(f"Yahoo GC=F error: {e}", flush=True)
        if len(candles) < 30:
            candles = fetch_binance_candles("PAXGUSDT", tf)
            source = "PAXG/USDT Gold Spot (Fallback)"
    elif symbol_upper in ("EURUSD", "GBPUSD", "USDJPY"):
        candles = fetch_yahoo_candles(f"{symbol_upper}=X", tf)
        source = f"FX {symbol_upper}"
    else:
        candles = fetch_binance_candles(symbol_upper, tf)
        source = f"Spot {symbol_upper}"

    if len(candles) >= 30:
        MARKET_CACHE[key] = {"ts": now, "candles": candles, "source": source}
    return candles, source


def format_vol(val):
    if val >= 1_000_000:
        return f"{val / 1_000_000:.2f}M"
    if val >= 1_000:
        return f"{val / 1_000:.2f}K"
    return f"{round(val, 2)}"


def compute_atr(candles, period=200):
    n = len(candles)
    tr = [0.0] * n
    for i in range(n):
        h = candles[i]["high"]
        l = candles[i]["low"]
        if i == 0:
            tr[i] = h - l
        else:
            pc = candles[i - 1]["close"]
            tr[i] = max(h - l, abs(h - pc), abs(l - pc))

    atr = [0.0] * n
    rma = tr[0]
    for i in range(n):
        p = min(i + 1, period)
        alpha = 1.0 / p
        rma = alpha * tr[i] + (1.0 - alpha) * rma
        atr[i] = rma
    return atr


def check_overlap_obs(bull_obs, bear_obs):
    def overlap_pair(a, b):
        return (
            (a["btm"] > b["btm"] and a["btm"] < b["top"])
            or (a["top"] < b["top"] and a["btm"] > b["btm"])
            or (a["top"] > b["top"] and a["btm"] < b["btm"])
            or (a["top"] < b["top"] and a["top"] > b["btm"])
        )

    for grp in (bull_obs, bear_obs):
        if len(grp) > 1:
            curr = grp[0]
            for i in range(len(grp) - 1, 0, -1):
                if overlap_pair(grp[i], curr):
                    grp.pop(i)

    if bull_obs and bear_obs:
        curr_b = bear_obs[0]
        for i in range(len(bull_obs) - 1, -1, -1):
            if overlap_pair(bull_obs[i], curr_b):
                bull_obs.pop(i)

    if bull_obs and bear_obs:
        curr_u = bull_obs[0]
        for i in range(len(bear_obs) - 1, -1, -1):
            if overlap_pair(bear_obs[i], curr_u):
                bear_obs.pop(i)


def check_overlap_fvgs(bl_fvgs, br_fvgs):
    def overlap_pair(a, b):
        return (
            (a["btm"] > b["btm"] and a["btm"] < b["top"])
            or (a["top"] < b["top"] and a["btm"] > b["btm"])
            or (a["top"] > b["top"] and a["btm"] < b["btm"])
            or (a["top"] < b["top"] and a["top"] > b["btm"])
        )

    for grp in (bl_fvgs, br_fvgs):
        if len(grp) > 1:
            curr = grp[0]
            for i in range(len(grp) - 1, 0, -1):
                if overlap_pair(grp[i], curr):
                    grp.pop(i)

    if bl_fvgs and br_fvgs:
        curr_b = br_fvgs[0]
        for i in range(len(bl_fvgs) - 1, -1, -1):
            if overlap_pair(bl_fvgs[i], curr_b):
                bl_fvgs.pop(i)

    if bl_fvgs and br_fvgs:
        curr_u = bl_fvgs[0]
        for i in range(len(br_fvgs) - 1, -1, -1):
            if overlap_pair(br_fvgs[i], curr_u):
                br_fvgs.pop(i)


def update_ob_umt(ob_item):
    if ob_item["dir"] == 1:
        if ob_item["move"] == 1:
            ob_item["blPOS"] += 1
            ob_item["move"] = 2
        elif ob_item["move"] == 2:
            ob_item["blPOS"] += 1
            ob_item["move"] = 3
        else:
            ob_item["brPOS"] += 1
            ob_item["move"] = 1
    else:
        if ob_item["move"] == 1:
            ob_item["brPOS"] += 1
            ob_item["move"] = 2
        elif ob_item["move"] == 2:
            ob_item["brPOS"] += 1
            ob_item["move"] = 3
        else:
            ob_item["blPOS"] += 1
            ob_item["move"] = 1


def run_gg_smc(candles, mslen=5, swing_limit=100, ob_last=5, fvg_num=5):
    n = len(candles)
    if n < 20:
        return {"structures": [], "order_blocks": [], "fvgs": [], "trend": 0, "last_event": "N/A"}

    atr = compute_atr(candles, 200)

    def find_ext(cur_i, anchor_idx, use_max, useob):
        span = (cur_i - anchor_idx) - 1
        end_k = span if span > 0 else (cur_i - anchor_idx)
        end_k = max(0, min(end_k, cur_i))
        best_idx = 0
        if use_max:
            mx = -1e18
            for k in range(end_k + 1):
                h = candles[cur_i - k]["high"]
                if h > mx:
                    mx = h
                    best_idx = k
            if useob and (cur_i - (best_idx + 1)) >= 0:
                if candles[cur_i - (best_idx + 1)]["high"] > candles[cur_i - best_idx]["high"]:
                    best_idx += 1
        else:
            mn = 1e18
            for k in range(end_k + 1):
                l = candles[cur_i - k]["low"]
                if l < mn:
                    mn = l
                    best_idx = k
            if useob and (cur_i - (best_idx + 1)) >= 0:
                if candles[cur_i - (best_idx + 1)]["low"] < candles[cur_i - best_idx]["low"]:
                    best_idx += 1
        return min(best_idx, cur_i)

    ms_start = 0
    ms_trend = 0
    ms_bos = None
    ms_choch = None
    ms_loc = 0
    ms_temp = 0
    ms_main = None
    ms_xloc = 0
    ms_txt = ""

    up_lvl = None
    dn_lvl = None
    php = []
    phn = []
    plp = []
    pln = []

    bldw = []
    brdw = []
    blob = []
    brob = []
    bl_fvg = []
    br_fvg = []

    for i in range(n):
        h = candles[i]["high"]
        l = candles[i]["low"]
        c = candles[i]["close"]
        o = candles[i]["open"]
        c1 = candles[i - 1]["close"] if i >= 1 else c
        o1 = candles[i - 1]["open"] if i >= 1 else o

        if i >= mslen * 2:
            c_idx = i - mslen
            win_h = [candles[j]["high"] for j in range(c_idx - mslen, c_idx + mslen + 1)]
            win_l = [candles[j]["low"] for j in range(c_idx - mslen, c_idx + mslen + 1)]
            ch = candles[c_idx]["high"]
            cl = candles[c_idx]["low"]
            if ch == max(win_h) and win_h.count(ch) == 1:
                phn.insert(0, c_idx)
                php.insert(0, ch)
            if cl == min(win_l) and win_l.count(cl) == 1:
                pln.insert(0, c_idx)
                plp.insert(0, cl)

        if php and h > php[0]:
            php.clear()
            phn.clear()
        if plp and l < plp[0]:
            plp.clear()
            pln.clear()

        crossup = False
        crossdn = False
        if up_lvl is None:
            up_lvl = h
        if dn_lvl is None:
            dn_lvl = l
        if h > up_lvl:
            up_lvl = h
            dn_lvl = l
            crossup = True
        if l < dn_lvl:
            up_lvl = h
            dn_lvl = l
            crossdn = True

        idbull = find_ext(i, ms_loc, False, True)
        idbear = find_ext(i, ms_loc, True, True)
        ob_idx_bear = i - idbear
        ob_idx_bull = i - idbull
        atr_bear = atr[ob_idx_bear]
        atr_bull = atr[ob_idx_bull]

        btm_p = max(candles[ob_idx_bear]["low"], candles[ob_idx_bear]["high"] - atr_bear)
        top_p = min(candles[ob_idx_bull]["high"], candles[ob_idx_bull]["low"] + atr_bull)

        def make_ob(is_bull, cords, ob_i):
            c_bar = candles[ob_i]
            return {
                "bull": is_bull,
                "top": cords if is_bull else c_bar["high"],
                "btm": c_bar["low"] if is_bull else cords,
                "avg": (cords + c_bar["low"]) / 2.0 if is_bull else (c_bar["high"] + cords) / 2.0,
                "x1": ob_i,
                "vol": c_bar["volume"],
                "dir": 1 if c_bar["close"] > c_bar["open"] else -1,
                "move": 1,
                "blPOS": 1,
                "brPOS": 1,
            }

        if ms_start == 0:
            ms_bos = h
            ms_choch = l
            ms_loc = i
            ms_temp = i
            ms_xloc = i
            ms_start = 1
            bldw.insert(0, {"x1": i, "x2": i, "y": h, "txt": "CHoCH", "dir": 1, "style": "dashed"})
            brdw.insert(0, {"x1": i, "x2": i, "y": l, "txt": "CHoCH", "dir": -1, "style": "dashed"})

        elif ms_start == 1:
            if l <= ms_choch and c >= ms_choch:
                ms_choch = l
                ms_xloc = i
                brdw[0]["x2"] = i
                brdw[0]["style"] = "dotted"
                brdw[0]["txt"] = "x"
                brdw.insert(0, {"x1": i, "x2": i, "y": l, "txt": "CHoCH", "dir": -1, "style": "dashed"})
            elif h >= ms_bos and c <= ms_bos:
                ms_bos = h
                ms_xloc = i
                bldw[0]["x2"] = i
                bldw[0]["style"] = "dotted"
                bldw[0]["txt"] = "x"
                bldw.insert(0, {"x1": i, "x2": i, "y": h, "txt": "CHoCH", "dir": 1, "style": "dashed"})
            elif c <= ms_choch:
                ms_txt = "CHoCH"
                blob.insert(0, make_ob(True, top_p, ob_idx_bull))
                ms_trend = -1
                ms_choch = ms_bos
                ms_bos = None
                ms_start = 2
                ms_loc = i
                ms_main = l
                ms_temp = i
                ms_xloc = i
                brdw[0]["x2"] = i
                brdw[0]["style"] = "solid"
            elif c >= ms_bos:
                ms_txt = "CHoCH"
                brob.insert(0, make_ob(False, btm_p, ob_idx_bear))
                ms_trend = 1
                ms_bos = None
                ms_start = 2
                ms_loc = i
                ms_main = h
                ms_temp = i
                ms_xloc = i
                bldw[0]["x2"] = i
                bldw[0]["style"] = "solid"

        elif ms_start == 2:
            if ms_trend == -1:
                if l <= ms_main:
                    ms_main = l
                    ms_temp = i

                if i % mslen == 0 and ms_bos is not None and php:
                    if php[0] < ms_choch:
                        ms_choch = php[0]
                        ms_loc = phn[0]
                        ms_xloc = phn[0]
                        ms_temp = phn[0]
                        bldw[0]["x1"] = phn[0]
                        bldw[0]["x2"] = i
                        bldw[0]["y"] = php[0]

                if ms_bos is None:
                    if crossup and c > o and c1 > o1:
                        ms_bos = ms_main
                        ms_loc = ms_temp
                        ms_xloc = ms_loc
                        brdw.insert(0, {
                            "x1": ms_loc,
                            "x2": i,
                            "y": candles[ms_loc]["low"],
                            "txt": "BOS",
                            "dir": -1,
                            "style": "dashed",
                        })

                if ms_bos is not None:
                    brdw[0]["x2"] = i
                bldw[0]["x2"] = i

                if ms_bos is not None and l <= ms_bos and c >= ms_bos:
                    ms_bos = l
                    brdw[0]["x2"] = i
                    brdw[0]["style"] = "dotted"
                    brdw[0]["txt"] = "x"
                    brdw.insert(0, {"x1": i, "x2": i, "y": l, "txt": "BOS", "dir": -1, "style": "dashed"})
                    ms_xloc = i
                elif ms_bos is not None and c <= ms_bos:
                    ms_txt = "BOS"
                    brob.insert(0, make_ob(False, btm_p, ob_idx_bear))
                    ext_id = find_ext(i, ms_loc, True, False)
                    ms_xloc = i
                    ms_bos = None
                    ms_choch = candles[i - ext_id]["high"]
                    ms_loc = i - ext_id
                    brdw[0]["x2"] = i
                    brdw[0]["style"] = "solid"
                    bldw[0]["x1"] = i - ext_id
                    bldw[0]["x2"] = i
                    bldw[0]["y"] = ms_choch

                if h >= ms_choch and c <= ms_choch:
                    ms_choch = h
                    ms_xloc = i
                    bldw[0]["x2"] = i
                    bldw[0]["style"] = "dotted"
                    bldw[0]["txt"] = "x"
                    bldw.insert(0, {"x1": i, "x2": i, "y": h, "txt": "CHoCH", "dir": 1, "style": "dashed"})
                elif c >= ms_choch:
                    ms_txt = "CHoCH"
                    blob.insert(0, make_ob(True, top_p, ob_idx_bull))
                    ext_id = find_ext(i, ms_loc, False, False)
                    if ms_bos is None:
                        ms_choch = candles[i - ext_id]["low"]
                        brdw.insert(0, {
                            "x1": ms_temp,
                            "x2": i,
                            "y": ms_choch,
                            "txt": "CHoCH",
                            "dir": -1,
                            "style": "dashed",
                        })
                    else:
                        ms_choch = ms_bos
                        brdw[0]["x2"] = i
                        brdw[0]["y"] = ms_choch
                        brdw[0]["txt"] = "CHoCH"
                    ms_bos = None
                    ms_main = h
                    ms_trend = 1
                    ms_loc = i
                    ms_temp = i
                    ms_xloc = i
                    bldw[0]["x2"] = i
                    bldw[0]["txt"] = "CHoCH"
                    bldw[0]["style"] = "solid"

            elif ms_trend == 1:
                if h >= ms_main:
                    ms_main = h
                    ms_temp = i

                if ms_bos is None:
                    if crossdn and c < o and c1 < o1:
                        ms_bos = ms_main
                        ms_loc = ms_temp
                        ms_xloc = ms_loc
                        bldw.insert(0, {
                            "x1": ms_loc,
                            "x2": i,
                            "y": candles[ms_loc]["high"],
                            "txt": "BOS",
                            "dir": 1,
                            "style": "dashed",
                        })

                if i % mslen == 0 and ms_bos is not None and plp:
                    if plp[0] > ms_choch:
                        ms_choch = plp[0]
                        ms_loc = pln[0]
                        ms_xloc = pln[0]
                        ms_temp = pln[0]
                        brdw[0]["x1"] = pln[0]
                        brdw[0]["x2"] = i
                        brdw[0]["y"] = plp[0]

                if ms_bos is not None:
                    bldw[0]["x2"] = i
                brdw[0]["x2"] = i

                if ms_bos is not None and h >= ms_bos and c <= ms_bos:
                    ms_bos = h
                    bldw[0]["x2"] = i
                    bldw[0]["style"] = "dotted"
                    bldw[0]["txt"] = "x"
                    bldw.insert(0, {"x1": i, "x2": i, "y": h, "txt": "BOS", "dir": 1, "style": "dashed"})
                    ms_xloc = i
                elif ms_bos is not None and c >= ms_bos:
                    ms_txt = "BOS"
                    blob.insert(0, make_ob(True, top_p, ob_idx_bull))
                    ext_id = find_ext(i, ms_loc, False, False)
                    ms_xloc = i
                    ms_bos = None
                    ms_choch = candles[i - ext_id]["low"]
                    ms_loc = i - ext_id
                    bldw[0]["x2"] = i
                    bldw[0]["style"] = "solid"
                    brdw[0]["x1"] = i - ext_id
                    brdw[0]["x2"] = i
                    brdw[0]["y"] = ms_choch

                if l <= ms_choch and c >= ms_choch:
                    ms_choch = l
                    ms_xloc = i
                    brdw[0]["x2"] = i
                    brdw[0]["style"] = "dotted"
                    brdw[0]["txt"] = "x"
                    brdw.insert(0, {"x1": i, "x2": i, "y": l, "txt": "CHoCH", "dir": -1, "style": "dashed"})
                elif c <= ms_choch:
                    ms_txt = "CHoCH"
                    brob.insert(0, make_ob(False, btm_p, ob_idx_bear))
                    ext_id = find_ext(i, ms_loc, True, False)
                    if ms_bos is None:
                        ms_choch = candles[i - ext_id]["high"]
                        bldw.insert(0, {
                            "x1": ms_temp,
                            "x2": i,
                            "y": ms_choch,
                            "txt": "CHoCH",
                            "dir": 1,
                            "style": "dashed",
                        })
                    else:
                        ms_choch = ms_bos
                        bldw[0]["x2"] = i
                        bldw[0]["y"] = ms_choch
                        bldw[0]["txt"] = "CHoCH"
                    ms_bos = None
                    ms_main = l
                    ms_trend = -1
                    ms_loc = i
                    ms_temp = i
                    ms_xloc = i
                    brdw[0]["x2"] = i
                    brdw[0]["txt"] = "CHoCH"
                    brdw[0]["style"] = "solid"

        # OB mitigation (confirmed bars only, matching barstate.isconfirmed)
        if i < n - 1:
            for idx_ob in range(len(blob) - 1, -1, -1):
                if min(c, o) < blob[idx_ob]["btm"]:
                    blob.pop(idx_ob)
            for idx_ob in range(len(brob) - 1, -1, -1):
                if max(c, o) > brob[idx_ob]["top"]:
                    brob.pop(idx_ob)
            check_overlap_obs(blob, brob)

        for item in blob:
            update_ob_umt(item)
        for item in brob:
            update_ob_umt(item)

        # FVG detection & mitigation
        if i >= 3:
            h2 = candles[i - 3]["high"]
            l2 = candles[i - 3]["low"]
            l_prev = candles[i - 1]["low"]
            h_prev = candles[i - 1]["high"]
            c_mid = candles[i - 2]["close"]
            h_mid = candles[i - 2]["high"]
            l_mid = candles[i - 2]["low"]

            if l_prev > h2 and c_mid > l_mid:
                bl_fvg.insert(0, {
                    "bull": True,
                    "top": l_prev,
                    "btm": h2,
                    "mid": (l_prev + h2) / 2.0,
                    "x1": i - 3,
                })
            if l2 > h_prev and c_mid < h_mid:
                br_fvg.insert(0, {
                    "bull": False,
                    "top": l2,
                    "btm": h_prev,
                    "mid": (l2 + h_prev) / 2.0,
                    "x1": i - 3,
                })

        for idx_f in range(len(bl_fvg) - 1, -1, -1):
            if min(c, o) < bl_fvg[idx_f]["btm"]:
                bl_fvg.pop(idx_f)
        for idx_f in range(len(br_fvg) - 1, -1, -1):
            if max(c, o) > br_fvg[idx_f]["top"]:
                br_fvg.pop(idx_f)
        check_overlap_fvgs(bl_fvg, br_fvg)

    # Slice latest 1000 candles for fast rendering while preserving full 5000-bar structure coordinates
    view_start = max(0, n - 1000)

    final_obs = []
    for grp in (blob[:ob_last], brob[:ob_last]):
        tot_v = sum(item["vol"] for item in grp) or 1.0
        for item in grp:
            pct = math.floor((item["vol"] / tot_v) * 100)
            rel_x1 = max(0, item["x1"] - view_start)
            rel_bl = min((n - 1) - view_start, max(0, (item["x1"] + item["blPOS"]) - view_start))
            rel_br = min((n - 1) - view_start, max(0, (item["x1"] + item["brPOS"]) - view_start))
            final_obs.append({
                "bull": item["bull"],
                "top": item["top"],
                "btm": item["btm"],
                "avg": item["avg"],
                "x1": rel_x1,
                "x2": (n - 1) - view_start,
                "xlocbl": rel_bl,
                "xlocbr": rel_br,
                "vol_label": f"{format_vol(item['vol'])} ({pct}%)",
            })

    final_fvgs = []
    for item in bl_fvg[:fvg_num] + br_fvg[:fvg_num]:
        if item["x1"] >= view_start - 100:
            final_fvgs.append({
                "bull": item["bull"],
                "top": item["top"],
                "btm": item["btm"],
                "mid": item["mid"],
                "x1": max(0, item["x1"] - view_start),
                "x2": (n - 1) - view_start,
            })

    structures = []
    for s in bldw[:swing_limit] + brdw[:swing_limit]:
        if s["x2"] >= view_start:
            structures.append({
                "x1": max(0, s["x1"] - view_start),
                "x2": s["x2"] - view_start,
                "y": s["y"],
                "txt": s["txt"],
                "dir": s["dir"],
                "style": s["style"],
            })

    return {
        "candles": candles[view_start:],
        "structures": structures,
        "order_blocks": final_obs,
        "fvgs": final_fvgs,
        "trend": ms_trend,
        "last_event": ms_txt or "CHoCH",
    }


@app.route("/api/gg-smc", methods=["GET"])
def api_gg_smc():
    symbol = request.args.get("symbol", "XAUUSD").strip().upper()
    tf = request.args.get("tf", "5m").strip().lower()
    if tf not in ("1m", "3m", "5m", "15m", "1h", "4h", "1d"):
        tf = "5m"

    try:
        candles, source = get_market_candles(symbol, tf)
        if len(candles) < 20:
            return jsonify({"ok": False, "error": "Insufficient market candles"}), 502

        smc = run_gg_smc(candles)
        last_c = candles[-1]
        prev_c = candles[-2]
        chg_pct = ((last_c["close"] - prev_c["close"]) / prev_c["close"]) * 100 if prev_c["close"] else 0.0

        return jsonify({
            "ok": True,
            "symbol": symbol,
            "tf": tf,
            "source": source,
            "price": last_c["close"],
            "change_pct": round(chg_pct, 3),
            "candles": smc["candles"],
            "structures": smc["structures"],
            "order_blocks": smc["order_blocks"],
            "fvgs": smc["fvgs"],
            "trend": smc["trend"],
            "last_event": smc["last_event"],
        }), 200
    except Exception as e:
        print(f"API /api/gg-smc error: {e}", flush=True)
        return jsonify({"ok": False, "error": str(e)}), 500


# ==============================================================================
# TELEGRAM WEBHOOK & AI BOT
# ==============================================================================

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
