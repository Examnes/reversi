from enum import Enum

class cell(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2

class phase(Enum):
    OPENING = 0
    MIDDLE = 1
    END = 2

class position:
    def __init__(self, x, y):
        self.row = x
        self.col = y
    
    def __eq__(self, other):
        return self.row == other.row and self.col == other.col
    
    def get_hash(self):
        return self.row * 8 + self.col