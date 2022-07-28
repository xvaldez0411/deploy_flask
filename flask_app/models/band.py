from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import user
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class Band:
    db = "band_together"
    def __init__(self,data):
        self.id = data['id']
        self.name = data['name']
        self.genre = data['genre']
        self.city = data['city']
        self.user_id = data['user_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.creator = None
        self.user_ids_who_joined = []
        self.members = []

    @classmethod
    def get_all(cls):
        query = '''SELECT * FROM bands JOIN users AS creators ON bands.user_id = creators.id
                LEFT JOIN joined_bands ON joined_bands.band_id = bands.id
                LEFT JOIN users AS members ON joined_bands.user_id = members.id'''
        results = connectToMySQL(cls.db). query_db(query)
        created_bands = []
        for row in results:
            new_band = True
            members_data = {
                'id': row['members.id'],
                'first_name': row['members.first_name'],
                'last_name': row['members.last_name'],
                'email': row['members.email'],
                'password': row['members.password'],
                'created_at': row['members.created_at'],
                'updated_at': row['members.updated_at']
            }
            number_of_bands = len(created_bands)
            if number_of_bands > 0:
                last_band = created_bands[number_of_bands-1]
                if last_band.id == row['id']:
                    last_band.user_ids_who_joined.append(row['members.id'])
                    last_band.members.append(user.User(members_data))
                    new_band = False

            if new_band:
                
                band = cls(row)
                user_data = {
                    'id': row['creators.id'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'email': row['email'],
                    'password': row['password'],
                    'created_at': row['creators.created_at'],
                    'updated_at': row['creators.updated_at']
                }
                creator = user.User(user_data)
                band.creator = creator


                if row['members.id']:
                    band.user_ids_who_joined.append(row['members.id'])
                    band.members.append(user.User(members_data))

                created_bands.append(band)

        return created_bands

    @classmethod
    def get_one(cls,data):
        query = '''SELECT * FROM bands JOIN users AS creators ON bands.user_id = creators.id
                LEFT JOIN joined_bands ON joined_bands.band_id = bands.id
                LEFT JOIN users AS members ON joined_bands.user_id = members.id
                WHERE bands.id = %(id)s;'''
        results = connectToMySQL(cls.db). query_db(query, data)
        if len(results) < 1:
            return False
        new_band = True
        for row in results:
            if new_band:
                band = cls(row)
                user_data = {
                    'id': row['creators.id'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'email': row['email'],
                    'password': row['password'],
                    'created_at': row['creators.created_at'],
                    'updated_at': row['creators.updated_at']
                }
                creator = user.User(user_data)
                band.creator = creator
                new_band = False
                
            if row['members.id']:
                members_data = {
                    'id': row['members.id'],
                    'first_name': row['members.first_name'],
                    'last_name': row['members.last_name'],
                    'email': row['members.email'],
                    'password': row['members.password'],
                    'created_at': row['members.created_at'],
                    'updated_at': row['members.updated_at']
            }
                members_data = user.User(members_data)
                band.members.append(members_data)
                band.user_ids_who_joined.append(row['members.id'])

        return band

    @classmethod
    def create(cls,data):
        query = "INSERT INTO bands(name, genre, city, user_id) VALUES(%(name)s, %(genre)s, %(city)s, %(user_id)s);"
        return connectToMySQL(cls.db). query_db(query, data)

    @classmethod
    def update(cls,data):
        query = "UPDATE bands SET name = %(name)s, genre = %(genre)s, city = %(city)s WHERE id = %(id)s;"
        return connectToMySQL(cls.db). query_db(query, data)

    @classmethod
    def delete(cls,data):
        query = "DELETE FROM bands WHERE id = %(id)s"
        return connectToMySQL(cls.db). query_db(query, data)

    @classmethod
    def join(cls,data):
        query = "INSERT INTO joined_bands(user_id, band_id) VALUES (%(user_id)s, %(id)s);"
        return connectToMySQL(cls.db). query_db(query, data)

    @classmethod
    def quit(cls,data):
        query = "DELETE FROM joined_bands WHERE user_id = %(user_id)s AND band_id = %(id)s;"
        return connectToMySQL(cls.db). query_db(query, data)

    @staticmethod
    def validate_create(band):
        is_valid = True
        if len(band['name']) < 2:
            flash('Band name must be at least 2 characters', "error")
            is_valid = False
        if len(band['genre']) < 2:
            flash('Music Genre must be at least 2 characters', "error")
            is_valid = False
        if len(band['city']) <= 0:
            flash('You must enter in a city', "error")
            is_valid = False
        return is_valid

    @staticmethod
    def validate_update(band):
        is_valid = True
        if len(band['name']) < 2:
            flash('Band name must be at least 2 characters', "error")
            is_valid = False
        if len(band['genre']) < 2:
            flash('Music Genre must be at least 2 characters', "error")
            is_valid = False
        if len(band['city']) <= 0:
            flash('You must enter in a city', "error")
            is_valid = False
        return is_valid