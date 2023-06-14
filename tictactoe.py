# SQLite Database
import random
import re
import sqlite3

conn = sqlite3.connect('leaderboard.db')
c = conn.cursor()

# Create leaderboard table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS leaderboard
             (name TEXT UNIQUE, score INTEGER)''')

c.execute("INSERT OR IGNORE INTO leaderboard VALUES (?,0)", ("Bot",))
conn.commit()


def display_artwork():
    print("""

████████╗██╗░█████╗░  ████████╗░█████╗░░█████╗░  ████████╗░█████╗░███████╗
╚══██╔══╝██║██╔══██╗  ╚══██╔══╝██╔══██╗██╔══██╗  ╚══██╔══╝██╔══██╗██╔════╝
░░░██║░░░██║██║░░╚═╝  ░░░██║░░░███████║██║░░╚═╝  ░░░██║░░░██║░░██║█████╗░░
░░░██║░░░██║██║░░██╗  ░░░██║░░░██╔══██║██║░░██╗  ░░░██║░░░██║░░██║██╔══╝░░
░░░██║░░░██║╚█████╔╝  ░░░██║░░░██║░░██║╚█████╔╝  ░░░██║░░░╚█████╔╝███████╗
░░░╚═╝░░░╚═╝░╚════╝░  ░░░╚═╝░░░╚═╝░░╚═╝░╚════╝░  ░░░╚═╝░░░░╚════╝░╚══════╝
    """)


# Login/Register
def login():
    display_artwork()
    while True:
        name = input("Enter your name: ")
        if name.strip() == '':
            print("Invalid input. Please enter a valid name.")
        else:
            data = c.execute("SELECT * FROM leaderboard WHERE name = ?", (name,)).fetchone()
            if data:
                print("Welcome back, " + name + "!")
                return name
            else:
                print("No such user. Registering new user.")
                c.execute("INSERT INTO leaderboard VALUES (?,0)", (name,))
                conn.commit()
                return name


# Tic-Tac-Toe game
class TicTacToe:
    def __init__(self, player1, player2):
        self.board = [' ' for _ in range(9)]  # 1-9 for user input
        self.current_winner = None  # keep track of winner!
        self.player1 = player1
        self.player2 = player2

    def print_board(self):
        for row in [self.board[i * 3:(i + 1) * 3] for i in range(3)]:
            print('| ' + ' | '.join(row) + ' |')

    def validate_input(self, square):
        pattern = "^[1-9]$"
        return bool(re.match(pattern, square))

    def make_move(self, letter, square):
        if self.board[square] == ' ':
            self.board[square] = letter
            if self.winner(square, letter):
                self.current_winner = self.player1 if letter == 'X' else self.player2
            return True
        return False

    def winner(self, square, letter):
        # check the row
        row_ind = square // 3
        row = self.board[row_ind * 3:(row_ind + 1) * 3]
        if all([spot == letter for spot in row]):
            return True
        # check the column
        col_ind = square % 3
        column = [self.board[col_ind + i * 3] for i in range(3)]
        if all([spot == letter for spot in column]):
            return True
        # check the diagonals
        if square % 2 == 0:
            diagonal1 = [self.board[i] for i in [0, 4, 8]]  # left to right diagonal
            if all([spot == letter for spot in diagonal1]):
                return True
            diagonal2 = [self.board[i] for i in [2, 4, 6]]  # right to left diagonal
            if all([spot == letter for spot in diagonal2]):
                return True
        # if all of these fail
        return False

    def is_draw(self):
        return ' ' not in self.board


def play():
    print("Welcome to Tic Tac Toe!")
    player1 = login()
    player2 = "Bot"
    while True:
        game = TicTacToe(player1, player2)
        current_player = 'X'
        while game.current_winner is None and not game.is_draw():
            game.print_board()
            if current_player == 'X':
                move = input(f'{game.player1}, make your move (1-9): ')
                if game.validate_input(move):
                    move = int(move) - 1
                else:
                    print('Invalid input.')
                    continue
            else:
                print(f'{game.player2} is thinking...')
                move = random.choice([i for i, x in enumerate(game.board) if x == ' '])
            if game.make_move(current_player, move):
                if game.current_winner:
                    print(f'{game.current_winner} wins!')
                    c.execute("UPDATE leaderboard SET score = score + 100 WHERE name = ?", (game.current_winner,))
                    conn.commit()
                elif game.is_draw():
                    print("It's a draw!")
                else:
                    current_player = 'O' if current_player == 'X' else 'X'
            else:
                print('Invalid move.')
        if game.current_winner or game.is_draw():
            game.print_board()
        show_leaderboard()
        play_again = input("Do you want to play again? (y/n): ")
        while play_again not in ['y', 'n']:
            print("Invalid input. Please enter 'y' or 'n'.")
            play_again = input("Do you want to play again? (y/n): ")
        if play_again == 'n':
            break


# Show leaderboard
def show_leaderboard():
    print('--------------------------------')
    print('{:<5} {:<15} {}'.format("Rank", "Name", "Score"))
    print('--------------------------------')
    rows = c.execute('SELECT * FROM leaderboard ORDER BY score DESC').fetchall()
    for i, row in enumerate(rows, start=1):
        print('{:<5} {:<15} {}'.format(i, row[0], row[1]))
    print('--------------------------------')


if __name__ == '__main__':
    play()
