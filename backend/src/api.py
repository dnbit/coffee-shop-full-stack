import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

# ROUTES


@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = []

    result = {
        "success": True,
    }

    try:
        drinks = Drink.query.all()
    except Exception as e:
        print(e)
        abort(500)

    formatted_drinks = [drink.short() for drink in drinks]
    result['drinks'] = formatted_drinks

    return jsonify(result)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth(permission='get:drinks-detail')
def get_drinks_details(payload):
    drinks = []

    result = {
        "success": True,
    }

    try:
        drinks = Drink.query.all()
    except Exception as e:
        print(e)
        abort(500)

    formatted_drinks = [drink.long() for drink in drinks]
    result['drinks'] = formatted_drinks

    return jsonify(result)


@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def create_new_drink(payload):
    drinks = []
    result = {
        "success": True,
    }

    body = json.loads(request.data)

    try:
        title = body['title']
        recipe = []
        recipe.append(body['recipe'])

        new_drink = Drink(title=title, recipe=json.dumps(recipe))
        new_drink.insert()

        drinks.append(new_drink.long())

    except Exception as e:
        print(e)
        abort(500)

    result['drinks'] = drinks

    return jsonify(result)


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def update_drink(payload, id):
    drinks = []
    result = {
        "success": True,
    }

    body = json.loads(request.data)
    print(id)
    try:
        title = body.get('title')
        recipe = body.get('recipe')

        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if title:
            drink.title = title

        if recipe:
            recipe_array = []
            recipe_array.append(recipe)
            drink.recipe = json.dumps(recipe_array)

        drink.update()

        drinks.append(drink.long())

    except Exception as e:
        print(e)
        abort(500)

    result['drinks'] = drinks

    return jsonify(result)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404


@app.errorhandler(500)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
