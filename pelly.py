###########################################

import math
import sqlite3
import yaml

###########################################

# SQL Database Connection
connection = sqlite3.connect('pelly.db')
c = connection.cursor()

# Create table
# c.execute("CREATE TABLE board_values (board text, value real)")

###########################################

def error(str, do):
	if do:
		print "//\n//\tERROR\n//\t" + str + "\n//"
	return False

def msg(str):
	print "> " + str + "..."

def process(command):
	print "You said: " + command

def debug(var, name):
	if hasattr(var,"__dict__"):
		print name + ": " + vars(var)
	if type(var) == int:
		print name + ": " + `var`
	if type(var) == str:
		print name + ": " + var

###########################################

class PellyBoard:

	# Optionally initialized with a list containing the initial board position
	# board is always in canonical orientation w/ current player's rack on top
	def __init__(self, b=[[1,2,2,1],[1,1,4,1],[1,1,1,1],[1,1,1,1]]):
		msg("initializing PellyBoard")
		self.b = b

		# orientation flags (true if switched)
		self.v = False
		self.h = False

		# immutable properties of b
		self.rows = len(self.b)
		self.cols = len(self.b[0])

	def __eq__(self, other):
		if type(other) is type(self):
			return self.__dict__ == other.__dict__
		return False

	def __ne__(self, other):
		return not self.__eq__(other)

	# prints board, game-oriented by default
	def echo(self, game=True):
		if game:
			# switch to game orientation
			self.orient()
		if not game or not self.v:
			print "//\t-------------------------"
		for row in self.b:
			print "// \t" + "\t".join([`col` for col in row])
		if game:
			if self.v:
				print "//\t-------------------------"
			# return to canonical orientation
			self.orient()
		print "// "

	# returns game-readable piece coordinate
	def spot(self,r,c):
		if self.v:
			r = self.rows - r - 1
		if self.h:
			c = self.cols - c - 1
		return "(" + `r` + ", " + `c` + ")"

	# toggle game/canonical orientation
	def orient(self):
		if self.v:
			self.reverse(False)
		if self.h:
			self.flip(False)

	# reverse rows (i.e. switch players)
	def reverse(self,flag=True):
		self.b.reverse()
		if flag:
			self.v = not self.v

	# reverse columns (does not affect board value)
	def flip(self,flag=True):
		for r in range(self.rows):
			self.b[r].reverse()
		if flag:
			self.h = not self.h

	# converts board to equivalent canonical form
	# such that first weighted row is positive
	# (i.e. weighted to the right)
	def canonical(self):
		for row in self.b:
			weight = 0
			for c in range(self.cols):
				half = math.floor(self.cols/2)
				if c < half:
					weight -= row[c]**2
				if c >= self.cols - half:
					weight += row[c]**2
			if not weight == 0:
				if weight < 0:
					self.flip()
				break

	# gets the piece count at a coordinate
	# defaults to canonical orientation
	def get(self, r, c, orient=False):
		if orient:
			# use game orientation
			self.orient()
			retval = self.b[r][c]
			self.orient()
			return retval
		return self.b[r][c]

	# checks if a coordinate is on the board
	def on(self, r, c):
		if r < 0 or r >= self.rows:
			return False
		if c < 0 or c >= self.cols:
			return False
		return True

	# translates game-oriented move to canonical move
	def moveoriented(self, fr, fc, tr, tc, do):
		if self.v:
			fr = self.rows - fr - 1
			tr = self.rows - tr - 1
		if self.h:
			fc = self.cols - fc - 1
			tc = self.cols - tc - 1
		return self.move(fr, fc, tr, tc, do)

	# validates a move in canonical orientation
	# then makes the move if "do" is true
	def move(self, fr, fc, tr, tc, do):
		if not self.on(fr,fc) or not self.on(tr,tc):
			return error("out of bounds",do)

		if not ((tr - fr)**2 + (tc - fc)**2) == 1:
			return error("spaces are not adjacent",do)

		f = self.get(fr,fc)
		t = self.get(tr,tc)

		if f <= 0:
			return error("no piece to move",do)

		if t > 0:
			if f > 1:
				return error("can't stack a stack",do)
			action = "stacking jack "

		elif t == 0:
			if f == 1:
				return error("can't slide a jack",do)
			action = "sliding stack "

		else: # this should never happen!
			return error("inconceivable!")

		if do:
			msg(action + self.spot(fr,fc) + " -> " + self.spot(tr,tc))
			self.b[tr][tc] += self.b[fr][fc]
			self.b[fr][fc] = 0
			self.reverse()
			self.canonical()

		return True

	# returns the number of currently available moves
	def available(self):
		num = 0
		#for every spot on the grid...
		for r in range(self.rows):
			for c in range(self.cols):

				# try all four directions
				for change in [[0,-1],[-1,0],[0,1],[1,0]]:
					if self.move(r,c,r+change[0],c+change[1],do=False):
						num = num + 1
		return num

###########################################

class PellyGame:

	# Optionally initialize with a PellyBoard object
	def __init__(self, board=PellyBoard(), player=1, rack1=0, rack2=0, moves=0):
		msg("initializing PellyGame")
		self.board = board
		self.player = player
		self.rack1 = rack1
		self.rack2 = rack2
		self.moves = moves

	def __eq__(self, other):
		if type(other) is type(self):
			return self.__dict__ == other.__dict__
		return False

	def __ne__(self, other):
		return not self.__eq__(other)

	# prints game-oriented board and all relevant game info
	def echo(self):
		print "//"
		print "// \tPELLYJACKS " + `self.board.rows` + "x" + `self.board.cols`
		print "// \tmoves made: " + `self.moves`
		print "// \tmoves available: " + `self.board.available()`
		print "// \tplayer 1 rack: " + `self.rack1`
		print "// \tplayer 2 rack: " + `self.rack2`
		print "// \tplayer " + `self.player` + "'s move \n// "
		print "// \tgame orientation:"
		self.board.echo(True)
		print "// \tcanonical orientation:"
		self.board.echo(False)

	# stores the current board and the board's value in the board_values table
	def save(self):
		msg("saving game position")
		board = yaml.dump(self.board.b)

		# TODO: only insert board if it doesn't exist yet
		c.execute("INSERT INTO board_values VALUES ('" + board + "', " + `self.value()` + ")")
		connection.commit()

	# returns a value for the board based on the current player's prospect of winning
	# (good is positive, bad is negative)
	def value(self):
		return 0

	# executes the given game-oriented move and updates all game info accordingly
	# returns True and prints the updated game on success, returns False otherwise
	def move(self, fr, fc, tr, tc):
		if self.board.moveoriented(fr, fc, tr, tc, True):
			self.player = -self.player
			self.moves = self.moves + 1
			self.echo()
			return True
		return False

	# racks the given column for the current player and updates all game info accordingly
	def rack(self, col, do=True):
		# do some stuff
		print ""

	# returns true if the game is over (no moves are left or it is
	# impossible for the losing player to make up the deficit)
	def over():
		# do some stuff
		print ""
		return False

###########################################

game = PellyGame()
game.move(1,0,0,0)
game.move(0,1,0,2)
game.move(0,0,1,0)
game.move(3,3,2,3)
game.echo()
# game.save()

###########################################

msg("player " + `game.player` + "'s turn")
command = raw_input()
while (command != "q"):
	process(command)
	msg("player " + `game.player` + "'s turn")
	command = raw_input()

# Close the database connection
connection.close()