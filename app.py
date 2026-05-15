from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import os, hashlib, datetime, pytz, requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__, static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "ms-hokej-2026-tajny-klic")
CORS(app, supports_credentials=True)

DATABASE_URL = os.environ.get("DATABASE_URL")  # Supabase connection string
ADMIN = "Admin"
CEST  = pytz.timezone("Europe/Prague")

# ── ZÁPASY ───────────────────────────────────────────────────────────────────

GAMES = [
    {"id":"a1",  "date":"2026-05-15","time":"16:20","home":"Finsko",    "away":"Německo",     "group":"A"},
    {"id":"a2",  "date":"2026-05-15","time":"20:20","home":"USA",       "away":"Lotyšsko",    "group":"A"},
    {"id":"a3",  "date":"2026-05-16","time":"16:20","home":"Švýcarsko", "away":"Maďarsko",    "group":"A"},
    {"id":"a4",  "date":"2026-05-16","time":"20:20","home":"Rakousko",  "away":"V. Británie", "group":"A"},
    {"id":"a5",  "date":"2026-05-17","time":"12:20","home":"Finsko",    "away":"Lotyšsko",    "group":"A"},
    {"id":"a6",  "date":"2026-05-17","time":"16:20","home":"USA",       "away":"Maďarsko",    "group":"A"},
    {"id":"a7",  "date":"2026-05-18","time":"12:20","home":"Finsko",    "away":"USA",         "group":"A"},
    {"id":"a8",  "date":"2026-05-18","time":"16:20","home":"Německo",   "away":"V. Británie", "group":"A"},
    {"id":"a9",  "date":"2026-05-19","time":"12:20","home":"Lotyšsko",  "away":"Maďarsko",    "group":"A"},
    {"id":"a10", "date":"2026-05-19","time":"16:20","home":"Švýcarsko", "away":"Rakousko",    "group":"A"},
    {"id":"a11", "date":"2026-05-20","time":"12:20","home":"Německo",   "away":"Maďarsko",    "group":"A"},
    {"id":"a12", "date":"2026-05-20","time":"16:20","home":"USA",       "away":"V. Británie", "group":"A"},
    {"id":"a13", "date":"2026-05-21","time":"12:20","home":"Finsko",    "away":"Švýcarsko",   "group":"A"},
    {"id":"a14", "date":"2026-05-21","time":"16:20","home":"Lotyšsko",  "away":"Rakousko",    "group":"A"},
    {"id":"a15", "date":"2026-05-22","time":"12:20","home":"Německo",   "away":"Lotyšsko",    "group":"A"},
    {"id":"a16", "date":"2026-05-22","time":"16:20","home":"Maďarsko",  "away":"V. Británie", "group":"A"},
    {"id":"a17", "date":"2026-05-23","time":"12:20","home":"USA",       "away":"Rakousko",    "group":"A"},
    {"id":"a18", "date":"2026-05-23","time":"16:20","home":"Švýcarsko", "away":"Německo",     "group":"A"},
    {"id":"a19", "date":"2026-05-24","time":"12:20","home":"Finsko",    "away":"Maďarsko",    "group":"A"},
    {"id":"a20", "date":"2026-05-24","time":"16:20","home":"Lotyšsko",  "away":"V. Británie", "group":"A"},
    {"id":"a21", "date":"2026-05-25","time":"12:20","home":"Německo",   "away":"Rakousko",    "group":"A"},
    {"id":"a22", "date":"2026-05-26","time":"16:20","home":"Finsko",    "away":"Švýcarsko",   "group":"A"},
    {"id":"a23", "date":"2026-05-26","time":"16:20","home":"USA",       "away":"Lotyšsko",    "group":"A"},
    {"id":"a24", "date":"2026-05-26","time":"20:20","home":"Maďarsko",  "away":"Rakousko",    "group":"A"},
    {"id":"a25", "date":"2026-05-26","time":"20:20","home":"Německo",   "away":"V. Británie", "group":"A"},
    {"id":"b1",  "date":"2026-05-15","time":"12:20","home":"Kanada",    "away":"Švédsko",    "group":"B"},
    {"id":"b2",  "date":"2026-05-15","time":"16:20","home":"Česko",     "away":"Dánsko",     "group":"B"},
    {"id":"b3",  "date":"2026-05-16","time":"12:20","home":"Slovensko", "away":"Itálie",     "group":"B"},
    {"id":"b4",  "date":"2026-05-16","time":"16:20","home":"Norsko",    "away":"Slovinsko",  "group":"B"},
    {"id":"b5",  "date":"2026-05-17","time":"12:20","home":"Kanada",    "away":"Norsko",     "group":"B"},
    {"id":"b6",  "date":"2026-05-17","time":"20:20","home":"Švédsko",   "away":"Dánsko",     "group":"B"},
    {"id":"b7",  "date":"2026-05-18","time":"12:20","home":"Česko",     "away":"Švédsko",    "group":"B"},
    {"id":"b8",  "date":"2026-05-18","time":"20:20","home":"Slovensko", "away":"Slovinsko",  "group":"B"},
    {"id":"b9",  "date":"2026-05-19","time":"12:20","home":"Norsko",    "away":"Itálie",     "group":"B"},
    {"id":"b10", "date":"2026-05-19","time":"20:20","home":"Kanada",    "away":"Dánsko",     "group":"B"},
    {"id":"b11", "date":"2026-05-20","time":"12:20","home":"Švédsko",   "away":"Slovensko",  "group":"B"},
    {"id":"b12", "date":"2026-05-20","time":"20:20","home":"Česko",     "away":"Norsko",     "group":"B"},
    {"id":"b13", "date":"2026-05-21","time":"12:20","home":"Dánsko",    "away":"Slovinsko",  "group":"B"},
    {"id":"b14", "date":"2026-05-21","time":"20:20","home":"Kanada",    "away":"Itálie",     "group":"B"},
    {"id":"b15", "date":"2026-05-22","time":"12:20","home":"Česko",     "away":"Slovensko",  "group":"B"},
    {"id":"b16", "date":"2026-05-22","time":"20:20","home":"Švédsko",   "away":"Norsko",     "group":"B"},
    {"id":"b17", "date":"2026-05-23","time":"12:20","home":"Dánsko",    "away":"Itálie",     "group":"B"},
    {"id":"b18", "date":"2026-05-23","time":"20:20","home":"Slovensko", "away":"Česko",      "group":"B"},
    {"id":"b19", "date":"2026-05-24","time":"12:20","home":"Kanada",    "away":"Slovinsko",  "group":"B"},
    {"id":"b20", "date":"2026-05-24","time":"20:20","home":"Švédsko",   "away":"Itálie",     "group":"B"},
    {"id":"b21", "date":"2026-05-25","time":"12:20","home":"Norsko",    "away":"Dánsko",     "group":"B"},
    {"id":"b22", "date":"2026-05-26","time":"12:20","home":"Kanada",    "away":"Česko",      "group":"B"},
    {"id":"b23", "date":"2026-05-26","time":"12:20","home":"Švédsko",   "away":"Slovinsko",  "group":"B"},
    {"id":"b24", "date":"2026-05-26","time":"20:20","home":"Slovensko", "away":"Norsko",     "group":"B"},
    {"id":"b25", "date":"2026-05-26","time":"20:20","home":"Dánsko",    "away":"Itálie",     "group":"B"},
]

GAMES_BY_ID = {g["id"]: g for g in GAMES}

def game_kickoff_cest(game):
    naive = datetime.datetime.strptime(f"{game['date']} {game['time']}", "%Y-%m-%d %H:%M")
    return CEST.localize(naive)

def is_tippable(game):
    return datetime.datetime.now(CEST) < game_kickoff_cest(game) - datetime.timedelta(hours=1)

# ── DB ────────────────────────────────────────────────────────────────────────

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    name     TEXT PRIMARY KEY,
                    pin_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS tips (
                    user_name  TEXT NOT NULL,
                    game_id    TEXT NOT NULL,
                    home_score INTEGER NOT NULL,
                    away_score INTEGER NOT NULL,
                    outcome    TEXT NOT NULL DEFAULT 'REG',
                    updated_at TIMESTAMP DEFAULT NOW(),
                    PRIMARY KEY (user_name, game_id)
                );
                CREATE TABLE IF NOT EXISTS results (
                    game_id    TEXT PRIMARY KEY,
                    home_score INTEGER NOT NULL,
                    away_score INTEGER NOT NULL,
                    outcome    TEXT NOT NULL DEFAULT 'REG',
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)
        conn.commit()

try:
    init_db()
except Exception as e:
    print(f"DB init error: {e}")

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

# ── BODOVÁNÍ ──────────────────────────────────────────────────────────────────

def calc_points(tip, result):
    if not tip or not result:
        return 0
    th, ta, to = tip["home_score"], tip["away_score"], tip.get("outcome","REG")
    rh, ra, ro = result["home_score"], result["away_score"], result.get("outcome","REG")
    if th == rh and ta == ra and to == ro:
        return 3
    def w(h, a): return "H" if h>a else ("A" if h<a else "D")
    return 1 if w(th,ta) == w(rh,ra) and w(th,ta) != "D" else 0

# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.route("/api/register", methods=["POST"])
def register():
    d = request.json
    name = (d.get("name") or "").strip()
    pin  = d.get("pin","")
    if not name or len(pin) < 2:
        return jsonify(error="Zadej jméno a PIN (min. 2 znaky)"), 400
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM users WHERE name=%s", (name,))
                if cur.fetchone():
                    return jsonify(error="Jméno je obsazeno"), 409
                cur.execute("INSERT INTO users (name, pin_hash) VALUES (%s,%s)", (name, hash_pin(pin)))
            conn.commit()
    except Exception as e:
        return jsonify(error=f"Chyba DB: {str(e)}"), 500
    session["user"] = name
    return jsonify(ok=True, name=name)

@app.route("/api/login", methods=["POST"])
def login():
    d = request.json
    name = (d.get("name") or "").strip()
    pin  = d.get("pin","")
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE name=%s", (name,))
                u = cur.fetchone()
    except Exception as e:
        return jsonify(error=f"Chyba DB: {str(e)}"), 500
    if not u:
        return jsonify(error="Hráč nenalezen — zaregistruj se"), 404
    if u["pin_hash"] != hash_pin(pin):
        return jsonify(error="Špatný PIN"), 401
    session["user"] = name
    return jsonify(ok=True, name=name)

@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify(ok=True)

@app.route("/api/me")
def me():
    u = session.get("user")
    if not u: return jsonify(error="Nepřihlášen"), 401
    return jsonify(name=u)

# ── TIPY ──────────────────────────────────────────────────────────────────────

@app.route("/api/tips")
def get_tips():
    u = session.get("user")
    if not u: return jsonify(error="Nepřihlášen"), 401
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT game_id, home_score, away_score, outcome FROM tips WHERE user_name=%s", (u,))
            rows = cur.fetchall()
    return jsonify(tips={r["game_id"]: dict(r) for r in rows})

@app.route("/api/tips", methods=["POST"])
def save_tip():
    u = session.get("user")
    if not u: return jsonify(error="Nepřihlášen"), 401
    d = request.json
    gid     = d.get("game_id")
    home    = d.get("home_score")
    away    = d.get("away_score")
    outcome = d.get("outcome","REG")
    if gid is None or home is None or away is None:
        return jsonify(error="Chybí data"), 400
    if outcome not in ("REG","OT","SO"):
        return jsonify(error="Neplatný outcome"), 400
    game = GAMES_BY_ID.get(gid)
    if not game:
        return jsonify(error="Neznámý zápas"), 404
    if not is_tippable(game):
        return jsonify(error="Tipování uzavřeno (méně než 1 hodina do začátku)"), 403
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tips (user_name, game_id, home_score, away_score, outcome, updated_at)
                VALUES (%s,%s,%s,%s,%s,NOW())
                ON CONFLICT (user_name, game_id) DO UPDATE SET
                    home_score=EXCLUDED.home_score, away_score=EXCLUDED.away_score,
                    outcome=EXCLUDED.outcome, updated_at=NOW()
            """, (u, gid, int(home), int(away), outcome))
        conn.commit()
    return jsonify(ok=True)

# ── VÝSLEDKY ──────────────────────────────────────────────────────────────────

@app.route("/api/results")
def get_results():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT game_id, home_score, away_score, outcome FROM results")
            rows = cur.fetchall()
    return jsonify(results={r["game_id"]: dict(r) for r in rows})

@app.route("/api/results", methods=["POST"])
def save_result():
    if session.get("user") != ADMIN:
        return jsonify(error="Pouze admin"), 403
    d = request.json
    gid, home, away, outcome = d.get("game_id"), d.get("home_score"), d.get("away_score"), d.get("outcome","REG")
    if gid is None or home is None or away is None:
        return jsonify(error="Chybí data"), 400
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO results (game_id, home_score, away_score, outcome, updated_at)
                VALUES (%s,%s,%s,%s,NOW())
                ON CONFLICT (game_id) DO UPDATE SET
                    home_score=EXCLUDED.home_score, away_score=EXCLUDED.away_score,
                    outcome=EXCLUDED.outcome, updated_at=NOW()
            """, (gid, int(home), int(away), outcome))
        conn.commit()
    return jsonify(ok=True)

# ── IIHF SCRAPING ─────────────────────────────────────────────────────────────

TEAM_MAP = {
    "FIN":"Finsko","GER":"Německo","USA":"USA","LAT":"Lotyšsko",
    "SUI":"Švýcarsko","HUN":"Maďarsko","AUT":"Rakousko","GBR":"V. Británie",
    "CAN":"Kanada","SWE":"Švédsko","CZE":"Česko","DEN":"Dánsko",
    "SVK":"Slovensko","NOR":"Norsko","SLO":"Slovinsko","ITA":"Itálie",
    "FINLAND":"Finsko","GERMANY":"Německo","LATVIA":"Lotyšsko",
    "SWITZERLAND":"Švýcarsko","HUNGARY":"Maďarsko","AUSTRIA":"Rakousko",
    "GREAT BRITAIN":"V. Británie","CANADA":"Kanada","SWEDEN":"Švédsko",
    "CZECHIA":"Česko","DENMARK":"Dánsko","SLOVAKIA":"Slovensko",
    "NORWAY":"Norsko","SLOVENIA":"Slovinsko","ITALY":"Itálie",
}

@app.route("/api/fetch-iihf")
def fetch_iihf():
    if session.get("user") != ADMIN:
        return jsonify(error="Pouze admin"), 403
    try:
        url  = "https://www.iihf.com/en/events/2026/wm/schedule"
        resp = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        updated = []
        blocks  = soup.select(".game-block, .schedule-item, [class*='game'], [class*='match']")
        if not blocks:
            return jsonify(ok=False, message="IIHF stránka nemá rozpoznatelnou strukturu — zadej výsledky ručně.", updated=[])
        for block in blocks:
            try:
                score_el = block.select_one("[class*='score'], [class*='result']")
                if not score_el or ":" not in score_el.get_text(): continue
                parts = score_el.get_text(strip=True).split(":")
                h_score, a_score = int(parts[0].strip()), int(parts[1].strip())
                teams = block.select("[class*='team'], [class*='country']")
                if len(teams) < 2: continue
                home_cz = TEAM_MAP.get(teams[0].get_text(strip=True).upper())
                away_cz = TEAM_MAP.get(teams[1].get_text(strip=True).upper())
                if not home_cz or not away_cz: continue
                outcome = "REG"
                bt = block.get_text(" ", strip=True).upper()
                if "SO" in bt or "SHOOTOUT" in bt: outcome = "SO"
                elif "OT" in bt or "OVERTIME" in bt: outcome = "OT"
                match = next((g for g in GAMES if g["home"]==home_cz and g["away"]==away_cz), None)
                if not match: continue
                with get_db() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO results (game_id, home_score, away_score, outcome, updated_at)
                            VALUES (%s,%s,%s,%s,NOW())
                            ON CONFLICT (game_id) DO UPDATE SET
                                home_score=EXCLUDED.home_score, away_score=EXCLUDED.away_score,
                                outcome=EXCLUDED.outcome, updated_at=NOW()
                        """, (match["id"], h_score, a_score, outcome))
                    conn.commit()
                updated.append(f"{home_cz} {h_score}:{a_score} {away_cz} ({outcome})")
            except Exception:
                continue
        if updated:
            return jsonify(ok=True, message=f"Aktualizováno {len(updated)} výsledků.", updated=updated)
        return jsonify(ok=False, message="Žádné výsledky nenalezeny — zadej ručně.", updated=[])
    except Exception as e:
        return jsonify(ok=False, message=f"Chyba: {str(e)}", updated=[])

# ── STAV ZÁPASŮ ───────────────────────────────────────────────────────────────

@app.route("/api/games")
def get_games():
    now = datetime.datetime.now(CEST)
    out = []
    for g in GAMES:
        kickoff  = game_kickoff_cest(g)
        deadline = kickoff - datetime.timedelta(hours=1)
        out.append({
            **g,
            "tippable": now < deadline,
            "minutes_to_deadline": int((deadline - now).total_seconds() / 60),
            "display_date": kickoff.strftime("%-d.%-m."),
        })
    return jsonify(games=out)

# ── ŽEBŘÍČEK ──────────────────────────────────────────────────────────────────

@app.route("/api/leaderboard")
def leaderboard():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM users")
            users = [r["name"] for r in cur.fetchall()]
            cur.execute("SELECT game_id, home_score, away_score, outcome FROM results")
            results = {r["game_id"]: dict(r) for r in cur.fetchall()}
    rows = []
    with get_db() as conn:
        with conn.cursor() as cur:
            for name in users:
                cur.execute("SELECT game_id, home_score, away_score, outcome FROM tips WHERE user_name=%s", (name,))
                tips = {r["game_id"]: dict(r) for r in cur.fetchall()}
                total = exact = correct = 0
                for gid, res in results.items():
                    p = calc_points(tips.get(gid), res)
                    total += p
                    if p == 3: exact += 1
                    if p == 1: correct += 1
                rows.append({"name":name,"total":total,"exact":exact,"correct":correct})
    rows.sort(key=lambda x: x["total"], reverse=True)
    return jsonify(leaderboard=rows)

# ── STATIC ────────────────────────────────────────────────────────────────────

@app.route("/", defaults={"path":""})
@app.route("/<path:path>")
def index(path):
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
