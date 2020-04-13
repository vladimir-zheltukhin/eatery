from flask_login import UserMixin

from logic import db, manager, ma

recipe_product = db.Table('recipe_product',
                          db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
                          db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
                          )

provider_product = db.Table('provider_product',
                          db.Column('provider_id', db.Integer, db.ForeignKey('provider.id'), primary_key=True),
                          db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
                          )

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=False, unique=True)
    text = db.Column(db.String(1024), nullable=False, unique=True)
    products = db.relationship('Product', secondary=recipe_product, lazy='subquery',
                                       backref='products')


class User (db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)


class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False, unique=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)


class Storage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, unique=True)
    count = db.Column(db.Integer, nullable=False)


class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    phone = db.Column(db.String(50), nullable=False, unique=True)
    products = db.relationship('Product', secondary=provider_product, lazy='subquery',
                               backref='products_provider')


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True

user_schema = UserSchema(many = True)
