from flask import Flask,render_template,redirect,request
import random

app = Flask(__name__)

GAMES_LIST = []

def createGame(answer):
    global GAMES_LIST
    answer = answer.upper()
    gameID = random.randint(1111,9999)
    while gameID in [game["gameID"] for game in GAMES_LIST]:
        gameID = random.randint(1111, 9999)
    game = {
        "gameID":gameID,
        "playersJoined":0,
        "answer":answer,
        "guessedLetters":[],
        "currentPlayerTurn":0
    }
    GAMES_LIST.append(game)
    return gameID

def renderCurrentLetters(answer, guessedLetters):
    return "".join([letter if letter in guessedLetters or letter == " " else "?" for letter in answer])

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/joingame/<int:gameID>')
def joingame(gameID):
    global GAMES_LIST
    playersJoined = 0
    playerNumber = 0
    
    game = next((game for game in GAMES_LIST if game["gameID"] == gameID), None)
    if game:
        playersJoined = game["playersJoined"]
    else:
        return render_template("error.html",error="Game not found")
    
    if playersJoined == 0:
        playerNumber = 0
    elif playersJoined == 1:
        playerNumber = 1
    elif playersJoined == 2:
        playerNumber = 2
    else:
        return render_template("error.html",error="Game is full")
    game["playersJoined"] += 1
    return redirect("/game/"+str(gameID)+"?playerNumber="+str(playerNumber))

@app.route('/newgame/<string:answer>')
def creategame(answer):
    return redirect("/game/"+str(createGame(answer)))

@app.route('/game/<int:gameID>')
def game(gameID):
    global GAMES_LIST
    currentLetters = ""
    game = next((game for game in GAMES_LIST if game["gameID"] == gameID), None)
    if game:
        currentLetters = renderCurrentLetters(game["answer"], game["guessedLetters"])
        playersJoined = game["playersJoined"]
        currentPlayerTurn = game["currentPlayerTurn"]
        if request.args.get('playerNumber'):
            if int(request.args.get('playerNumber')) == 0:
                playerNumber = 1
            if int(request.args.get('playerNumber')) == 1:
                playerNumber = 2
        else:
            if playersJoined == 0:
                playerNumber = 0
            elif playersJoined == 1:
                playerNumber = 1
            elif playersJoined == 2:
                playerNumber = 2
            else:
                return render_template("error.html",error="Game is full")
        return render_template('game.html', gameID=gameID, currentLetters=currentLetters, guessedLetters=[], playerNumber=playerNumber, currentPlayerTurn=currentPlayerTurn)
    else:
        return render_template("error.html",error="Game not found")

@app.route('/submitguess/<int:gameID>/<int:playerNumber>/<string:guess>')
def submitguess(gameID, playerNumber, guess):
    global GAMES_LIST
    
    game = next((game for game in GAMES_LIST if game["gameID"] == gameID), None)
    if game:
        guess = guess.upper()
        game["guessedLetters"].append(guess)
        if game["currentPlayerTurn"] == 0:
            game["currentPlayerTurn"] = 1
        else:
            game["currentPlayerTurn"] = 0
        
    return "200 OK"

@app.route('/getcurrentplayersturn/<int:gameID>')
def getcurrentplayersturn(gameID):
    global GAMES_LIST
    
    game = next((game for game in GAMES_LIST if game["gameID"] == gameID), None)
    if game:
        return str(game["currentPlayerTurn"])
    else:
        return "404 Not Found",404

if __name__ == '__main__':
    gameID = createGame("The quick brown fox jumps over the lazy dog")
    game = next((game for game in GAMES_LIST if game["gameID"] == gameID), None)
    if game:
        game["gameID"] = 1234
    
    app.run(host="0.0.0.0", port=8000)