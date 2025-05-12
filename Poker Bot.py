import random
import time
import math
from collections import Counter
from itertools import combinations

RANKS = "23456789TJQKA"
SUITS = "cdhs"
DECK = [r + s for r in RANKS for s in SUITS]

HAND_RANKS = {
    'high': 0,
    'pair': 1,
    '2pair': 2,
    '3kind': 3,
    'straight': 4,
    'flush': 5,
    'fullhouse': 6,
    '4kind': 7,
    'strflush': 8,
    'royal': 9
}

def rank_value(card):
    return RANKS.index(card[0])

def get_deck(exclude):
    return [card for card in DECK if card not in exclude]

def draw_cards(deck, num):
    return random.sample(deck, num)

def simulate_one_game(my_hand, community_cards, unknown_board, opp_hand):
    my_final = my_hand + community_cards + unknown_board
    opp_final = opp_hand + community_cards + unknown_board

    my_rank = evaluate_hand(my_final)
    opp_rank = evaluate_hand(opp_final)

    return my_rank > opp_rank

def generate_opponent_arms(deck, limit=100):
    seen = set()
    arms = []

    while len(arms) < limit:
        opp_hand = tuple(sorted(random.sample(deck, 2)))
        if opp_hand not in seen:
            seen.add(opp_hand)
            arms.append(opp_hand)
    return arms

def evaluate_hand(cards):
    best_rank = (-1,)

    for combo in combinations(cards, 5):
        ranks = [card[0] for card in combo]
        suits = [card[1] for card in combo]
        count = Counter(ranks)
        rank_counts = sorted(count.items(), key=lambda x: (-x[1], -RANKS.index(x[0])))
        rank_values = sorted([RANKS.index(r) for r in ranks], reverse=True)
        flush = len(set(suits)) == 1

        unique_ranks = sorted(set(rank_values), reverse=True)
        is_straight = False
        straight_high = None

        is_straight = False
        straight_high = None
        if len(unique_ranks) >= 5:
            for i in range(len(unique_ranks) - 4):
                window = unique_ranks[i:i+5]
                if all(window[j] - 1 == window[j+1] for j in range(4)):
                    is_straight = True
                    straight_high = window[0]
                    break
                
        if not is_straight and set([12, 0, 1, 2, 3]).issubset(set(rank_values)):
            is_straight = True
            straight_high = 3

        if is_straight and flush:
            if straight_high == 12:
                rank = (HAND_RANKS['royal'],)
            else:
                rank = (HAND_RANKS['strflush'], straight_high)
        elif rank_counts[0][1] == 4:
            rank = (HAND_RANKS['4kind'], RANKS.index(rank_counts[0][0]), RANKS.index(rank_counts[1][0]))
        elif rank_counts[0][1] == 3 and rank_counts[1][1] == 2:
            rank = (HAND_RANKS['fullhouse'], RANKS.index(rank_counts[0][0]), RANKS.index(rank_counts[1][0]))
        elif flush:
            rank = (HAND_RANKS['flush'], rank_values)
        elif is_straight:
            rank = (HAND_RANKS['straight'], straight_high)
        elif rank_counts[0][1] == 3:
            kickers = [RANKS.index(rc[0]) for rc in rank_counts[1:]]
            rank = (HAND_RANKS['3kind'], RANKS.index(rank_counts[0][0]), kickers)
        elif rank_counts[0][1] == 2 and rank_counts[1][1] == 2:
            pair_vals = sorted([RANKS.index(rank_counts[0][0]), RANKS.index(rank_counts[1][0])], reverse=True)
            kicker = RANKS.index(rank_counts[2][0])
            rank = (HAND_RANKS['2pair'], pair_vals[0], pair_vals[1], kicker)
        elif rank_counts[0][1] == 2:
            kickers = [RANKS.index(rc[0]) for rc in rank_counts[1:3]]
            rank = (HAND_RANKS['pair'], RANKS.index(rank_counts[0][0]), kickers)
        else:
            rank = (HAND_RANKS['high'], rank_values)

        best_rank = max(best_rank, rank)

    return best_rank

def monte_carlo_decision(my_hand, community_cards):
    start = time.time()
    wins = {}
    plays = {}
    total_simulations = 0

    used_cards = my_hand + community_cards
    remaining_deck = get_deck(used_cards)

    opponent_arms = generate_opponent_arms(remaining_deck, limit=100)

    for arm in opponent_arms:
        wins[arm] = 0
        plays[arm] = 0

    while time.time() - start < 9.8:
        best_ucb = -float('inf')
        chosen_arm = None

        for arm in opponent_arms:
            if plays[arm] == 0:
                chosen_arm = arm
                break
            win_rate = wins[arm] / plays[arm]
            ucb = win_rate + math.sqrt(2 * math.log(total_simulations + 1) / plays[arm])
            if ucb > best_ucb:
                best_ucb = ucb
                chosen_arm = arm

        if chosen_arm is None:
            break

        deck_copy = get_deck(used_cards + list(chosen_arm))
        unknown_board = draw_cards(deck_copy, 5 - len(community_cards))

        result = simulate_one_game(my_hand, community_cards, unknown_board, list(chosen_arm))
        wins[chosen_arm] += int(result)
        plays[chosen_arm] += 1
        total_simulations += 1

    total_wins = sum(wins[arm] for arm in opponent_arms)
    win_prob = total_wins / total_simulations if total_simulations else 0

    print(f"Win probability: {win_prob:.3f} after {total_simulations} simulations")
    return 'stay' if win_prob >= 0.5 else 'fold'

if __name__ == "__main__":
    my_hand = ['7C', '2H']
    community = ['QD', '9S', '5C']
    decision = monte_carlo_decision(my_hand, community)
    print(f"Decision with {my_hand}: {decision}")
