from flask import Flask,render_template,redirect,request
import random,os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

app = Flask(__name__)

GAMES_LIST = []
DEFAULT_LETTERS = [".",",","!","?","-","_","(",")","[","]","{","}","<",">","/","\\","|","=","+","*","&","^","%","$","#","@","~","'","1","2","3","4","5","6","7","8","9","0"]

def createGame(answer):
    global GAMES_LIST,DEFAULT_LETTERS
    answer = answer.upper()
    gameID = random.randint(1111,9999)
    while gameID in [game["gameID"] for game in GAMES_LIST]:
        gameID = random.randint(1111, 9999)
    game = {
        "gameID":gameID,
        "playersJoined":0,
        "answer":answer,
        "guessedLetters":DEFAULT_LETTERS,
        "currentPlayerTurn":0,
        "p1Points":0,
        "p2Points":0
    }
    GAMES_LIST.append(game)
    return gameID

def renderCurrentLetters(answer, guessedLetters):
    return "".join([letter if letter in guessedLetters or letter == " " else "?" for letter in answer])

@app.route('/')
def index():
    global GAMES_LIST
    return render_template('index.html',numOfGames=len(GAMES_LIST))

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

@app.route('/newaigame')
def newaigame():
    global GAMES_LIST
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens=32,
        messages=[
            {"role": "user", "content": "Give me a sentence that is at least 5 words"}
        ]
    )
    return redirect("/joingame/"+str(createGame(completion.choices[0].message.content)))

@app.route('/game/<int:gameID>')
def game(gameID):
    global GAMES_LIST
    currentLetters = ""
    game = next((game for game in GAMES_LIST if game["gameID"] == gameID), None)
    if game:
        currentLetters = renderCurrentLetters(game["answer"], game["guessedLetters"])
        playersJoined = game["playersJoined"]
        currentPlayerTurn = game["currentPlayerTurn"]
        p1Points = game["p1Points"]
        p2Points = game["p2Points"]
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
        return render_template('game.html', gameID=gameID, currentLetters=currentLetters, guessedLetters=[], playerNumber=playerNumber, currentPlayerTurn=currentPlayerTurn, player1Points=p1Points, player2Points=p2Points)
    else:
        return render_template("error.html",error="Game not found")

@app.route('/submitguess/<int:gameID>/<int:playerNumber>/<string:guess>')
def submitguess(gameID, playerNumber, guess):
    global GAMES_LIST
    
    game = next((game for game in GAMES_LIST if game["gameID"] == gameID), None)
    if game:
        guess = guess.upper()
        game["guessedLetters"].append(guess)
        if all(letter in game["guessedLetters"] or letter == " " for letter in game["answer"]):
            game["currentPlayerTurn"] = 3
        if guess in game["answer"]:
            if playerNumber-1 == 0:
                game["p1Points"] += 1
            elif playerNumber-1 == 1:
                game["p2Points"] += 1
        else:
            if playerNumber-1 == 0:
                game["p1Points"] -= 1
            elif playerNumber-1 == 1:
                game["p2Points"] -= 1
        if game["currentPlayerTurn"] == 0:
            game["currentPlayerTurn"] = 1
        elif game["currentPlayerTurn"] == 1:
            game["currentPlayerTurn"] = 0

        if game["p1Points"] < 0:
            game["p1Points"] = 0
        if game["p2Points"] < 0:
            game["p2Points"] = 0
    return "200 OK"

@app.route('/submitsolve/<int:gameID>/<int:playerNumber>/<string:solve>')
def submitsolve(gameID, playerNumber, solve):
    global GAMES_LIST
    
    game = next((game for game in GAMES_LIST if game["gameID"] == gameID), None)
    if game:
        solve = solve.upper()
        if solve == game["answer"]:
            if playerNumber-1 == 0:
                game["p1Points"] += 3
            elif playerNumber-1 == 1:
                game["p2Points"] += 3
            game["guessedLetters"] = list(game["answer"])
            game["currentPlayerTurn"] = 3
            return "200 OK"
        else:
            if playerNumber-1 == 0:
                game["p1Points"] -= 2
            elif playerNumber-1 == 1:
                game["p2Points"] -= 2
            
            if game["p1Points"] < 0:
                game["p1Points"] = 0
            if game["p2Points"] < 0:
                game["p2Points"] = 0
            return "INCORRECT"
    else:
        return "404 Not Found",404

@app.route('/getcurrentplayersturn/<int:gameID>')
def getcurrentplayersturn(gameID):
    global GAMES_LIST
    
    game = next((game for game in GAMES_LIST if game["gameID"] == gameID), None)
    if game:
        return str(game["currentPlayerTurn"])
    else:
        return "404 Not Found",404
    
@app.route('/deletegame/<int:gameID>')
def deletegame(gameID):
    global GAMES_LIST
    
    game = next((game for game in GAMES_LIST if game["gameID"] == gameID), None)
    if game:
        GAMES_LIST.remove(game)
        return "200 OK"
    else:
        return "404 Not Found",404
    
@app.route('/deleteallgames')
def deleteallgames():
    global GAMES_LIST
    
    GAMES_LIST = []
    return "200 OK"

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    global GAMES_LIST,DEFAULT_LETTERS

    if request.method == "GET":
        return render_template('adminauth.html')
    
    if request.method == "POST":
        if request.form["answer"] == "ADMIN_PASSWORD":
            games_list_without_default_letters = []
            for game in GAMES_LIST:
                game["guessedLetters"] = [letter for letter in game["guessedLetters"] if letter not in DEFAULT_LETTERS]
                games_list_without_default_letters.append(game)
            return render_template('admin.html', games_list=games_list_without_default_letters, numOfGames=len(GAMES_LIST))
        else:
            return render_template('adminauth.html', error="Incorrect password")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)