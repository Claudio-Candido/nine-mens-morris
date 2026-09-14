// Nine Men's Morris - Frontend JavaScript

const POSITIONS_COORDS = {
    0: [50, 50],   1: [300, 50],  2: [550, 50],
    3: [550, 300], 4: [550, 550], 5: [300, 550],
    6: [50, 550],  7: [50, 300],
    8: [130, 130], 9: [300, 130], 10: [470, 130],
    11: [470, 300], 12: [470, 470], 13: [300, 470],
    14: [130, 470], 15: [130, 300],
    16: [210, 210], 17: [300, 210], 18: [390, 210],
    19: [390, 300], 20: [390, 390], 21: [300, 390],
    22: [210, 390], 23: [210, 300]
};

const BOARD_LINES = [
    [0, 2], [2, 4], [4, 6], [6, 0],
    [8, 10], [10, 12], [12, 14], [14, 8],
    [16, 18], [18, 20], [20, 22], [22, 16],
    [1, 17], [3, 19], [5, 21], [7, 23]
];

const ADJACENT = {
    0: [1, 7], 1: [0, 2, 9], 2: [1, 3],
    3: [2, 4, 11], 4: [3, 5], 5: [4, 6, 13],
    6: [5, 7], 7: [0, 6, 15], 8: [9, 15],
    9: [1, 8, 10, 17], 10: [9, 11], 11: [3, 10, 12, 19],
    12: [11, 13], 13: [5, 12, 14, 21], 14: [13, 15],
    15: [7, 8, 14, 23], 16: [17, 23], 17: [9, 16, 18],
    18: [17, 19], 19: [11, 18, 20], 20: [19, 21],
    21: [13, 20, 22], 22: [21, 23], 23: [15, 16, 22]
};

let gameState = null;
let selectedPos = null;

document.addEventListener('DOMContentLoaded', () => {
    initBoard();
    fetchGameState();

    document.getElementById('btn-reset').addEventListener('click', resetGame);
    document.getElementById('btn-rules').addEventListener('click', () => {
        document.getElementById('rules-modal').style.display = 'flex';
    });
    document.getElementById('modal-close').addEventListener('click', () => {
        document.getElementById('rules-modal').style.display = 'none';
    });
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('rules-modal');
        if (e.target === modal) modal.style.display = 'none';
    });
});

function initBoard() {
    const svg = document.getElementById('board-svg');
    BOARD_LINES.forEach(([a, b]) => {
        const [x1, y1] = POSITIONS_COORDS[a];
        const [x2, y2] = POSITIONS_COORDS[b];
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', x1);
        line.setAttribute('y1', y1);
        line.setAttribute('x2', x2);
        line.setAttribute('y2', y2);
        line.setAttribute('class', 'board-line');
        svg.appendChild(line);
    });

    for (let i = 0; i < 24; i++) {
        const [cx, cy] = POSITIONS_COORDS[i];
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', cx);
        circle.setAttribute('cy', cy);
        circle.setAttribute('r', 18);
        circle.setAttribute('class', 'node node-base');
        circle.setAttribute('data-pos', i);
        circle.addEventListener('click', () => handleNodeClick(i));
        svg.appendChild(circle);

        const piece = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        piece.setAttribute('cx', cx);
        piece.setAttribute('cy', cy);
        piece.setAttribute('r', 14);
        piece.setAttribute('class', 'piece');
        piece.setAttribute('data-pos', i);
        piece.style.display = 'none';
        svg.appendChild(piece);
    }
}

async function fetchGameState() {
    try {
        const res = await fetch('/api/state');
        const data = await res.json();
        if (data.success) {
            gameState = data.game_state;
            selectedPos = null;
            render();
        }
    } catch (err) {
        console.error('Error fetching state:', err);
        document.getElementById('status-message').textContent = 'Erro ao carregar o jogo.';
    }
}

async function sendAction(payload) {
    try {
        const res = await fetch('/api/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.game_state) {
            gameState = data.game_state;
            selectedPos = null;
            render();
        }
    } catch (err) {
        console.error('Error sending action:', err);
    }
}

async function resetGame() {
    try {
        const res = await fetch('/api/reset', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            gameState = data.game_state;
            selectedPos = null;
            render();
        }
    } catch (err) {
        console.error('Error resetting game:', err);
    }
}

function getLegalMovesForSelected() {
    if (selectedPos === null || !gameState) return [];
    if (gameState.game_over || gameState.must_remove) return [];
    const phase = gameState.phase;
    if (phase === 1) return [];
    if (phase === 2) {
        return ADJACENT[selectedPos].filter(adj => gameState.board[adj] === null);
    } else if (phase === 3) {
        return gameState.board.map((val, idx) => val === null ? idx : null).filter(val => val !== null);
    }
    return [];
}

function handleNodeClick(pos) {
    if (!gameState || gameState.game_over) return;

    if (gameState.must_remove) {
        if (gameState.valid_removals.includes(pos)) {
            sendAction({ action: 'remove', pos: pos });
        }
        return;
    }

    if (gameState.phase === 1) {
        if (gameState.valid_placements.includes(pos)) {
            sendAction({ action: 'place', pos: pos });
        }
        return;
    }

    const piece = gameState.board[pos];

    if (piece === gameState.current_player) {
        if (selectedPos === pos) {
            selectedPos = null;
        } else {
            selectedPos = pos;
        }
        render();
        return;
    }

    if (selectedPos !== null && piece === null) {
        const legalMoves = getLegalMovesForSelected();
        if (legalMoves.includes(pos)) {
            const from = selectedPos;
            selectedPos = null;
            sendAction({ action: 'move', from_pos: from, to_pos: pos });
        }
    }
}

function render() {
    if (!gameState) return;

    const legalMoves = getLegalMovesForSelected();

    // Status
    const statusBanner = document.getElementById('status-banner');
    const statusMsg = document.getElementById('status-message');
    statusMsg.textContent = gameState.message || '';
    statusBanner.classList.remove('alert-remove', 'game-over');
    if (gameState.must_remove) statusBanner.classList.add('alert-remove');
    if (gameState.game_over) statusBanner.classList.add('game-over');

    // Player cards
    document.getElementById('card-p1').classList.toggle('active', gameState.current_player === 'P1' && !gameState.game_over);
    document.getElementById('card-p2').classList.toggle('active', gameState.current_player === 'P2' && !gameState.game_over);

    document.getElementById('p1-unplaced').textContent = gameState.unplaced_pieces.P1;
    document.getElementById('p1-board').textContent = gameState.pieces_on_board.P1;
    document.getElementById('p2-unplaced').textContent = gameState.unplaced_pieces.P2;
    document.getElementById('p2-board').textContent = gameState.pieces_on_board.P2;

    const phaseLabel = (p) => p === 1 ? 'Fase 1' : p === 2 ? 'Fase 2' : 'Fase 3 (Voo)';
    document.getElementById('p1-phase').textContent = phaseLabel(gameState.current_player === 'P1' ? gameState.phase : gameState.opponent_phase);
    document.getElementById('p2-phase').textContent = phaseLabel(gameState.current_player === 'P2' ? gameState.phase : gameState.opponent_phase);

    // Nodes and pieces
    for (let i = 0; i < 24; i++) {
        const node = document.querySelector(`.node[data-pos="${i}"]`);
        const pieceEl = document.querySelector(`.piece[data-pos="${i}"]`);
        if (!node || !pieceEl) continue;

        node.className = 'node node-base';
        if (!gameState.must_remove && gameState.phase === 1 && gameState.valid_placements.includes(i)) {
            node.classList.add('node-valid');
        } else if (!gameState.must_remove && (gameState.phase === 2 || gameState.phase === 3) && selectedPos !== null && legalMoves.includes(i)) {
            node.classList.add('node-valid');
        }
        if (selectedPos === i) node.classList.add('node-selected');
        if (gameState.must_remove && gameState.valid_removals.includes(i)) node.classList.add('node-remove');

        const owner = gameState.board[i];
        if (owner) {
            pieceEl.style.display = 'block';
            pieceEl.setAttribute('class', 'piece ' + (owner === 'P1' ? 'piece-p1-svg' : 'piece-p2-svg'));
        } else {
            pieceEl.style.display = 'none';
        }
    }
}
