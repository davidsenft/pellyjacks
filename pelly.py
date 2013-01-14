def error(str):
	print "//\n//\tERROR\n//\t" + str + "\n//"

def process(command):
	print "You said: " + command

class PellyBoard:

	"Game board"
	def __init__(self):
		print "initializing board"
		self.b = [[1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1]]
		self.t = 1
		self.s1 = 0
		self.s2 = 0
		self.m = 0

	def echo(self):
		print "//"
		print "// \tPELLYJACKS"
		print "// \t" + `self.m` + " moves have been made" 
		print "// \tplayer 1 score: " + `self.s1`
		print "// \tplayer 2 score: " + `self.s2`
		print "// \tplayer " + `self.t` + "'s move \n// "
		for row in self.b:
			print "// \t" + "\t".join([`col` for col in row])
		print "// "

	def html(self):
		buf = "<table>"
		for row in self.b:
			buf += "<tr><td>"
			buf +=  "</td><td>".join([`col` for col in row])
			buf += "</td></tr>"
		buf += "</table>"
		print buf

	def move(self, fr, fc, tr, tc):
		t = self.b[tr][tc]

		if t > 0:
			"stacky town"
			return stack(fr,fc,tr,tc)

		elif t == 0:
			"slidey town"
			return slide(fr,fc,tr,tc)

		"funky town"
		error("inconceivable!")
		return False


	def slide(self, fr, fc, tr, tc):
		f = self.b[fr][fc]
		t = self.b[tr][tc]

		if f == 0:
			error("no stack to slide")
			return False
			
		elif f == 1:
			error("can't slide a jack")
			return False

		return self.domove(fr, fc, tr, tc)


	def stack(self, fr, fc, tr, tc):
		f = self.b[fr][fc]
		t = self.b[tr][tc]

		if f == 0:
			error("no jack to stack")
			return False

		elif f > 1:
			error("can't stack a stack")
			return False

		return self.domove(fr, fc, tr, tc)


	def domove(self, fr, fc, tr, tc):
		self.b[tr][tc] += self.b[fr][fc]
		self.b[fr][fc] = 0
		self.echo()
		return True


board = PellyBoard()
board.stack(0,0,1,1)

command = raw_input("Player " + `board.t` + "'s turn... \n")
while (command != "stop"):
	process(command)
	command = raw_input("Player " + `board.t` + "'s turn... \n")

