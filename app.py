from flask import Flask, request, Response
from flask_cors import CORS
import mariadb
import json
import dbcreds
import secrets
import datetime


app = Flask(__name__)
CORS(app)

# ...connection to database...
def connect():
    return mariadb.connect(
        user = dbcreds.user,
        password = dbcreds.password,
        host = dbcreds.host,
        port = dbcreds.port,
        database = dbcreds.database
    )

# # ...........................End Points For users................................................. 
@app.route('/api/users', methods=['GET','POST', 'PATCH', 'DELETE'])

# ....Get Users....
def users():
    if request.method == 'GET':
        conn = None
        cursor = None
        user = None
        users = None
        userId = request.args.get("id")
        try:
            conn = connect()
            cursor = conn.cursor()
            if (userId != None):
                cursor.execute("SELECT * FROM user WHERE id = ?", [userId])
            else:    
                cursor.execute("SELECT * FROM user")
            users = cursor.fetchall()
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (users != None):
                results = []
                for user in users:
                    result = {
                        "userId": user[0],
                        "email": user[1],
                        "username": user[2],
                        "bio": user[3],
                        "birthdate": user[4]
                    }
                    results.append(result)
                return Response(
                    json.dumps(results, default=str),
                    mimetype = "application/json",
                    status=200
                ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                ) 
    # .....Sign Up....            
   
    elif request.method == 'POST':
        conn = None
        cursor = None
        user = None
        results = None
        email = request.json.get("email")
        username = request.json.get("username")
        bio = request.json.get("bio")
        birthdate = request.json.get("birthdate")
        password = request.json.get("password")

        
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user(email, username, bio, birthdate, password) VALUES(?, ?, ?, ?, ?)", [email, username, bio, birthdate, password])
            results = cursor.rowcount 
            if results == 1:
                loginToken = secrets.token_hex(16)
                userId = cursor.lastrowid
                cursor.execute("INSERT INTO user_session(userId, loginToken) VALUES (?, ?)", [userId, loginToken])
                conn.commit()
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results == 1):
                    user_data = {
                        "userId": userId,
                        "email": email,
                        "username": username,
                        "bio": bio,
                        "birthdate": birthdate,
                        "loginToken": loginToken
                    }
                    return Response(
                       json.dumps(user_data, default=str),
                       mimetype = "application/json",
                       status=200
                    ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                ) 

    # .......Edit User Details....            
    elif request.method == 'PATCH':
        conn = None
        cursor = None
        results = None
        email = request.json.get("email")
        username = request.json.get("username")
        bio = request.json.get("bio")
        birthdate = request.json.get("birthdate")
        password = request.json.get("password")
        loginToken = request.json.get("loginToken")

        
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken = ?", [loginToken])
            target = cursor.fetchone() 
            print(target)
            if target:
                if (email != "" and email != None):
                    cursor.execute("UPDATE user SET email = ? WHERE id = ?", [email, target[0]])
                if (username != "" and username != None):
                    cursor.execute("UPDATE user SET username = ? WHERE id = ?", [username, target[0]])
                if (bio != "" and bio != None):
                    cursor.execute("UPDATE user SET bio = ? WHERE id = ?", [bio, target[0]])
                if (birthdate != "" and birthdate != None):
                    cursor.execute("UPDATE user SET birthdate = ? WHERE id = ?", [birthdate, target[0]])
                if (password != "" and password != None):
                    cursor.execute("UPDATE user SET password = ? WHERE id = ?", [password, target[0]])
                conn.commit()
                results = cursor.rowcount
                cursor.execute("SELECT * FROM user WHERE id = ?", [target[0]]) 
                user = cursor.fetchall()  
                print(user)                 
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results != None):
                    user_data = {
                        "userId": target[0],
                        "email": user[0][1],
                        "username": user[0][2],
                        "bio": user[0][3],
                        "birthdate": user[0][4],
                    }
                    return Response(
                       json.dumps(user_data, default=str),
                       mimetype = "application/json",
                       status=200
                    ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                )
    # ........Delete User Profile....
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        results = None
        password = request.json.get("password")
        loginToken = request.json.get("loginToken")

        try:
            conn = connect()
            cursor = conn.cursor()   
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken])
            user = cursor.fetchall()
            print(user, password)
            userId = user[0][0]
            if user[0][1] == loginToken:
                cursor.execute("DELETE FROM user WHERE id = ? AND password = ?", [userId, password])
                conn.commit()
                results = cursor.rowcount
                print(results)
            else: 
                return Response(
                    "invalid password",
                    mimetype="text/html",
                    status=500
                )    
            
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results == 1):
                return Response(
                    "Deleted!...",
                    mimetype = "text/html",
                    status=204
                ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                )              





# # ...........................End Points For Login.................................................
@app.route('/api/login', methods=['POST', 'DELETE'])

# ......Sign In......
def login():
    if request.method == 'POST':
        conn = None
        cursor = None
        userId = None
        results = None
        email = request.json.get("email")
        password = request.json.get("password")

        
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, username, bio, birthdate, password FROM user WHERE email = ? AND password = ?", [email, password])
            userId = cursor.fetchall()
            loginToken = secrets.token_hex(16)
            print(userId) 
            print(loginToken)
            if (userId != None):
                cursor.execute("INSERT INTO user_session(userId, loginToken) VALUES (?, ?)", [userId[0][0], loginToken])
                conn.commit()
                results = cursor.rowcount
            else:
                print("wrong data")    
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results == 1):
                    user_data = {
                        "userId": userId[0][0],
                        "email": userId[0][1],
                        "username": userId[0][2],
                        "bio": userId[0][3],
                        "birthdate": userId[0][4],
                        "loginToken": loginToken
                    }
                    return Response(
                       json.dumps(user_data, default=str),
                       mimetype = "application/json",
                       status=200
                    ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                )
    # ......Sign Out.....
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        results = None
        loginToken = request.json.get("loginToken")

        try:
            conn = connect()
            cursor = conn.cursor()   
            cursor.execute("DELETE FROM user_session WHERE loginToken = ?", [loginToken])  
            conn.commit()
            results = cursor.rowcount  
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results == 1):
                return Response(
                    "logout.....!",
                    mimetype = "text/html",
                    status=204
                ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                ) 

# # # ...........................End Points For game.................................................
# @app.route('/api/game', methods=['GET'])

# def game():


# # # ...........................End Points For game-like.................................................
@app.route('/api/game-like', methods=['GET', 'POST', 'DELETE'])

# .....Get Likes For Game.....
def game_like():
    if request.method == "GET":
        conn = None
        cursor = None
        game_likes =None
        gameId = request.args.get("gameId")
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT game_like.gameId, game_like.userId, user.username FROM game_like JOIN user ON game_like.userId = user.id WHERE game_like.gameId = ? ", [gameId])
            game_likes = cursor.fetchall()
            print(game_likes)
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (cursor != None):
                conn.rollback()
                conn.close()
            if (game_likes != None):
                results = []
                for game_like in game_likes:
                    likes_data = {
                        "gameId": game_like[0],
                        "userId": game_like[1],
                        "username": game_like[2]
                    }
                    results.append(likes_data)
                return Response(
                    json.dumps(results, default=str),
                    mimetype = "application/json",
                    status=200
                )
            else:
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                )
# ......Like this Game....
    elif request.method == "POST":
        conn = None
        cursor = None
        results = None
        gameId = request.json.get("gameId")
        loginToken = request.json.get("loginToken")

        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken])
            new_like = cursor.fetchall()
            print(new_like)
            if (new_like[0][1] == loginToken):
                cursor.execute("INSERT INTO game_like(gameId, userId) VALUES (?, ?)", [gameId, new_like[0][0]])
                conn.commit()
                results = cursor.rowcount
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                 cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results != None):
                return Response(
                    "you liked this game!..",
                    mimetype="application/json",
                    status=200
                )
            else:
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                )
# .......Unlike This Game....
    elif request.method == "DELETE":
        conn = None
        cursor = None
        results = None
        loginToken = request.json.get("loginToken")
        gameId = request.json.get("gameId")

        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken])
            target = cursor.fetchall()
            print(target)
            if target[0][1] == loginToken:
                cursor.execute("DELETE FROM game_like WHERE gameId = ? AND userID = ?", [gameId, target[0][0]])
                conn.commit()
                results = cursor.rowcount
                print(results)
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (cursor != None):
                conn.rollback()
                conn.close()
            if (results != None):
                return Response(
                    "you unlike this game!..",
                    mimetype="text/html",
                    status=204
                )
            else:
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                )




# # # ...........................End Points For game-review.................................................
@app.route('/api/game-review', methods=['GET', 'POST','PATCH', 'DELETE'])

# .....get reviews...
def game_review():
    if request.method == "GET":
        conn = None
        cursor = None
        reviews = None
        gameId = request.args.get("gameId")
        try:
            conn = connect()
            cursor = conn.cursor()
            if (gameId != "" and gameId != None):
                cursor.execute("SELECT game_review.*, user.username FROM game_review JOIN user ON game_review.userId = user.id WHERE game_review.gameId = ?", [gameId])
                reviews = cursor.fetchall()
            elif (gameId == "" and gameId == None):
                cursor.execute("SELECT * FROM game_review")
                reviews = cursor.fetchall()
                print(reviews)
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (reviews != None):
                results = []
                for review in reviews:
                    result = {
                        "reviewId": review[0],
                        "gameId": review[1],
                        "userId": review[2],
                        "content": review[3],
                        "createdAt": review[4],
                        "username": review[5],
                    }
                    results.append(result)
                return Response(
                    json.dumps(results, default=str),
                    mimetype="application/json",
                    status=200
                )
            else:
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                )

# .......post new review for this game.....
    elif request.method == "POST":
        conn = None
        cursor = None
        results = None
        target = None
        new_reviewId = None
        new_review = None
        loginToken = request.json.get("loginToken")
        gameId = request.json.get("gameId")
        content = request.json.get("content")
        createdAt = request.json.get("createdAt")

        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken])
            target = cursor.fetchall()
            print(target)
            results = cursor.rowcount
            if (target[0][1] == loginToken):
                cursor.execute("INSERT INTO game_review(content, createdAt, gameId, userId) VALUES(?, ?, ?, ?)", [content, createdAt, gameId, target[0][0]])
                new_reviewId = cursor.lastrowid
                conn.commit()
                results = cursor.rowcount
                cursor.execute("SELECT game_review.*, user.username FROM game_review JOIN user ON game_review.userId = user.id WHERE game_review.id = ?", [new_reviewId])
                new_review = cursor.fetchall()
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results == 1):
                review_data = {
                    "reviewId": new_reviewId,
                    "gameId": gameId,
                    "userId": target[0][0],
                    # "username": new_review[0][5],
                    "content": content,
                    "createdAt": createdAt
                }
                return Response(
                    json.dumps(review_data, default=str),
                    mimetype="application/json",
                    status=200
                )
            else:
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                )

# ........edit review....
    elif request.method == "PATCH":
        conn = None
        cursor = None
        results = None
        reviewId = request.json.get("reviewId")
        content = request.json.get("content")
        createdAt = request.json.get("createdAt")
        loginToken = request.json.get("loginToken")

        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken])
            target = cursor.fetchall()
            cursor.execute("SELECT userId FROM game_review WHERE id = ?", [reviewId])
            review_target = cursor.fetchall()
            print(target)
            print(review_target)
            if target[0][1] == loginToken and target[0][0] == review_target[0][0]:
                cursor.execute("UPDATE game_review SET content = ? WHERE id = ?", [content, reviewId])
                conn.commit()
                results = cursor.rowcount
                print(results)
            if (results != None):
                cursor.execute("SELECT game_review.*, user.username FROM user JOIN game_review ON user.id = game_review.userId WHERE game_review.id = ?", [reviewId])
                new_review = cursor.fetchall()
                print(new_review)
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results == 1):
                newreview_data = {
                    "reviewId": reviewId,
                    "gameId": new_review[0][1],
                    "userId": new_review[0][2],
                    "username": new_review[0][5],
                    "content": content,
                    "createdAt": createdAt
                }
                return Response(
                    json.dumps(newreview_data, default=str),
                    mimetype="application/json",
                    status=200
                )
            else:
                return Response(
                    "something wrong...",
                    mimetype="text/html",
                    status=500
                )
# .......Delete the review......
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        results = None
        loginToken = request.json.get("loginToken")
        reviewId = request.json.get("reviewId")

        try:
            conn = connect()
            cursor = conn.cursor()   
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken])
            target = cursor.fetchall()
            print(target)
            cursor.execute("SELECT userId FROM game_review WHERE id = ?", [reviewId])
            review_target = cursor.fetchall()
            if target[0][1] == loginToken and target[0][0] == review_target[0][0]:
                cursor.execute("DELETE FROM game_review WHERE id = ?", [reviewId])
                conn.commit()
                results = cursor.rowcount
                print(results)  
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results != None):
                return Response(
                    "Deleted!...",
                    mimetype = "text/html",
                    status=204
                ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                )        
