# full_poker_streamlit.py — Complete with Position Tracking
import streamlit as st
from treys import Card, Evaluator, Deck
from db import save_hand, get_hand_history, clear_history
import random
import matplotlib.pyplot as plt
import pandas as pd
import json
import os

from postflop_actions import postflop_actions
from preflop_rules import preflop_rules
from preflop_actions import preflop_actions

def categorize_flop(board):
    ranks = [card[0] for card in board]
    suits = [card[1] for card in board]
    unique_ranks = set(ranks)
    unique_suits = set(suits)
    is_paired = len(unique_ranks) < 3
    is_monotone = len(unique_suits) == 1
    is_rainbow = len(unique_suits) == 3
    is_two_tone = len(unique_suits) == 2
    has_ace = "A" in ranks
    high_cards = {"J", "Q", "K", "T", "9"}
    has_broadway = any(r in high_cards for r in ranks)
    is_connected = False
    try:
        rank_order = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        idxs = sorted([rank_order.index(r) for r in ranks])
        is_connected = idxs[2] - idxs[0] <= 4
    except Exception:
        pass
    if is_paired and is_rainbow:
        return "PairedRainbow"
    if has_ace and is_monotone:
        return "AceHighMonotone"
    if has_ace and is_rainbow:
        return "DryAceHigh"
    if has_broadway and is_two_tone and is_connected:
        return "WetBroadway"
    if is_connected and is_two_tone and not has_ace:
        return "LowConnectedTwoTone"
    if is_paired and not has_ace:
        return "StaticMidPair"
    return "Generic"

def get_hand_notation(card1, card2):
    r1, s1 = card1[0], card1[1]
    r2, s2 = card2[0], card2[1]
    if r1 == r2:
        return r1 + r2
    suited = "s" if s1 == s2 else "o"
    rank_order = {"A": 14, "K": 13, "Q": 12, "J": 11, "T": 10,
                  "9": 9, "8": 8, "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2}
    if rank_order[r1] > rank_order[r2]:
        ranks = r1 + r2
    else:
        ranks = r2 + r1
    return ranks + suited

# Session State Init
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 100.0
if 'pot_size' not in st.session_state:
    st.session_state.pot_size = 0.01
if 'hands_played' not in st.session_state:
    st.session_state.hands_played = 0
if 'history' not in st.session_state:
    st.session_state.history = []
if 'position_index' not in st.session_state:
    st.session_state.position_index = 0

# GTO Load
suits = ['s', 'h', 'd', 'c']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
card_options = [r + s for r in ranks for s in suits]

GTO_JSON_PATH = os.path.join(os.path.dirname(__file__), "gto_strategy_9max.json")
try:
    with open(GTO_JSON_PATH, "r") as f:
        gto_data = json.load(f)
    if "GTO" in gto_data:
        preflop_actions["GTO"] = gto_data["GTO"]
        preflop_rules["GTO"] = "Game Theory Optimal (9-max)"
except Exception as e:
    st.warning(f"Failed to load GTO strategy: {e}")

# UI Starts
st.title("♠ Multi-Way Poker Equity & Kelly Betting Simulator")

st.subheader("🧑‍💼 Hero Pre-Flop Strategy")
hero_preflop_type = st.selectbox("Select Your Pre-Flop Strategy", options=list(preflop_rules.keys()), key="hero_preflop_type")
st.caption(f"Rule: {preflop_rules[hero_preflop_type]}")

positions = ["UTG", "UTG+1", "MP", "MP+1", "HJ", "CO", "BTN", "SB", "BB"]
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button("➡ Next Position"):
        st.session_state.position_index += 1
        st.rerun()
with col2:
    if st.button("⬅ Previous Position"):
        st.session_state.position_index -= 1
        st.rerun()
with col3:
    st.markdown(f"**Current Position**: `{positions[st.session_state.position_index % len(positions)]}`")
hero_position = positions[st.session_state.position_index % len(positions)]

# Hero hand input
c1, c2 = st.columns(2)
with c1:
    hero_card1 = st.selectbox("Hero Card 1", card_options)
    hero_card2 = st.selectbox("Hero Card 2", [c for c in card_options if c != hero_card1])
hero_hand = [hero_card1, hero_card2]

# Board input
st.subheader("🃏 Community Board")
board = []
bcols = st.columns(5)
for i in range(5):
    card = bcols[i].selectbox(f"Board {i+1}", [""] + [c for c in card_options if c not in hero_hand + board], key=f"board{i}")
    if card:
        board.append(card)

# Villains
st.subheader("👥 Villain Ranges")
num_villains = st.slider("Number of Villains", 1, 5, 2)
villain_range_types = {
    "Tight": "22+, AJ+, KQ, ATs+, KJs+, QJs",
    "Aggressive": "Any pair, any broadway, suited connectors 54s+, any ace",
    "Loose": "Any two cards",
    "Random": "random"
}
villain_ranges = [
    st.selectbox(f"Villain {i+1} Range Type", list(villain_range_types.keys()), key=f"villain_type_{i}")
    for i in range(num_villains)
]

# Kelly form
with st.form("kelly_form"):
    pot_size = st.number_input("Current Pot Size ($)", min_value=0.01, value=max(st.session_state.pot_size, 0.01), step=0.5)
    call_amount = st.number_input("Amount to Call ($)", min_value=0.01, value=5.0, step=0.5)
    use_half_kelly = st.toggle("Use Half Kelly", value=True)
    bankroll_choice = st.selectbox("Reset Starting Bankroll", [50, 100, 250, 500, "Custom..."], index=1)
    starting_bankroll = st.number_input("Enter Custom Bankroll", min_value=1.0, value=100.0, step=1.0) if bankroll_choice == "Custom..." else float(bankroll_choice)
    calculate = st.form_submit_button("🧮 Calculate Equity & Suggest Bet")
    apply_bet = st.form_submit_button("Apply Bet")
    reset = st.form_submit_button("🔄 Reset Bankroll")

if reset:
    st.session_state.bankroll = float(starting_bankroll)
    st.session_state.pot_size = 0.01
    st.session_state.hands_played = 0
    st.session_state.history.clear()
    clear_history()

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
        scores = [evaluator.evaluate(full_board_cards, hero)] + [evaluator.evaluate(full_board_cards, v) for v in villains]
        if scores[0] == min(scores):
            hero_wins += 1 if scores.count(scores[0]) == 1 else 0.5
    return hero_wins / num_simulations

if calculate:
    equity = estimate_equity_multiway(hero_hand, board, num_villains=num_villains)
    st.session_state.equity = equity
    net_odds = pot_size / call_amount
    kelly_fraction = ((net_odds * equity) - (1 - equity)) / net_odds
    kelly_fraction = max(0, round(kelly_fraction, 4))
    if use_half_kelly:
        kelly_fraction /= 2
    suggested_bet = round(kelly_fraction * st.session_state.bankroll, 2)

    strategy = hero_preflop_type
    action = "Fold"
    if strategy == "GTO":
        hand_notation = get_hand_notation(hero_card1, hero_card2)
        pos_actions = gto_data["GTO"]["Preflop"].get(hero_position, {})
        for act_type, hands in pos_actions.items():
            if hand_notation in hands or "Any" in hands:
                action = act_type
                break
    else:
        action = preflop_actions.get(strategy, {}).get(get_hand_notation(hero_card1, hero_card2), preflop_actions.get(strategy, {}).get("Any", "Check"))

    if action == "All-in":
        suggested_bet = st.session_state.bankroll
    elif action.startswith("Raise"):
        try:
            multiplier = float(action.split()[1][:-1])
            suggested_bet = round(multiplier * call_amount, 2)
        except:
            suggested_bet = round(3 * call_amount, 2)
    elif action == "Fold":
        suggested_bet = 0.0

    st.session_state.suggested_bet = suggested_bet
    st.info(f"Preflop Action ({strategy} - {hero_position}): {action}")
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
        "Bankroll": st.session_state.bankroll,
        "Position": hero_position
    })
    try:
        save_hand(st.session_state.hands_played, suggested_bet, equity_pct, st.session_state.bankroll, hero_position)
    except Exception as e:
        st.error(f"DB Error: {e}")
    st.success(f"Bet ${suggested_bet} applied. Pot now ${st.session_state.pot_size:.2f}")

if st.checkbox("📜 Show Hand History and Bankroll Chart"):
    rows = get_hand_history()
    hist_df = pd.DataFrame(rows, columns=["id", "hand", "bet", "equity", "bankroll", "position", "created_at"])
    if not hist_df.empty:
        hist_df["bankroll"] = hist_df["bankroll"].astype(float)
        hist_df["bet"] = hist_df["bet"].astype(float)
        hist_df["equity"] = hist_df["equity"].astype(float)
        st.line_chart(hist_df.set_index("hand")["bankroll"])
        st.dataframe(hist_df[["hand", "bet", "equity", "bankroll", "position", "created_at"]])
