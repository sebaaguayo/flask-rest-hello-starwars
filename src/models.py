from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
class Character (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    gender = db.Column(db.String(10), nullable=True)
    eyecolor = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        return '<Character %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "eyecolor": self.eyecolor
            # do not serialize the password, its a security breach
        }

class FavoritesCharacter (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    character_id = db.Column(db.Integer, db.ForeignKey("character.id"))
    connect_user = db.relationship("User")
    connect_char = db.relationship("Character")

    def __repr__(self):
        return '<FavCharacter %r>' % self.character_id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id
            # do not serialize the password, its a security breach
        }

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    weather = db.Column(db.String(10))
    diameter = db.Column(db.Integer)

    def __repr__(self):
        return '<Planet %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "weather": self.weather,
            "diameter": self.diameter,
            # do not serialize the password, its a security breach
        }

class FavoritesPlanets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey ('user.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey ('planet.id'))
    connect_user = db.relationship("User")
    connect_planet = db.relationship("Planet")

    def __repr__(self):
        return '<FavPlanet %r>' % self.planet_id

    def serialize(self):
        return {
            "id": self.id,
            "userID": self.user_id,
            "planetID": self.planet_id
            # do not serialize the password, its a security breach
        }
