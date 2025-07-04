
import streamlit as st
from treys import Card, Evaluator, Deck
import random

# ---------- Session State Initialization ----------
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 100.0

if 'pot_size' not in st.session_state:
    st.session_state.pot_size = 0.0

if 'hands_played' not in st.session_state:
    st.session_state.hands_played = 0

if 'history' not in st.session_state:
    st.session_state.history = []

# ---------- Card Selection UI ----------
suits = ['s', 'h', 'd', 'c']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
card_options = [r + s for r in ranks for s in suits]

st.title("♠ Poker Equity & Kelly Betting Simulator")

col1, col2 = st.columns(2)
with col1:
    hero_card1 = st.selectbox("Hero Card 1", card_options)
    hero_card2 = st.selectbox("Hero Card 2", [c for c in card_options if c != hero_card1])
hero_hand = [hero_card1, hero_card2]

st.subheader("🃏 Community Board")
board = []
cols = st.columns(5)
for i in range(5):
    card = cols[i].selectbox(f"Board {i+1}", [""] + [c for c in card_options if c not in hero_hand + board], key=f"board{i}")
    if card:
        board.append(card)

# ---------- Equity Estimator ----------
def estimate_equity(hero_hand, board, num_simulations=500):
    evaluator = Evaluator()
    wins = 0
    total = 0
    for _ in range(num_simulations):
        deck = Deck()
        for c in hero_hand + board:
            deck.cards.remove(Card.new(c))

        villain_hand = [deck.draw(1)[0], deck.draw(1)[0]]
        full_board = board + [Card.int_to_str(c) for c in deck.draw(5 - len(board))]

        hero_score = evaluator.evaluate([Card.new(c) for c in full_board], [Card.new(c) for c in hero_hand])
        villain_score = evaluator.evaluate([Card.new(c) for c in full_board], villain_hand)

        if hero_score < villain_score:
            wins += 1
        total += 1
    return wins / total if total > 0 else 0

# ---------- Kelly Betting UI ----------
if st.button("🧮 Calculate Equity & Suggest Bet"):
    equity = estimate_equity(hero_hand, board)
    st.metric(label="Estimated Hero Equity vs 1 Villain", value=f"{equity*100:.2f}%")

    # User bankroll reset
    starting_bankroll = st.selectbox("Reset Starting Bankroll", [50, 100, 250, 500], index=1)
    if st.button("🔄 Reset Bankroll"):
        st.session_state.bankroll = float(starting_bankroll)
        st.session_state.pot_size = 0.0
        st.session_state.hands_played = 0
        st.session_state.history.clear()
        st.success(f"Bankroll reset to ${starting_bankroll}")

    # Kelly inputs
    pot_size = st.number_input("Current Pot Size ($)", min_value=0.01, value=10.0, step=0.5, format="%.2f")
    call_amount = st.number_input("Amount to Call ($)", min_value=0.01, value=5.0, step=0.5, format="%.2f")
    use_half_kelly = st.toggle("Use Half Kelly", value=True)
    bankroll = st.session_state.bankroll

    net_odds = pot_size / call_amount
    kelly_fraction = ((net_odds * equity) - (1 - equity)) / net_odds
    kelly_fraction = max(0, round(kelly_fraction, 4))

    if use_half_kelly:
        kelly_fraction /= 2

    suggested_bet = round(kelly_fraction * bankroll, 2)

    st.write(f"📦 Current Bankroll: ${bankroll:.2f}")
    st.write(f"📊 Pot Odds: {call_amount / (pot_size + call_amount):.2%}")
    st.write(f"📈 Kelly Fraction: {kelly_fraction:.2%} {'(Half Kelly)' if use_half_kelly else '(Full Kelly)'}")
    st.success(f"💵 Suggested Bet: ${suggested_bet}")

    if st.button("Apply Bet"):
        st.session_state.bankroll -= suggested_bet
        st.session_state.pot_size += suggested_bet
        st.session_state.hands_played += 1
        st.session_state.history.append({
            "Hand": st.session_state.hands_played,
            "Bet": suggested_bet,
            "Equity": round(equity * 100, 2),
            "Bankroll": st.session_state.bankroll
        })
        st.success(f"Bet ${suggested_bet} applied. Pot is now ${st.session_state.pot_size:.2f}")

# ---------- History Viewer ----------
if st.checkbox("📜 Show Hand History"):
    for h in reversed(st.session_state.history[-10:]):
        st.write(f"🃏 Hand {h['Hand']}: Equity {h['Equity']}%, Bet ${h['Bet']} → Bankroll: ${h['Bankroll']}")
