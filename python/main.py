#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import json
import logging
import random
import webapp2

# Reads json description of the board and provides simple interface.
#黒:1　白:2
#{"board":
#{"Pieces":[[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],
#[0,0,0,2,1,0,0,0],[0,0,0,1,1,0,0,0],[0,0,0,0,1,0,0,0],
# [0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]],"Next":2},
# "gamekey":"ag5zfnN0ZXAtcmV2ZXJzaXIRCxIER2FtZRiAgKCjzfKMCgw",
# "history":[{"Where":[5,6],"As":1}],
# "valid_moves":[{"Where":[6,4],"As":2},{"Where":[4,6],"As":2},{"Where":[6,6],"As":2}]}

#game
#{ "board":{"Pieces":[],"Next":0or2}, "gamekey":"", "history":[{"Where":[],"As":1or2}], "valid_moves":[{},{}.. }

#g = Game(self.request.get('json'))
class Game:
	# Takes json or a board directly.
	def __init__(self, body=None, board=None):
		if body:
			game = json.loads(body)
			self._board = game["board"]
			#{"Pieces":[配列],"Next":1 or 2}
		else:
			self._board = board

	# Returns piece on the board.
	# 0 for no pieces, 1 for player 1, 2 for player 2.
	# None for coordinate out of scope.
	def Pos(self, x, y):
		return Pos(self._board["Pieces"], x, y) #Pos(オセロの配列,x,y)

	# Returns who plays next.
	def Next(self):
		return self._board["Next"]
	#1 of 2
	# Returns the array of valid moves for next player.
	# Each move is a dict
	#   "Where": [x,y]
	#   "As": player number

	def ValidMoves(self):
		moves = []
		for y in xrange(1,9):
			for x in xrange(1,9):
				move = {"Where": [x,y],"As": self.Next()}
				if self.NextBoardPosition(move):
					moves.append(move)
		return moves

	# Helper function of NextBoardPosition.  It looks towards
	# (delta_x, delta_y) direction for one of our own pieces and
	# flips pieces in between if the move is valid. Returns True
	# if pieces are captured in this direction, False otherwise.
	def __UpdateBoardDirection(self, new_board, x, y, delta_x, delta_y):
		player = self.Next()
		opponent = 3 - player
		look_x = x + delta_x
		look_y = y + delta_y
		flip_list = []
		while Pos(new_board, look_x, look_y) == opponent:
			flip_list.append([look_x, look_y])
			look_x += delta_x
			look_y += delta_y
		if Pos(new_board, look_x, look_y) == player and len(flip_list) > 0:
            # there's a continuous line of our opponents
            # pieces between our own pieces at
	        # [look_x,look_y] and the newly placed one at
            # [x,y], making it a legal move.
			SetPos(new_board, x, y, player)
			for flip_move in flip_list:
				flip_x = flip_move[0]
				flip_y = flip_move[1]
				SetPos(new_board, flip_x, flip_y, player)
			return True
		return False

	# Takes a move dict and return the new Game state after that move.
	# Returns None if the move itself is invalid.

	def NextBoardPosition(self, move):
		x = move["Where"][0]
		y = move["Where"][1]
		if self.Pos(x, y) != 0:
			# x,y is already occupied.
			return None
		new_board = copy.deepcopy(self._board)
		pieces = new_board["Pieces"]
		if not (self.__UpdateBoardDirection(pieces, x, y, 1, 0)
				| self.__UpdateBoardDirection(pieces, x, y, 0, 1)
				| self.__UpdateBoardDirection(pieces, x, y, -1, 0)
				| self.__UpdateBoardDirection(pieces, x, y, 0, -1)
				| self.__UpdateBoardDirection(pieces, x, y, 1, 1)
				| self.__UpdateBoardDirection(pieces, x, y, -1, 1)
				| self.__UpdateBoardDirection(pieces, x, y, 1, -1)
				| self.__UpdateBoardDirection(pieces, x, y, -1, -1)):
			# Nothing was captured. Move is invalid.
			return None
		# Something was captured. Move is valid.
		new_board["Next"] = 3 - self.Next()
		return Game(board=new_board)

	def CountBlack_White(self,color):
		counter = 0
		for piece in self._board["Pieces"]:
			counter += piece.count(color)
		return counter

	def WorstScore(self,player):
		if player == 1:
			return 70
		else:
			return -70


	def MinMaxScore(self, depth,g):
		best_move = {"Where":[0,0],"As":1}
		valid_moves = self.ValidMoves()
		player = valid_moves[0]["As"]
		best = self.WorstScore(player)
		if depth < 1:
			return self.CountBlack_White(1) - self.CountBlack_White(2)
		for move in valid_moves:
			nextBoard = self.NextBoardPosition(move)
			score = self.MinMaxScore(depth-1,nextBoard)
			if move["As"] == 1:
				if score > best:
					best = score
					best_move = move
			elif move["As"]==2:
				if score < best:
					best = score
					best_move = move
		return best_move


# Returns piece on the board.
# 0 for no pieces, 1 for player 1, 2 for player 2.
# None for coordinate out of scope.
#
# Pos and SetPos takes care of converting coordinate from 1-indexed to
# 0-indexed that is actually used in the underlying arrays.
def Pos(board, x, y):
	if 1 <= x and x <= 8 and 1 <= y and y <= 8:
		return board[y-1][x-1]
	return None

# Set piece on the board at (x,y) coordinate
def SetPos(board, x, y, piece):
	if x < 1 or 8 < x or y < 1 or 8 < y or piece not in [0,1,2]:
		return False
	board[y-1][x-1] = piece

# Debug function to pretty print the array representation of board.
def PrettyPrint(board, nl="<br>"):
	s = ""
	for row in board:
		for piece in row:
			s += str(piece)
		s += nl
	return s

def PrettyMove(move):
	m = move["Where"]
	return '%s%d' % (chr(ord('A') + m[0] - 1), m[1])



#webapp2.WSGIApplicationで呼び出される
class MainHandler(webapp2.RequestHandler):
    # Handling GET request, just for debugging purposes.
    # If you open this handler directly, it will show you the
    # HTML form here and let you copy-paste some game's JSON
    # here for testing.
    def get(self):
        if not self.request.get('json'):
          self.response.write("""
<body><form method=get>
Paste JSON here:<p/><textarea name=json cols=80 rows=24></textarea>
<p/><input type=submit>
</form>
</body>
""")
          return
        else:
          g = Game(self.request.get('json')) #はじめに呼び出される g = {"Pieces":[配列],"Next":1 or 2}
          self.pickMove(g)

    def post(self):
    	# Reads JSON representation of the board and store as the object.
    	g = Game(self.request.body)
        # Do the picking of a move and print the result.
        self.pickMove(g)


    def pickMove(self, g):
		# Gets all valid moves.
		valid_moves = g.ValidMoves()
		#置くことができるますのリスト
		if len(valid_moves) == 0:
			# Passes if no valid moves.
			self.response.write("PASS")
		else:
    		# Chooses a valid move randomly if available.
            # TO STEP STUDENTS:
            # You'll probably want to change how this works, to do something
            # more clever than just picking a random move.
			#move = random.choice(valid_moves)
			best_move = g.MinMaxScore(3,g)
			self.response.write(PrettyMove(best_move))

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
