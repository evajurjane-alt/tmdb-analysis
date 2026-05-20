
import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import requests
import os

# ═══════════════════════════════
# KONFIGURĀCIJA
# ═══════════════════════════════
DB_CONFIGS = {
    "tmdb": {
        "host": "87.110.123.151",
        "port": 3306,
        "user": "fita2",
        "password": "2026-04-28",
        "database": "tmdb"
    }
}
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Krāsas
ZILS  = "#2E5F8A"
ZALS  = "#4CAF50"
ORANSS = "#FF8C00"
TUMSI  = "#1B2A4A"

# ═══════════════════════════════
# CSS
# ═══════════════════════════════
st.markdown("""
<style>
    .stApp { background-color: #F0F7F0; }
    .stButton>button {
        background-color: #FF8C00;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #e67e00; }
    .metric-card {
        background-color: #2E5F8A;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: white;
        height: 100px;
    }
    .metric-number { font-size: 2.2em; font-weight: bold; color: #FF8C00; }
    .metric-label { font-size: 0.9em; color: #dddddd; margin-top: 5px; }
    h1 { color: #1B2A4A !important; }
    h3 { color: #2E5F8A !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════
# FUNKCIJAS
# ═══════════════════════════════
def get_connection(db_name):
    return mysql.connector.connect(**DB_CONFIGS[db_name])

def run_query(sql, db_name):
    conn = get_connection(db_name)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    results = cursor.fetchall()
    conn.close()
    return results

def ask_gemini(prompt):
    models = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
        except:
            continue
    return None

def get_db_context(db_name):
    conn = get_connection(db_name)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    context = f"Datubāze: {db_name}\n\n"
    for t in tables:
        table_name = list(t.values())[0]
        context += f"{table_name}:\n"
        cursor.execute(f"DESCRIBE {table_name}")
        for col in cursor.fetchall():
            context += f"  - {col['Field']} ({col['Type']})\n"
        context += "\n"
    conn.close()
    return context

def grafiks_setup(fig, ax, title):
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    ax.set_title(title, color=TUMSI, pad=15, fontsize=11)
    ax.tick_params(colors=TUMSI)
    ax.spines['bottom'].set_color(TUMSI)
    ax.spines['left'].set_color(TUMSI)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

def html_tabula(df):
    html = "<table style='width:100%; border-collapse:collapse; margin-top:10px;'>"
    html += "<tr style='background-color:#2E5F8A; color:white;'>"
    for col in df.columns:
        html += f"<th style='padding:10px; text-align:left;'>{col}</th>"
    html += "</tr>"
    for i, row in df.iterrows():
        bg = "#F0F7F0" if i % 2 == 0 else "white"
        html += f"<tr style='background-color:{bg};'>"
        for val in row:
            html += f"<td style='padding:10px; color:#1B2A4A;'>{val}</td>"
        html += "</tr>"
    html += "</table>"
    return html

# ═══════════════════════════════
# 1. RINDA — VIRSRAKSTS
# ═══════════════════════════════
st.markdown("<h1>🎬 TMDB Datu Analīze</h1>", unsafe_allow_html=True)
st.markdown("---")

# ═══════════════════════════════
# 2. RINDA — KARTĪTES
# ═══════════════════════════════
try:
    filmu_skaits  = run_query("SELECT COUNT(*) as n FROM movies", "tmdb")[0]['n']
    videjais      = run_query("SELECT ROUND(AVG(vote_average),1) as n FROM movies", "tmdb")[0]['n']
    zanri_skaits  = run_query("SELECT COUNT(*) as n FROM genres", "tmdb")[0]['n']
    aktieri_skaits = run_query("SELECT COUNT(DISTINCT id_person) as n FROM movie_cast", "tmdb")[0]['n']

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='metric-card'><div class='metric-number'>{filmu_skaits}</div><div class='metric-label'>🎬 Filmas</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><div class='metric-number'>{videjais}</div><div class='metric-label'>⭐ Vērtējums</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'><div class='metric-number'>{zanri_skaits}</div><div class='metric-label'>🎭 Žanri</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric-card'><div class='metric-number'>{aktieri_skaits:,}</div><div class='metric-label'>👤 Aktieri</div></div>", unsafe_allow_html=True)
except Exception as e:
    st.error(f"❌ Nevar ielādēt statistiku: {e}")

st.markdown("---")

# ═══════════════════════════════
# 3. RINDA — 3 GRAFIKI
# ═══════════════════════════════
g1, g2, g3 = st.columns(3)

with g1:
    st.markdown("### 🎭 Populārākie žanri")
    try:
        dati = run_query("""
            SELECT g.name AS Žanrs, COUNT(mg.id_movie) AS Skaits
            FROM genres g
            JOIN movie_genre mg ON g.id_genre = mg.id_genre
            GROUP BY g.name ORDER BY Skaits DESC LIMIT 8
        """, "tmdb")
        df = pd.DataFrame(dati)
        fig, ax = plt.subplots(figsize=(4, 4))
        grafiks_setup(fig, ax, "")
        ax.barh(df['Žanrs'], df['Skaits'], color=ZALS)
        ax.tick_params(colors=TUMSI)
        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.error(f"❌ Kļūda: {e}")

with g2:
    st.markdown("### 📅 Filmas pa gadiem")
    try:
        dati = run_query("""
            SELECT SUBSTRING(release_date, 1, 4) AS Gads, COUNT(*) AS Skaits
            FROM movies
            WHERE release_date IS NOT NULL AND release_date != ''
            AND SUBSTRING(release_date, 1, 4) >= '2015'
            GROUP BY Gads ORDER BY Gads
        """, "tmdb")
        df = pd.DataFrame(dati)
        fig, ax = plt.subplots(figsize=(4, 4))
        grafiks_setup(fig, ax, "")
        ax.plot(df['Gads'], df['Skaits'], marker="o", color=ORANSS, linewidth=2)
        ax.fill_between(df['Gads'], df['Skaits'], alpha=0.3, color=ZALS)
        plt.xticks(rotation=45, color=TUMSI)
        plt.yticks(color=TUMSI)
        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.error(f"❌ Kļūda: {e}")

with g3:
    st.markdown("### 🌍 Top valodas")
    try:
        dati = run_query("""
            SELECT original_language AS Valoda, COUNT(*) AS Skaits
            FROM movies
            GROUP BY Valoda ORDER BY Skaits DESC LIMIT 6
        """, "tmdb")
        df = pd.DataFrame(dati)
        fig, ax = plt.subplots(figsize=(4, 4))
        fig.patch.set_alpha(0)
        krāsas = [ZALS, ORANSS, ZILS, "#FFD700", "#FF6347", "#9B59B6"]
        ax.pie(df['Skaits'], labels=df['Valoda'], autopct="%1.1f%%",
               colors=krāsas, textprops={'color': TUMSI})
        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.error(f"❌ Kļūda: {e}")

st.markdown("---")

# ═══════════════════════════════
# 4. RINDA — INTERAKTĪVAIS LAUKS
# ═══════════════════════════════
st.markdown("### 💬 Uzdod savu jautājumu")

col_l, col_r = st.columns([2, 1])
with col_l:
    jautajums = st.text_input("Jautājums:", placeholder="Piemēram: Kuras 10 filmas ir ar augstāko vērtējumu?")
with col_r:
    grafika_tips = st.selectbox("📊 Grafiks:", ["Tabula", "Stabiņu grafiks", "Līniju grafiks", "Sektoru grafiks"])

if st.button("🔍 Analizēt") and jautajums:
    with st.spinner("⏳ Strādājam..."):
        db_context = get_db_context("tmdb")
        sql_prompt = f"""Tev ir šāda MySQL datubāze:
{db_context}
Uzraksti SQL vaicājumu: {jautajums}
Prasības:
- Tikai SELECT
- Tikai SQL kods bez paskaidrojumiem
- Kolonnu nosaukumiem izmanto latviskas etiķetes ar AS, piemēram: SELECT title AS Nosaukums
"""
        sql = ask_gemini(sql_prompt)
        if sql:
            sql = sql.replace("```sql", "").replace("```", "").strip()

    if not sql:
        st.warning("🤖 AI šobrīd nav pieejams. Mēģini vēlreiz!")
    else:
        try:
            dati = run_query(sql, "tmdb")
            if not dati:
                st.info("🔍 Netika atrasti dati par šo jautājumu.")
            else:
                df = pd.DataFrame(dati)
                if grafika_tips == "Tabula":
                    st.markdown(html_tabula(df), unsafe_allow_html=True)
                elif len(df.columns) >= 2:
                    x_kol = df.columns[0]
                    y_kol = df.columns[1]
                    fig, ax = plt.subplots(figsize=(10, 4))
                    grafiks_setup(fig, ax, jautajums)
                    if grafika_tips == "Stabiņu grafiks":
                        ax.bar(df[x_kol].astype(str), df[y_kol], color=ZALS)
                        plt.xticks(rotation=45, ha="right", color=TUMSI)
                        plt.yticks(color=TUMSI)
                    elif grafika_tips == "Līniju grafiks":
                        ax.plot(df[x_kol].astype(str), df[y_kol], marker="o", color=ORANSS)
                        plt.xticks(rotation=45, ha="right", color=TUMSI)
                        plt.yticks(color=TUMSI)
                    elif grafika_tips == "Sektoru grafiks":
                        ax.pie(df[y_kol], labels=df[x_kol].astype(str), autopct="%1.1f%%",
                               colors=[ZALS, ORANSS, ZILS, "#FFD700", "#FF6347"])
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.warning("⚠️ Lūdzu precizē jautājumu!")

                apraksts = ask_gemini(f"""Apraksti šos datus latviešu valodā 2-3 teikumos.
Jautājums: {jautajums}
Dati: {str(dati[:10])}""")
                if apraksts:
                    st.info(apraksts)

        except Exception as e:
            st.error("❌ Neizdevās iegūt datus. Mēģini pārfrāzēt jautājumu!")
