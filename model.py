from utils import *
    
class board:
    def __init__(self, size = 8):
        self.size = size
        self.board = [[cell.EMPTY for i in range(size)] for j in range(size)]
        self.last_flip_count = 0
        self.last_put_pos = position(-1, -1)
        self.turn_number = 0
        self.current_player = 1
        self.board[3][3] = cell.WHITE
        self.board[4][4] = cell.WHITE
        self.board[3][4] = cell.BLACK
        self.board[4][3] = cell.BLACK

    
    def get_opponent(player_or_self, player = None):
        if player == None:
            player = player_or_self
        if player == 1:
            return 2
        else:
            return 1
    
    def opposite_color(color_or_self, color = None):
        if color == None:
            color = color_or_self
        if color == cell.BLACK:
            return cell.WHITE
        else:
            return cell.BLACK
    
    def cell_by_pos(self, pos):
        return self.board[pos.row][pos.col]
    
    def set_cell(self, pos, color):
        self.board[pos.row][pos.col] = color

    
    def get_board_phase(self):
        number_of_disks = self.total_number_of_disks()
        if number_of_disks <= 20:
            return phase.OPENING
        elif number_of_disks <= 40:
            return phase.MIDDLE
        else:
            return phase.END
    
    def get_winner(self):
        if self.number_of_black() > self.number_of_white():
            return "Black"
        elif self.number_of_black() < self.number_of_white():
            return "White"
        else:
            return "Draw"
    
    def print(self):
        print("  0 1 2 3 4 5 6 7")
        for i in range(8):
            print(i, end = " ")
            for j in range(8):
                if self.board[i][j] == cell.EMPTY:
                    print(".", end = " ")
                elif self.board[i][j] == cell.BLACK:
                    print("B", end = " ")
                else:
                    print("W", end = " ")
            print()
        print()

    def get_phase(self):
        number_of_disks = sum([row.count(cell.BLACK) for row in self.board])
        + sum([row.count(cell.WHITE) for row in self.board])
        if number_of_disks <= 20:
            return phase.OPENING
        elif number_of_disks <= 40:
            return phase.MIDDLE
        else:
            return phase.END
        
    def legal_move(self, pos, player):
        if pos.row < 0 or pos.row > 7 or pos.col < 0 or pos.col > 7:
            return False
        if self.board[pos.row][pos.col] != cell.EMPTY:
            return False
        opponent_color = board.player_color(board.get_opponent(player))
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x == 0 and y == 0:
                    continue
                has_at_least_one_opponent = False
                pos_check = position(pos.row, pos.col)
                while True:
                    pos_check.row += x
                    pos_check.col += y
                    if pos_check.row < 0 or pos_check.row > 7 or pos_check.col < 0 or pos_check.col > 7:
                        break
                    if self.board[pos_check.row][pos_check.col] == opponent_color:
                        has_at_least_one_opponent = True
                    if self.board[pos_check.row][pos_check.col] == cell.EMPTY:
                        break
                    if self.board[pos_check.row][pos_check.col] == board.player_color(player):
                        if has_at_least_one_opponent:
                            return True
                        else:
                            break
                    if self.board[pos_check.row][pos_check.col] == opponent_color:
                        has_at_least_one_opponent = True
        return False

    
    def check_direction(self, pos, x, y, player, opponent_color):
        pos.row += x
        pos.col += y
        if pos.row < 0 or pos.row > 7 or pos.col < 0 or pos.col > 7:
            return False
        if self.board[pos.row][pos.col] == opponent_color:
            return self.check_direction(pos, x, y, player, opponent_color)
        elif self.board[pos.row][pos.col] == board.player_color(player):
            return True
        else:
            return False
        
    def number_of_black(self):
        return sum([row.count(cell.BLACK) for row in self.board])

    def number_of_white(self):
        return sum([row.count(cell.WHITE) for row in self.board])
    
    def number_of_disks(self, player):
        return sum([row.count(board.player_color(player)) for row in self.board])
    
    def total_number_of_disks(self):
        return sum([row.count(cell.BLACK) for row in self.board]) + sum([row.count(cell.WHITE) for row in self.board])

    def player_color(player_or_self, player = None):
        if player == None:
            player = player_or_self
        if player == 1:
            return cell.BLACK
        else:
            return cell.WHITE
    
    def switch_player(self):
        self.current_player = board.get_opponent(self.current_player)

    def put_and_switch(self, pos, player):
        self.last_flip_count = 0
        if not self.legal_move(pos, player):
            raise Exception("Illegal move")
        self.set_cell(pos, board.player_color(player))
        opponent_color = board.player_color(board.get_opponent(player))
        flip_pos = []
        for x in range(-1, 2):
            flip_pos_in_direction = []
            for y in range(-1, 2):
                if x == 0 and y == 0:
                    continue
                pos_check = position(pos.row, pos.col)
                flip_pos_in_direction = []
                while True:
                    pos_check.row += x
                    pos_check.col += y
                    if pos_check.row < 0 or pos_check.row > 7 or pos_check.col < 0 or pos_check.col > 7:
                        break
                    if self.board[pos_check.row][pos_check.col] == cell.EMPTY:
                        break
                    elif self.board[pos_check.row][pos_check.col] == board.player_color(player):
                        if len(flip_pos_in_direction) > 0:
                            flip_pos += flip_pos_in_direction
                        break
                    elif self.board[pos_check.row][pos_check.col] == opponent_color:
                        flip_pos_in_direction.append(position(pos_check.row, pos_check.col))
        for pos in flip_pos:
            self.set_cell(pos, board.player_color(player))
        self.last_flip_count = len(flip_pos)
        self.last_put_pos = pos
        self.switch_player()

    def is_there_place_to_put(self):
        for i in range(8):
            for j in range(8):
                if self.legal_move(position(i, j), self.current_player):
                    return True
        return False
    
    def get_legal_moves(self, player):
        legal_moves = []
        for i in range(8):
            for j in range(8):
                if self.legal_move(position(i, j), player):
                    legal_moves.append(position(i, j))
        return legal_moves
    
    def player_passed(self):
        self.switch_player()

    def get_hash(self):
        hash = 17
        for i in range(8):
            for j in range(8):
                hash = hash * 31 + self.board[i][j].value
        return hash
        
    