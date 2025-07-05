import streamlit as st
from treys import Card, Evaluator, Deck
from db import save_hand, get_hand_history, clear_history
import random
import matplotlib.pyplot as plt
import pandas as pd
from preflop_rules import preflop_rules
from preflop_actions import preflop_actions

# ---------- Session State Initialization ----------
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 100.0
if 'pot_size' not in st.session_state:
    st.session_state.pot_size = 0.01
if 'hands_played' not in st.session_state:
    st.session_state.hands_played = 0
if 'history' not in st.session_state:
    st.session_state.history = []


# ---------- Card Options ----------
suits = ['s', 'h', 'd', 'c']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
card_options = [r + s for r in ranks for s in suits]

# ---------- UI for Hero Hand ----------
st.title("♠ Multi-Way Poker Equity & Kelly Betting Simulator")
# ---------- Hero Pre-Flop Strategy ----------
st.subheader("🧑‍💼 Hero Pre-Flop Strategy")
hero_preflop_type = st.selectbox(
    "Select Your Pre-Flop Strategy",
    options=list(preflop_rules.keys()),
    key="hero_preflop_type"
)
st.caption(f"Rule: {preflop_rules[hero_preflop_type]}")

col1, col2 = st.columns(2)
with col1:
    hero_card1 = st.selectbox("Hero Card 1", card_options)
    hero_card2 = st.selectbox("Hero Card 2", [c for c in card_options if c != hero_card1])
hero_hand = [hero_card1, hero_card2]

# ---------- Board Input ----------
st.subheader("🃏 Community Board")
board = []
cols = st.columns(5)
for i in range(5):
    card = cols[i].selectbox(f"Board {i+1}", [""] + [c for c in card_options if c not in hero_hand + board], key=f"board{i}")
    if card:
        board.append(card)

# ---------- Villain Range Input ----------
st.subheader("👥 Villain Ranges")
num_villains = st.slider("Number of Villains", 1, 5, 2)

# Define preset ranges for each type
villain_range_types = {
    "Tight": "22+, AJ+, KQ, ATs+, KJs+, QJs",
    "Aggressive": "Any pair, any broadway, suited connectors 54s+, any ace",
    "Loose": "Any two cards",
    "Random": "random"
}

villain_ranges = []
for i in range(num_villains):
    range_type = st.selectbox(
        f"Villain {i+1} Range Type",
        options=list(villain_range_types.keys()),
        key=f"villain_type_{i}"
    )
    villain_ranges.append(villain_range_types[range_type])

# ---------- Monte Carlo Multi-way Equity Estimator ----------
def estimate_equity_multiway(hero_hand, board, num_simulations=500, num_villains=2):
    evaluator = Evaluator()
    hero_wins = 0
    ties = 0

    for _ in range(num_simulations):
        deck = Deck()
        for c in hero_hand + board:
            deck.cards.remove(Card.new(c))

        hero = [Card.new(c) for c in hero_hand]
        villains = [[deck.draw(1)[0], deck.draw(1)[0]] for _ in range(num_villains)]
        full_board = board + [Card.int_to_str(c) for c in deck.draw(5 - len(board))]
        full_board_cards = [Card.new(c) for c in full_board]

        scores = [evaluator.evaluate(full_board_cards, hero)]
        for v in villains:
            scores.append(evaluator.evaluate(full_board_cards, v))

        if scores[0] == min(scores):
            if scores.count(scores[0]) == 1:
                hero_wins += 1
            else:
                ties += 1

    return (hero_wins + ties * 0.5) / num_simulations

def get_hand_notation(card1, card2):
    r1, s1 = card1[0], card1[1]
    r2, s2 = card2[0], card2[1]
    if r1 == r2:
        return r1 + r2  # e.g., "AA"
    suited = "s" if s1 == s2 else "o"
    # Sort ranks for standard notation (AK, not KA)
    ranks = "".join(sorted([r1, r2], reverse=True))
    return ranks + suited

# ---------- Equity & Kelly Section ----------
with st.form("kelly_form"):
    pot_size = st.number_input(
        "Current Pot Size ($)",
        min_value=0.01,
        value=max(st.session_state.pot_size, 0.01),
        step=0.5,
        format="%.2f"
    )
    call_amount = st.number_input("Amount to Call ($)", min_value=0.01, value=5.0, step=0.5, format="%.2f")
    use_half_kelly = st.toggle("Use Half Kelly", value=True)
    
    preset_options = [50, 100, 250, 500, "Custom..."]
    starting_bankroll_choice = st.selectbox("Reset Starting Bankroll", preset_options, index=1)
    if starting_bankroll_choice == "Custom...":
        custom_bankroll = st.number_input("Enter Custom Bankroll", min_value=1.0, value=100.0, step=1.0, format="%.2f")
        starting_bankroll = custom_bankroll
    else:
        starting_bankroll = float(starting_bankroll_choice)
    
    calculate = st.form_submit_button("🧮 Calculate Equity & Suggest Bet")
    apply_bet = st.form_submit_button("Apply Bet")
    reset = st.form_submit_button("🔄 Reset Bankroll")

if reset:
    st.session_state.bankroll = float(starting_bankroll)
    st.session_state.pot_size = 0.01
    st.session_state.hands_played = 0
    st.session_state.history.clear()
    clear_history()

# Sync the input value to session state if changed
if pot_size != st.session_state.pot_size:
    st.session_state.pot_size = pot_size

if calculate:
    equity = estimate_equity_multiway(hero_hand, board, num_simulations=500, num_villains=num_villains)
    st.session_state.equity = equity
    bankroll = st.session_state.bankroll
    net_odds = pot_size / call_amount
    kelly_fraction = ((net_odds * equity) - (1 - equity)) / net_odds
    kelly_fraction = max(0, round(kelly_fraction, 4))
    if use_half_kelly:
        kelly_fraction /= 2
    suggested_bet = round(kelly_fraction * bankroll, 2)
    st.session_state.suggested_bet = suggested_bet
    st.write(f"📦 Current Bankroll: ${bankroll:.2f}")
    st.write(f"📊 Pot Odds: {call_amount / (pot_size + call_amount):.2%}")
    st.write(f"📈 Kelly Fraction: {kelly_fraction:.2%} {'(Half Kelly)' if use_half_kelly else '(Full Kelly)'}")
    hero_hand_notation = get_hand_notation(hero_card1, hero_card2)
    strategy = hero_preflop_type
    action = preflop_actions.get(strategy, {}).get(hero_hand_notation, preflop_actions.get(strategy, {}).get("Any", "Check"))

    if action == "All-in":
        suggested_bet = st.session_state.bankroll
        st.session_state.suggested_bet = suggested_bet
    elif action.startswith("Raise"):
        try:
            multiplier = float(action.split()[1][:-1])  # e.g., "4x" -> 4
        except Exception:
            multiplier = 3
        suggested_bet = round(multiplier * call_amount, 2)
        st.session_state.suggested_bet = suggested_bet
    elif action == "Fold":
        suggested_bet = 0.0
        st.session_state.suggested_bet = suggested_bet
    else:
        # fallback to Kelly
        net_odds = pot_size / call_amount
        kelly_fraction = ((net_odds * equity) - (1 - equity)) / net_odds
        kelly_fraction = max(0, round(kelly_fraction, 4))
        if use_half_kelly:
            kelly_fraction /= 2
        suggested_bet = round(kelly_fraction * bankroll, 2)
        st.session_state.suggested_bet = suggested_bet

    st.info(f"Preflop Action ({strategy}): {action}")
    st.success(f"💵 Suggested Bet: ${suggested_bet}")

if apply_bet:
    suggested_bet = st.session_state.get("suggested_bet", 0)
    equity = st.session_state.get("equity", 0)
    st.session_state.bankroll -= suggested_bet
    st.session_state.pot_size += suggested_bet
    st.session_state.hands_played += 1
    equity_pct = round(equity * 100, 2)
    st.session_state.history.append({
        "Hand": st.session_state.hands_played,
        "Bet": suggested_bet,
        "Equity": equity_pct,
        "Bankroll": st.session_state.bankroll
    })
    st.write(f"Saving to DB: hand={st.session_state.hands_played}, bet={suggested_bet}, equity={equity_pct}, bankroll={st.session_state.bankroll}")
    try:
        save_hand(
            st.session_state.hands_played,
            suggested_bet,
            equity_pct,
            st.session_state.bankroll
        )
    except Exception as e:
        st.error(f"Failed to save hand to the database: {e}")
    st.success(f"Bet ${suggested_bet} applied. Pot is now ${st.session_state.pot_size:.2f}")

# ---------- History & Chart ----------
if st.checkbox("📜 Show Hand History and Bankroll Chart"):
    rows = get_hand_history()
    hist_df = pd.DataFrame(rows, columns=["id", "hand", "bet", "equity", "bankroll", "created_at"])
    if not hist_df.empty:
        # Convert bankroll and bet to float for plotting
        hist_df["bankroll"] = hist_df["bankroll"].astype(float)
        hist_df["bet"] = hist_df["bet"].astype(float)
        hist_df["equity"] = hist_df["equity"].astype(float)
        st.line_chart(hist_df.set_index("hand")[["bankroll"]])
        st.dataframe(hist_df)

