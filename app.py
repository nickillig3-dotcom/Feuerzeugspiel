import streamlit as st
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Tuple
import os

# --------- Grund-Setup & Theme ---------

st.set_page_config(
    page_title="Feuerzeugspiel",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

PLAYERS_FILE = "data/players.json"
FEED_FILE = "data/feed.json"
RULES_FILE = "data/feuerzeugspiel_gesetzbuch.md"

OATH_TEXT_ANG = "Ich schwöre, ich habe ihn gestochen."
OATH_TEXT_OPF = "Ich schwöre, er hat mich nicht gestochen."

# ---------------- Globale Styles (für bessere Lesbarkeit) ----------------
# --- Layout / CSS Tweaks für Mobile ---

st.markdown("""
    <style>
    /* Verhindert, dass Tabellen‑Header auf Mobile jeden Buchstaben umbrechen */
    .stTable th, .stTable td, .stDataFrame th, .stDataFrame td {
        white-space: nowrap;
    }
    </style>
""", unsafe_allow_html=True)

def inject_global_styles():
    st.markdown(
        """
        <style>
            /* Gesamter App-Hintergrund + Standardtext */
            .stApp {
                background: radial-gradient(circle at top left, #020617 0%, #020617 40%, #000000 100%);
                color: #e5e7eb;
            }

            /* Sidebar dunkler + Text hell */
            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #020617, #0b1120);
            }
            section[data-testid="stSidebar"] * {
                color: #e5e7eb !important;
            }

            /* Überschriften & normaler Text */
            h1, h2, h3, h4, h5, h6,
            p, label, span,
            .stMarkdown, .stText {
                color: #e5e7eb !important;
            }

            /* Tabellen & DataFrames lesbarer machen */
            [data-testid="stTable"] table,
            [data-testid="stDataFrame"] table {
                background-color: #020617 !important;
                color: #e5e7eb !important;
            }

            [data-testid="stTable"] thead tr,
            [data-testid="stDataFrame"] thead tr {
                background-color: #0f172a !important;
            }

            [data-testid="stTable"] tbody tr:nth-child(odd),
            [data-testid="stDataFrame"] tbody tr:nth-child(odd) {
                background-color: rgba(15, 23, 42, 0.85) !important;
            }

            [data-testid="stTable"] tbody tr:nth-child(even),
            [data-testid="stDataFrame"] tbody tr:nth-child(even) {
                background-color: rgba(15, 23, 42, 0.55) !important;
            }

            /* Tabellen‑Border leicht sichtbar */
            [data-testid="stTable"] td, [data-testid="stTable"] th,
            [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
                border-color: rgba(148, 163, 184, 0.35) !important;
            }

            /* Buttons etwas „gameiger“ und gut lesbar */
            .stButton > button {
                border-radius: 999px;
                padding: 0.40rem 1.3rem;
                border: 1px solid rgba(248, 250, 252, 0.25);
                background: linear-gradient(90deg, #f97316, #ec4899);
                color: #0b1120 !important;
                font-weight: 600;
            }
            .stButton > button:hover {
                filter: brightness(1.08);
                transform: translateY(-1px);
            }

            /* Input-Labels & Radio/Checkbox lesbar machen */
            .stSelectbox label,
            .stTextInput label,
            .stRadio label,
            .stCheckbox label {
                color: #e5e7eb !important;
            }

            /* Alerts (Info / Warnung / Fehler) – Text dunkel auf hellem Kasten lassen */
            .stAlert p {
                color: inherit !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Styles direkt beim Start aktivieren
inject_global_styles()


def inject_global_css():
    st.markdown(
        """
        <style>
        /* Gesamt-Hintergrund */
        .stApp {
            background: radial-gradient(circle at top left, #111827 0, #020617 45%, #000000 100%);
            color: #e5e7eb;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #020617, #111827);
            border-right: 1px solid rgba(148,163,184,0.3);
        }
        [data-testid="stSidebar"] * {
            color: #e5e7eb !important;
        }

        /* Überschriften */
        h1, h2, h3 {
            font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Metric-Kacheln */
        div[data-testid="metric-container"] {
            background: rgba(15,23,42,0.9);
            border-radius: 0.75rem;
            padding: 0.6rem 0.9rem;
            border: 1px solid rgba(148,163,184,0.4);
            box-shadow: 0 0 25px rgba(15,23,42,0.9);
        }

        /* Tabellen & DataFrames */
        .stTable, .stDataFrame {
            background: rgba(15,23,42,0.9);
            border-radius: 0.75rem;
            padding: 0.5rem;
            border: 1px solid rgba(55,65,81,0.9);
            box-shadow: 0 0 25px rgba(15,23,42,0.8);
        }

        /* Buttons */
        .stButton>button {
            border-radius: 999px;
            border: none;
            padding: 0.5rem 1.3rem;
            background: linear-gradient(135deg, #fb923c, #f97316);
            color: white;
            font-weight: 600;
            box-shadow: 0 8px 20px rgba(249,115,22,0.35);
        }
        .stButton>button:hover {
            background: linear-gradient(135deg, #f97316, #ea580c);
            box-shadow: 0 10px 30px rgba(248,113,22,0.65);
        }

        /* Kleine Badge z.B. für Status / Großmacht */
        .fsp-badge {
            display: inline-block;
            padding: 0.15rem 0.7rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: .08em;
            background: rgba(31,41,55,0.9);
            border: 1px solid rgba(148,163,184,0.9);
            color: #e5e7eb;
        }

        /* Paragraph-„Chat“-Style (hilft v.a. im Feed) */
        [data-testid="stMarkdownContainer"] > p {
            background: rgba(15,23,42,0.7);
            padding: 0.3rem 0.7rem;
            border-radius: 0.5rem;
            margin-bottom: 0.25rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------- Basis-Ladefunktionen ----------------

def load_players() -> Dict[str, Dict[str, Any]]:
    if not os.path.exists(PLAYERS_FILE):
        st.error(f"Spielerdatei '{PLAYERS_FILE}' nicht gefunden.")
        st.stop()
    with open(PLAYERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_players(players: Dict[str, Dict[str, Any]]) -> None:
    with open(PLAYERS_FILE, "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, indent=2)


def load_feed() -> List[Dict[str, Any]]:
    if not os.path.exists(FEED_FILE):
        return []
    with open(FEED_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_feed(feed: List[Dict[str, Any]]) -> None:
    with open(FEED_FILE, "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)


def load_rules() -> str:
    if not os.path.exists(RULES_FILE):
        return "# Gesetzbuch-Datei nicht gefunden.\nLege 'feuerzeugspiel_gesetzbuch.md' in den FSP-Ordner."
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        return f.read()


# ---------------- Score / Fronten-Logik ----------------

def parse_score(score_str: str) -> Tuple[int, int]:
    try:
        left, right = score_str.split(":")
        return int(left), int(right)
    except Exception:
        return 0, 0


def score_to_str(a: int, b: int) -> str:
    return f"{a}:{b}"


def get_active_front(
    player_name: str,
    opponent_name: str,
    players: Dict[str, Dict[str, Any]]
) -> Tuple[int, int]:
    """
    Holt den aktiven Front-Stand (aus Sicht von player_name) gegen opponent_name.
    Nutzt eigene active_fronts oder spiegelt die des Gegners.
    """
    p = players[player_name]
    entry = p.get("active_fronts", {}).get(opponent_name)
    if entry:
        return parse_score(entry)

    opp = players[opponent_name]
    entry2 = opp.get("active_fronts", {}).get(player_name)
    if entry2:
        of, oa = parse_score(entry2)
        return oa, of

    return 0, 0


def set_active_front(
    attacker: str,
    defender: str,
    a_for: int,
    a_against: int,
    players: Dict[str, Dict[str, Any]]
) -> None:
    """
    Setzt die aktive Front symmetrisch:
    attacker: a_for:a_against
    defender: a_against:a_for
    """
    players[attacker].setdefault("active_fronts", {})
    players[defender].setdefault("active_fronts", {})

    players[attacker]["active_fronts"][defender] = score_to_str(a_for, a_against)
    players[defender]["active_fronts"][attacker] = score_to_str(a_against, a_for)


def transfer_land(
    attacker: str,
    defender: str,
    land_name: str,
    players: Dict[str, Dict[str, Any]]
) -> bool:
    """
    Verschiebt ein Land von defender zu attacker.

    - Entfernt land_name aus players[defender]["lands"]
    - Fügt land_name zu players[attacker]["lands"] hinzu
    - Speichert players.json

    Gibt True zurück, wenn es geklappt hat, sonst False.
    """
    defender_lands = players.get(defender, {}).get("lands", [])
    if land_name not in defender_lands:
        return False

    # Land beim Verteidiger entfernen
    defender_lands.remove(land_name)
    players[defender]["lands"] = defender_lands

    # Land beim Angreifer hinzufügen
    players.setdefault(attacker, {})
    players[attacker].setdefault("lands", [])
    if land_name not in players[attacker]["lands"]:
        players[attacker]["lands"].append(land_name)

    # Speichern
    save_players(players)
    return True


def list_active_opponents(
    player_name: str,
    players: Dict[str, Dict[str, Any]]
) -> List[str]:
    """
    Alle Gegner, mit denen player_name eine aktive Front hat,
    egal bei wem sie eingetragen ist.
    """
    opponents = set()
    me = players[player_name]

    for opp in me.get("active_fronts", {}).keys():
        opponents.add(opp)

    for pname, pdata in players.items():
        if pname == player_name:
            continue
        if player_name in pdata.get("active_fronts", {}):
            opponents.add(pname)

    return sorted(opponents)


def compute_matchups(players: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Baut eine Übersicht aller 'Kriege':
    Für jedes Spieler-Paar: Stiche A->B, B->A, Gesamt, Differenz.
    Basis sind die History-Werte, NICHT nur aktive Fronten.
    """
    pairs: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for pname, pdata in players.items():
        hist = pdata.get("history", {})
        for opp, score in hist.items():
            if pname == opp:
                continue
            key = tuple(sorted([pname, opp]))
            if key not in pairs:
                pairs[key] = {
                    "Spieler 1": key[0],
                    "Spieler 2": key[1],
                    "Stiche 1→2": 0,
                    "Stiche 2→1": 0,
                }
            if pname == key[0]:
                pairs[key]["Stiche 1→2"] += score
            else:
                pairs[key]["Stiche 2→1"] += score

    result = []
    for data in pairs.values():
        s12 = data["Stiche 1→2"]
        s21 = data["Stiche 2→1"]
        gesamt = s12 + s21
        diff = s12 - s21
        result.append(
            {
                **data,
                "Gesamtstiche": gesamt,
                "Differenz (1-2)": diff,
                "Differenz absolut": abs(diff),
            }
        )
    return result


# ---------------- Feed / Event-Logik ----------------

def next_feed_id(feed: List[Dict[str, Any]]) -> int:
    if not feed:
        return 1
    return max(e.get("id", 0) for e in feed) + 1


def confirm_stich(
    event_id: int,
    players: Dict[str, Dict[str, Any]],
    feed: List[Dict[str, Any]],
) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Normale Bestätigung eines Stichs:
    - Grundsätzlich +1 Punkt für den Angreifer (History & aktive Front)
    - Wenn der Angreifer eine Großmacht ist UND es kein Duell ist:
      zählen die Stiche doppelt (+2).
    """
    event = None
    for e in feed:
        if e.get("id") == event_id:
            event = e
            break

    if event is None or event.get("bestaetigt"):
        return players, feed

    ang = event["angreifer"]
    victim = event["opfer"]
    art = event.get("art", "normal")

    # Basis: 1 Punkt
    punkte = 1

    # Großmacht: doppelte Punkte, außer bei Duell
    if players.get(ang, {}).get("is_grossmacht") and art != "duell":
        punkte = 2

    # History: Punkte mehr für Angreifer
    players[ang].setdefault("history", {})
    players[victim].setdefault("history", {})
    players[ang]["history"][victim] = players[ang]["history"].get(victim, 0) + punkte

    # Aktive Front aktualisieren
    a_for, a_against = get_active_front(ang, victim, players)
    a_for += punkte
    set_active_front(ang, victim, a_for, a_against, players)

    # Event markieren (optional: Punkte mitschreiben)
    event["bestaetigt"] = True
    event["stand_nachher"] = score_to_str(a_for, a_against)
    event["punkte"] = punkte

    return players, feed


def apply_duell_result(
    event_id: int,
    winner: str,
    players: Dict[str, Dict[str, Any]],
    feed: List[Dict[str, Any]],
) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Streitfall/Duell: Gewinner bekommt genau 1 Punkt gegen den anderen.
    """
    event = None
    for e in feed:
        if e.get("id") == event_id:
            event = e
            break

    if event is None or event.get("bestaetigt"):
        return players, feed

    # Nur, wenn beide geschworen haben
    if not event.get("oath_ang_ok") or not event.get("oath_opf_ok"):
        return players, feed

    a = event["angreifer"]
    b = event["opfer"]
    if winner not in (a, b):
        return players, feed

    if winner == a:
        loser = b
    else:
        loser = a

    players[winner].setdefault("history", {})
    players[winner]["history"][loser] = players[winner]["history"].get(loser, 0) + 1

    w_for, w_against = get_active_front(winner, loser, players)
    w_for += 1
    set_active_front(winner, loser, w_for, w_against, players)

    event["bestaetigt"] = True
    event["duell_gewinner"] = winner
    event["stand_nachher"] = score_to_str(w_for, w_against)
    event["streitfall"] = True

    return players, feed


# ---------------- App: Daten laden + Login ----------------

players = load_players()
feed = load_feed()

st.session_state.setdefault("user", None)

if st.session_state["user"] is None:
    st.title("🔥 Feuerzeugspiel – Login")

    username = st.text_input("Spielername")
    password = st.text_input("Passwort", type="password")

    if st.button("Login"):
        if username in players and players[username]["password"] == password:
            st.session_state["user"] = username
            st.experimental_rerun()
        else:
            st.error("❌ Falscher Benutzername oder Passwort")

    st.stop()

user = st.session_state["user"]
me = players[user]

# CSS nach erfolgreichem Login injizieren
inject_global_css()

# ---------------- Navigation ----------------

st.sidebar.title(f"Eingeloggt als: {user}")
page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Stiche",
        "Feed",
        "Historie",
        "Kriege & Story",
        "Streuner & Comeback",
        "Länder & Reiche",
        "Leaderboards",
        "Spielerklärung",
        "Gesetzbuch",
    ],
)

if st.sidebar.button("Logout"):
    st.session_state["user"] = None
    st.experimental_rerun()

# ===================== DASHBOARD =====================

if page == "Dashboard":
    # Hero-Header
    st.markdown(
        f"""
        <div style='display:flex;align-items:center;gap:0.9rem;margin-bottom:0.8rem;'>
          <div style='font-size:2.4rem;'>🔥</div>
          <div>
            <h1 style='margin-bottom:0;'>Feuerzeugspiel – {user}</h1>
            <p style='margin-top:0.1rem;color:#9ca3af;'>Dein persönliches Kriegs-Dashboard.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    lives = me.get("lives", 0)
    lands = me.get("lands", [])
    total_my_stiche = sum(me.get("history", {}).values())
    incoming_hits = sum(
        pdata.get("history", {}).get(user, 0)
        for pname, pdata in players.items()
        if pname != user
    )
    is_gm = me.get("is_grossmacht")
    status_label = "🟢 Aktiv" if not me.get("offline") else "⚫ Offline"

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Leben", lives)
    with m2:
        st.metric("Länder", len(lands))
    with m3:
        st.metric("Gesetzte Stiche", total_my_stiche)
    with m4:
        st.metric("Eingesteckte Stiche", incoming_hits)

    if lands:
        st.caption("🌍 Deine Länder: " + ", ".join(lands))
    else:
        st.caption("🌍 Du besitzt aktuell kein Land.")

    st.markdown(
        f"<span class='fsp-badge'>{status_label}"
        f"{' · 🛡 Großmacht' if is_gm else ''}</span>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ---- Aktive Fronten ----
    st.subheader("⚔️ Aktive Fronten")

    opponents = list_active_opponents(user, players)
    land_hints = []
    rows = []

    if opponents:
        for opp in opponents:
            my_for, my_against = get_active_front(user, opp, players)
            rows.append(
                {
                    "Gegner": opp,
                    "Deine Stiche": my_for,
                    "Seine Stiche": my_against,
                    "Stand (du:er)": f"{my_for}:{my_against}",
                }
            )
            if my_for - my_against >= 10:
                land_hints.append((opp, my_for, my_against))

        df_fronten = pd.DataFrame(rows)
        st.dataframe(df_fronten, use_container_width=True)
    else:
        st.write("📭 Du hast aktuell keine aktiven Fronten.")

    # Landnahme-Hinweise + Aktion
    if land_hints:
        st.subheader("🔔 Mögliche Landnahmen (10 Punkte Vorsprung)")
        st.caption(
            "Regel: Bei mindestens 10 Punkten Vorsprung darfst du 1 Land deines Gegners nehmen. "
            "Ihr klärt außerhalb, welches Land – hier wird es nur im System eingetragen."
        )

        for opp, mf, ma in land_hints:
            defender_lands = players.get(opp, {}).get("lands", [])

            # Falls Gegner gar keine Länder (mehr) hat
            if not defender_lands:
                st.write(f"- Gegen **{opp}**: {mf}:{ma} – Gegner hat aktuell keine Länder mehr.")
                continue

            with st.expander(f"🏰 Landnahme gegen {opp} ({mf}:{ma})", expanded=False):
                st.write(f"Aktueller Vorsprung: **{mf - ma} Punkte**.")

                selected_land = st.selectbox(
                    f"Land wählen, das du von {opp} übernehmen willst",
                    defender_lands,
                    key=f"landwahl_{opp}",
                )

                if st.button("Landnahme durchführen", key=f"landnahme_btn_{opp}"):
                    ok = transfer_land(user, opp, selected_land, players)
                    if ok:
                        # Landnahme im Feed loggen
                        current_feed = load_feed()
                        new_id = next_feed_id(current_feed)
                        current_feed.append(
                            {
                                "id": new_id,
                                "angreifer": user,
                                "opfer": opp,
                                "zeit": datetime.now().isoformat(timespec="seconds"),
                                "bestaetigt": True,
                                "stand_nachher": None,
                                "art": "landnahme",
                                "video": "",
                                "streitfall": False,
                                "oath_ang_ok": False,
                                "oath_opf_ok": False,
                                "land": selected_land,
                            }
                        )
                        save_feed(current_feed)

                        st.success(f"Land **{selected_land}** wurde von {opp} zu dir übertragen.")
                        if not players.get(opp, {}).get("lands"):
                            st.warning(
                                f"{opp} besitzt jetzt kein Land mehr – "
                                "prüft nach eurem Gesetzbuch, ob ein Leben verloren geht oder er zum Streuner wird."
                            )
                        st.experimental_rerun()
                    else:
                        st.error("Landnahme fehlgeschlagen – Land nicht gefunden oder schon weg.")

    st.markdown("---")

    # ---- Generelle Fronten aus gesamter Historie ----
    st.subheader("📊 Gesamte Fronten (Historie gegen alle Spieler)")

    hist_rows = []
    my_hist = me.get("history", {})
    for opp_name, opp_data in players.items():
        if opp_name == user:
            continue
        my_vs = my_hist.get(opp_name, 0)
        opp_hist = players[opp_name].get("history", {})
        them_vs = opp_hist.get(user, 0)
        if my_vs == 0 and them_vs == 0:
            continue
        if my_vs > them_vs:
            status = "🔥 Führt"
        elif my_vs < them_vs:
            status = "❌ Verliert"
        else:
            status = "➖ Unentschieden"
        hist_rows.append(
            {
                "Gegner": opp_name,
                f"{user} → {opp_name}": my_vs,
                f"{opp_name} → {user}": them_vs,
                "Status (gesamt)": status,
            }
        )

    if hist_rows:
        st.dataframe(pd.DataFrame(hist_rows), use_container_width=True)
    else:
        st.write("Noch keine Stiche in der Gesamt-Historie.")

    st.markdown("---")

    # ---- Spielerübersicht inkl. Gesamtstiche ----
    st.subheader("👥 Spielerübersicht")
    overview_rows = []
    for pname, pdata in players.items():
        overview_rows.append(
            {
                "Spieler": pname,
                "Leben": pdata.get("lives", 0),
                "Länder": ", ".join(pdata.get("lands", [])),
                "Großmacht": "Ja" if pdata.get("is_grossmacht") else "Nein",
                "Status": "Offline" if pdata.get("offline") else "Aktiv",
                "Gesamtstiche": sum(pdata.get("history", {}).values()),
            }
        )
    st.dataframe(pd.DataFrame(overview_rows), use_container_width=True)

# ===================== STICHE =====================

elif page == "Stiche":
    st.title("⚔️ Stichsystem")

    feed = load_feed()  # neu laden, falls sich was geändert hat

    # ---- Stich melden ----
    st.subheader("🗡 Ich habe jemanden gestochen")

    possible_targets = [name for name in players.keys() if name != user]
    target = st.selectbox("Gegner wählen", possible_targets)

    # Zeige aktuellen aktiven Stand + Historie
    a_for, a_against = get_active_front(user, target, players)
    my_hist_vs = me.get("history", {}).get(target, 0)
    their_hist_vs = players[target].get("history", {}).get(user, 0)

    st.markdown(
        f"**Aktive Front vs {target}:** {a_for}:{a_against}  \n"
        f"**Gesamte Historie vs {target}:** du → {my_hist_vs}, er → {their_hist_vs}"
    )

    art = st.selectbox(
        "Art des Stichs",
        ["normal", "duell", "wurf", "schlafstich"],
        format_func=lambda x: {
            "normal": "Normaler Stich",
            "duell": "Duell-Stich (Streitfall möglich)",
            "wurf": "Wurf (1x pro Woche)",
            "schlafstich": "Schlafstich (mit Video-Beweis)",
        }[x],
    )
    video = st.text_input("Videolink / Beweis (optional)", "")

    if st.button("Stich melden"):
        # Wurf-Limit: max. 1 Wurf pro Kalenderwoche pro Spieler
        if art == "wurf":
            now = datetime.now()
            year, week, _ = now.isocalendar()
            already_used = False
            for e in feed:
                if e.get("angreifer") == user and e.get("art") == "wurf":
                    try:
                        t = datetime.fromisoformat(e.get("zeit", ""))
                        y, w, _ = t.isocalendar()
                    except Exception:
                        continue
                    if y == year and w == week:
                        already_used = True
                        break
            if already_used:
                st.error("Du hast deinen Wurf in dieser Kalenderwoche bereits genutzt (§ 9).")
                st.stop()

        # Hinweis bei Schlafstich ohne Video
        if art == "schlafstich" and not video.strip():
            st.warning("Schlafstiche sollten mit Videobeweis dokumentiert werden (§ 7a).")

        new_id = next_feed_id(feed)
        event = {
            "id": new_id,
            "angreifer": user,
            "opfer": target,
            "zeit": datetime.now().isoformat(timespec="seconds"),
            "bestaetigt": False,
            "stand_nachher": None,
            "art": art,
            "video": video.strip() or "",
            "streitfall": False,
            "oath_ang_ok": False,
            "oath_opf_ok": False,
        }
        feed.append(event)
        save_feed(feed)
        st.success(f"Stich gegen {target} gemeldet. Wartet auf Bestätigung.")
        st.experimental_rerun()

    st.markdown("---")

    # ---- Eigene offene Stiche ----
    st.subheader("⏳ Offene Stiche, die du gemeldet hast")
    feed = load_feed()
    outgoing = [
        e for e in feed if e["angreifer"] == user and not e.get("bestaetigt") and not e.get("streitfall")
    ]
    if outgoing:
        for e in outgoing:
            st.write(f"- Gegen **{e['opfer']}**, gemeldet um {e['zeit']} (wartet auf Bestätigung)")
    else:
        st.write("Du hast keine offenen gemeldeten Stiche.")

    st.markdown("---")

    # ---- Eingehende Bestätigungen ----
    st.subheader("✅ Stiche, die du bestätigen musst")
    incoming = [
        e for e in feed if e["opfer"] == user and not e.get("bestaetigt") and not e.get("streitfall")
    ]
    if incoming:
        for e in incoming:
            st.write(
                f"**{e['angreifer']}** behauptet, dich gestochen zu haben (gemeldet um {e['zeit']})."
            )
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Bestätigen", key=f"confirm_{e['id']}"):
                    players, feed = confirm_stich(e["id"], players, feed)
                    save_players(players)
                    save_feed(feed)
                    st.success("Stich bestätigt und eingetragen! (Dashboard, Leaderboards etc. aktualisiert)")
                    st.experimental_rerun()
            with c2:
                if st.button("Ablehnen (Streitfall + Schwur)", key=f"reject_{e['id']}"):
                    # Streitfall setzen + Schwur-Flags initialisieren
                    for ev in feed:
                        if ev.get("id") == e["id"]:
                            ev["streitfall"] = True
                            ev["oath_ang_ok"] = ev.get("oath_ang_ok", False)
                            ev["oath_opf_ok"] = ev.get("oath_opf_ok", False)
                            break
                    save_feed(feed)
                    st.warning("Stich abgelehnt – jetzt müssen beide schwören, dann Duell.")
                    st.experimental_rerun()
    else:
        st.write("Du musst aktuell keine Stiche bestätigen.")

    st.markdown("---")

    # ---- Streitfälle / Duelle + Schwur ----
    st.subheader("⚖ Streitfälle, Schwüre & Duelle")

    feed = load_feed()
    conflicts = [
        e
        for e in feed
        if e.get("streitfall") and not e.get("bestaetigt") and user in (e["angreifer"], e["opfer"])
    ]

    if conflicts:
        for e in conflicts:
            ang = e["angreifer"]
            opf = e["opfer"]
            st.write(f"Streitfall zwischen **{ang}** und **{opf}** (gemeldet um {e['zeit']}).")

            oath_ang_ok = e.get("oath_ang_ok", False)
            oath_opf_ok = e.get("oath_opf_ok", False)

            # Schwur-Eingabe für Angreifer
            if user == ang and not oath_ang_ok:
                st.markdown("**Dein Schwur (Angreifer):**")
                st.caption(f"Du musst exakt folgenden Satz eingeben:\n`{OATH_TEXT_ANG}`")
                oath_input = st.text_input(
                    f"Schwur eingeben (Event {e['id']})",
                    key=f"oath_ang_{e['id']}",
                )
                if st.button("Schwur abschicken (Angreifer)", key=f"oath_ang_btn_{e['id']}"):
                    if oath_input == OATH_TEXT_ANG:
                        e["oath_ang_ok"] = True
                        save_feed(feed)
                        st.success("Schwur akzeptiert.")
                        st.experimental_rerun()
                    else:
                        st.error("Schwur falsch eingegeben. Du musst den Text 1:1 eingeben.")

            # Schwur-Eingabe für Opfer
            if user == opf and not oath_opf_ok:
                st.markdown("**Dein Schwur (Opfer):**")
                st.caption(f"Du musst exakt folgenden Satz eingeben:\n`{OATH_TEXT_OPF}`")
                oath_input = st.text_input(
                    f"Schwur eingeben (Event {e['id']})",
                    key=f"oath_opf_{e['id']}",
                )
                if st.button("Schwur abschicken (Opfer)", key=f"oath_opf_btn_{e['id']}"):
                    if oath_input == OATH_TEXT_OPF:
                        e["oath_opf_ok"] = True
                        save_feed(feed)
                        st.success("Schwur akzeptiert.")
                        st.experimental_rerun()
                    else:
                        st.error("Schwur falsch eingegeben. Du musst den Text 1:1 eingeben.")

            oath_ang_ok = e.get("oath_ang_ok", False)
            oath_opf_ok = e.get("oath_opf_ok", False)

            if not oath_ang_ok or not oath_opf_ok:
                st.info("Duell erst möglich, wenn **beide** ihren Schwur korrekt eingegeben haben.")
                st.markdown("---")
                continue

            st.success("Beide Schwüre sind abgegeben – jetzt muss das Duell entschieden werden.")

            other = opf if user == ang else ang
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Ich habe das Duell gewonnen", key=f"duell_me_{e['id']}"):
                    players, feed = apply_duell_result(e["id"], user, players, feed)
                    save_players(players)
                    save_feed(feed)
                    st.success("Duell-Gewinn eingetragen! (alles aktualisiert)")
                    st.experimental_rerun()
            with c2:
                if st.button(f"{other} hat gewonnen", key=f"duell_other_{e['id']}"):
                    players, feed = apply_duell_result(e["id"], other, players, feed)
                    save_players(players)
                    save_feed(feed)
                    st.info("Duell-Gewinn für den anderen eingetragen.")
                    st.experimental_rerun()

            st.markdown("---")
    else:
        st.write("Keine offenen Streitfälle/Duelle.")

# ===================== FEED =====================

elif page == "Feed":
    st.title("🕒 Öffentlicher Stich-Feed")

    feed = load_feed()
    if not feed:
        st.write("Noch keine Stiche im Feed.")
    else:
        only_me = st.checkbox("Nur Stiche anzeigen, an denen ich beteiligt bin")

        confirmed = [e for e in feed if e.get("bestaetigt")]
        confirmed = sorted(confirmed, key=lambda x: x.get("zeit", ""), reverse=True)

        icon_map = {
            "normal": "⚔️",
            "duell": "⚖️ Duell",
            "wurf": "🎯 Wurf",
            "schlafstich": "😴 Schlafstich",
            "landnahme": "🏰 Landnahme",
        }

        for e in confirmed:
            if only_me and user not in (e["angreifer"], e["opfer"]):
                continue

            zeit = e.get("zeit", "?")
            ang = e.get("angreifer", "?")
            opf = e.get("opfer", "?")
            stand = e.get("stand_nachher", "?")
            art = e.get("art", "normal")
            icon = icon_map.get(art, "⚔️")

            if art == "landnahme":
                land = e.get("land", "?")
                line = (
                    f"**{zeit}** – {icon} **{ang}** hat das Land **{land}** "
                    f"von **{opf}** übernommen."
                )
            else:
                line = (
                    f"**{zeit}** – {icon} **{ang}** hat **{opf}** gestochen. "
                    f"Neuer Stand: `{stand}`"
                )
                if e.get("duell_gewinner"):
                    line += f" (Duell-Gewinner: {e['duell_gewinner']})"

            st.markdown(line)
            if e.get("video"):
                st.caption(f"Beweis: {e['video']}")

# ===================== HISTORIE =====================

elif page == "Historie":
    st.title("📜 Komplette Stich-Historie (Summen)")

    all_rows = []
    for pname, pdata in players.items():
        hist = pdata.get("history", {})
        for opp, score in hist.items():
            all_rows.append(
                {
                    "Spieler": pname,
                    "Gegner": opp,
                    "Stiche von Spieler gegen Gegner": score,
                }
            )

    if not all_rows:
        st.write("Noch keine History-Daten vorhanden.")
    else:
        df = pd.DataFrame(all_rows)
        player_names = sorted(players.keys())
        selected_player = st.selectbox(
            "Nur Stiche eines Spielers anzeigen (optional)", ["Alle"] + player_names
        )

        if selected_player != "Alle":
            df = df[df["Spieler"] == selected_player]

        st.dataframe(df, use_container_width=True)

# ===================== KRIEGE & STORY =====================

elif page == "Kriege & Story":
    st.title("⚔📖 Kriege & Story")

    matchups = compute_matchups(players)
    if not matchups:
        st.write("Noch keine Kriege vorhanden – es wurden noch keine Stiche verteilt.")
    else:
        df = pd.DataFrame(matchups)

        st.subheader("🔥 Größte Kriege (nach Gesamtstichen)")
        df_sorted_total = df.sort_values("Gesamtstiche", ascending=False)
        st.dataframe(df_sorted_total.head(10), use_container_width=True)

        st.subheader("💥 Engste Duelle (kleine Differenz, viele Stiche)")
        df_eng = df[(df["Gesamtstiche"] >= 5)].copy()
        if not df_eng.empty:
            df_eng = df_eng.sort_values(["Differenz absolut", "Gesamtstiche"])
            st.dataframe(df_eng.head(10), use_container_width=True)
        else:
            st.write("Noch keine engen Duelle mit genug Stichen.")

        st.subheader("📜 Alle Kriege")
        st.dataframe(df, use_container_width=True)

# ===================== STREUNER & COMEBACK =====================

elif page == "Streuner & Comeback":
    st.title("🧟‍♂️ Streuner & Comebacks")

    # --- Globale Landnahme-Möglichkeiten nach aktiven Fronten ---
    st.subheader("🌍 Mögliche Landnahmen (Vorsprung ≥ 10 in aktiven Fronten)")

    ln_rows = []
    player_names = list(players.keys())

    # Jedes Spielerpaar genau einmal betrachten
    for i, p1 in enumerate(player_names):
        for j in range(i + 1, len(player_names)):
            p2 = player_names[j]

            # Aktiver Stand aus Sicht von p1
            s1_for, s1_against = get_active_front(p1, p2, players)
            diff = s1_for - s1_against

            if diff >= 10:
                leader = p1
                loser = p2
                stand = f"{s1_for}:{s1_against}"  # Führender:Unterlegener
            elif diff <= -10:
                leader = p2
                loser = p1
                # aus Sicht des Führenden drehen wir den Stand um
                stand = f"{s1_against}:{s1_for}"
            else:
                continue  # keine Landnahme-Berechtigung

            loser_lands = players[loser].get("lands", [])
            ln_rows.append(
                {
                    "Führender": leader,
                    "Unterlegener": loser,
                    "Aktueller Front-Stand (Führender:Unterlegener)": stand,
                    "Länder des Unterlegenen": ", ".join(loser_lands)
                    if loser_lands
                    else "Keine (landlos)",
                }
            )

    if ln_rows:
        st.table(pd.DataFrame(ln_rows))
        st.caption(
            "Dies sind nur theoretische Landnahme-Möglichkeiten nach eurem Punktesystem "
            "(Vorsprung von mindestens 10 Stichen in einer aktiven Front). "
            "Welche Länder wirklich genommen werden, und ob ggf. Leben verloren gehen "
            "oder neue Länder vergeben werden, entscheidet ihr weiterhin selbst "
            "nach dem Gesetzbuch."
        )
    else:
        st.write("Aktuell gibt es keine aktiven Fronten mit mindestens 10 Stichen Vorsprung.")

    st.markdown("---")

    # --- Streuner finden: keine Länder und 0 Leben ---
    streuner_namen = []
    for pname, pdata in players.items():
        lives = pdata.get("lives", 0)
        lands = pdata.get("lands", [])
        if lives == 0 and len(lands) == 0:
            streuner_namen.append(pname)

    if streuner_namen:
        st.subheader("Aktuelle Streuner")

        rows = []
        for s in streuner_namen:
            s_hist = players[s].get("history", {})
            opponents = [name for name in players.keys() if name != s]

            erledigt_gegen = []
            for opp in opponents:
                s_to_opp = s_hist.get(opp, 0)
                opp_to_s = players[opp].get("history", {}).get(s, 0)
                diff = s_to_opp - opp_to_s
                # Orientierungswert: Vorsprung ≥ 5 gegen einen Gegner
                if diff >= 5:
                    erledigt_gegen.append(f"{opp} (+{diff})")

            rows.append(
                {
                    "Streuner": s,
                    "Gegner mit Vorsprung ≥ 5": ", ".join(erledigt_gegen)
                    if erledigt_gegen
                    else "-",
                    "Anzahl erfüllter Gegner": len(erledigt_gegen),
                }
            )

        st.write(
            "Diese Tabelle zeigt für jeden Streuner, gegen welche Gegner er bereits "
            "mindestens 5 Stiche Vorsprung hat. Das soll euch helfen einzuschätzen, "
            "ob ein Comeback nach eurem Gesetzbuch möglich ist – die finale Entscheidung "
            "liegt natürlich trotzdem bei euch."
        )
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.write("Es gibt aktuell keine Streuner (keine Spieler mit 0 Leben und ohne Länder).")

    st.markdown("---")

    # --- Landlose Spieler mit Leben > 0 ---
    st.subheader("Landlose Spieler (aber noch Leben)")

    no_land_rows = []
    for pname, pdata in players.items():
        lands = pdata.get("lands", [])
        lives = pdata.get("lives", 0)
        if len(lands) == 0 and lives > 0:
            no_land_rows.append({"Spieler": pname, "Leben": lives})

    if no_land_rows:
        st.dataframe(pd.DataFrame(no_land_rows), use_container_width=True)
        st.caption(
            "Diese Spieler haben kein Land, aber noch Leben. "
            "Nach Landnahmen müsst ihr hier ggf. neues Land vergeben oder Leben anpassen – "
            "das macht ihr aktuell noch manuell nach Gesetzbuch."
        )
    else:
        st.write("Keine landlosen Spieler mit verbleibenden Leben.")

# ===================== LÄNDER & REICHE =====================

elif page == "Länder & Reiche":
    st.title("🌍 Länder & Reiche")

    # --- Alle Länder als Liste ---
    all_land_rows = []
    for pname, pdata in players.items():
        lands = pdata.get("lands", [])
        for land in lands:
            all_land_rows.append(
                {
                    "Land": land,
                    "Besitzer": pname,
                    "Großmacht": "Ja" if pdata.get("is_grossmacht") else "Nein",
                    "Status Spieler": "Offline" if pdata.get("offline") else "Aktiv",
                }
            )

    st.subheader("Alle vergebenen Länder")
    if all_land_rows:
        st.dataframe(pd.DataFrame(all_land_rows), use_container_width=True)
    else:
        st.write("Es sind aktuell keine Länder vergeben.")

    st.markdown("---")

    # --- Übersicht der Reiche / Imperien ---
    st.subheader("Reiche & Imperien (Kurzüberblick)")

    reich_rows = []
    for pname, pdata in players.items():
        lands = pdata.get("lands", [])
        is_gm = pdata.get("is_grossmacht")
        power = 5 if is_gm else len(lands)  # gleiche Logik wie im Leaderboard

        reich_rows.append(
            {
                "Spieler": pname,
                "Leben": pdata.get("lives", 0),
                "Anzahl Länder": len(lands),
                "Länder": ", ".join(lands),
                "Großmacht": "Ja" if is_gm else "Nein",
                "Machtpunkte": power,
                "Status": "Offline" if pdata.get("offline") else "Aktiv",
            }
        )

    if reich_rows:
        df_reiche = pd.DataFrame(reich_rows)
        df_reiche = df_reiche.sort_values("Machtpunkte", ascending=False)
        st.dataframe(df_reiche, use_container_width=True)
    else:
        st.write("Keine Spieler im System.")

# ===================== LEADERBOARDS =====================

elif page == "Leaderboards":
    st.title("🏆 Leaderboards")

    # Meiste Stiche
    st.subheader("🔥 Wer hat die meisten Stiche gesetzt?")

    stitch_scores = []
    for pname, pdata in players.items():
        total = sum(pdata.get("history", {}).values())
        stitch_scores.append((pname, total))
    stitch_scores.sort(key=lambda x: x[1], reverse=True)

    df = pd.DataFrame(stitch_scores, columns=["Spieler", "Gesetzte Stiche (gesamt)"])
    st.dataframe(df, use_container_width=True)
    # Größte Imperien
    st.subheader("🌍 Größte Imperien (Großmacht = 5 Punkte)")

    empire_scores = []
    for pname, pdata in players.items():
        power = 5 if pdata.get("is_grossmacht") else len(pdata.get("lands", []))
        empire_scores.append((pname, power))
    empire_scores.sort(key=lambda x: x[1], reverse=True)

    df2 = pd.DataFrame(empire_scores, columns=["Spieler", "Machtpunkte"])
    st.dataframe(df2, use_container_width=True)

# ===================== SPIELERKLÄRUNG =====================

elif page == "Spielerklärung":
    st.title("🎮 Wie funktioniert das Feuerzeugspiel?")

    st.markdown(
        """
        Das **Gesetzbuch** ist für Streitfälle da – hier kommt die **kurze Erklärung** für Einsteiger:

        ### Grundidee
        - Jeder Spieler hat **Leben** und kann **Länder / Städte** besitzen.
        - Wenn du jemanden **mit dem Feuerzeug triffst**, ist das ein **Stich**.
        - Stiche werden immer **zwischen zwei Spielern** gezählt – das sind eure **Fronten**.

        ### Aktive Fronten
        - Eine *aktive Front* ist ein laufender Krieg zwischen zwei Spielern.
        - Im Dashboard siehst du für jede aktive Front den aktuellen Stand: `du : er`.
        - Nur die aktiven Fronten sind wichtig für **Landnahmen** und aktuelle Kämpfe.

        ### Stiche eintragen
        1. Du triffst jemanden → geh auf **„Stiche“**.
        2. Wähle den Gegner und die **Art des Stichs** (normal, Duell, Wurf, Schlafstich).
        3. Schick den Stich ab – der andere muss **bestätigen**.
        4. Erst wenn er bestätigt (oder das Duell entschieden ist), zählt der Stich
           und alle Anzeigen (Dashboard, Leaderboards, Fronten) werden aktualisiert.

        ### Streitfälle & Duelle
        - Bestreitet jemand einen Stich, kann er ihn **ablehnen**.
        - Dann müssen beide einen **Schwur** mit festem Text eintippen.
        - Danach tragt ihr ein, wer das **Duell gewonnen** hat – der Gewinner bekommt **1 Stich**.

        ### Landnahmen (vereinfacht)
        - Hast du in einer aktiven Front **mindestens 10 Stiche Vorsprung**, darfst du
          nach euren Regeln ein **Land des Gegners übernehmen**.
        - Welche Stadt / welches Land genau rübergeht, klärt ihr unter euch
          und tragt es dann im Dashboard bei der Landnahme ein.

        ### Leaderboards
        - **„Wer hat die meisten Stiche?“** ⟶ wer hat am meisten ausgeteilt.
        - **„Größte Imperien“** ⟶ wer ist als Großmacht oder mit vielen Ländern gerade am stärksten.

        Für alle Sonderfälle, Würfe, Streuner, Comebacks und Detail-Regeln:
        👉 Nutzt den Tab **„Gesetzbuch“**, wenn es ernst oder kompliziert wird.
        """
    )

# ===================== GESETZBUCH =====================

elif page == "Gesetzbuch":
    st.title("📘 Feuerzeugspiel-Gesetzbuch")
    st.markdown(load_rules())
