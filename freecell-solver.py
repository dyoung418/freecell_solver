import search, msfreecell, random, math, collections, copy, sys, io, time, functools

#######################################################################
# Representing state in freecell:
ranks = ['A','2','3','4','5','6','7','8','9','T','J','Q','K']
suits = ['H','C','D','S']
numCards = len(ranks) * len(suits)
tableauCols = 8
maxTableauRows = math.ceil(numCards/tableauCols) + len(ranks) # if king is built up from 7th row on...
validTableauNeighborSuit = {'H':['C','S'], 'C':['H','D'],
                            'D':['C','S'], 'S':['H','D']}
RANK = 0
SUIT = 1

allCardsInPriority = [r+s for r in ranks for s in suits]
#print(allCardsInPriority) #debug

# t3:s2 means 'tableau column 3 to stack 2'
# b1:t4 means 'bay one to tableau column 4'
#
# Actions TODO
# 1. Have a dict of where each card is (key=cardcode, val=where it is, such as t3 or b0).  Then
#    when listing all possible moves, start first with the stacks that have the next lowest
#    cards that aren't already in the stacks.
# 2. Instead of doing the cardLocation dict, change "action" so that it is origin:destination:card 
#    instead of orgin:destination.  (e.g. "t1:b0:9H" instead of "t1:b0").  Then you can have a 
#    heuristic that favors nodes whose action acts on priority cards (Nodes include the state and
#    the action that gets to that state and other things)


class FreecellState(object):
    def __init__(self, tableau=None, dealSeed=None, 
                stacks=None, bays=None, bayMax=4, shorthand=None):
        #print('debug: FreecellState.__init__: dealSeed={}, tableau={}'.format(dealSeed,tableau))
        self.bayMax = bayMax
        self.dealSeed = dealSeed
        self.cardLocations = {}
        if shorthand:
            nospace_shorthand = shorthand.translate(shorthand.maketrans({' ':None, '\n':None, '\t':None}))
            b2, s2, t2 = nospace_shorthand.split(':')
            self.bays = [[] for b in range(self.bayMax)] 
            self.stacks = [[] for s in range(len(suits))]
            self.tableau = [[] for c in range(tableauCols)]
            for i, val in enumerate(b2.split(',')):
                if val != '_':
                    self.bays[i%self.bayMax].append(val)
            for i, val in enumerate(s2.split(',')):
                if val != '_':
                    rank, suit = tuple(val)
                    for r in range(ranks.index(rank)+1):
                        self.stacks[i%len(suits)].append(ranks[r]+suit)
                    #self.stacks[i%len(suits)].append(val)
            for i, row in enumerate(t2.split(';')):
                for j, val in enumerate(row.split(',')):
                    if val != '_':
                        self.tableau[j%tableauCols].append(val)
            # for i, val in enumerate(t2.split(',')):
            #     if val != '_':
            #         self.tableau[i%tableauCols].append(val)
        else:
            if tableau:
                self.tableau = copy.deepcopy(tableau)
            else:
                # Note: tableau is a list of lists.  The inner lists are the
                # *columns*, not the rows.  (easier to see the leaf cards.)
                self.tableau = [[] for c in range(tableauCols)]
                if dealSeed:
                    randomDeal = msfreecell.msFreecellDeal(dealSeed)
                    for i, card in enumerate(randomDeal):
                        # TODO, pull in msCardNumToString into this object
                        self.tableau[i%tableauCols].append(msfreecell.msCardNumToString(card))
            if stacks:
                self.stacks = copy.deepcopy(stacks)
            else:
                self.stacks = [[] for s in range(len(suits))]
            if bays:
                self.bays = copy.deepcopy(bays)
            else:
                self.bays = [[] for b in range(self.bayMax)] 
        self.everyLocation = ['b'+str(b) for b in range(self.bayMax)] # Bays
        self.everyLocation += ['s'+str(s) for s in range(len(suits))] # Stacks
        self.everyLocation += ['t'+str(t) for t in range(tableauCols)] # Tableaus
        self.__initializeCardLocations()

    def __initializeCardLocations(self):
        for i, bay in enumerate(self.bays):
            if len(bay) > 0:
                self.cardLocations[bay[0]] = "b"+str(i);
        for i, stack in enumerate(self.stacks):
            for j in range(len(stack)):
                self.cardLocations[stack[j]] = "s"+str(i);
        for i, tableau in enumerate(self.tableau):
            for j in range(len(tableau)):
                self.cardLocations[tableau[j]] = "t"+str(i)
        #print(self.cardLocations) # debug

    def __repr__(self):
        '''Shorthand notation for the state -- should be code executable'''
        bays = ','.join(self.getRowX(self.bays, 0))
        stacks = ','.join(self.getRowX(self.stacks, -1))
        tableau = ';'.join( [','.join(self.getRowX(self.tableau, r)) for r in range(maxTableauRows)])
        return 'FreecellState(shorthand="' + bays + ':' + stacks + ':' + tableau + '")'

    def __eq__(self, other):
        if repr(self) == repr(other):
            return True
        else:
            return False

    def __hash__(self):
        return hash(repr(self))

    def getRowX(self, listOfLists, x):
        '''gets the xth row of a list of Lists where each inner
        list is considered to be a column.  If one inner column
        is shorter than others and has run out, return '_' for that
        column.
        If x == -1, get the final row of each column'''
        result = []
        for l in listOfLists:
            if x == -1:
                if len(l) > 0:
                    result.append(l[x])
                else:
                    result.append('_')
            else:
                if x < len(l):
                    result.append(l[x])
                else:
                    result.append('_')
        return result

    def printState(self, unicode=True, file=sys.stdout, tableauLabels=True):
        if unicode:
            empty = '\N{WHITE VERTICAL RECTANGLE} '
        else:
            empty = '__'
        #tableauEmpty = '  '
        tableauEmpty = '__'
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
        for row in range(maxTableauRows): 
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
        if tableauLabels:
            print('', file=file)
            print(space.join([' 0',' 1',' 2',' 3',' 4',' 5',' 6',' 7']), file=file)

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
        origin, destination = action.split(sep=':', maxsplit=1)
        origin_areaCode, origin_index = tuple(origin)
        origin_index = int(origin_index)
        card = self.getArea(origin)[origin_index].pop()
        if self.validSpot(destination, card):
            dest_areaCode, dest_index = tuple(destination)
            dest_index = int(dest_index)
            self.getArea(destination)[dest_index].append(card)
            # update card locations
            self.cardLocations[card] = destination
        else:
            raise RuntimeError

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

    def getNextXStackCardsNeededPerSuit(self, x=3):
        '''return a dict of cards representing the next X cards needed on each of
        the stacks.  So with 4 suits, if X is 3, this will be 12 cards maximum.'''
        result = {}
        for i, stackCol in enumerate(self.stacks):
            if len(stackCol) > 0:
                stacktop = stackCol[-1]
                r, s = tuple(stacktop)
                # add cards in order from top stack card to topcard+x
                for count, index in enumerate(range(ranks.index(stacktop[RANK])+1, len(ranks))):
                    if count >= x: return result
                    result[ranks[index]+s] = 1
        return result


    def validSpot(self, location, card):
        '''return True or False depending on whether location is
        a valid spot for card.
        location = one of (BAY, index), (TABLEAU, index), (STACK, index)'''
        areaCode, index = tuple(location)
        index = int(index)
        area = self.getArea(location) 
        if len(area[index]) == 0:
            # an empty spot is valid for Tableau and Bay
            # we may need to change this for optional rule where only a King
            # can occupy an empty tableau column
            if areaCode != 's': # not stack
                return True
            else:
                #if (card[RANK] == ranks[0]) and (card[SUIT] not in self.getStackSuits()):
                # Need to force stacks in HCDS order so that games match the GOAL at end.
                if (card[RANK] == ranks[0]) and (suits.index(card[SUIT]) == index):
                    return True
                else:
                    return False
        elif areaCode == 'b':
            return False # non-empty bay is an invalid spot to move card
        elif areaCode == 's':
            if (card[SUIT]==self.getStackSuits()[index]) and \
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
            


freecellGoal = FreecellState(stacks= [[r+suit for r in ranks] for suit in suits])
#print(freecellGoal)
#print(repr(freecellGoal))

#######################################################################
# Freecell problem

class Freecell(search.Problem):
    """docstring for Freecell"""
    def __init__(self, initial, goal=None, seed=1, shorthand=None, debug=False):
        super(Freecell, self).__init__(initial, goal)
        if not self.initial:
            if shorthand:
                self.initial = FreecellState(shorthand=shorthand)
            else:
                self.initial = FreecellState(dealSeed=seed)
        if not isinstance(self.initial, FreecellState):
            raise TypeError
        #import pdb; pdb.set_trace() #debug
        if not goal:
            self.goal = FreecellState(stacks= [[r+suit for r in ranks] for suit in suits])
        self.lastActions = None
        self.lastState = self.initial
        if debug: print('Problem initial state:\n{}\n'.format(str(self.initial)))

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        oldway = '''
        result = []
        for loc in state.everyLocation:
            if loc[0] == 's': continue # don't allow movement off stacks
            card = state.getCard(loc)
            if card:
                for otherLoc in state.everyLocation:
                    if loc != otherLoc:
                        if state.validSpot(otherLoc, card):
                            result.append(loc+':'+otherLoc)
        #print('debug: actions: {}'.format(result))
        self.lastActions = result
        self.lastState = state
        return result
        '''
        result = []
        locsAdded = {}
        for card in allCardsInPriority:
            loc = state.cardLocations[card]
            if loc in locsAdded:  # don't duplicate starting locs already considered
                continue
            else:
                locsAdded[loc] = 1
            if loc[0] == 's': continue # don't allow movement off stacks
            #if loc[0] == 't': # allCardsInPriority includes row info for tableau (e.g. "t3:1")
            #    locparts = loc.split(sep=':', maxsplit=1)
            #    loc = locparts[0]
            #    row = int(locparts[1])
            #    #print("card {}, loc {}, row {}, len of column {}".format(card,loc,row,len(state.tableau[int(loc[1])]))) #debug
            #    if row < len(state.tableau[int(loc[1])]) -1: continue # can't move tableau card unless at bottom of column
            for otherLoc in state.everyLocation:
                if loc != otherLoc:
                    if (loc[0]=='b') and (otherLoc[0]=='b'): continue
                    if (loc[0]=='s') and (otherLoc[0]=='s'): continue
                    #if state.validSpot(otherLoc, card):
                    if state.validSpot(otherLoc, state.getCard(loc)):
                        result.append(loc+':'+otherLoc)
        #print('debug: actions: {}'.format(result))
        self.lastActions = result
        self.lastState = state
        return result

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        newState = FreecellState(tableau=state.tableau, stacks=state.stacks,
                                bays=state.bays, bayMax=state.bayMax, dealSeed=None)
        newState.takeAction(action)
        #print('debug: result(state, {}) -> \n{}'.format(action, str(newState)))
        return newState


    def value(self, state):
        """For optimization problems, each state has a value.  Hill-climbing
        and related algorithms try to maximize this value."""
        abstract

    def __str__(self):
        return '\nstate: \n{}\nactions: \n{}'.format(str(self.lastState), str(self.lastActions))

def cardsNotOnStacks(node):
    #import pdb; pdb.set_trace()
    return numCards - sum([len(s) for s in node.state.stacks])

def obviousUnstacked(node):
    '''Count of cards in the tableau that could be placed on
    the stack right now.
    NOTE: this one is counterproductive as a heuristic because
    it penalizes a move that exposes an obviousUnstack.  For example,
    A King covering an Ace is moved to the bay.  That move
    *increases* the heuristic (which needs to be minimized) because
    now the Ace is an obviousUnstacked'''
    #import pdb; pdb.set_trace()
    r = 0
    edges = node.state.getRowX(node.state.tableau, -1)
    for card in edges:
        if card != '_' and (
           node.state.validSpot('s0', card) or \
           node.state.validSpot('s1', card) or \
           node.state.validSpot('s2', card) or \
           node.state.validSpot('s3', card)):
           r += 1
    return r

def cardsInBay(node):
    #import pdb; pdb.set_trace()
    return sum([len(b) for b in node.state.bays])

def bayCardsThatCouldBeTableau(node):
    #import pdb; pdb.set_trace()
    r = 0
    for b in node.state.bays:
        if len(b) > 0:
            for i, t in enumerate(node.state.tableau):
                if len(t) > 0:
                    if node.state.validSpot('t'+str(i), b[0]):
                        r += 1
                        break
    return r

def buriedTableauCards(node):
    '''Count of cards in the tableau which have a higher rank card
    on top of them'''
    #import pdb; pdb.set_trace()
    buried_tableau_cards = 0
    for tCol in node.state.tableau:
        for i, buriedcard in enumerate(tCol):
            buriedcardrank = ranks.index(buriedcard[RANK])
            for j, highercard in enumerate(tCol[i+1:]):
                if buriedcardrank <= ranks.index(highercard[RANK]):
                    buried_tableau_cards += 1
                    break
    return buried_tableau_cards

def buriedSelectCards(node):
    '''Count of a select set of cards in the tableau which have a higher rank card
    on top of them.  In this case the select set are the 3 next cards needed on
    the stack (so if the stack already has up to 3H, the select set for hearts would
    be [4H, 5H, 6H]'''
    #import pdb; pdb.set_trace()
    selectCards = node.state.getNextXStackCardsNeededPerSuit(x=3)
    buried_select_tableau_cards = 0
    for tCol in node.state.tableau:
        for i, buriedcard in enumerate(tCol):
            if buriedcard in selectCards:
                buriedcardrank = ranks.index(buriedcard[RANK])
                for j, highercard in enumerate(tCol[i+1:]):
                    if buriedcardrank <= ranks.index(highercard[RANK]):
                        buried_select_tableau_cards += 1
                        break
    #print('selectCards: {}, val: {}'.format(selectCards, buried_select_tableau_cards)) #debug
    return buried_select_tableau_cards

def depthBuriedSelectCards(node):
    '''Weighted Count of a select set of cards in the tableau which have a higher rank card
    on top of them (weighted by how far it is burried).  In this case the select set are 
    the 3 next cards needed on the stack (so if the stack already has up to 3H, the 
    select set for hearts would be [4H, 5H, 6H]'''
    #import pdb; pdb.set_trace()
    selectCards = node.state.getNextXStackCardsNeededPerSuit(x=3)
    buried_select_tableau_cards = 0
    for tCol in node.state.tableau:
        for i, buriedcard in enumerate(tCol):
            if buriedcard in selectCards:
                buriedcardrank = ranks.index(buriedcard[RANK])
                for j, highercard in enumerate(tCol[i+1:]):
                    if buriedcardrank <= ranks.index(highercard[RANK]):
                        buried_select_tableau_cards += len(tCol) - i
                        #print('tCol:{}, buriedcard:{}, val:{}'.format(tCol, buriedcard, len(tCol)-i))
                        break
    #print('selectCards: {}, val: {}'.format(selectCards, buried_select_tableau_cards)) #debug
    return buried_select_tableau_cards

def depthBuriedTableauCards(node):
    '''Weighted count of cards in the tableau which have a higher rank
    card on top of them'''
    #import pdb; pdb.set_trace()
    rankWeights = [w for w in range(len(ranks)-1, -1, -1)] # 12, 11, 10, ...
    depth_buried_tableau_cards = 0
    for tCol in node.state.tableau:
        for i, bottomcard in enumerate(tCol):
            bottomcardrank = ranks.index(bottomcard[RANK])
            for j, highercard in enumerate(tCol[i+1:]):
                if bottomcardrank < ranks.index(highercard[RANK]):
                    # weight by how far it is buried and the rank of the card
                    #depth_buried_tableau_cards += (len(tCol) - (i+j)) * rankWeights[bottomcardrank]
                    depth_buried_tableau_cards += (len(tCol) - i) * rankWeights[bottomcardrank]
                    break
    return depth_buried_tableau_cards

def depthLowestRank(node):
    '''The depth in the tableau of the lowest un-stacked rank
    of each suit added together'''
    #import pdb; pdb.set_trace()
    r = 0
    suitNextStackRank = {'H':0, 'C':0, 'D':0, 'S':0}
    for i, s in enumerate(node.state.stacks):
        if len(s) > 0:
            suitNextStackRank[suits[i]] = ranks[min(len(ranks)-1,ranks.index(s[-1][RANK])+1)] # i.e. stack rank + 1
    lowestRankNonStackCards = [suitNextStackRank[s]+s for s in suits]
    for t in node.state.tableau:
        for ic, card in enumerate(t):
            if card in lowestRankNonStackCards:
                r += len(t) - ic -1 
    return r

def stackCardsAheadOfNeighborSuit(node):
    '''Stack cards that have run ahead of neighbor suits.
    For example, if both red stacks are at 4 (4H and 4D)
    but black cards are only at Ace, that means that there
    are no cards for the black 3's to be placed on in the 
    tableaus (black 2s are OK since black Aces are already
    in the stacks)'''
    #import pdb; pdb.set_trace()
    suitNextStackRank = {'H':0, 'C':0, 'D':0, 'S':0}
    for i, s in enumerate(node.state.stacks):
        if len(s) > 0:
            suitNextStackRank[suits[i]] = ranks.index(s[-1][RANK])
    blackMin = min(suitNextStackRank['C'], suitNextStackRank['S'])
    redMin = min(suitNextStackRank['H'], suitNextStackRank['D'])
    return abs(redMin - blackMin)

def nonEmptyTableaus(node):
    #import pdb; pdb.set_trace()
    return sum([1 for t in node.state.tableau if len(t)>0])

heuristics = {
            'cardsNotOnStacks':{'max':numCards, 'function':cardsNotOnStacks},
            'cardsInBay':{'max':4, 'function':cardsInBay},
            'buriedTableauCards':{'max':numCards - tableauCols, 'function':buriedTableauCards},
            'buriedSelectCards':{'max':3*4, 'function':buriedSelectCards},
            'depthBuriedSelectCards':{'max':3*4*maxTableauRows, 'function':depthBuriedSelectCards},
            'depthBuriedTableauCards':{'max': sum([r * rr for r in range(len(ranks)-1) 
                                                      for rr in range(len(ranks)-1, -1, -1)]),
                                          'function':depthBuriedTableauCards},
            'stackCardsAheadOfNeighborSuit':{'max':len(ranks)-1,'function':stackCardsAheadOfNeighborSuit},
            'bayCardsThatCouldBeTableau': {'max':4,'function':bayCardsThatCouldBeTableau},
            'nonEmptyTableaus': {'max':tableauCols, 'function':nonEmptyTableaus},
            'depthLowestRank': {'max':len(suits)*(numCards/tableauCols), 'function':depthLowestRank},
            'obviousUnstacked': {'max':len(suits), 'function':obviousUnstacked},
}

def heuristic(node, w=None):
    if not w:
        w = {
            'cardsNotOnStacks':                 9,
#            'obviousUnstacked':                 0,
            'cardsInBay':                       0.2,
#            'buriedTableauCards':               1,
#            'buriedSelectCards':               1,
            'depthBuriedSelectCards':               2,
#            'depthBuriedTableauCards':          0.5,
#            'depthLowestRank':                  1,
#            'stackCardsAheadOfNeighborSuit':    1,
#            'bayCardsThatCouldBeTableau':       1,
#            'nonEmptyTableaus':                 1,
        }
        ''' Good weights:
        9, 0, 1, 0, 0.5, 0, 0, 0, 0, 0'''
    #import pdb; pdb.set_trace()
    val = {}
    for h in w:
        if w[h] > 0:
            val[h] = heuristics[h]['function'](node)
    #print(val) # debug
    #print(node.state) # debug
    return sum([w[i] * val[i]/heuristics[i]['max'] for i in val.keys()])

def timedcall(fn, *args):
    "Call function with args; return the time in seconds and result."
    t0 = time.clock()
    result = fn(*args)
    t1 = time.clock()
    return t1-t0, result

def average(numbers):
    "Return the average (arithmetic mean) of a sequence of numbers."
    return sum(numbers) / float(len(numbers))

def timedcalls(n, fn, *args):
    """Call fn(*args) repeatedly: n times if n is an int, or up to
    n seconds if n is a float; return the min, avg, and max time"""
    if isinstance(n, int):
        times = [timedcall(fn, *args)[0] for _ in range(n)]
    else:
        times = []
        total = 0.0
        while total < n:
            t = timedcall(fn, *args)[0]
            total += t
            times.append(t)
    return min(times), average(times), max(times)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    # Very hard seed is 11982
    seed = int(sys.argv[1]) if len(sys.argv) == 2 else random.randrange(1, 32000) # MS deals from 0 to 32k
    
    if False:
        seed = 2659
        problem = Freecell(None, seed=seed)
        state = problem.initial
        print('{}'.format(str(problem.initial))) # example of using StringIO
        problem.initial.printState()
        shorthand = repr(problem.initial)
        print(shorthand)
        print(eval(shorthand))
    if False:
        print(repr(freecellGoal))
        print('freecell goal =')
        print(eval(repr(freecellGoal)))
    if True:
        # This is a good thing to run if you are coming back after a long period away
        testState = FreecellState(shorthand='''JS,_,_,_:QH,KC,KD,9S:
             _,TS,_,_,_,KS,_,_
            ;_,KH,_,_,_,_,_,_
            ;_,QS,_,_,_,_,_,_
            ;_,_,_,_,_,_,_,_
            ;_,_,_,_,_,_,_,_
            ;_,_,_,_,_,_,_,_
            ;_,_,_,_,_,_,_,_
            ;_,_,_,_,_,_,_,_
            ;_,_,_,_,_,_,_,_;_,_,_,_,_,_,_,_;_,_,_,_,_,_,_,_;_,_,_,_,_,_,_,_
            ;_,_,_,_,_,_,_,_;_,_,_,_,_,_,_,_;_,_,_,_,_,_,_,_;_,_,_,_,_,_,_,_
            ;_,_,_,_,_,_,_,_;_,_,_,_,_,_,_,_;_,_,_,_,_,_,_,_;_,_,_,_,_,_,_,_''')
        problem = Freecell(initial=testState, debug=True)
        print("----------------")
        solution = search.best_first_graph_search(problem, heuristic, debug=True)
    if False:
        testprob = Freecell(None, shorthand=str('_,_,_,_:KH,JC,KD,KS:KC,QC,'+'_,'*(maxTableauRows-2))[:-1])
        print(testprob.initial)
        print(repr(testprob.initial))
        print(testprob.actions(testprob.initial))
        print('goal= \n{}'.format(str(freecellGoal)))
        print('repr(goal)= \n{}'.format(repr(freecellGoal)))
    if False:
        prob2659 = Freecell(None, seed=2659)
        prob2659.initial.printState(unicode=False)
        state = prob2659.initial
        print('Actions on this problem: {}'.format(prob2659.actions(state)))
        for action in ['t0:s0', 't5:s1', 't6:b0', 't7:t6', 't2:t7', 
                        't3:b1', 't3:b2', 't3:b3']:
            print('Action: {}'.format(action))
            state = prob2659.result(state, action)
            state.printState(unicode=True)
        print('Actions on this problem: {}'.format(prob2659.actions(state)))

    if True:
        try:
            #seed = 2659
            #seed = 5152 #tough
            seed = 2483 #interesting test case
            problem = Freecell(None, seed=seed)
            print(problem)
            print('Starting...')
            t0 = time.clock()
            solution = search.best_first_graph_search(problem, heuristic, debug=True)
            t1 = time.clock()
            print('Deal {} ({} sec): Solution path is: {}'.format(seed, t1-t0, solution.solution()))
        except KeyboardInterrupt:
            import pdb; pdb.set_trace()
            print(str(problem))
            #raise
    if False:
        try:
            for i in range(20):
                t0 = time.clock()
                problem = Freecell(None, seed=i)
                solution = search.best_first_graph_search(problem, heuristic, debug=True)
                t1 = time.clock()
            print('Deal {} ({} sec): Solution path is: {}'.format(i, t1-t0, solution.solution()))
        except KeyboardInterrupt:
            print(str(problem))
            raise


