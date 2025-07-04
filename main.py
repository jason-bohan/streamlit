from utils.poker_engine import PokerSimulator

player_profiles = {
    "Hero": "tight-aggressive",
    "Villain1": "loose-aggressive",
    "Villain2": "loose-passive",
    "Villain3": "maniac"
}

sim = PokerSimulator(player_profiles)
result = sim.simulate_hand()

print("\n🃏 Community Board:")
print(" ".join(result["board"]))

print("\n👥 Players & Hands:")
for player, hand in result["hands"].items():
    print(f"{player}: {' '.join(hand)} — Score: {result['scores'][player]}")

print(f"\n🏆 Winner: {result['winner']}")
