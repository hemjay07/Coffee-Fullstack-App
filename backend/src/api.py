import os
from urllib import response
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError,get_token_auth_header, requires_auth,verify_decode_jwt

app = Flask(__name__)
setup_db(app)
CORS(app)


    
'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()
# ----------------------------------------------------------------------------------------------------------------------------------
# ROUTES
# ----------------------------------------------------------------------------------------------------------------------------------

'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks")
def get_drinks():
    drinks_queried = Drink.query.all()
    drinks = [drink.short() for drink in drinks_queried]
    return jsonify({
    'success': True,
    'drinks': drinks,
    })

# ----------------------------------------------------------------------------------------------------------------------------------
'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def drinks_detail(payload):
    try:

        drinks = Drink.query.all()
        drink=[drink.long() for drink in drinks]
        return jsonify({"success":True,"drinks":drink})

    except:
        abort(422)

# ----------------------------------------------------------------------------------------------------------------------------------
'''
@TODO implement endpoint 
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
# '''
@app.route("/drinks",methods=["POST"])
@requires_auth("post:drinks")
def post_drinks(payload):
    try:
        print('✅')
        body = request.get_json()
        new_title = body["title"]
        #since our input("recipe") is an array and therefore not a json but the data type stored in the database is a json, we have to convert the "recipe" to a json
        new_recipe = json.dumps(body["recipe"])
        print(new_title,new_recipe)
        drink = Drink(title=new_title,recipe=new_recipe)
        drink.insert()
        drinks_queried= Drink.query.filter(Drink.title==new_title).first()
        drinks = [drinks_queried.long()]
        return jsonify({
            "success":True,
            "drinks":drinks

        })
    except:
        abort(422)
    

# ----------------------------------------------------------------------------------------------------------------------------------
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks/<int:id>",methods=["PATCH"])
@requires_auth("patch:drinks")
def patch_drinks(payload,id):

    drink= Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort (404)
    
    try:
        data = request.get_json()
        if data.get("title"):
            drink.title = data.get("title")
        if data.get("recipe"):
            drink.recipe= json.dumps(data.get("recipe"))
        drink.update()
    except:
        abort(422)
    
    updated_drink = Drink.query.filter(Drink.title==drink.title).first()
    formated_drink= [updated_drink.long()]
    
    return jsonify({"success":True,"drinks":formated_drink})


# ----------------------------------------------------------------------------------------------------------------------------------
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:id>",methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drinks(payload,id):
    try:
        drink = Drink.query.filter(Drink.id==id).one_or_none()
        if drink == None:
            abort(405)

        drink.delete()
        
        return jsonify({
            "success":True,
            "delete":id
        })
    except:
        abort(422)


# ----------------------------------------------------------------------------------------------------------------------------------
# Error Handling
'''
# ----------------------------------------------------------------------------------------------------------------------------------
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success":False,
        "error":401,
        "message":"you are not authorized for this action"
    }),401


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success":False,
        "error":404,
        "message":"Not found"
    }),404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def autherror(error):
    return jsonify({"success":False,"message":error.error["description"],"error":error.status_code}),error.status_code
