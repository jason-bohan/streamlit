from db import save_hand
import random

for i in range(1, 21):
    save_hand(
        hand=i,
        bet=round(random.uniform(1, 5), 2),
        equity=round(random.uniform(0.3, 0.8) * 100, 2),
        bankroll=round(100 - i * random.uniform(1, 2), 2)
    )
