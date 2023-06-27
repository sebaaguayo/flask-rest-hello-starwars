"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, FavoritesCharacter, FavoritesPlanets
from sqlalchemy.exc import IntegrityError

# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/users', methods=['GET'])
def get_user():
    all_users = User.query.all()

    all_users = list(map(lambda users: users.serialize(), all_users))

    return jsonify(all_users), 200


@app.route('/users/favorites/<int:user_id>', methods=['GET'])
def get_userFavorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    favorites_characters = FavoritesCharacter.query.filter_by(
        user_id=user_id).all()
    favorites_planets = FavoritesPlanets.query.filter_by(user_id=user_id).all()

    serialized_favorites_characters = list(
        map(lambda character: character.serialize(), favorites_characters))
    serialized_favorites_planets = list(
        map(lambda planet: planet.serialize(), favorites_planets))
    serialized_user = user.serialize()

    return jsonify({'favorites_characters': serialized_favorites_characters,
                    'favorites_planets': serialized_favorites_planets,
                    'user': serialized_user}), 200


@app.route('/characters', methods=['GET'])
def get_characters():
    all_characters = Character.query.all()

    serialized_characters = [character.serialize()
                             for character in all_characters]
    return jsonify(serialized_characters), 200


@app.route('/characters/<int:characters_id>', methods=['GET'])
def getcharactersID(characters_id):
    character = Character.query.get(characters_id)
    if not character:
        return jsonify({"message": 'Character not found'}), 404

    return jsonify(character.serialize())


@app.route('/planets', methods=['GET'])
def get_planets():
    all_planets = Planet.query.all()

    serialized_planets = [planet.serialize() for planet in all_planets]
    return jsonify(serialized_planets)


@app.route('/planets/<int:planets_id>', methods=['GET'])
def getplanetsID(planets_id):
    planet = Planet.query.get(planets_id)
    if not planet:
        return jsonify({"message": 'Planet not found'}), 404

    return jsonify(planet.serialize())


@app.route('/favorite/characters/<int:character_id>', methods=['POST'])
def add_character(character_id):
    character = FavoritesCharacter.query.get(character_id)

    if not character:
        # character does not exist, create a new one
        body = request.get_json()
        if 'user_id' not in body or 'character_id' not in body:
            return jsonify({'message': 'Missing required fields'}), 400
        try:
            new_character = FavoritesCharacter(
                user_id=body['user_id'], character_id=body['character_id'])
            db.session.add(new_character)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return jsonify({'message': 'Invalid user_id or character_id'}), 400

        return jsonify(new_character.serialize()), 201

    # character already exists, update it
    body = request.get_json()
    if 'user_id' in body:
        character.user_id = body['user_id']
    if 'character_id' in body:
        character.character_id = body['character_id']
    db.session.commit()
    return jsonify(character.serialize()), 200

    # transform to a dictionary
    # new_character.name = body['name'] the long way


@app.route('/favorite/planets/<int:planet_id>', methods=['POST'])
def add_planet(planet_id):
    planet = FavoritesPlanets.query.get(planet_id)

    if not planet:
        # planet does not exist, create a new one
        body = request.get_json()
        if 'user_id' not in body or 'planet_id' not in body:
            return jsonify({'message': 'Missing required fields'}), 400
        try:
            new_planet = FavoritesPlanets(
                user_id=body['user_id'], planet_id=body['planet_id'])
            db.session.add(new_planet)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return jsonify({'message': "Invalid user_id or planet_id" }), 400

        return jsonify(new_planet.serialize()), 201

    # planet already exists, update it
    body = request.get_json()
    if 'user_id' in body:
        planet.user_id = body['user_id']
    if 'planet_id' in body:
        planet.planet_id = body['planet_id']
    db.session.commit()
    return jsonify(planet.serialize()), 200


@app.route('/favorite/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = FavoritesPlanets.query.get(planet_id)

    if not planet:
        return jsonify({'message': 'Planet not found'}), 404

    db.session.delete(planet)
    db.session.commit()

    return jsonify({'message': 'Planet deleted'}), 200


@app.route('/favorite/characters/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    character = FavoritesCharacter.query.get(character_id)

    if not character:
        return jsonify({'message': 'Favorite character not found'}), 404

    db.session.delete(character)
    db.session.commit()

    return jsonify({'message': 'Favorite character deleted'}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)