from time import sleep
from gameplay.game import Game
from resource import static, templates, color, cprint
from traceback import format_exc
from flask import (
    Flask,
    make_response,
    redirect,
    render_template,
    request,
    Response,
    url_for,
)
app = Flask(__name__, static_folder=static(), template_folder=templates())
game = Game()
###########################################################################

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        try:
            # TODO Verify no two players have the same name
            player = game.add_player(request.form['name'])
            response = redirect(url_for('player_view'))
            response.set_cookie('gameID', game.id)
            response.set_cookie('playerID', player.id)
            return response
        except Exception as e:
            cprint(format_exc(), "red")

@app.route('/game/state')
def game_state():
    def eventStream():
        with app.app_context():
            player_id = cookie("playerID")
            while True:
                sleep(.1)
                # if game.state_changed():
                print('Yeilding players')
                data = render_template('player-view.html', hand=game.player(player_id).hand)
                yield f'data: {data}\n\n'
    return Response(eventStream(), mimetype="text/event-stream")

@app.route('/debug')
def debug():
    for _, player in game.players.items(): 
        tile = game.deck.draw()
        player.deal(tile)
    return "OK", 200

@app.route('/game/player_view', methods=['GET'])
def player_view():
    player_id = cookie("playerID")
    return render_template('player-view.html', hand=game.player(player_id).hand)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/game/board')
def board():
    return '<h1>This is where the board will be</h1>'

def cookie(name):
    return request.cookies.get(name)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
