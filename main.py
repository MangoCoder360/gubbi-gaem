from flask import Flask,render_template,redirect
import random

app = Flask(__name__)

SAMPLE_GAME = {
    "gameID":1234,
    "playersJoined":0,
    "answer":"DEEZ NUTS",
    "guessedLetters":[],
    "currentPlayerTurn":0
}

GAMES_LIST = [SAMPLE_GAME]

def createGame(answer):
    global GAMES_LIST
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
    return "".join([letter if letter in guessedLetters else "?" for letter in answer])

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
    
    if playersJoined == 0:
        playerNumber = 1
    elif playersJoined == 1:
        playerNumber = 2
    else:
        return redirect("/")
    
    return redirect("/game/"+str(gameID)+"?playerNumber="+str(playerNumber))

@app.route('/creategame')
def creategame():
    return redirect("/game/"+str(createGame("DEEZ NUTS")))

@app.route('/game/<int:gameID>')
def game(gameID):
    global GAMES_LIST
    currentLetters = ""
    game = next((game for game in GAMES_LIST if game["gameID"] == gameID), None)
    if game:
        currentLetters = renderCurrentLetters(game["answer"], game["guessedLetters"])
    return render_template('game.html', gameID=gameID, currentLetters=currentLetters, guessedLetters=[], playerNumber=0, currentPlayerTurn=0)

@app.route('/submitguess/<int:gameID>/<int:playerNumber>/<string:guess>')
def submitguess(gameID, playerNumber, guess):
    global GAMES_LIST
    
    game = next((game for game in GAMES_LIST if game["gameID"] == gameID), None)
    if game and game["currentPlayerTurn"] == playerNumber:
        guess = guess.upper()  # Convert guess to uppercase
        game["guessedLetters"].append(guess)
    return redirect("/game/"+str(gameID))

if __name__ == '__main__':
    app.run(host="0.0.0.0")