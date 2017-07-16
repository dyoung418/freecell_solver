import search, freecell, random, math, collections, copy
from sys import argv

#######################################################################
# Representing state in freecell:
ranks = ['A','2','3','4','5','6','7','8','9','T','J','Q','K']
suits = ['H','C','D','S']
numCards = len(ranks) * len(suits)
tableauCols = 8
tableauRows = math.ceil(numCards/tableauCols) # 7, but last 4 are empty
validTableauNeighborSuit = {'H':['C','S'], 'C':['H','D'],
                            'D':['C','S'], 'S':['H','D']}
RANK = 0
SUIT = 1
TABLEAU = 100
BAY = 101
STACK = 102

Action = collections.namedtuple('Action', ['originLoc', 'originCard', 'destLoc', 'destCard'])


class Location(object):
    def __init__(self, state, areaCode, index):
        self.state = state
        self.areaCode = areaCode
        self.index = index
        if self.areaCode == BAY:
            self.area = state.bays
        elif self.areaCode == STACK:
            self.area = state.stacks
        else:
            self.area = state.tableau
    def getCard(self):
        if len(self.area) == 0:
            return None
        else:
            return self.area[self.index][-1]
    def __str__(self):
        areaCodeStrings = {TABLEAU:'TABLEAU', BAY:'BAY', STACK:'STACK'}
        return '({0}, {1})'.format(areaCodeStrings[self.areaCode], self.index)


class FreecellState(object):
    def __init__(self, tableau=None, dealSeed=None, 
                stacks=None, bays=None, bayMax=4):
        print('debug: FreecellState.__init__: dealSeed={}, tableau={}'.format(dealSeed,tableau))
        if tableau:
            self.tableau = copy.deepcopy(tableau)
        else:
            # Note: tableau is a list of lists.  The inner lists are the
            # *columns*, not the rows.  That makes it easier to see the
            # leaf cards.
            self.tableau = [[] for c in range(tableauCols)]
            self.dealSeed = dealSeed
            if dealSeed:
                randomDeal = freecell.msFreecellDeal(dealSeed)
                for i, card in enumerate(randomDeal):
                    self.tableau[i%tableauCols].append(freecell.msCardNumToString(card))
        if stacks:
            self.stacks = copy.deepcopy(stacks)
        else:
            self.stacks = { 'H':[],
                            'C':[],
                            'D':[],
                            'S':[],}
        self.bayMax = bayMax
        if bays:
            self.bays = copy.deepcopy(bays)
        else:
            self.bays = [[] for b in range(self.bayMax)] 
        print('before error: self.tableau={}'.format(self.tableau))
        self.printState()
        #print(''.join([str(Location(self, BAY, b)) for b in range(self.bayMax)])) #debug
        bayLocations = [Location(self, BAY, b) for b in range(self.bayMax)]
        stackLocations = [Location(self, STACK, s) for s in suits]
        tableauLocations = [Location(self, TABLEAU, t) for t in range(tableauCols)]
        print(bayLocations)
        print(stackLocations)
        print(tableauLocations)
        self.everyLocation = copy.deepcopy(bayLocations)
        self.everyLocation += stackLocations
        self.everyLocation += tableauLocations
        # self.everyLocation = [Location(self, BAY, b) for b in range(self.bayMax)].extend(
        #                        [Location(self, STACK, s) for s in suits].extend(
        #                          [Location(self, TABLEAU, t) for t in range(tableauCols)]
        #                          ))

    def printState(self, unicode=True):
        if unicode:
            empty = '\N{WHITE VERTICAL RECTANGLE}'
        else:
            empty = '_'
        space = '  '
        # Bays 
        for b in range(self.bayMax):
            if len(self.bays[b]) > 0:
                print(self.printableCard(self.bays[b][0], unicode) + space*2, end='')
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
                if len(self.tableau[col]) == 0:
                    print(empty + space, end='')
                if row < len(self.tableau[col]):
                    print(self.printableCard(self.tableau[col][row], unicode) + space, end='')
            print('')
        print('')

    def printableCard(self, card, unicode=True):
        if unicode:
            printSuits = {'H':'\u2661', 'C':'\u2663', 'D':'\u2662', 'S':'\u2660'}
        else:
            printSuits = {'H':'H', 'C':'C', 'D':'D', 'S':'S'}
        return card[RANK] + printSuits[card[SUIT]]

    def takeAction(self, action):
        origin = action[originLoc]
        card = origin.area[origin.index].pop()
        #assert card = action[originCard]
        destination = action[destLoc]
        destination.area[destination.index].append(card)





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
        for loc in state.everyLocation:
            card = loc.getCard()
            if card:
                for otherLoc in state.everyLocation:
                    if loc != otherLoc:
                        if _validSpot(otherLoc, card):
                            result.append(Action(loc, card, otherLoc, otherLoc.getCard()))

    def _validSpot(location, card):
        '''return True or False depending on whether location is
        a valid spot for card.
        location = one of (BAY, index), (TABLEAU, index), (STACK, index)'''
        if len(location.area[location.index]) == 0:
            # an empty spot is valid for Tableau and Bay
            # we may need to change this for optional rule where only a King
            # can occupy an empty tableau column
            if location.areaCode != STACK:
                return True
            else:
                if (location.index == card[SUIT]) and (card[RANK] == ranks[0]):
                    return True
                else:
                    return False
        elif location.areaCode == BAY:
            return False # non-empty bay is an invalid spot to move card
        elif location.areaCode == STACK:
            if (location.index == card[SUIT]) and (ranks.find(location.area[location.index][-1][RANK]) == (ranks.find(card[RANK])-1)):
                return True
            else:
                return False
        elif location.areaCode == TABLEAU:
            if (card[SUIT] in validTableauNeighborSuit[cardSuit]) and (ranks.find(location.area[location.index][-1][RANK]) > ranks.find(card[RANK])):
                return True
            else:
                return False
            
    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        newState = FreecellState(tableau=state.tableau, stacks=state.stacks,
                                bay=state.bay, bayMax=state.bayMax, dealSeed=None)
        newState.takeAction(action)
        return newState


    def value(self, state):
        """For optimization problems, each state has a value.  Hill-climbing
        and related algorithms try to maximize this value."""
        abstract


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    # Very hard seed is 11982
    seed = int(argv[1]) if len(argv) == 2 else random.randrange(1, 32000) # MS deals from 0 to 32k
    problem = Freecell(None, seed=seed)
    problem.initial.printState()
    problem.initial.printState(unicode=False)


    solution = search.tree_search(problem, [])
    print(solution)




