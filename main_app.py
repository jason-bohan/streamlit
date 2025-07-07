# main.py — Navigation hub
import streamlit as st
from poker_simulator_app import render_poker_simulator
from gto_range_viewer_ui import render_gto_range_viewer

PAGES = {
    "Simulator": "♠ Multi-Way Poker Equity & Kelly Betting Simulator",
    "GTO Viewer": "📊 GTO Range Viewer"
}

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

if selection == "Simulator":
    st.title(PAGES["Simulator"])
    render_poker_simulator()

elif selection == "GTO Viewer":
    st.title(PAGES["GTO Viewer"])
    render_gto_range_viewer()
