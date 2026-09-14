"""
Nine Men's Morris (Trilha / Moinho) - Game Logic Module
"""

POSITIONS_COORDS = {
    0: (0, 0), 1: (3, 0), 2: (6, 0),
    3: (6, 3), 4: (6, 6), 5: (3, 6),
    6: (0, 6), 7: (0, 3),
    8: (1, 1), 9: (3, 1), 10: (5, 1),
    11: (5, 3), 12: (5, 5), 13: (3, 5),
    14: (1, 5), 15: (1, 3),
    16: (2, 2), 17: (3, 2), 18: (4, 2),
    19: (4, 3), 20: (4, 4), 21: (3, 4),
    22: (2, 4), 23: (2, 3)
}

ADJACENT = {
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
    23: [15, 16, 22]
}

MILLS = [
    # Outer square
    [0, 1, 2], [2, 3, 4], [4, 5, 6], [6, 7, 0],
    # Middle square
    [8, 9, 10], [10, 11, 12], [12, 13, 14], [14, 15, 8],
    # Inner square
    [16, 17, 18], [18, 19, 20], [20, 21, 22], [22, 23, 16],
    # Cross connections
    [1, 9, 17], [3, 11, 19], [5, 13, 21], [7, 15, 23]
]


class NineMensMorris:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [None] * 24
        self.current_player = 'P1'
        self.unplaced_pieces = {'P1': 9, 'P2': 9}
        self.pieces_on_board = {'P1': 0, 'P2': 0}
        self.must_remove = False
        self.winner = None
        self.game_over = False
        self.winner_reason = ""
        self.message = "Vez do Jogador 1 (Brancas) - Coloque uma peça no tabuleiro."

    @property
    def opponent(self):
        return 'P2' if self.current_player == 'P1' else 'P1'

    def get_phase(self, player=None):
        if player is None:
            player = self.current_player
        if self.unplaced_pieces[player] > 0:
            return 1  # Placement
        elif self.pieces_on_board[player] > 3:
            return 2  # Movement
        else:
            return 3  # Flying (Saltos)

    def is_in_mill(self, pos, player):
        """Checks if the piece at `pos` belongs to `player` and is part of a mill."""
        if self.board[pos] != player:
            return False
        for mill in MILLS:
            if pos in mill:
                if all(self.board[p] == player for p in mill):
                    return True
        return False

    def get_valid_placements(self):
        if self.game_over or self.must_remove:
            return []
        if self.get_phase() != 1:
            return []
        return [i for i in range(24) if self.board[i] is None]

    def get_valid_moves_from(self, from_pos):
        if self.game_over or self.must_remove:
            return []
        if self.board[from_pos] != self.current_player:
            return []
        phase = self.get_phase()
        if phase == 1:
            return []
        elif phase == 2:
            return [adj for adj in ADJACENT[from_pos] if self.board[adj] is None]
        elif phase == 3:
            return [i for i in range(24) if self.board[i] is None]
        return []

    def get_valid_removals(self):
        if not self.must_remove or self.game_over:
            return []
        opp = self.opponent
        opp_pieces = [i for i in range(24) if self.board[i] == opp]
        
        # Check if all opponent pieces are in mills
        non_mill_pieces = [pos for pos in opp_pieces if not self.is_in_mill(pos, opp)]
        if non_mill_pieces:
            return non_mill_pieces
        else:
            # If all are in mills, any opponent piece can be removed
            return opp_pieces

    def has_valid_moves(self, player):
        phase = self.get_phase(player)
        if phase == 1:
            return any(spot is None for spot in self.board)
        elif phase == 3:
            return any(spot is None for spot in self.board)
        elif phase == 2:
            player_pieces = [i for i in range(24) if self.board[i] == player]
            for pos in player_pieces:
                if any(self.board[adj] is None for adj in ADJACENT[pos]):
                    return True
            return False
        return False

    def check_victory_and_switch_turn(self):
        opp = self.opponent
        opp_phase = self.get_phase(opp)

        # Check piece count condition for opponent
        if opp_phase != 1 and self.pieces_on_board[opp] < 3:
            self.game_over = True
            self.winner = self.current_player
            p_name = "Jogador 1 (Brancas)" if self.winner == 'P1' else "Jogador 2 (Pretas)"
            self.winner_reason = f"O {p_name} venceu! O oponente ficou com menos de 3 peças."
            self.message = self.winner_reason
            return

        # Check block condition for opponent
        if not self.has_valid_moves(opp):
            self.game_over = True
            self.winner = self.current_player
            p_name = "Jogador 1 (Brancas)" if self.winner == 'P1' else "Jogador 2 (Pretas)"
            self.winner_reason = f"O {p_name} venceu! O oponente não possui movimentos válidos (bloqueio total)."
            self.message = self.winner_reason
            return

        # Switch turn
        self.current_player = opp
        curr_p_name = "Jogador 1 (Brancas)" if self.current_player == 'P1' else "Jogador 2 (Pretas)"
        phase = self.get_phase()
        if phase == 1:
            self.message = f"Vez do {curr_p_name} - Coloque uma peça."
        elif phase == 2:
            self.message = f"Vez do {curr_p_name} - Mova uma peça para uma casa adjacente."
        else:
            self.message = f"Vez do {curr_p_name} (Fase de Voo!) - Mova uma peça para qualquer casa livre."

    def place_piece(self, pos):
        if self.game_over:
            return False, "O jogo já terminou."
        if self.must_remove:
            return False, "Você deve remover uma peça adversária primeiro."
        if self.get_phase() != 1:
            return False, "Não está na fase de colocação."
        if pos < 0 or pos >= 24 or self.board[pos] is not None:
            return False, "Posição inválida ou já ocupada."

        self.board[pos] = self.current_player
        self.unplaced_pieces[self.current_player] -= 1
        self.pieces_on_board[self.current_player] += 1

        # Check if a mill was formed by this placement
        if self.is_in_mill(pos, self.current_player):
            self.must_remove = True
            curr_p_name = "Jogador 1 (Brancas)" if self.current_player == 'P1' else "Jogador 2 (Pretas)"
            self.message = f"Moinho formado! {curr_p_name}, remova uma peça adversária."
            return True, "Moinho formado!"
        else:
            self.check_victory_and_switch_turn()
            return True, "Peça colocada."

    def move_piece(self, from_pos, to_pos):
        if self.game_over:
            return False, "O jogo já terminou."
        if self.must_remove:
            return False, "Você deve remover uma peça adversária primeiro."
        if self.get_phase() == 1:
            return False, "Ainda há peças não colocadas."
        if from_pos < 0 or from_pos >= 24 or self.board[from_pos] != self.current_player:
            return False, "Seleção de peça inválida."
        if to_pos < 0 or to_pos >= 24 or self.board[to_pos] is not None:
            return False, "Destino inválido ou ocupado."

        phase = self.get_phase()
        if phase == 2:
            if to_pos not in ADJACENT[from_pos]:
                return False, "Movimento deve ser para uma posição adjacente."

        self.board[from_pos] = None
        self.board[to_pos] = self.current_player

        # Check if a mill was formed by this move
        if self.is_in_mill(to_pos, self.current_player):
            self.must_remove = True
            curr_p_name = "Jogador 1 (Brancas)" if self.current_player == 'P1' else "Jogador 2 (Pretas)"
            self.message = f"Moinho formado! {curr_p_name}, remova uma peça adversária."
            return True, "Moinho formado!"
        else:
            self.check_victory_and_switch_turn()
            return True, "Peça movida."

    def remove_piece(self, pos):
        if self.game_over:
            return False, "O jogo já terminou."
        if not self.must_remove:
            return False, "Nenhuma remoção pendente."
        
        valid_removals = self.get_valid_removals()
        if pos not in valid_removals:
            return False, "Peça inválida para remoção (não pertence ao oponente ou está em um moinho protegido)."

        opp = self.opponent
        self.board[pos] = None
        self.pieces_on_board[opp] -= 1
        self.must_remove = False

        self.check_victory_and_switch_turn()
        return True, "Peça removida."

    def to_dict(self):
        return {
            'board': self.board,
            'current_player': self.current_player,
            'unplaced_pieces': self.unplaced_pieces,
            'pieces_on_board': self.pieces_on_board,
            'must_remove': self.must_remove,
            'winner': self.winner,
            'game_over': self.game_over,
            'winner_reason': self.winner_reason,
            'message': self.message,
            'valid_placements': self.get_valid_placements(),
            'valid_removals': self.get_valid_removals(),
            'phase': self.get_phase(),
            'opponent_phase': self.get_phase(self.opponent)
        }

    @classmethod
    def from_dict(cls, data):
        game = cls()
        game.board = data.get('board', [None] * 24)
        game.current_player = data.get('current_player', 'P1')
        game.unplaced_pieces = data.get('unplaced_pieces', {'P1': 9, 'P2': 9})
        game.pieces_on_board = data.get('pieces_on_board', {'P1': 0, 'P2': 0})
        game.must_remove = data.get('must_remove', False)
        game.winner = data.get('winner', None)
        game.game_over = data.get('game_over', False)
        game.winner_reason = data.get('winner_reason', "")
        game.message = data.get('message', "")
        return game
