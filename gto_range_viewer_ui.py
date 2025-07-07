# gto_range_viewer_ui.py — Full with interactive strategy display
import streamlit as st
import json
import os

GTO_JSON_PATH = os.path.join(os.path.dirname(__file__), "gto_strategy_9max.json")

def load_gto_strategy():
    try:
        with open(GTO_JSON_PATH, "r") as f:
            return json.load(f)["GTO"]["Preflop"]
    except Exception as e:
        st.error(f"Failed to load GTO strategy: {e}")
        return {}

def display_range(position_data):
    raise_range = position_data.get("Raise", [])
    call_range = position_data.get("Call", [])
    fold_range = position_data.get("Fold", [])
    st.markdown("### Actions by Hand")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### Raise")
        for hand in raise_range:
            st.write(hand)
    with col2:
        st.markdown("#### Call")
        for hand in call_range:
            st.write(hand)
    with col3:
        st.markdown("#### Fold")
        for hand in fold_range:
            st.write(hand)

def render_gto_range_viewer():
    st.title("♠ The Smoothest GTO Range Viewer")
    st.caption("Find the correct strategy for every preflop situation in only 2 clicks.")

    gto_data = load_gto_strategy()

    tabs = st.tabs([
        "General Viewer",
        "Big Blind Defense",
        "3-Bet / Flat",
        "3-Bet Defense",
        "4-Bet Defense",
    ])

    with tabs[0]:
        st.header("General Poker Range Viewer")
        rfi_position = st.selectbox("RFI Position", list(gto_data.keys()))
        _ = st.selectbox("Facing Position", list(gto_data.keys()))
        if rfi_position in gto_data:
            display_range(gto_data[rfi_position])

    with tabs[1]:
        st.header("Big Blind Defense")
        _ = st.selectbox("Who Opened?", ["UTG", "MP", "CO", "BTN", "SB"], key="bb_opener")
        _ = st.selectbox("Opening Size (BB)", ["2.0x", "2.5x", "3.0x"], key="bb_open_size")
        _ = st.selectbox("# Cold Callers", [0, 1, 2], key="bb_num_callers")
        _ = st.multiselect("Cold Caller Positions", ["MP", "CO", "BTN"], key="bb_cold_positions")
        st.markdown("(Stub) Range viewer would visualize BB defense here.")

    with tabs[2]:
        st.header("3-Bet / Flat")
        _ = st.selectbox("Initial Raiser", ["UTG", "MP", "CO"], key="threebet_rfi")
        _ = st.selectbox("You (3-Bet or Flat)", ["MP", "CO", "BTN", "SB", "BB"], key="threebet_hero")
        _ = st.multiselect("Cold Callers Between", ["MP", "CO", "BTN"], key="threebet_between")
        st.markdown("(Stub) Chart for 3-bet/flat ranges would go here.")

    with tabs[3]:
        st.header("3-Bet Defense")
        _ = st.selectbox("Your Position (You RFI'd)", ["UTG", "MP", "CO", "BTN"], key="defense_hero")
        _ = st.selectbox("Facing 3-Bet From", ["CO", "BTN", "SB", "BB"], key="defense_villain")
        st.markdown("(Stub) Show your 3-bet defense strategy here.")

    with tabs[4]:
        st.header("4-Bet Defense")
        _ = st.selectbox("You 3-Bet From", ["MP", "CO", "BTN", "SB"], key="fourbet_hero")
        _ = st.selectbox("Facing 4-Bet From", ["UTG", "MP", "CO", "BTN"], key="fourbet_villain")
        st.markdown("(Stub) Show your response to 4-bets here.")

    st.sidebar.header("GTO Viewer Options")
    sizing_mode = st.sidebar.radio("Strategy Mode", ["Single Sizing", "Multi Sizing"])
    show_rng = st.sidebar.checkbox("Show RNG for Mixed Strategies", value=True)
    st.sidebar.code(f"Mode: {sizing_mode}\nRNG: {show_rng}")