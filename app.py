import os
from flask import Flask, render_template, request, jsonify, session
from game_logic import NineMensMorris

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'nine_mens_morris_secret_key_12345')

def get_game():
    if 'game_state' not in session:
        game = NineMensMorris()
        session['game_state'] = game.to_dict()
        return game
    return NineMensMorris.from_dict(session['game_state'])

def save_game(game):
    session['game_state'] = game.to_dict()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/state', methods=['GET'])
def get_state():
    game = get_game()
    return jsonify({
        'success': True,
        'game_state': game.to_dict()
    })

@app.route('/api/action', methods=['POST'])
def handle_action():
    data = request.get_json() or {}
    action_type = data.get('action')
    game = get_game()

    success = False
    message = "Ação inválida."

    if action_type == 'place':
        pos = data.get('pos')
        if pos is not None:
            success, message = game.place_piece(int(pos))
    elif action_type == 'move':
        from_pos = data.get('from_pos')
        to_pos = data.get('to_pos')
        if from_pos is not None and to_pos is not None:
            success, message = game.move_piece(int(from_pos), int(to_pos))
    elif action_type == 'remove':
        pos = data.get('pos')
        if pos is not None:
            success, message = game.remove_piece(int(pos))
    else:
        message = "Tipo de ação desconhecido."

    save_game(game)

    return jsonify({
        'success': success,
        'message': message,
        'game_state': game.to_dict()
    })

@app.route('/api/reset', methods=['POST'])
def reset_game():
    game = NineMensMorris()
    save_game(game)
    return jsonify({
        'success': True,
        'message': "Jogo reiniciado com sucesso.",
        'game_state': game.to_dict()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
