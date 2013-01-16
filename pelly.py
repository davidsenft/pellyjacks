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

def spot(r,c):
	return "(" + `r` + ", " + `c` + ")"

def debug(var, name):
	if hasattr(var,"__dict__"):
		print name + ": " + vars(var)
	if type(var) == int:
		print name + ": " + `var`
	if type(var) == str:
		print name + ": " + var

###########################################

class PellyBoard:

	# Optionally initialize with a list containing the initial board position
	def __init__(self, b=[[1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1]]):
		msg("initializing PellyBoard")
		self.b = b

		# immutable properties of b
		self.rows = len(self.b)
		self.cols = len(self.b[0])

	def __eq__(self, other):
		if type(other) is type(self):
			return self.__dict__ == other.__dict__
		return False

	def __ne__(self, other):
		return not self.__eq__(other)

	def echo(self):
		for row in self.b:
			print "// \t" + "\t".join([`col` for col in row])
		print "// "

	def html(self):
		html = "<table>"
		for row in self.b:
			html += "<tr><td>"
			html +=  "</td><td>".join([`col` for col in row])
			html += "</td></tr>"
		html += "</table>"
		print html

	def get(self, r, c):
		return self.b[r][c]

	def on(self, r, c):
		if r < 0 or r >= len(self.b):
			return False
		if c < 0 or c >= len(self.b[0]):
			return False
		return True

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
			msg(action + spot(fr,fc) + " -> " + spot(tr,tc))
			self.b[tr][tc] += self.b[fr][fc]
			self.b[fr][fc] = 0

		return True

	def available(self):
		num = 0
		#for every spot on the grid...
		for r in range(self.rows):
			for c in range(self.cols):

				# try all four directions
				for change in [[0,-1],[-1,0],[0,1],[1,0]]:
					if self.move(r,c,r+change[0],c+change[1],False):
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

	def echo(self):
		print "//"
		print "// \tPELLYJACKS " + `self.board.rows` + "x" + `self.board.cols`
		print "// \tmoves made: " + `self.moves`
		print "// \tmoves available: " + `self.board.available()`
		print "// \tplayer 1 rack: " + `self.rack1`
		print "// \tplayer 2 rack: " + `self.rack2`
		print "// \tplayer " + `self.player` + "'s move \n// "
		self.board.echo()

	def save(self):
		msg("saving game position")
		board = yaml.dump(self.board.b)

		# TODO: only insert board if it doesn't exist yet
		c.execute("INSERT INTO board_values VALUES ('" + board + "', " + `self.value()` + ")")
		connection.commit()

	def value(self):
		# return a value for the board based on the current player's prospect of winning
		# good is positive, bad is negative
		return 0

	def move(self, fr, fc, tr, tc, do=True):
		if self.board.move(fr, fc, tr, tc, do):
			if do:
				self.player = -self.player
				self.moves = self.moves + 1
				self.echo()

	def rack(self, col, do=True):
		# do some stuff
		print ""

###########################################

game = PellyGame()
game.move(0,0,0,0)
game.move(0,1,0,2)
game.move(0,0,1,0)
game.move(3,3,2,3)
game.move(0,2,0,1)
game.save()

# print "YAML DUMP: " + yaml.dump(board)

msg("player " + `game.player` + "'s turn")
command = raw_input()
while (command != "q"):
	process(command)
	msg("player " + `game.player` + "'s turn")
	command = raw_input()

# Close the database connection
connection.close()