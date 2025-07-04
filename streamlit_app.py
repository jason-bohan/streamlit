import streamlit as st
from utils.poker_engine import PokerSimulator

# Define player profiles
player_profiles = {
    "Hero": st.selectbox("Hero Profile", ["tight-aggressive", "loose-aggressive", "loose-passive", "maniac", "nit"]),
    "Villain1": st.selectbox("Villain 1 Profile", ["tight-aggressive", "loose-aggressive", "loose-passive", "maniac", "nit"]),
    "Villain2": st.selectbox("Villain 2 Profile", ["tight-aggressive", "loose-aggressive", "loose-passive", "maniac", "nit"]),
    "Villain3": st.selectbox("Villain 3 Profile", ["tight-aggressive", "loose-aggressive", "loose-passive", "maniac", "nit"])
}

st.title("♠ Poker Hand Simulator")

if st.button("🎲 Deal Hand"):
    sim = PokerSimulator(player_profiles)
    result = sim.simulate_hand()

    st.subheader("🃏 Community Board")
    st.write(" ".join(result["board"]))

    st.subheader("👥 Players & Hands")
    for player, hand in result["hands"].items():
        st.write(f"{player}: {' '.join(hand)} — Score: {result['scores'][player]}")

    st.success(f"🏆 Winner: {result['winner']}")