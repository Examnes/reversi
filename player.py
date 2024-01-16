from utils import position

class player():
	def __init__(self, id):
		self.id = id
		self.name = "Player" + str(id)
	
	def get_move(self, board):
		# read input from stdin
		# return a position
		possible_moves = board.get_legal_moves(self.id)
		print("Possible moves:")
		for pos in possible_moves:
			print("({0}, {1})".format(pos.row, pos.col))
		while True:
			x = input("Input x: ")
			y = input("Input y: ")
			pos = position(int(x), int(y))
			if pos in possible_moves:
				break
			else:
				print("Invalid move")
		return pos
	
	def get_name(self):
		return self.name