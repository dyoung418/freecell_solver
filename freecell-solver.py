import search, freecell, random, math
from sys import argv

#######################################################################
# Representing state in freecell:
ranks = ['1','2','3','4','5','6','7','8','9','T','J','Q','K']
suits = ['H','C','D','S']
numCards = len(ranks) * len(suits)
tableauCols = 8
tableauRows = math.ceil(numCards/tableauCols) # 7, but last 4 are empty

class FreecellState(object):
    def __init__(self, tableau=None, dealSeed=None, 
                stacks=None, bays=None, bayMax=4):
        if tableau:
            self.tableau = tableau
        else:
            # Note: tableau is a list of lists.  The inner lists are the
            # *columns*, not the rows.  That makes it easier to see the
            # leaf cards.
            self.tableau = [[] for c in range(tableauCols)]
            if not dealSeed:
                dealSeed = random.randrange(1, 32000) # MS deals from 0 to 32k
            randomDeal = freecell.msFreecellDeal(dealSeed)
            for i, card in enumerate(randomDeal):
                self.tableau[i%tableauCols].append(freecell.msCardNumToString(card))
        if stacks:
            self.stacks = stacks
        else:
            self.stacks = { 'H':[],
                            'C':[],
                            'D':[],
                            'S':[],}
        if bays:
            self.bays = bays
        else:
            self.bays = [] 
        self.bayMax = bayMax

    def printState(self, unicode=True):
        if unicode:
            empty = '\N{WHITE VERTICAL RECTANGLE}'
        else:
            empty = '_'
        space = '  '
        # Bays 
        for bay in range(self.bayMax):
            if bay < len(self.bays):
                print(self.printableCard(self.bays[bay], unicode) + space*2, end='')
            else:
                print(empty + space*2, end='')
        print('   ', end='') # space between bays and stacks
        # Stacks
        for stack in self.stacks:
            if len(self.stacks[stack]) > 0:
                print(self.printableCard(self.stacks[stack][-1], unicode) + space*2, end='')
            else:
                print(empty + space*2, end='')
        print(''); print('')
        # Tableau
        for row in range(tableauRows):
            for col in range(tableauCols):
                if row < len(self.tableau[col]):
                    print(self.printableCard(self.tableau[col][row], unicode) + space, end='')
            print('')
        print('')

    def printableCard(self, card, unicode=True):
        if unicode:
            printSuits = {'H':'\u2661', 'C':'\u2663', 'D':'\u2662', 'S':'\u2660'}
        else:
            printSuits = {'H':'H', 'C':'C', 'D':'D', 'S':'S'}
        return card[0] + printSuits[card[1]]




freecellGoal = FreecellState(stacks= {
    'H' : [r+'H' for r in ranks],
    'C' : [r+'C' for r in ranks],
    'D' : [r+'D' for r in ranks],
    'S' : [r+'S' for r in ranks]
    })

#######################################################################
# Freecell problem

class Freecell(search.Problem):
    """docstring for Freecell"""
    def __init__(self, initial, goal=None, seed=None):
        super(Freecell, self).__init__(initial, goal)
        # DAY TODO: check type of initial and if it isn't
        # a FreecellState object, error.  if it is, then it is OK.
        # if 'initial' is None, we need to instantiate a freecellState
        # object
        if not self.initial:
            self.initial = FreecellState(dealSeed=seed)
        if not isinstance(self.initial, FreecellState):
            raise TypeError
        if not goal:
            self.goal == freecellGoal

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        result = []


    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        abstract

    def value(self, state):
        """For optimization problems, each state has a value.  Hill-climbing
        and related algorithms try to maximize this value."""
        abstract


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    seed = int(argv[1]) if len(argv) == 2 else 11982
    d = Freecell(None, seed=seed)
    d.initial.printState()
    d.initial.printState(unicode=False)



