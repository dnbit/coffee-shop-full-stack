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
    result = {
        "success": True,
    }

    try:
        drinks = Drink.query.all()

        formatted_drinks = [drink.short() for drink in drinks]
        result['drinks'] = formatted_drinks
    except Exception as e:
        print(e)
        abort(500)

    return jsonify(result)


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

    try:
        body = json.loads(request.data)

        title = body['title']
        recipe = body['recipe']

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

    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)

    try:
        body = json.loads(request.data)

        title = body.get('title')
        recipe = body.get('recipe')

        if title:
            drink.title = title

        if recipe:
            drink.recipe = json.dumps(recipe)

        drink.update()

        drinks.append(drink.long())

    except Exception as e:
        print(e)
        abort(500)

    result['drinks'] = drinks

    return jsonify(result)


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink(payload, id):
    result = {
        "success": True,
        'delete': id
    }

    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)

    try:
        drink.delete()
    except Exception as e:
        abort(500)

    return jsonify(result)


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
