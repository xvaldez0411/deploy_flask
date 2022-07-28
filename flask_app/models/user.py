from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import band
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class User:
    db = "band_together"
    def __init__(self,data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.bands = []
        self.join = []

    @classmethod
    def register_user(cls, data):
        query = "INSERT INTO users(first_name,last_name,email, password) VALUES(%(first_name)s, %(last_name)s, %(email)s, %(password)s);"
        return connectToMySQL(cls.db). query_db(query, data)

    @classmethod
    def get_user_by_email(cls, data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        results = connectToMySQL(cls.db). query_db(query, data)
        if len(results) < 1:
            return False
        row = results[0]
        user = cls(row)
        return user

    @classmethod
    def get_user_by_id(cls, data):
        query = "SELECT * FROM users WHERE id = %(id)s;"
        results = connectToMySQL(cls.db). query_db(query, data)
        if len(results) < 1:
            return False
        row = results[0]
        user = cls(row)
        return user

    @classmethod
    def get_user_with_bands(cls,data):
        query = '''SELECT * FROM users
                LEFT JOIN joined_bands ON joined_bands.user_id = users.id
                LEFT JOIN bands ON bands.id = joined_bands.band_id
                LEFT JOIN users AS creators ON bands.user_id = creators.id WHERE users.id = %(id)s;'''
        results = connectToMySQL(cls.db). query_db(query, data)
        if len(results) < 1:
            return False
        user = cls(results[0])
        for row in results:
            if row['bands.id'] ==  None:
                return user
            creators_data = {
                'id': row['creators.id'],
                'first_name': row['creators.first_name'],
                'last_name': row['creators.last_name'],
                'email': row['creators.email'],
                'password': row['creators.password'],
                'created_at': row['creators.created_at'],
                'updated_at': row['creators.updated_at']
            }
            band_data = {
                'id': row['bands.id'],
                'name': row['name'],
                'genre': row['genre'],
                'city': row['city'],
                'created_at': row['bands.created_at'],
                'updated_at': row['bands.updated_at'],
                'user_id': row['user_id'],
                }
            created_bands = band.Band(band_data)
            created_bands.creator = User(creators_data)
            user.join.append(created_bands)
        return user

    @classmethod
    def get(cls,data):
        query = '''SELECT * FROM users 
                LEFT JOIN bands ON users.id = bands.user_id
                LEFT JOIN joined_bands ON joined_bands.band_id = bands.id
                LEFT JOIN users AS members ON joined_bands.user_id = members.id
                WHERE users.id = %(id)s'''
        results = connectToMySQL(cls.db).query_db(query, data)
        if len(results) < 1:
            return False
        user = cls(results[0])
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
            number_of_bands = len(user.bands)
            if number_of_bands > 0:
                last_band = user.bands[-1]
                if last_band.id == row['bands.id']:
                    last_band.user_ids_who_joined.append(row['members.id'])
                    last_band.members.append(User(members_data))
                    new_band = False
            if new_band and row['bands.id']:
                
                band_data = {
                    'id': row['bands.id'],
                    'name': row['name'],
                    'genre': row['genre'],
                    'city': row['city'],
                    'created_at': row['bands.created_at'],
                    'updated_at': row['bands.updated_at'],
                    'user_id': row['user_id'],
                }
                this_band = band.Band(band_data)
                if row['members.id']:
                    this_band.user_ids_who_joined.append(row['members.id'])
                    this_band.members.append(User(members_data))

                user.bands.append(this_band)
        return user

    @staticmethod
    def validate_register(user):
        is_valid = True
        user_in_db = User.get_user_by_email(user)
        if user_in_db:
            flash('Email is associated with another account')
            is_valid = False
        if len(user['first_name']) < 2:
            flash('First name must be at least 2 characters', "error")
            is_valid = False
        if len(user['last_name']) < 2:
            flash('Last name must be at least 2 characters', "error")
            is_valid = False
        if len(user['password']) < 8:
            flash('Password must be at least 8 characters', "error")
            is_valid = False
        if user['password'] != user['confirm_password']:
            flash('Passwords must match')
            is_valid = False
        if not EMAIL_REGEX.match(user['email']):
            flash('Invalid email address!')
            is_valid = False

        return is_valid

    @staticmethod
    def validate_login(user):
        is_valid = True
        user_in_db = User.get_user_by_email(user)
        if not user_in_db:
            flash('Email is not associated with an account!')
            is_valid = False

        if not EMAIL_REGEX.match(user['email']):
                flash('Invalid email address!')
                is_valid = False

        if len(user['password']) < 8:
                flash('Password must be at least 8 characters', "error")
                is_valid = False
        return is_valid