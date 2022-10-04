from time import sleep
from gameplay.game import Game
from resource import static, templates, color, cprint, log
from traceback import format_exc
from flask_socketio import SocketIO
from form import LoginForm
from functools import wraps
from flask import (
    copy_current_request_context,
    Flask,
    make_response,
    redirect,
    render_template,
    request,
    Response,
    url_for,
)

app = Flask(__name__, static_folder=static(), template_folder=templates())
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

game = Game(socketio)
###########################################################################

def cookie(name):
    return request.cookies.get(name)

def validate(func):
    @wraps(func)
    def wrapper(*args, **kw):
        gameID = cookie("gameID")
        if gameID != game.id:
            print("Invalid gameID, redirecting to login.")
            return redirect('/login')
        return func(*args, **kw)
    return wrapper

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', form=LoginForm())
    elif request.method == 'POST':
        try:
            name = request.form['name']
            player = game.add_player(name)
            response = redirect(url_for('waiting_for_players'))
            response.set_cookie('gameID', game.id)
            response.set_cookie('playerID', player.id)  
            socketio.emit('player_joined', {'html': f"Players: {len(game.players)}"}, broadcast=True)
            return response
        except Exception as e:
            cprint(format_exc(), "red")

@app.route('/waiting-for-players', methods=['GET', 'POST'])
@validate
def waiting_for_players():
    if request.method == 'GET':
        player = game.player(cookie('playerID'))
        return render_template('waiting-for-players.html', num_players=len(game.players), player=player)

@socketio.on('register')
@validate
def register_socket(data):
    player = game.player(cookie('playerID'))
    if not hasattr(player, 'sessionID'):
        print(f'Registered socketio connection with {player.name}')
    else:
        print(f'Re-registered socketio connection with {player.name}')
    player.sessionID = request.sid
    if game.state != game.WAITING_FOR_PLAYERS:
        return
    for p in game.players:
        if not hasattr(p, 'sessionID'):
            return
    print(f'All players are registered.')
    game.deal()
    game.start_turn()

@socketio.on('discard_tile')
@validate
def discard_tile(id):
    player = game.player(cookie('playerID'))
    if game.player_can_discard(player):
        game.discard(id, player)

@socketio.on('steal_tile')
@validate
def steal_tile(group):
    player = game.player(cookie('playerID'))
    if game.player_can_steal(player):
        game.steal(group, player)
        game.end_steal(player)

@socketio.on('request_start_game')
@validate
def start_game():
    player = game.player(cookie('playerID'))
    print(f"{player.name} requested to start the game.")
    if player.is_party_leader:
        socketio.emit('start_game', {}, broadcast=True)
        return "OK", 200
    return "Not party lead", 401

@socketio.on('accept_win')
@validate
def accept_win():
    player = game.player(cookie('playerID'))
    print(f"{player.name} accepted their win.")
    game.game_won()

@app.route('/game/player_view', methods=['GET'])
@validate
def player_view():
    with app.app_context():
        player_id = cookie("playerID")
        return render_template('player-view.html', game=game, player=game.player(player_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/game/board')
def board():
    return '<h1>This is where the board will be</h1>'

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
