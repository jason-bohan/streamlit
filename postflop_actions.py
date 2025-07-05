def postflop_actions(street, board_category, hand_class):
    if street != "Flop":
        return "Check"  # You can later expand for Turn/River logic

    postflop_data = {
        "PairedRainbow": {
            "Quads": "Check",
            "Trips": "Bet 66%",
            "Overpair": "Bet 50%",
            "Air": "Check"
        },
        "LowConnectedTwoTone": {
            "TopPair": "Bet 50%",
            "Draw (OESD)": "Bet 33%",
            "Air": "Check/Fold"
        },
        "AceHighMonotone": {
            "Flush": "Bet 66%",
            "TopPair": "Check",
            "Air": "Check"
        }
    }

    board_actions = postflop_data.get(board_category)
    if not board_actions:
        return "Unknown board"

    return board_actions.get(hand_class, "Check")  # Default fallback

# Example usage:
action = postflop_actions("Flop", "PairedRainbow", "Trips")
print(action)  # ➝ Bet 66%
