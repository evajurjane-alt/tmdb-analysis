# 🎬 TMDB Datu Analīze

Interaktīvs datu analīzes dashboard filmām no TMDB datubāzes.

## Ko tas dara?
- Rāda statistiku — filmu skaits, vērtējumi, žanri, aktieri
- Vizualizē datus — žanru popularitāte, filmas pa gadiem, valodas
- Atbild uz jautājumiem latviski izmantojot Gemini AI

## Tehnoloģijas
- Python + Streamlit
- MySQL datubāze
- Google Gemini AI

## Palaišana
1. Uzstādi bibliotēkas: `pip install -r requirements.txt`
2. Iestati `GEMINI_API_KEY` vides mainīgo
3. Palaid: `streamlit run tmdb_dashboard.py`
