import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os

st.set_page_config(page_title="Søvn og Karakterer", layout="centered")

# Navigationsmenu i sidebaren
side = st.sidebar.radio("Vælg visning", ["Besvar Spørgeskema", "Se Data"])

# Filnavn hvor data gemmes
datafil = "besvarelser.json"

# Hjælpefunktion til at omkode søvnintervaller og karakterer
def soevn_til_tal(s):
    mapping = {
        "Under 5 timer": 4.5,
        "5-6 timer": 5.5,
        "7-8 timer": 7.5,
        "Mere end 8 timer": 9.0
    }
    return mapping.get(s, None)

def karakter_til_tal(k):
    mapping = {
        "-3": -3,
        "00": 0,
        "02": 2,
        "4": 4,
        "7": 7,
        "10": 10,
        "12": 12
    }
    return mapping.get(k, None)

# ----------------------
# SIDE 1: BESVAR SPØRGESKEMA
# ----------------------
if side == "Besvar Spørgeskema":
    st.title("Spørgeskema: Søvn og Præstation")
    st.markdown("Udfyld felterne nedenfor og klik på 'Indsend'.")

    soevn = st.radio("Hvor mange timer søvn får du gennemsnitligt på en skoledag?", [
        "", "Under 5 timer", "5-6 timer", "7-8 timer", "Mere end 8 timer"
    ])

    skaermtid = st.radio("Hvor lang tid før sengetid bruger du typisk skærm?", [
        "", "Under 30 min", "30-60 min", "1-2 timer", "Mere end 2 timer"
    ])

    skriftlig = st.radio("Hvordan præsterer du typisk i skriftlige prøver?", [
        "", "Meget godt", "Godt", "Middel", "Dårligt", "Meget dårligt"
    ])

    mundtlig = st.radio("Hvordan præsterer du typisk i mundtlige prøver?", [
        "", "Meget godt", "Godt", "Middel", "Dårligt", "Meget dårligt"
    ])

    karakter = st.selectbox("Hvilken karakter er den, du får flest af?", [
        "", "-3", "00", "02", "4", "7", "10", "12"
    ])

    if st.button("Indsend"):
        if "" in [soevn, skaermtid, skriftlig, mundtlig, karakter]:
            st.warning("Udfyld venligst alle spørgsmål, før du indsender.")
        else:
            svar = {
                "Søvn": soevn,
                "Skærmtid": skaermtid,
                "Skriftlig præstation": skriftlig,
                "Mundtlig præstation": mundtlig,
                "Mest almindelige karakter": karakter
            }

            if os.path.exists(datafil):
                with open(datafil, "r") as f:
                    data = json.load(f)
            else:
                data = []

            data.append(svar)

            with open(datafil, "w") as f:
                json.dump(data, f, indent=4)

            st.success("Tak for dit svar! Dine data er nu gemt.")

    # Mulighed for at nulstille data
    if st.button("Nulstil alle data"):
        if os.path.exists(datafil):
            os.remove(datafil)
            st.success("Alle data er blevet slettet.")
        else:
            st.info("Der var ingen data at slette.")

# ----------------------
# SIDE 2: SE DATA
# ----------------------
elif side == "Se Data":
    st.title("Dataanalyse")

    if os.path.exists(datafil):
        with open(datafil, "r") as f:
            df = pd.DataFrame(json.load(f))

        st.subheader("Alle besvarelser")
        st.dataframe(df)

        st.subheader("Fordeling af karakterer")
        karakter_fordeling = df["Mest almindelige karakter"].value_counts().sort_index()
        fig1, ax1 = plt.subplots()
        karakter_fordeling.plot(kind="bar", ax=ax1, color="#18351f")
        ax1.set_xlabel("Karakter")
        ax1.set_ylabel("Antal")
        ax1.set_title("Hyppigst opnåede karakterer blandt deltagerne")
        st.pyplot(fig1)

        # Omkode til tal og beregn gennemsnit
        df["Søvn (tal)"] = df["Søvn"].apply(soevn_til_tal)
        df["Karakter (tal)"] = df["Mest almindelige karakter"].apply(karakter_til_tal)

        if df["Søvn (tal)"].notnull().any() and df["Karakter (tal)"].notnull().any():
            st.subheader("Søvn og karakter (scatterplot)")
            fig2, ax2 = plt.subplots()
            ax2.scatter(df["Søvn (tal)"], df["Karakter (tal)"])
            ax2.set_xlabel("Søvn (timer)")
            ax2.set_ylabel("Karakter")
            ax2.set_title("Sammenhæng mellem søvn og karakter")
            st.pyplot(fig2)

            st.subheader("Gennemsnitlige karakterer pr. søvnmængde")
            gruppet = df.groupby("Søvn (tal)")["Karakter (tal)"].mean()
            fig3, ax3 = plt.subplots()
            gruppet.plot(kind="bar", ax=ax3, color="#18351f")
            ax3.set_xlabel("Søvn (timer)")
            ax3.set_ylabel("Gennemsnitlig karakter")
            ax3.set_title("Karaktergennemsnit fordelt på søvnmængde")
            st.pyplot(fig3)

    else:
        st.warning("Der er endnu ingen data. Udfyld spørgeskemaet først.")