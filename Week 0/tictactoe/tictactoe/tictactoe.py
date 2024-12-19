"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Track each player's move count

    x_count = 0
    o_count = 0

    # Count moves made by each player.

    for row in board:
        for move in row:
            if move == 'X':
                x_count += 1
            elif move == 'O':
                o_count += 1
    
    # Check whose turn based on moves played

    if x_count <= o_count:
        return 'X'
    else:
        return 'O'


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # Set of tuple of actions
    possible_actions = set()

    # Iterate the board for empty cells
    for index_row, row in enumerate(board):
        for  index_column, move in enumerate(row):
            if move == EMPTY:
                possible_actions.add((index_row, index_column))

    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Making copy to avoid changing the original
    working_board = copy.deepcopy(board)

    # Extracting row and column action from action tuple.
    row_move, column_move = action

    # Handle invalid move
    if working_board[row_move][column_move] is not EMPTY:
        raise Exception("Not a valid move.")

    current_player = player(board)
    
    # Perform the action of current player.
    working_board[row_move][column_move] = current_player

    return working_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # Check horizontal and vertical wins
    for i in range(3):
        # Check rows for horizontal win
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] is not EMPTY:
            return board[i][0]
        
        # Check columns for vertical win
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] is not EMPTY:
            return board[0][i]
        
    # Check Diagonal Winner
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not EMPTY:
        return board[0][0]
    if board[2][0] == board[1][1] == board[0][2] and board[2][0] is not EMPTY:
        return board[2][0]
    
    # No winner, draw or game in progress.
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Check if someone already won game.
    if winner(board) is not None:
        return True
    
    # Give False if board empty
    for row in board:
        for move in row:
            if move is EMPTY:
                return False
    
    # No winners and board full game over.
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    winner_player = winner(board)

    if winner_player == 'X':
        return 1
    elif winner_player == 'O':
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    # Check if minimax is needed, board is terminal give None
    if terminal(board):
        return None

    # Current player
    current_player = player(board)

    # Initialize best action
    best_action = None

    # Initialize best value based on current player (x- maximize & o- minimize)
    if current_player == 'X':
        best_value = float('-inf')
    else:
        best_value = float('inf')

    # Iterate over all possible actions
    for action in actions(board):

        # New board from action
        new_board = result(board, action)

        # Recursively calculate minimax value
        value = minimax_value(new_board)

        if current_player == 'X' and value > best_value:
            best_value = value
            best_action = action
        elif current_player == 'O' and value < best_value:
            best_value = value
            best_action = action

    # Return move
    return best_action

def minimax_value(board):
    # End of moves, terminal
    if terminal(board):
        return utility(board)
    
    current_player = player(board)

    # Maximize (x) and minimize (o) value based on players
    # Recursively call the minimax_value 
    if current_player == 'X':
        value = float('-inf')
        for action in actions(board):
            value = max(value, minimax_value(result(board, action)))
    else:
        value = float('inf')
        for action in actions(board):
            value = min(value, minimax_value(result(board, action)))
    
    # Return the minimax_value
    return value