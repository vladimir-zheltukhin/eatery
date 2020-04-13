#!/usr/local/bin/python
# coding: utf-8
from flask import render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired
from flask_login import login_user, login_required, logout_user, current_user

from logic import app, db
from logic.models import User, Recipe, Menu, Product, Provider, Storage, recipe_product, provider_product


class LoginForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class AddRecipeForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    text = TextAreaField('text', validators=[DataRequired()])


class AddProviderForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    phone = TextAreaField('phone', validators=[DataRequired()])


class ChangeStorageForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    count = StringField('count', validators=[DataRequired()])


class AddProductForm(FlaskForm):
    name = StringField('new product', validators=[DataRequired()])


@app.route('/', methods=['GET', 'POST'])
def main_page():
    dishes = db.session.query(Recipe).join(Menu).filter(Menu.dish_id == Recipe.id)
    if current_user.is_authenticated:
        return render_template('index.html', dishes=dishes)
    else:
        return render_template('index_for_guest.html', dishes=dishes)


@app.route('/new_menu', methods=['GET', 'POST'])
@login_required
def new_menu_page():
    if request.method == 'POST':
        indexes = request.form.getlist('indexes')

        dishes = Menu.query.all()
        for dish in dishes:
            db.session.delete(dish)

        db.session.commit()

        for ind in indexes:
            new_dish = Menu(dish_id=ind)
            db.session.add(new_dish)
            db.session.commit()

        return redirect(url_for('main_page'))
    else:
        recipes = Recipe.query.order_by(Recipe.id)
        return render_template('new_menu.html', recipes=recipes)


@app.route('/recipes', methods=['GET', 'POST'])
@login_required
def recipes_page():
    recipes = Recipe.query.order_by(Recipe.id)
    products = Product.query.order_by(Product.id)
    return render_template('recipes.html', recipes = recipes, products=products )


@app.route('/new_recipe', methods=['GET', 'POST'])
@login_required
def new_recipe_page():
    form = AddRecipeForm()
    title = form.title.data
    text = form.text.data
    products = Product.query.all()

    if form.validate_on_submit():
        if not (title or text):
            flash('Пожалуйста, заполните все поля!')
        else:
            recipe = Recipe.query.filter_by(title=title).first()

            if recipe is None:
                new_recipe = Recipe(title=title, text=text)
                db.session.add(new_recipe)
                db.session.commit()

                if request.method == 'POST':
                    indexes = request.form.getlist('indexes')

                recipe = Recipe.query.filter_by(title=title).first()
                for index in indexes:
                    statement = recipe_product.insert().values(recipe_id=recipe.id, product_id=index)
                    db.session.execute(statement)
                    db.session.commit()
            else:
                flash('Такой продукт уже существует')

        return redirect(url_for('recipes_page'))
    return render_template('new_recipe_page.html',form=form, products=products)


@app.route('/products', methods=['GET', 'POST'])
@login_required
def products_page():
    products = Product.query.order_by(Product.id)
    return render_template('products.html', products = products)


@app.route('/new_product', methods=['GET', 'POST'])
@login_required
def new_product_page():
    form = AddProductForm()
    name = form.name.data
    if form.validate_on_submit():
        if not name:
            flash('Пожалуйста, заполните все поля!')
        else:
            product = Product.query.filter_by(name=name).first()
            if product is not None:
                flash('Такой продукт уже существует')
            else:
                new_product = Product(name=name)
                db.session.add(new_product)
                db.session.commit()

        return redirect(url_for('products_page'))
    return render_template('new_product_page.html',form=form)



@app.route('/providers', methods=['GET', 'POST'])
@login_required
def providers_page():
    providers = Provider.query.order_by(Provider.id)
    products = Product.query.order_by(Product.id)
    return render_template('providers.html', providers = providers, products=products)


@app.route('/new_provider', methods=['GET', 'POST'])
@login_required
def new_provider_page():
    form = AddProviderForm()
    name = form.name.data
    phone = form.phone.data
    products = Product.query.all()

    if form.validate_on_submit():
        if not (name or phone):
            flash('Пожалуйста, заполните все поля!')
        else:
            provider = Provider.query.filter_by(name=name).first()

            if provider is None:
                new_provider = Provider(name=name, phone=phone)
                db.session.add(new_provider)
                db.session.commit()

                if request.method == 'POST':
                    indexes = request.form.getlist('indexes')


                for index in indexes:
                    statement = provider_product.insert().values(provider_id=new_provider.id, product_id=index)
                    db.session.execute(statement)
                    db.session.commit()

            else:
                flash('Такой поставщик уже существует')

        return redirect(url_for('providers_page'))
    return render_template('new_provider_page.html',form=form, products=products)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    login = form.login.data
    password = form.password.data
    if form.validate_on_submit():
        if login and password:
            user = User.query.filter_by(login=login).first()
            if user and user.password == password:
                login_user(user)
                return redirect(url_for('main_page'))
            else:
                flash('Логин или пароль введены неверно')
        else:
            flash('Пожалуйста, заполните поля логина и пароля!')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_page'))


@app.route('/storage', methods=['GET', 'POST'])
@login_required
def storage_page():
    products = db.session.query(Product).join(Storage, Product.id == Storage.product_id).add_columns(Product.name, Storage.count)

    return render_template('storage.html', products=products)


@app.route('/change_products_in_storage', methods=['GET', 'POST'])
@login_required
def change_products_storage():
    form = ChangeStorageForm()
    name = form.name.data
    count = form.count.data

    if form.validate_on_submit():
        if not (name):
            flash('Пожалуйста, заполните все поля!')
        else:
            if(int(count) > 0):
                product = Product.query.filter_by(name=name).first()
                if product is not None:
                    storage_product = Storage.query.filter_by(product_id=product.id).first()
                    if storage_product is not None:
                        storage_product.count=count
                        db.session.commit()
                    else:
                        new_prod = Storage(product_id=product.id, count=count)
                        db.session.add(new_prod)
                        db.session.commit()
                else:
                    flash('Такого продукта нет в базе')
            else:
                product = Product.query.filter_by(name=name).first()
                if product is not None:
                    storage_product = Storage.query.filter_by(product_id=product.id).first()
                    if storage_product is not None:
                        db.session.delete(storage_product)
                        db.session.commit()
                    else:
                        flash('Такого продукта нет на складе')
                else:
                    flash('Такого продукта нет в базе')

        return redirect(url_for('storage_page'))
    return render_template('edit_storage.html',form=form)


if __name__=="__main__":
    app.run(debug=True)