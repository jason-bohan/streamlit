import streamlit as st
from treys import Card, Evaluator, Deck
import random

# Helper: generate card dropdown options
suits = ['s', 'h', 'd', 'c']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
card_options = [r + s for r in ranks for s in suits]

def to_int_card(card_str):
    return Card.new(card_str)

def pretty(card_strs):
    return [Card.int_to_pretty_str(Card.new(c)) for c in card_strs]

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

st.title("♠ Poker Equity Simulator")

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

if st.button("🧮 Calculate Equity"):
    equity = estimate_equity(hero_hand, board)
    st.metric(label="Estimated Hero Equity vs 1 Villain", value=f"{equity*100:.2f}%")

    # --- Kelly Betting Suggestion ---
    st.subheader("💰 Kelly Betting Suggestion")

    # Pot and Call size input
    pot_size = st.number_input("Current Pot Size ($)", min_value=0.01, value=10.0, step=0.5, format="%.2f")
    call_amount = st.number_input("Amount to Call ($)", min_value=0.01, value=5.0, step=0.5, format="%.2f")
    bankroll = st.number_input("Your Bankroll ($)", min_value=1.0, value=100.0, step=1.0, format="%.2f")

    # Toggle for Half Kelly
    use_half_kelly = st.toggle("Use Half Kelly", value=True)

    # Net odds (b) = amount won / amount bet
    net_odds = pot_size / call_amount
    kelly_fraction = ((net_odds * equity) - (1 - equity)) / net_odds
    kelly_fraction = max(0, round(kelly_fraction, 4))  # Clamp at 0

    if use_half_kelly:
        kelly_fraction /= 2

    suggested_bet = round(kelly_fraction * bankroll, 2)

    # Display output
    st.write(f"📊 Pot Odds: {call_amount / (pot_size + call_amount):.2%}")
    st.write(f"📈 Kelly Fraction: {kelly_fraction:.2%} {'(Half Kelly)' if use_half_kelly else '(Full Kelly)'}")
    st.success(f"💵 Suggested Bet: ${suggested_bet}")
