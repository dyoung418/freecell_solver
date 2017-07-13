import search, freecell

#######################################################################
# Representing state in freecell:
ranks = ['1','2','3','4','5','6','7','8','9','T','J','Q','K']
suits = ['H','C','D','S']

class FState(object):
	def __init__(self, tableau=None, stacks=None, bays=None, bayMax=4):
		if tableau:
			self.tableau = tableau
			self.leaves = self.updateLeaves()
		else:

			# DAY TODO: change this so that each internal list of the 
			#  list of lists is the *column* of the deal rather than
			#  the row of the deal.  That way, it is easy to look at
			#  each column. 
			#  Also, make it so these go up and down in length rathern
			#  than stay constant length. (but number of columns will
			#   be constant.)
			self.tableau = [[None for r in range(8)] for c in range(6)]
			self.tableau.append([None for r in range(4)])
			#tableau = [[r+(c*8) for r in range(8)] for c in range(6)]
			#tableau.append([r+48 for r in range(4)])	
			self.leaves = []		
		if stacks:
			self.stacks = stacks
		else:
			self.stacks = {	'H'=[None for r in range(13)],
							'C'=[None for r in range(13)],
							'D'=[None for r in range(13)],
							'S'=[None for r in range(13)],}
		if bays:
			self.bays = bays
		else:
			self.bays = [] 
		self.bayMax = bayMax

	def updateLeaves(self):
		'''Returns the bottom card of each column in list of 
		(col#, card) tuples'''
		result = []


freecellGoal = Fstate(stacks= {
	'H' = [r+'H' for r in ranks],
	'C' = [r+'C' for r in ranks],
	'D' = [r+'D' for r in ranks],
	'S' = [r+'S' for r in ranks]
	})

#######################################################################
# Freecell problem

class Freecell(search.Problem):
	"""docstring for Freecell"""
	def __init__(self, initial, goal=None):
		super(Freecell, self).__init__()
		if not goal:
			self.goal == freecellGoal

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        result = []
        if len(self.bays) < self.bayMax:
        	for


    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        abstract

    def value(self, state):
        """For optimization problems, each state has a value.  Hill-climbing
        and related algorithms try to maximize this value."""
        abstract



