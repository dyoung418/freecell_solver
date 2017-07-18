import search, freecell, random, math, collections, copy, sys, io

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

# Actions
# t3:s2 means 'tableau column 3 to stack 2'
# b1:t4 means 'bay one to tableau column 4'
#


class FreecellState(object):
    def __init__(self, tableau=None, dealSeed=None, 
                stacks=None, bays=None, bayMax=4):
        #print('debug: FreecellState.__init__: dealSeed={}, tableau={}'.format(dealSeed,tableau))
        self.dealSeed = dealSeed
        if tableau:
            self.tableau = copy.deepcopy(tableau)
        else:
            # Note: tableau is a list of lists.  The inner lists are the
            # *columns*, not the rows.  That makes it easier to see the
            # leaf cards.
            self.tableau = [[] for c in range(tableauCols)]
            if dealSeed:
                randomDeal = freecell.msFreecellDeal(dealSeed)
                for i, card in enumerate(randomDeal):
                    # TODO, pull in msCardNumToString into this object
                    self.tableau[i%tableauCols].append(freecell.msCardNumToString(card))
        if stacks:
            self.stacks = copy.deepcopy(stacks)
        else:
            self.stacks = [[] for s in range(len(suits))]
        self.bayMax = bayMax
        if bays:
            self.bays = copy.deepcopy(bays)
        else:
            self.bays = [[] for b in range(self.bayMax)] 
        self.everyLocation = ['b'+str(b) for b in range(self.bayMax)] # Bays
        self.everyLocation += ['s'+str(s) for s in range(len(suits))] # Stacks
        self.everyLocation += ['t'+str(t) for t in range(tableauCols)] # Tableaus

    def printState(self, unicode=True, file=sys.stdout):
        if unicode:
            empty = '\N{WHITE VERTICAL RECTANGLE} '
        else:
            empty = '__'
        tableauEmpty = '  '
        space = '  '
        if self.dealSeed:
            print('Deal number {}:'.format(self.dealSeed), file=file)
        # Bays 
        for b in range(self.bayMax):
            if len(self.bays[b]) > 0:
                print(self.printableCard(self.bays[b][0], unicode) + space*2, end='', file=file)
            else:
                print(empty + space*2, end='', file=file)
        print('   ', end='', file=file) # space between bays and stacks
        # Stacks
        for stack in self.stacks:
            if len(stack) > 0:
                print(self.printableCard(stack[-1], unicode) + space*2, end='', file=file)
            else:
                print(empty + space*2, end='', file=file)
        print('', file=file); print('', file=file)
        # Tableau
        for row in range(tableauRows+len(ranks)): # a column could grow beyond tableauRows by len(ranks) cards
            emptyCols = 0 # counter to see when all cols are run out of cards
            for col in range(tableauCols):
                if row < len(self.tableau[col]):
                    print(self.printableCard(self.tableau[col][row], unicode) + space, end='', file=file)
                else:
                    emptyCols += 1
                    print(tableauEmpty + space, end='', file=file)
            if emptyCols == tableauCols:
                break
            print('', file=file)
        print('', file=file)

    def printableCard(self, card, unicode=True):
        if unicode:
            printSuits = {'H':'\u2661', 'C':'\u2663', 'D':'\u2662', 'S':'\u2660'}
        else:
            printSuits = {'H':'H', 'C':'C', 'D':'D', 'S':'S'}
        return card[RANK] + printSuits[card[SUIT]]

    def __str__(self):
        stringOutput = io.StringIO()
        self.printState(file=stringOutput)
        return stringOutput.getvalue()

    def takeAction(self, action):
        '''Modify this state object with the results of taking the 
        input 'action'.'''
        #TODO, I'd like to be able to check the validity of this action,
        # but _validAction is in the Problem object.  Should it be here?
        origin, destination = action.split(sep=':', maxsplit=1)
        origin_areaCode, origin_index = tuple(origin)
        origin_index = int(origin_index)
        card = self.getArea(origin)[origin_index].pop()
        #card = origin.area[origin.index].pop()
        #assert card = action[originCard]
        dest_areaCode, dest_index = tuple(destination)
        dest_index = int(dest_index)
        self.getArea(destination)[dest_index].append(card)
        #destination = action.destLoc
        #destination.area[destination.index].append(card)

    def getCard(self, location):
        #print('debug: Location.getCard(): areaCode={}, index={}'.format(self.areaCode, self.index))
        areaCode, index = tuple(location)
        index = int(index)
        area = self.getArea(location)
        if len(area[index]) == 0:
            return None
        else:
            return area[index][-1]

    def getArea(self, location):
        areaCode, index = tuple(location)
        index = int(index)
        if areaCode == 't':
            area = self.tableau
        elif areaCode == 'b':
            area = self.bays
        else:
            area = self.stacks
        return area

    def getStackSuits(self):
        '''return a list of suits currently occupied on each of the 4 stacks.
        This is used to check that we aren't doubling up on some suits'''
        result = [None for s in range(len(self.stacks))]
        for i, stackCol in enumerate(self.stacks):
            if len(stackCol) > 0:
                result[i] = stackCol[-1][SUIT]
        return result


freecellGoal = FreecellState(stacks= [[r+suit for r in ranks] for suit in suits])

#######################################################################
# Freecell problem

class Freecell(search.Problem):
    """docstring for Freecell"""
    def __init__(self, initial, goal=None, seed=1):
        super(Freecell, self).__init__(initial, goal)
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
            card = state.getCard(loc)
            if card:
                for otherLoc in state.everyLocation:
                    if loc != otherLoc:
                        if self._validSpot(state, otherLoc, card):
                            result.append(loc+':'+otherLoc)
        return result

    def _validSpot(self, state, location, card):
        '''return True or False depending on whether location is
        a valid spot for card.
        location = one of (BAY, index), (TABLEAU, index), (STACK, index)'''
        areaCode, index = tuple(location)
        index = int(index)
        area = state.getArea(location) 
        if len(area[index]) == 0:
            # an empty spot is valid for Tableau and Bay
            # we may need to change this for optional rule where only a King
            # can occupy an empty tableau column
            if areaCode != 's': # not stack
                return True
            else:
                if (card[RANK] == ranks[0]) and (card[SUIT] not in state.getStackSuits()):
                    return True
                else:
                    return False
        elif areaCode == 'b':
            return False # non-empty bay is an invalid spot to move card
        elif areaCode == 's':
            if (card[SUIT]==state.getStackSuits()[index]) and \
               (ranks.index(area[index][-1][RANK]) == (ranks.index(card[RANK])-1)):
                return True
            else:
                return False
        elif areaCode == 't':
            if (card[SUIT] in validTableauNeighborSuit[area[index][-1][SUIT]]) and \
               (ranks.index(area[index][-1][RANK]) == ranks.index(card[RANK])+1):
                return True
            else:
                return False
            
    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        newState = FreecellState(tableau=state.tableau, stacks=state.stacks,
                                bays=state.bays, bayMax=state.bayMax, dealSeed=None)
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
    seed = int(sys.argv[1]) if len(sys.argv) == 2 else random.randrange(1, 32000) # MS deals from 0 to 32k
    
    seed = 2659
    problem = Freecell(None, seed=seed)
    state = problem.initial
    problem.initial.printState()
    problem.initial.printState(unicode=False)
    print('Actions on this problem: {}'.format(problem.actions(state)))
    for action in ['t0:s0', 't5:s1', 't6:b0', 't7:t6', 't2:t7', 't3:b1', 't3:b2', 't3:b3']:
        print('Action: {}'.format(action))
        state = problem.result(state, action)
        state.printState(unicode=False)
    print('Actions on this problem: {}'.format(problem.actions(state)))

    if False:
        solution = search.tree_search(problem, [])
        print('Solution path is: {}'.format(solution.path()))




