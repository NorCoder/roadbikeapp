import pandas as pd
import streamlit as st

from search_sources import SOURCES, build_query, search_all_sources


st.set_page_config(page_title="Sykkelsøk", page_icon="🚲", layout="wide")

st.title("🚲 Søk etter Cannondale Supersix Evo")
st.write(
    "Denne appen søker på FINN.no og relevante norske nettbutikker/markedsplasser "
    "etter ønsket modell, farge og størrelse."
)

with st.sidebar:
    st.header("Søkekriterier")
    model = st.text_input("Modell", value="Cannondale Supersix Evo 6 2026")
    color = st.text_input("Farge", value="Cashmere")
    size = st.text_input("Størrelse", value="56")
    max_per_source = st.slider("Maks treff per kilde", 5, 40, 20)

query = build_query(model=model, color=color, size=size)
st.info(f"Søketekst: **{query}**")

if st.button("Søk nå", type="primary"):
    with st.spinner("Henter treff fra kilder..."):
        listings = search_all_sources(
            model=model,
            color=color,
            size=size,
            max_items_per_source=max_per_source,
        )

    if not listings:
        st.warning(
            "Fant ingen tydelige treff akkurat nå. Prøv å justere søketekst, "
            "eller åpne direkte søkelenker under."
        )

    rows = [
        {
            "Kilde": item.source,
            "Tittel": item.title,
            "Pris (hvis funnet)": item.price or "-",
            "Lenke": item.url,
        }
        for item in listings
    ]

    if rows:
        df = pd.DataFrame(rows)
        st.success(f"Fant {len(df)} potensielle treff.")
        st.dataframe(df, use_container_width=True)

        st.subheader("Klikkbare treff")
        for r in rows:
            st.markdown(f"- **{r['Kilde']}**: [{r['Tittel']}]({r['Lenke']}) — {r['Pris (hvis funnet)']}")

st.subheader("Direkte søkelenker")
for source in SOURCES:
    st.markdown(f"- **{source.name}**: {source.search_url(query)}")

st.caption(
    "Tips: Markedsplasser endrer ofte HTML-struktur. Hvis automatisk uthenting blir tom, "
    "fungerer de direkte søkelenkene fortsatt."
)
