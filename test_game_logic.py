import unittest
import sys
import os

sys.path.append(os.path.dirname(__file__))

from game_logic import NineMensMorris
from app import app


class TestNineMensMorris(unittest.TestCase):
    def test_initial_state(self):
        game = NineMensMorris()
        self.assertEqual(game.current_player, "P1")
        self.assertEqual(game.unplaced_pieces, {"P1": 9, "P2": 9})
        self.assertEqual(game.pieces_on_board, {"P1": 0, "P2": 0})
        self.assertFalse(game.must_remove)
        self.assertFalse(game.game_over)
        self.assertEqual(game.get_phase(), 1)
        self.assertEqual(len(game.get_valid_placements()), 24)
        self.assertEqual(game.get_all_valid_moves(), {})
        self.assertEqual(game.get_movable_pieces(), [])

    def test_placement_and_turn_switch(self):
        game = NineMensMorris()
        success, msg = game.place_piece(0)
        self.assertTrue(success)
        self.assertEqual(game.board[0], "P1")
        self.assertEqual(game.unplaced_pieces["P1"], 8)
        self.assertEqual(game.pieces_on_board["P1"], 1)
        self.assertEqual(game.current_player, "P2")
        self.assertEqual(game.last_action["type"], "place")
        self.assertEqual(game.last_action["pos"], 0)

    def test_mill_formation_and_removal(self):
        game = NineMensMorris()
        game.place_piece(0)
        game.place_piece(8)
        game.place_piece(1)
        game.place_piece(9)
        success, msg = game.place_piece(2)
        self.assertTrue(success)
        self.assertTrue(game.must_remove)
        self.assertEqual(game.current_player, "P1")
        self.assertEqual(set(game.get_valid_removals()), {8, 9})

        success, msg = game.remove_piece(0)
        self.assertFalse(success)

        success, msg = game.remove_piece(8)
        self.assertTrue(success)
        self.assertIsNone(game.board[8])
        self.assertFalse(game.must_remove)
        self.assertEqual(game.pieces_on_board["P2"], 1)
        self.assertEqual(game.current_player, "P2")
        self.assertEqual(game.last_action["type"], "remove")

    def test_protected_mill_removal_rule(self):
        game = NineMensMorris()
        game.unplaced_pieces = {"P1": 0, "P2": 0}
        game.pieces_on_board = {"P1": 4, "P2": 4}
        game.board[8] = "P2"
        game.board[9] = "P2"
        game.board[10] = "P2"
        game.board[12] = "P2"
        game.board[0] = "P1"
        game.board[1] = "P1"
        game.board[2] = "P1"
        game.board[4] = "P1"
        game.current_player = "P1"
        game.must_remove = True

        removals = game.get_valid_removals()
        self.assertEqual(removals, [12])

        game.board[12] = None
        game.pieces_on_board["P2"] = 3
        removals_all_in_mill = game.get_valid_removals()
        self.assertEqual(set(removals_all_in_mill), {8, 9, 10})

    def test_movement_and_flying(self):
        game = NineMensMorris()
        game.unplaced_pieces = {"P1": 0, "P2": 0}
        game.pieces_on_board = {"P1": 4, "P2": 3}
        game.board[0] = "P1"
        game.board[4] = "P1"
        game.board[6] = "P1"
        game.board[14] = "P1"
        game.board[8] = "P2"
        game.board[12] = "P2"
        game.board[16] = "P2"
        game.current_player = "P1"

        self.assertEqual(game.get_phase("P1"), 2)
        self.assertEqual(game.get_phase("P2"), 3)
        self.assertEqual(set(game.get_valid_moves_from(0)), {1, 7})

        moves = game.get_all_valid_moves()
        self.assertIn("0", moves)
        self.assertEqual(set(moves["0"]), {1, 7})

        success, msg = game.move_piece(0, 1)
        self.assertTrue(success)
        self.assertIsNone(game.board[0])
        self.assertEqual(game.board[1], "P1")
        self.assertEqual(game.current_player, "P2")

        self.assertEqual(len(game.get_valid_moves_from(8)), 17)
        success, msg = game.move_piece(8, 23)
        self.assertTrue(success)
        self.assertIsNone(game.board[8])
        self.assertEqual(game.board[23], "P2")

    def test_victory_condition_less_than_3_pieces(self):
        game = NineMensMorris()
        game.unplaced_pieces = {"P1": 0, "P2": 0}
        game.pieces_on_board = {"P1": 3, "P2": 3}
        game.board[0] = "P1"
        game.board[1] = "P1"
        game.board[4] = "P1"
        game.board[8] = "P2"
        game.board[9] = "P2"
        game.board[10] = "P2"
        game.current_player = "P1"
        game.must_remove = True

        success, msg = game.remove_piece(8)
        self.assertTrue(success)
        self.assertTrue(game.game_over)
        self.assertEqual(game.winner, "P1")
        self.assertIn("menos de 3 peças", game.winner_reason)

    def test_to_dict_includes_new_fields(self):
        game = NineMensMorris()
        d = game.to_dict()
        self.assertIn("valid_moves", d)
        self.assertIn("movable_pieces", d)
        self.assertIn("last_action", d)
        self.assertIn("move_count", d)
        self.assertEqual(d["valid_moves"], {})
        self.assertEqual(d["movable_pieces"], [])

    def test_invalid_actions(self):
        game = NineMensMorris()
        ok, _ = game.place_piece(-1)
        self.assertFalse(ok)
        ok, _ = game.place_piece(0)
        self.assertTrue(ok)
        ok, _ = game.place_piece(0)
        self.assertFalse(ok)
        ok, _ = game.move_piece(0, 1)
        self.assertFalse(ok)

    def test_flask_routes(self):
        client = app.test_client()

        res = client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Nine Men's Morris", res.data)

        res = client.get("/api/state")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["game_state"]["current_player"], "P1")
        self.assertIn("valid_moves", data["game_state"])
        self.assertIn("movable_pieces", data["game_state"])

        res = client.post("/api/action", json={"action": "place", "pos": 0})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["game_state"]["board"][0], "P1")
        self.assertEqual(data["game_state"]["current_player"], "P2")

        res = client.post("/api/reset")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsNone(data["game_state"]["board"][0])


if __name__ == "__main__":
    unittest.main()
