# See https://rosettacode.org/wiki/Deal_cards_for_FreeCell

from sys import argv
 
def randomGenerator(seed=1):
    # This is the linear congruential generator used in MS freecell
    # state_n+1 = 214013 x stat_n + 2531011 (mod 2^31)
    # rand_n = state_n / 2^16
    # rand_n is in range 0 to 32767
    while True:
        seed = (seed * 214013 + 2531011) & max_int32
        yield seed >> 16
 
def deal(seed):
    # 1. Seed the RNG with the number of the deal
    # 2. Create an array of cards, AC, AD, AH, AS, 2C, 2D, 2H, 2S, etc.
    #    with array indexes of 0 to 51
    # 3. Until the array is empty:
    #    * choose card at index = next rnd # (mod array length)
    #    * Swap this card with card at end
    #    * Remove the card from array (array length goes down by 1)
    #    * Deal this removed card.  Dealing is done in 8
    #      columns across the columns and then repeating at the first
    #      column, etc.  At end you will have 8 columns with the
    #      first 4 columns having 7 cards and the last 4 having 6
    #      cards.
    nc = 52
    cards = range(nc - 1, -1, -1)
    rnd = randomGenerator(seed)
    for i, r in zip(range(nc), rnd):
        j = (nc - 1) - r % (nc - i)
        cards[i], cards[j] = cards[j], cards[i]
    return cards
 
def show(cards):
    l = ["A23456789TJQK"[c / 4] + "CDHS"[c % 4] for c in cards]
    for i in range(0, len(cards), 8):
        print " ", " ".join(l[i : i+8])
 
if __name__ == '__main__':
    seed = int(argv[1]) if len(argv) == 2 else 11982
    print "Hand", seed
    deck = deal(seed)
    show(deck)