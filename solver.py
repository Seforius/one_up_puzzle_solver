class Square:

    def __init__(self, value: int):
        self.value = value # zero represents an empty square
        self.possible_values = []

    def set_value(self, value: int):
        self.value = value
    
    def add_possible_value(self, value: int):
        self.possible_values.append(value)

class Coordinate:
    
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))
    
    def __str__(self):
        return f'({self.row}, {self.col})'
    
    def __repr__(self) -> str:
        return f'({self.row}, {self.col})'

class Segment:
    
    def __init__(self, coordinates: list[Coordinate]):
        self.coordinates = coordinates

    def get_length(self) -> int:
        return len(self.coordinates)

    def get_values(self) -> list[int]:
        values = []
        for coordinate in self.coordinates:
            values.append(board[coordinate.row][coordinate.col].value)
        return values
    
    def get_values_except(self, coordinate_to_exclude: Coordinate) -> list[int]:
        values = []
        for coordinate in self.coordinates:
            if coordinate != coordinate_to_exclude:
                values.append(board[coordinate.row][coordinate.col].value)

        return values
    
    def get_coordinates_except(self, coordinate_to_exclude: Coordinate) -> list[Coordinate]:
        coordinates = []
        for coordinate in self.coordinates:
            if coordinate != coordinate_to_exclude:
                coordinates.append(coordinate)

        return coordinates

def load_board(file_path: str):

    board: list[list[Square]] = []

    with open(file_path) as file:
        for line in file:
            row = []
            for value in line.strip().split(','):
                row.append(Square(int(value)))
            board.append(row)

    return board

def load_blockades(file_path: str):

    blockades: dict[tuple[Coordinate, Coordinate]] = {}

    with open(file_path) as file:
        for line in file:
            coordinate_strings = line.strip().split('|')
            coordinates = [Coordinate(int(coordinate_string.split(',')[0]), int(coordinate_string.split(',')[1])) for coordinate_string in coordinate_strings]
            blockades[(coordinates[0], coordinates[1])] = True
            blockades[(coordinates[1], coordinates[0])] = True

    return blockades

# the current state of the board. list of rows
board = load_board('board.txt')

# an unchanging list of the blockades on the board, which is a list of pairs of coordinates, where the coordinates correspond to the two squares that the blockade is between
blockades = load_blockades('blockades.txt')

# given a set of coordinates, return the segments that the square is a part of: (vertical segment, horizontal segment)
def get_segments(coordinate: Coordinate) -> tuple[Segment, Segment]:

    # parse the board vertically until the end of the board or a blockade is reached

    # go up
    current_coordinate = coordinate
    next_coordinate = Coordinate(coordinate.row - 1, coordinate.col)

    current_row = coordinate.row
    current_col = coordinate.col

    while current_row > 0 and (current_coordinate, next_coordinate) not in blockades:

        current_row -= 1
        current_coordinate = next_coordinate
        next_coordinate = Coordinate(current_row - 1, current_col)

    vertical_segment_upper_coordinate = Coordinate(current_row, current_col)

    # go down
    current_coordinate = coordinate
    next_coordinate = Coordinate(coordinate.row + 1, coordinate.col)

    current_row = coordinate.row
    current_col = coordinate.col

    while current_row < len(board) - 1 and (current_coordinate, next_coordinate) not in blockades:

        current_row += 1
        current_coordinate = next_coordinate
        next_coordinate = Coordinate(current_row + 1, current_col)
    
    vertical_segment_lower_coordinate = Coordinate(current_row, current_col)

    # parse the board horizontally until the end of the board or a blockade is reached

    # go left
    current_coordinate = coordinate
    next_coordinate = Coordinate(coordinate.row, coordinate.col - 1)

    current_row = coordinate.row
    current_col = coordinate.col

    while current_col > 0 and (current_coordinate, next_coordinate) not in blockades:

        current_col -= 1
        current_coordinate = next_coordinate
        next_coordinate = Coordinate(current_row, current_col - 1)

    horizontal_segment_left_coordinate = Coordinate(current_row, current_col)

    # go right
    current_coordinate = coordinate
    next_coordinate = Coordinate(coordinate.row, coordinate.col + 1)

    current_row = coordinate.row
    current_col = coordinate.col

    while current_col < len(board[0]) - 1 and (current_coordinate, next_coordinate) not in blockades:

        current_col += 1
        current_coordinate = next_coordinate
        next_coordinate = Coordinate(current_row, current_col + 1)

    horizontal_segment_right_coordinate = Coordinate(current_row, current_col)

    # use bounds to create vertical and horizontal segments

    vertical_segment_coordinates = []
    for row in range(vertical_segment_upper_coordinate.row, vertical_segment_lower_coordinate.row + 1):
        vertical_segment_coordinates.append(Coordinate(row, vertical_segment_upper_coordinate.col))
    
    horizontal_segment_coordinates = []
    for col in range(horizontal_segment_left_coordinate.col, horizontal_segment_right_coordinate.col + 1):
        horizontal_segment_coordinates.append(Coordinate(horizontal_segment_left_coordinate.row, col))

    return (Segment(vertical_segment_coordinates), Segment(horizontal_segment_coordinates))

# given a coordinate, return the possible values that can be placed in the square at that coordinate
def get_possible_values(coordinate: Coordinate) -> list[int]:

    if board[coordinate.row][coordinate.col].value != 0:
        return []

    # get segments for square
    vertical_segment, horizontal_segment = get_segments(coordinate)

    # check vertical segment
    possible_values_vertical = []
    values_in_vertical_segment = vertical_segment.get_values_except(coordinate)

    for value in range(1, 10):
        # if value is not in the segment and is less than the length of the segment, add it to the possible values
        if value not in values_in_vertical_segment and value <= vertical_segment.get_length():
            possible_values_vertical.append(value)

    # check horizontal segment
    possible_values_horizontal = []
    values_in_horizontal_segment = horizontal_segment.get_values_except(coordinate)

    for value in range(1, 10):
        # if value is not in the segment and is less than the length of the segment, add it to the possible values
        if value not in values_in_horizontal_segment and value <= horizontal_segment.get_length():
            possible_values_horizontal.append(value)

    intersection = list(set(possible_values_vertical) & set(possible_values_horizontal))

    return intersection

# fill in a coordinate with a value, and then update the possible values for all squares that share a segment with the square at the coordinate
def fill_in_value(coordinate: Coordinate, value: int):
    
    # add value and clear possible values
    board[coordinate.row][coordinate.col].set_value(value)
    board[coordinate.row][coordinate.col].possible_values = []

    # update possible values for all squares in the segments
    vertical_segment, horizontal_segment = get_segments(coordinate)
    for segment in [vertical_segment, horizontal_segment]:
        for segment_coordinate in segment.coordinates:
            if segment_coordinate != coordinate:
                possible_values = get_possible_values(segment_coordinate)
                board[segment_coordinate.row][segment_coordinate.col].possible_values = possible_values

# check whether the board is filled
def board_is_filled() -> bool:

    for row in board:
        for square in row:
            if square.value == 0:
                return False
    return True

# print the board
def print_board():

    for row in board:
        for square in row:
            print(square.value, end = " ")
        print()

# print the blockades
def print_blockades():

    for key in blockades:
        print(key[0].row, key[0].col, '|' , key[1].row, key[1].col)

# print the board with blockades
def print_board_with_blockades():
    pass

# check whether a square has a unique possible value in a segment
def has_unique_possible_value(coordinate: Coordinate, segment: Segment) -> tuple[bool, int]:

    # get possible values for the square. NOTE: this is dangerous because it assumes the possible values attached to the square are up to date
    possible_values = board[coordinate.row][coordinate.col].possible_values

    # for each value, check every other square that shares the segment of the coordinate. if any square has the value as a possible value, then the value is not unique
    for value in possible_values:
        
        unique = True
        for segment_coordinate in segment.get_coordinates_except(coordinate):
            if value in board[segment_coordinate.row][segment_coordinate.col].possible_values:
                # this value is not unique
                unique = False
                break

        if unique:
            return (True, value)
    
    return (False, 0)

# solve the board
def solve():
    iterations = 0

    while not board_is_filled() and iterations < 100:
    # loop through each square and fill in possible values
        for row in range(len(board)):
            for col in range(len(board[0])):
                square = board[row][col]

                # skip squares that are already filled
                if square.value != 0:
                    possible_values = []
                    continue

                possible_values = get_possible_values(Coordinate(row, col))

                square.possible_values = possible_values

    # if a square has only one possible value OR if a square has a value that is not possible in any other square in a segment that it shares, then fill in that value
        for row in range(len(board)):
            for col in range(len(board[0])):
                square = board[row][col]

                # skip squares that are already filled
                if square.value != 0:
                    continue

                if len(square.possible_values) == 1:
                    fill_in_value(Coordinate(row, col), square.possible_values[0])
                else:
                    for segment in get_segments(Coordinate(row, col)):
                        has_unique_value, unique_possible_value = has_unique_possible_value(Coordinate(row, col), segment)

                        if has_unique_value:
                            fill_in_value(Coordinate(row, col), unique_possible_value)
    
        # repeat until the board is filled
        iterations += 1
        print('Board after iteration', iterations)
        print_board()

def main():
    solve()

if __name__ == "__main__":
    main()