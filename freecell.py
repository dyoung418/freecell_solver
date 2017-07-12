# See https://rosettacode.org/wiki/Deal_cards_for_FreeCell

from sys import argv
 
def randomGenerator(seed=1):
    # This is the linear congruential generator used in MS freecell
    #   state_n+1 = 214013 x state_n + 2531011 (mod 2^31)
    #   rand_n = state_n / 2^16
    #   rand_n is in range 0 to 32767
    max_int32 = (1 << 31) -1
    #print('{0:0=32b}'.format(max_int32)) # debug
    seed = seed & max_int32
    while True:
        #   calculate the next state (AND[&] max_int32 strips off high bit
        #   and is equivalent to mod 2^31)
        seed = (seed * 214013 + 2531011) & max_int32
	#   recall that 32 >> 4 == 32 / 2^4. So seed >> 16 == seed / 2^16
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
    cards = list(range(nc - 1, -1, -1)) # [51-0] - note that last card is first here
    rnd = randomGenerator(seed) # rnd is a generator function
    for i, r in zip(range(nc), rnd):
        j = (nc - 1) - (r % (nc - i))
        cards[i], cards[j] = cards[j], cards[i]
    #  since this is done "backwards" relative to the description above,
    #  the first card to be dealt will be in the 0th array spot rather
    #  than the last array spot as in the description above.
    #print('deal: exiting: cards={}'.format(cards))
    return cards
 
def show(cards):
    l = ["A23456789TJQK"[c // 4] + "CDHS"[c % 4] for c in cards]
    for i in range(0, len(cards), 8):
        print(" ", " ".join(l[i : i+8]))

def showUnicode(cards):
    l = [str(list(range(1,14))[c // 4] + [0x1F0A0, 0x1F0C0, 0x1F0B0, 0x1F0D0][c % 4]) for c in cards]
    for i in range(0, len(cards), 8):
        print(" ", " ".join(l[i : i+8]))
        print(" ", "{0:x}".format(" ".join(l[i : i+8])))
 
def showHand(handNumber):
    '''
    >>> showHand(2647)
    Hand 2647
      KH 3S 7H 4C QD 5H TD 7S
      7D 5C AD 3C AH AC 6D 8D
      6C TH QS 2C KD 6H QH 7C
      TC 6S JD KC 5D QC JC JS
      2D 9S 3H 5S 3D 8H 9C 9D
      JH 4H 4D TS 2S KS AS 9H
      8S 2H 4S 8C
    >>>
    '''
    print("Hand {}".format(handNumber))
    deck = deal(handNumber)
    show(deck)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    seed = int(argv[1]) if len(argv) == 2 else 11982
    showHand(seed)
    showUnicode(deal(seed))
