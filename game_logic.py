"""
Nine Men's Morris (Trilha / Moinho) - Game Logic Module

Regras implementadas (variante clássica):
- 24 posições, 9 peças por jogador
- Fase 1: colocação (enquanto houver peças por colocar)
- Fase 2: movimento para casa adjacente (quando tem > 3 peças no tabuleiro)
- Fase 3: voo / flying (quando tem exatamente 3 peças)
- Moinho: 3 peças alinhadas → remover 1 peça adversária
  (preferência por peças fora de moinho; se todas estiverem em moinho, qualquer uma)
- Vitória: oponente com < 3 peças (após fase de colocação) ou sem movimentos legais
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

POSITIONS_COORDS = {
    0: (0, 0), 1: (3, 0), 2: (6, 0),
    3: (6, 3), 4: (6, 6), 5: (3, 6),
    6: (0, 6), 7: (0, 3),
    8: (1, 1), 9: (3, 1), 10: (5, 1),
    11: (5, 3), 12: (5, 5), 13: (3, 5),
    14: (1, 5), 15: (1, 3),
    16: (2, 2), 17: (3, 2), 18: (4, 2),
    19: (4, 3), 20: (4, 4), 21: (3, 4),
    22: (2, 4), 23: (2, 3),
}

ADJACENT: Dict[int, List[int]] = {
    0: [1, 7],
    1: [0, 2, 9],
    2: [1, 3],
    3: [2, 4, 11],
    4: [3, 5],
    5: [4, 6, 13],
    6: [5, 7],
    7: [0, 6, 15],
    8: [9, 15],
    9: [1, 8, 10, 17],
    10: [9, 11],
    11: [3, 10, 12, 19],
    12: [11, 13],
    13: [5, 12, 14, 21],
    14: [13, 15],
    15: [7, 8, 14, 23],
    16: [17, 23],
    17: [9, 16, 18],
    18: [17, 19],
    19: [11, 18, 20],
    20: [19, 21],
    21: [13, 20, 22],
    22: [21, 23],
    23: [15, 16, 22],
}

MILLS: List[List[int]] = [
    # Outer square
    [0, 1, 2], [2, 3, 4], [4, 5, 6], [6, 7, 0],
    # Middle square
    [8, 9, 10], [10, 11, 12], [12, 13, 14], [14, 15, 8],
    # Inner square
    [16, 17, 18], [18, 19, 20], [20, 21, 22], [22, 23, 16],
    # Cross connections
    [1, 9, 17], [3, 11, 19], [5, 13, 21], [7, 15, 23],
]

PLAYER_NAMES = {
    "P1": "Jogador 1 (Brancas)",
    "P2": "Jogador 2 (Pretas)",
}


class NineMensMorris:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.board: List[Optional[str]] = [None] * 24
        self.current_player: str = "P1"
        self.unplaced_pieces: Dict[str, int] = {"P1": 9, "P2": 9}
        self.pieces_on_board: Dict[str, int] = {"P1": 0, "P2": 0}
        self.must_remove: bool = False
        self.winner: Optional[str] = None
        self.game_over: bool = False
        self.winner_reason: str = ""
        self.message: str = (
            f"Vez do {PLAYER_NAMES['P1']} — Coloque uma peça no tabuleiro."
        )
        self.last_action: Optional[Dict[str, Any]] = None
        self.move_count: int = 0

    @property
    def opponent(self) -> str:
        return "P2" if self.current_player == "P1" else "P1"

    def get_phase(self, player: Optional[str] = None) -> int:
        if player is None:
            player = self.current_player
        if self.unplaced_pieces[player] > 0:
            return 1
        if self.pieces_on_board[player] > 3:
            return 2
        return 3

    def is_in_mill(self, pos: int, player: str) -> bool:
        if self.board[pos] != player:
            return False
        for mill in MILLS:
            if pos in mill and all(self.board[p] == player for p in mill):
                return True
        return False

    def mills_formed_at(self, pos: int, player: str) -> List[List[int]]:
        formed = []
        if self.board[pos] != player:
            return formed
        for mill in MILLS:
            if pos in mill and all(self.board[p] == player for p in mill):
                formed.append(list(mill))
        return formed

    def get_valid_placements(self) -> List[int]:
        if self.game_over or self.must_remove or self.get_phase() != 1:
            return []
        return [i for i in range(24) if self.board[i] is None]

    def get_valid_moves_from(self, from_pos: int) -> List[int]:
        if self.game_over or self.must_remove:
            return []
        if not (0 <= from_pos < 24) or self.board[from_pos] != self.current_player:
            return []
        phase = self.get_phase()
        if phase == 1:
            return []
        if phase == 2:
            return [adj for adj in ADJACENT[from_pos] if self.board[adj] is None]
        return [i for i in range(24) if self.board[i] is None]

    def get_all_valid_moves(self) -> Dict[str, List[int]]:
        if self.game_over or self.must_remove or self.get_phase() == 1:
            return {}
        result: Dict[str, List[int]] = {}
        for pos in range(24):
            if self.board[pos] == self.current_player:
                moves = self.get_valid_moves_from(pos)
                if moves:
                    result[str(pos)] = moves
        return result

    def get_movable_pieces(self) -> List[int]:
        return [int(p) for p in self.get_all_valid_moves().keys()]

    def get_valid_removals(self) -> List[int]:
        if not self.must_remove or self.game_over:
            return []
        opp = self.opponent
        opp_pieces = [i for i in range(24) if self.board[i] == opp]
        non_mill = [p for p in opp_pieces if not self.is_in_mill(p, opp)]
        return non_mill if non_mill else list(opp_pieces)

    def has_valid_moves(self, player: str) -> bool:
        phase = self.get_phase(player)
        if phase == 1:
            return any(spot is None for spot in self.board)
        if phase == 3:
            return any(spot is None for spot in self.board)
        for pos in range(24):
            if self.board[pos] == player:
                if any(self.board[adj] is None for adj in ADJACENT[pos]):
                    return True
        return False

    def _player_label(self, player: str) -> str:
        return PLAYER_NAMES.get(player, player)

    def check_victory_and_switch_turn(self) -> None:
        opp = self.opponent
        opp_phase = self.get_phase(opp)
        if opp_phase != 1 and self.pieces_on_board[opp] < 3:
            self.game_over = True
            self.winner = self.current_player
            self.winner_reason = (
                f"O {self._player_label(self.winner)} venceu! "
                f"O oponente ficou com menos de 3 peças."
            )
            self.message = self.winner_reason
            return
        if not self.has_valid_moves(opp):
            self.game_over = True
            self.winner = self.current_player
            self.winner_reason = (
                f"O {self._player_label(self.winner)} venceu! "
                f"O oponente não possui movimentos válidos (bloqueio total)."
            )
            self.message = self.winner_reason
            return
        self.current_player = opp
        self._set_turn_message()

    def _set_turn_message(self) -> None:
        name = self._player_label(self.current_player)
        phase = self.get_phase()
        if phase == 1:
            remaining = self.unplaced_pieces[self.current_player]
            self.message = (
                f"Vez do {name} — Coloque uma peça "
                f"({remaining} restante{'s' if remaining != 1 else ''})."
            )
        elif phase == 2:
            self.message = (
                f"Vez do {name} — Mova uma peça para uma casa adjacente."
            )
        else:
            self.message = (
                f"Vez do {name} (Fase de Voo!) — "
                f"Mova uma peça para qualquer casa livre."
            )

    def _set_mill_message(self) -> None:
        name = self._player_label(self.current_player)
        self.message = f"Moinho formado! {name}, remova uma peça adversária."

    def place_piece(self, pos: int) -> Tuple[bool, str]:
        if self.game_over:
            return False, "O jogo já terminou."
        if self.must_remove:
            return False, "Você deve remover uma peça adversária primeiro."
        if self.get_phase() != 1:
            return False, "Não está na fase de colocação."
        if not isinstance(pos, int) or pos < 0 or pos >= 24:
            return False, "Posição inválida."
        if self.board[pos] is not None:
            return False, "Posição já ocupada."
        self.board[pos] = self.current_player
        self.unplaced_pieces[self.current_player] -= 1
        self.pieces_on_board[self.current_player] += 1
        self.move_count += 1
        self.last_action = {"type": "place", "player": self.current_player, "pos": pos}
        if self.is_in_mill(pos, self.current_player):
            self.must_remove = True
            self._set_mill_message()
            return True, "Moinho formado!"
        self.check_victory_and_switch_turn()
        return True, "Peça colocada."

    def move_piece(self, from_pos: int, to_pos: int) -> Tuple[bool, str]:
        if self.game_over:
            return False, "O jogo já terminou."
        if self.must_remove:
            return False, "Você deve remover uma peça adversária primeiro."
        if self.get_phase() == 1:
            return False, "Ainda há peças por colocar."
        if not isinstance(from_pos, int) or not isinstance(to_pos, int):
            return False, "Posições inválidas."
        if from_pos < 0 or from_pos >= 24 or self.board[from_pos] != self.current_player:
            return False, "Seleção de peça inválida."
        if to_pos < 0 or to_pos >= 24 or self.board[to_pos] is not None:
            return False, "Destino inválido ou ocupado."
        phase = self.get_phase()
        if phase == 2 and to_pos not in ADJACENT[from_pos]:
            return False, "Movimento deve ser para uma posição adjacente."
        self.board[from_pos] = None
        self.board[to_pos] = self.current_player
        self.move_count += 1
        self.last_action = {
            "type": "move",
            "player": self.current_player,
            "from_pos": from_pos,
            "to_pos": to_pos,
        }
        if self.is_in_mill(to_pos, self.current_player):
            self.must_remove = True
            self._set_mill_message()
            return True, "Moinho formado!"
        self.check_victory_and_switch_turn()
        return True, "Peça movida."

    def remove_piece(self, pos: int) -> Tuple[bool, str]:
        if self.game_over:
            return False, "O jogo já terminou."
        if not self.must_remove:
            return False, "Nenhuma remoção pendente."
        if not isinstance(pos, int) or pos < 0 or pos >= 24:
            return False, "Posição inválida."
        valid = self.get_valid_removals()
        if pos not in valid:
            return (
                False,
                "Peça inválida para remoção "
                "(não pertence ao oponente ou está num moinho protegido).",
            )
        opp = self.opponent
        self.board[pos] = None
        self.pieces_on_board[opp] -= 1
        self.must_remove = False
        self.move_count += 1
        self.last_action = {
            "type": "remove",
            "player": self.current_player,
            "pos": pos,
            "removed_player": opp,
        }
        self.check_victory_and_switch_turn()
        return True, "Peça removida."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "board": self.board,
            "current_player": self.current_player,
            "unplaced_pieces": self.unplaced_pieces,
            "pieces_on_board": self.pieces_on_board,
            "must_remove": self.must_remove,
            "winner": self.winner,
            "game_over": self.game_over,
            "winner_reason": self.winner_reason,
            "message": self.message,
            "valid_placements": self.get_valid_placements(),
            "valid_removals": self.get_valid_removals(),
            "valid_moves": self.get_all_valid_moves(),
            "movable_pieces": self.get_movable_pieces(),
            "phase": self.get_phase(),
            "opponent_phase": self.get_phase(self.opponent),
            "last_action": self.last_action,
            "move_count": self.move_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NineMensMorris":
        game = cls()
        game.board = data.get("board", [None] * 24)
        game.current_player = data.get("current_player", "P1")
        game.unplaced_pieces = data.get("unplaced_pieces", {"P1": 9, "P2": 9})
        game.pieces_on_board = data.get("pieces_on_board", {"P1": 0, "P2": 0})
        game.must_remove = data.get("must_remove", False)
        game.winner = data.get("winner")
        game.game_over = data.get("game_over", False)
        game.winner_reason = data.get("winner_reason", "")
        game.message = data.get("message", "")
        game.last_action = data.get("last_action")
        game.move_count = data.get("move_count", 0)
        return game
