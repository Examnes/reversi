from player import player
from model import board
from utils import *
from time import time
from copy import deepcopy
import random

opening_positions_score = [
		[ 100, -50, 20, 5, 5, 20, -50, 100],
		[-50 , -70, -5, -5, -5, -5, -70, -50],
		[20  , -5 , 15, 3, 3, 15, -5, 20],
		[5   , -5 , 3, 3, 3, 3, -5, 5],
		[5   , -5 , 3, 3, 3, 3, -5, 5],
		[20  , -5 , 15, 3, 3, 15, -5, 20],
		[-50 , -70, -5, -5, -5, -5, -70, -50],
		[100 , -50, 20, 5, 5, 20, -50, 100]
	]

midgame_positions_score = [
		[ 140, -20, 20, 5, 5, 20, -20, 140],
		[-20 , -40, -5, -5, -5, -5, -40, -20],
		[20  , -5 , 15, 3, 3, 15, -5, 20],
		[5   , -5 , 3, 3, 3, 3, -5, 5],
		[5   , -5 , 3, 3, 3, 3, -5, 5],
		[20  , -5 , 15, 3, 3, 15, -5, 20],
		[-20 , -40, -5, -5, -5, -5, -40, -20],
		[140 , -20, 20, 5, 5, 20, -20, 140]
	]

endgame_positions_score = [
		[ 20, -5, 10, 5, 5, 10, -5, 20],
		[-5 , -10, 5, 5, 5, 5, -10, -5],
		[20  , 5 , 5, 5, 5, 5, 5, 10],
		[5   , 5 , 5, 5, 5, 5, 5, 5],
		[5   , 5 , 3, 5, 5, 5, 5, 5],
		[10  , 5 , 5, 5, 5, 5, 5, 10],
		[-5 , -10, 5, 5, 5, 5, -10, -5],
		[20 , -5, 10, 5, 5, 10, -5, 20]
	]

class evaluate_score:
	def __init__(self):
		self.number_of_possible_moves = 0
		self.number_of_stable_disk = 0
		self.number_of_disk_can_flip = 0
		self.disk_count = 0
		self.score_position_weight = 0
		self.score_stable_disk_weight = 0
		self.score_pass_weight = 0
		self.score_disk_can_flip = 0

	def __sub__(self, other):
		result = evaluate_score()
		result.number_of_possible_moves = self.number_of_possible_moves - other.number_of_possible_moves
		result.number_of_stable_disk = self.number_of_stable_disk - other.number_of_stable_disk
		result.number_of_disk_can_flip = self.number_of_disk_can_flip - other.number_of_disk_can_flip
		result.disk_count = self.disk_count - other.disk_count
		result.score_position_weight = self.score_position_weight - other.score_position_weight
		result.score_stable_disk_weight = self.score_stable_disk_weight - other.score_stable_disk_weight
		result.score_pass_weight = self.score_pass_weight - other.score_pass_weight
		result.score_disk_can_flip = self.score_disk_can_flip - other.score_disk_can_flip
		return result

	def total_score(self):
		return self.score_position_weight + self.score_stable_disk_weight + self.score_pass_weight + self.score_disk_can_flip

class score_dict:
	def __init__(self):
		self.dic_hash = {}
		self.dic_eval_score = {}
		self.score_for_non_exist = -1000000

	def add(self, board_hash, score, depth):
		dic_depth_score = {}
		if board_hash in self.dic_hash:
			dic_depth_score = self.dic_hash[board_hash]
			if depth in dic_depth_score:
				return
			for depth_key in dic_depth_score:
				if depth_key >= depth:
					return
		else:
			self.dic_hash[board_hash] = dic_depth_score
		dic_depth_score[depth] = score
	
	def get_score(self, board_hash, depth):
		if not board_hash in self.dic_hash:
			return self.score_for_non_exist
		for depth_key in self.dic_hash[board_hash]:
			if depth_key >= depth:
				return self.dic_hash[board_hash][depth_key]
		return self.score_for_non_exist
	
	def get_eval_score(self, board_hash):
		if board_hash in self.dic_eval_score:
			return self.dic_eval_score[board_hash]
		return self.score_for_non_exist
	
	def add_eval_score(self, board_hash, score):
		if board_hash in self.dic_eval_score:
			return
		self.dic_eval_score[board_hash] = score

	def contain_eval_score(self, board_hash):
		return self.get_score(board_hash) != self.score_for_non_exist
	
	def contain_eval_score(self, board_hash):
		return board_hash in self.dic_eval_score
	
	def number_of_node_count(self):
		result = 0
		for board_hash in self.dic_hash:
			result += len(self.dic_hash[board_hash])
		result += len(self.dic_eval_score)
		return result

	def get_hash(self, board: board):
		return board.get_hash() * board.turn_number
	
class evaluator:
	def __init__(self):
		self.is_use_score_from_position = True
		self.stable_disk_score = 10
		self.force_pass_score = 1000
		self.won_score = 100000
		self.lost_score = -100000
		self.board_size = 8
	
	def evaluate_board(self, board,  bot_color):
		return self.get_score(board,  bot_color)
	
	def score_number_move(self, board_phase):
		if board_phase == phase.OPENING:
			return 10
		if board_phase == phase.MIDDLE:
			return 40
		if board_phase == phase.END:
			return 20
		return 1
	
	def position_score(self, board_phase):
		if board_phase == phase.OPENING:
			return opening_positions_score
		if board_phase == phase.MIDDLE:
			return midgame_positions_score
		if board_phase == phase.END:
			return endgame_positions_score
		return opening_positions_score
	
	def get_score_from_position(self, board: board, position_score, bot_disk_color, bot_score: evaluate_score, opponent_score: evaluate_score):
		for i in range(self.board_size):
			for j in range(self.board_size):
				if board.board[i][j] == bot_disk_color:
					bot_score.score_position_weight += position_score[i][j]
					bot_score.disk_count += 1
				else:
					opponent_score.score_position_weight += position_score[i][j]
					opponent_score.disk_count += 1

	def get_score(self, board: board, bot_color):
		boardphase = board.get_board_phase()
		bot_score = evaluate_score()
		opponent_score = evaluate_score()
		position_score = self.position_score(boardphase)
		return self.calculate(board, bot_color, \
			bot_score, opponent_score, position_score, \
			self.stable_disk_score, self.score_number_move(boardphase), \
			self.is_use_score_from_position)

	def calculate(self, board: board, bot_id, \
	bot_score: evaluate_score, opponent_score: evaluate_score, \
	position_score, stable_disk_score, mobility_piece_score, \
	is_use_score_from_position):
		is_use_statble_disk_score = stable_disk_score != 0
		oppo_id = board.get_opponent(bot_id)
		bot_possible_moves = board.get_legal_moves(bot_id)
		opponent_possible_moves = board.get_legal_moves(oppo_id)
		bot_score.number_of_possible_moves = len(bot_possible_moves)
		opponent_score.number_of_possible_moves = len(opponent_possible_moves)
		is_end_game = False
		is_i_won = False
		is_draw = False
		if bot_score.number_of_possible_moves == 0 and opponent_score.number_of_possible_moves == 0:
			is_end_game = True
		if is_use_score_from_position:
			self.get_score_from_position(board, position_score, board.player_color(bot_id), bot_score, opponent_score)
		if is_end_game:
			bot_score.disk_count = board.number_of_disks(bot_id)
			opponent_score.disk_count = board.number_of_disks(oppo_id)
			if bot_score.disk_count == opponent_score.disk_count:
				is_draw = True
			else:
				is_i_won = bot_score.disk_count > opponent_score.disk_count
			if is_draw:
				return 0
			if is_i_won:
				return self.won_score
			return self.lost_score
		
		is_i_need_to_pass = False
		is_enemy_need_to_pass = False
		if opponent_score.number_of_possible_moves == 0 and bot_score.number_of_possible_moves > 0:
			is_enemy_need_to_pass = True
		if bot_score.number_of_possible_moves == 0 and opponent_score.number_of_possible_moves > 0:
			is_i_need_to_pass = True
		if is_enemy_need_to_pass:
			bot_score.score_pass_weight += self.force_pass_score
		if is_i_need_to_pass:
			opponent_score.score_pass_weight += self.force_pass_score
		if is_use_statble_disk_score:
			bot_score.number_of_stable_disk = self.get_number_of_stable_disks(board, board.player_color(bot_id))
			opponent_score.number_of_stable_disk = self.get_number_of_stable_disks(board, board.player_color(oppo_id))
			bot_score.score_stable_disk_weight = bot_score.number_of_stable_disk * stable_disk_score
			opponent_score.score_stable_disk_weight = opponent_score.number_of_stable_disk * stable_disk_score
		bot_score.number_of_disk_can_flip = self.get_number_can_be_flipped(board, bot_id, bot_possible_moves)
		opponent_score.number_of_disk_can_flip = self.get_number_can_be_flipped(board, oppo_id, opponent_possible_moves)
		bot_score.score_disk_can_flip = mobility_piece_score * bot_score.number_of_disk_can_flip
		opponent_score.score_disk_can_flip = mobility_piece_score * opponent_score.number_of_disk_can_flip
		result_score = bot_score - opponent_score
		score_total = result_score.total_score()
		return score_total
	
	def get_number_can_be_flipped(self, board: board, color, possible_moves):
		result = 0
		for move in possible_moves:
			new_board = deepcopy(board)
			new_board.put_and_switch(move, color)
			result += new_board.last_flip_count
		return result
	
	class Corner:
		TOP_LEFT = (0, 0)
		TOP_RIGHT = (0, 7)
		BOTTOM_LEFT = (7, 0)
		BOTTOM_RIGHT = (7, 7)
	
	class NEWS:
		NORTH = 0
		EAST = 1
		WEST = 2
		SOUTH = 3

	def get_number_of_stable_disks(self, board: board, color):
		from_corner = self.get_number_of_stable_discs_from_corner(board, color, self.Corner.TOP_LEFT) + \
			self.get_number_of_stable_discs_from_corner(board, color, self.Corner.TOP_RIGHT) + \
			self.get_number_of_stable_discs_from_corner(board, color, self.Corner.BOTTOM_LEFT) + \
			self.get_number_of_stable_discs_from_corner(board, color, self.Corner.BOTTOM_RIGHT)
		from_edge = self.get_stable_discs_from_full_edge(board, color, (0,0), (0,7)) + \
			self.get_stable_discs_from_full_edge(board, color, (0,7), (7,7)) + \
			self.get_stable_discs_from_full_edge(board, color, (7,0), (7,7)) + \
			self.get_stable_discs_from_full_edge(board, color, (0,0), (7,0))
		return from_corner + from_edge
	
	def get_number_of_stable_discs_from_corner(self, board: board, color, position_corner):
		disk_count = 0
		row_delta = 1
		column_delta = 1
		last_row = 7
		last_column = 7
		if position_corner[0] != 0:
			row_delta = -1
			last_row = 0
		if position_corner[1] != 0:
			column_delta = -1
			last_column = 0

		for index_row in range(position_corner[0], last_row, row_delta):
			for index_column in range(position_corner[1], last_column, column_delta):
				if board.board[index_row][index_column] != color:
					break
				disk_count += 1
			is_there_column_need_to_check = \
				(column_delta > 0 and index_column < 7) or \
				(column_delta < 0 and index_column > 0)
			if not is_there_column_need_to_check:
				continue
			last_column = index_column - column_delta
			if column_delta > 0 and last_column == 0:
				last_column += 1
			elif column_delta < 0 and last_column == 7:
				last_column -= 1
			if (column_delta > 0 and last_column < 0) \
				or (column_delta < 0 and last_column > 7):
				break
		return disk_count
	
	def get_stable_discs_from_full_edge(self, board: board, color, position_begin, position_end):
		opposite_color = board.opposite_color(color)
		if not self.is_edge_full(board, position_begin, position_end):
			return 0
		has_found_opposite_color = False
		repeat_count = 0
		result = 0
		for index_row in range(position_begin[0], position_end[0]):
			for index_column in range(position_begin[1], position_end[1]):
				disk_color = board.board[index_row][index_column]
				if not has_found_opposite_color and disk_color == opposite_color:
					has_found_opposite_color = True
					repeat_count = 0
					continue
				if has_found_opposite_color:
					if disk_color == color:
						repeat_count += 1
					else:
						result += repeat_count
						repeat_count = 0
		return result
	
	def is_edge_full(self, board: board, position_begin, position_end):
		for index_row in range(position_begin[0], position_end[0]):
			for index_column in range(position_begin[1], position_end[1]):
				if board.board[index_row][index_column] == cell.EMPTY:
					return False
		return True

class MiniMax:
	def __init__(self, id):
		self.evaluate = evaluator()
		self.first_level_depth = 0
		self.list_first_level_depth_moves = None
		self.node_count = 0
		self.evaluate_count = 0
		self.hash_tranportable = score_dict()
		self.i_count_hash_can_access = 0
		self.id = id
	
	class position_score:
		def __init__(self, score=0, row=-1, col=-1):
			self.score = score
			self.row = row
			self.col = col
			
		def __str__(self):
			return "Score::" + str(self.score) + "\n" + \
				"Position::" + str(self.row) + "," + str(self.col) + "\n"

		def __sub__(self, other):
			return self.score - other.score

		def __gt__(self, other):
			return self.score > other.score

		def __lt__(self, other):
			return self.score < other.score

		def __eq__(self, other):
			return self.score == other.score

		def __ge__(self, other):
			return self.score >= other.score

		def __le__(self, other):
			return self.score <= other.score
		
		def get_hash(self):
			return self.row * 8 + self.col
	
	class MiniMaxParameterExtend:
		def __init__(self):
			self.depth = 0
			self.board = None
			self.is_max = False
			self.alpha = 0
			self.beta = 0
			self.bot_color = None
			self.child = []
			self.position_score = None
			
		
		def CloneExtend(self):
			result = MiniMax.MiniMaxParameterExtend()
			result.depth = self.depth
			result.board = deepcopy(self.board)
			result.is_max = self.is_max
			result.alpha = self.alpha
			result.beta = self.beta
			result.bot_color = self.bot_color
			result.child = []
			result.position_score = deepcopy(self.position_score)
			return result

		def __deepcopy__(self, memo):
			result = MiniMax.MiniMaxParameterExtend()
			result.depth = self.depth
			result.board = deepcopy(self.board)
			result.is_max = self.is_max
			result.alpha = self.alpha
			result.beta = self.beta
			result.bot_color = self.bot_color
			result.child = []
			result.position_score = deepcopy(self.position_score)
			return result
	
	def calculate_next_move(self, board, depth, evaluate: evaluator, bot_color, is_using_alpha_beta, is_keeping_child_value, is_using_random_if_node_value_is_the_same, is_sorted_node):
		self.evaluate = evaluate
		move = position(-1, -1)
		para = self.MiniMaxParameterExtend()
		para.depth = depth - 1
		para.board = deepcopy(board)
		para.is_max = True
		para.alpha = -1000000
		para.beta = 1000000
		para.bot_color = bot_color
		self.node_count = 0
		self.evaluate_count = 0
		self.i_count_hash_can_access = 0
		self.first_level_depth = para.depth
		self.list_first_level_depth_moves = []
		score = self.minimax_alpha_beta_extend(para, is_using_alpha_beta, is_keeping_child_value, is_sorted_node)
		move = position(score.row, score.col)
		if para.board.total_number_of_disks() <= 14:
			if is_using_random_if_node_value_is_the_same:
				score = self.get_random_from_max_score_node(self.list_first_level_depth_moves)
				move = position(score.row, score.col)
		return move
	
	def get_random_from_max_score_node(self, list_first_level_depth_moves):
		if list_first_level_depth_moves is None or len(list_first_level_depth_moves) == 0:
			raise Exception("list_first_level_depth_moves is null")
		sorted_list = sorted(list_first_level_depth_moves, key=lambda x: x.score, reverse=True)
		result_position = None
		if len(sorted_list) > 0:
			max_score = sorted_list[0].score
			for i in range(len(sorted_list) - 1, -1, -1):
				if sorted_list[i].score >= max_score:
					break
				sorted_list.pop(i)
			random_index = random.randint(0, len(sorted_list) - 1)
			result_position = sorted_list[random_index]
		return result_position

	def minimax_alpha_beta_extend(self, para, is_using_alpha_beta, is_keeping_child_value, is_sorted_node):
		self.node_count += 1
		disk_color = para.bot_color
		opponent_color = board.get_opponent(para.bot_color)
		if not para.is_max:
			disk_color = opponent_color


		is_need_to_pass = False
		avilable_move_positions = []
		is_final_move = False
		if para.depth <= 0:
			is_final_move = True

		if not is_final_move:
			avilable_move_positions = para.board.get_legal_moves(disk_color)
			if len(avilable_move_positions) == 0:
				is_need_to_pass = True
				avilable_move_positions_for_opposite_color = []
				if disk_color == para.bot_color:
					avilable_move_positions_for_opposite_color = para.board.get_legal_moves(opponent_color)
					disk_color = opponent_color
				else:
					avilable_move_positions_for_opposite_color = para.board.get_legal_moves(para.bot_color)
					disk_color = para.bot_color
				avilable_move_positions = avilable_move_positions_for_opposite_color
			if len(avilable_move_positions) == 0:
				is_final_move = True
		
		best_score = self.position_score()
		if is_final_move:
			board_hash = self.hash_tranportable.get_hash(para.board)
			score = 0
			if self.hash_tranportable.contain_eval_score(board_hash):
				self.i_count_hash_can_access += 1
				score = self.hash_tranportable.get_eval_score(board_hash)
			else:
				self.evaluate_count += 1
				score = self.evaluate.evaluate_board(para.board,  para.bot_color)
				self.hash_tranportable.add_eval_score(board_hash, score)
			best_score = self.position_score(score)
			return best_score
		
		best_score = self.position_score(1000000)
		if para.is_max:
			best_score.score = -1000000

		if is_sorted_node and para.depth >= self.first_level_depth - 1:
			list_position = []
			dic_board = {}
			for next_move in avilable_move_positions:
				temp_board = deepcopy(para.board)
				temp_board.put_and_switch(next_move, disk_color)
				score = self.evaluate.evaluate_board(temp_board,  para.bot_color)
				list_position.append(self.position_score(score, next_move.row, next_move.col))
				dic_board[next_move.get_hash()] = temp_board
			sorted_list = []
			if para.is_max:
				sorted_list = sorted(list_position, key=lambda x: x.score, reverse=True)
			else:
				sorted_list = sorted(list_position, key=lambda x: x.score)
			avilable_move_positions = []
			for move in sorted_list:
				avilable_move_positions.append(position(move.row, move.col))
		
		for next_move in avilable_move_positions:
			child_para = para.CloneExtend()
			child_para.board.put_and_switch(next_move, disk_color)
			if is_keeping_child_value:
				para.child.append(child_para)

			child_para.is_max = not para.is_max
			if is_need_to_pass:
				child_para.is_max = para.is_max
				child_para.board.player_passed()
			child_para.depth -= 1
			score = 0
			board_hash = self.hash_tranportable.get_hash(child_para.board)
			child_score = None
			score_from_hash = self.hash_tranportable.get_score(board_hash, child_para.depth)
			if score_from_hash != self.hash_tranportable.score_for_non_exist:
				self.i_count_hash_can_access += 1
				child_score = self.position_score(score_from_hash)
			else:
				child_score = self.minimax_alpha_beta_extend(child_para, is_using_alpha_beta, is_keeping_child_value, is_sorted_node)
				self.hash_tranportable.add(board_hash, child_score.score, child_para.depth)
			child_para.position_score = self.position_score(child_score.score, next_move.row, next_move.col)
			if para.depth == self.first_level_depth:
				self.list_first_level_depth_moves.append(self.position_score(child_score.score, next_move.row, next_move.col))
			if para.is_max:
				if child_score.score > best_score.score:
					best_score = self.position_score(child_score.score, next_move.row, next_move.col)
					if is_using_alpha_beta:
						para.alpha = max(best_score.score, para.alpha)
						if para.beta < best_score.score:
							break
			else:
				if child_score.score < best_score.score:
					best_score = self.position_score(child_score.score, next_move.row, next_move.col)
					if is_using_alpha_beta:
						para.beta = min(para.beta, best_score.score)
						if best_score.score <= para.alpha:
							break
		return best_score
	
	def get_prefered_depth(self, board: board):
		phase = board.get_board_phase()
		if phase == phase.OPENING:
			return 2
		if phase == phase.MIDDLE:
			return 3
		if phase == phase.END:
			return 5
		
			
	def get_move(self, board):
		return self.calculate_next_move(board, self.get_prefered_depth(board), self.evaluate, self.id, True, True, True, True)