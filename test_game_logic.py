import unittest
import sys
import os

sys.path.append(os.path.dirname(__file__))

from game_logic import NineMensMorris
from app import app

class TestNineMensMorris(unittest.TestCase):
    def test_initial_state(self):
        game = NineMensMorris()
        self.assertEqual(game.current_player, 'P1')
        self.assertEqual(game.unplaced_pieces, {'P1': 9, 'P2': 9})
        self.assertEqual(game.pieces_on_board, {'P1': 0, 'P2': 0})
        self.assertFalse(game.must_remove)
        self.assertFalse(game.game_over)
        self.assertEqual(game.get_phase(), 1)
        self.assertEqual(len(game.get_valid_placements()), 24)

    def test_placement_and_turn_switch(self):
        game = NineMensMorris()
        success, msg = game.place_piece(0)
        self.assertTrue(success)
        self.assertEqual(game.board[0], 'P1')
        self.assertEqual(game.unplaced_pieces['P1'], 8)
        self.assertEqual(game.pieces_on_board['P1'], 1)
        self.assertEqual(game.current_player, 'P2')

    def test_mill_formation_and_removal(self):
        game = NineMensMorris()
        # P1 places 0
        game.place_piece(0)
        # P2 places 8
        game.place_piece(8)
        # P1 places 1
        game.place_piece(1)
        # P2 places 9
        game.place_piece(9)
        # P1 places 2 (forms mill [0, 1, 2])
        success, msg = game.place_piece(2)
        self.assertTrue(success)
        self.assertTrue(game.must_remove)
        self.assertEqual(game.current_player, 'P1')

        self.assertEqual(set(game.get_valid_removals()), {8, 9})

        # Attempt to remove invalid piece
        success, msg = game.remove_piece(0)
        self.assertFalse(success)

        # Remove valid
        success, msg = game.remove_piece(8)
        self.assertTrue(success)
        self.assertFalse(game.must_remove)
        self.assertEqual(game.board[8], None)
        self.assertEqual(game.pieces_on_board['P2'], 1)
        self.assertEqual(game.current_player, 'P2')

    def test_protected_mill_removal_rule(self):
        game = NineMensMorris()
        # Build a protected mill scenario roughly
        # Place pieces to form mills for both
        # Simplified: force state
        game.board = [None]*24
        game.board[0] = 'P1'
        game.board[1] = 'P1'
        game.board[2] = 'P1'  # mill
        game.board[8] = 'P2'
        game.board[9] = 'P2'
        game.board[10] = 'P2' # mill
        game.unplaced_pieces = {'P1': 0, 'P2': 0}
        game.pieces_on_board = {'P1': 3, 'P2': 3}
        game.current_player = 'P1'
        game.must_remove = True
        # All P2 pieces in mill -> can remove any
        removals = game.get_valid_removals()
        self.assertEqual(set(removals), {8, 9, 10})

    def test_movement_and_flying(self):
        game = NineMensMorris()
        game.board = [None]*24
        game.board[0] = 'P1'
        game.board[1] = 'P1'
        game.board[3] = 'P1'
        game.board[8] = 'P2'
        game.board[9] = 'P2'
        game.board[10] = 'P2'
        game.unplaced_pieces = {'P1': 0, 'P2': 0}
        game.pieces_on_board = {'P1': 3, 'P2': 3}
        game.current_player = 'P1'
        # Phase 3 for P1 (3 pieces)
        self.assertEqual(game.get_phase('P1'), 3)
        moves = game.get_valid_moves_from(0)
        self.assertIn(2, moves)  # any empty
        self.assertNotIn(1, moves)  # occupied by self

        success, msg = game.move_piece(0, 2)
        self.assertTrue(success)
        self.assertEqual(game.board[0], None)
        self.assertEqual(game.board[2], 'P1')

    def test_victory_condition_less_than_3_pieces(self):
        game = NineMensMorris()
        game.board = [None]*24
        game.board[0] = 'P1'
        game.board[1] = 'P1'
        game.board[2] = 'P1'
        game.board[8] = 'P2'
        game.board[9] = 'P2'
        game.unplaced_pieces = {'P1': 0, 'P2': 0}
        game.pieces_on_board = {'P1': 3, 'P2': 2}
        game.current_player = 'P1'
        game.must_remove = True
        success, msg = game.remove_piece(8)
        self.assertTrue(success)
        self.assertTrue(game.game_over)
        self.assertEqual(game.winner, 'P1')

    def test_flask_routes(self):
        client = app.test_client()
        with client.session_transaction() as sess:
            sess.clear()
        r = client.get('/')
        self.assertEqual(r.status_code, 200)
        r = client.get('/api/state')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json()['success'])
        r = client.post('/api/action', json={'action': 'place', 'pos': 0})
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertTrue(data['success'])
        r = client.post('/api/reset')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json()['success'])

if __name__ == '__main__':
    unittest.main()
