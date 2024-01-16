from model import *
from player import *
from ai import MiniMax

	
class game():
	def __init__(self):
		self.board = board()
		self.player1 = MiniMax(1)
		self.player2 = MiniMax(2)
		self.current_player = self.player1
		self.winner = None
	
	def opponent(self):
		if self.current_player == self.player1:
			return self.player2
		else:
			return self.player1
	
	def play(self):
		while True:
			self.board.print()
			pos = self.current_player.get_move(self.board)
			self.board.put_and_switch(pos, self.current_player.id)
			print("Player " + str(self.current_player.id) + " put a disk at ({0}, {1})".format(pos.row, pos.col))
			if not self.board.is_there_place_to_put():
				self.current_player = self.opponent()
				if not self.board.is_there_place_to_put():
					break
			self.current_player = self.opponent()
		self.board.print()
		print("Game over")
		print("Winner: " + self.board.get_winner())

