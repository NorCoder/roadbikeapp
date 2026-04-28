# Sykkelsøk-app (FINN + nettbutikker)

En enkel Streamlit-app som søker etter:

- **Cannondale Supersix Evo 6 2026**
- farge: **Cashmere**
- størrelse: **56**

…på FINN.no og andre relevante norske kilder.

## Kjør lokalt

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Kilder

Appen søker i dag mot:

- FINN
- Bikeshop
- XXL
- Sykkelkomponenter

## Merk

- Kilder kan endre HTML-struktur, som kan påvirke automatisk uthenting av treff.
- Appen viser derfor også direkte søkelenker per kilde.
