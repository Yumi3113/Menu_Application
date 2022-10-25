from pickle import TRUE
from flask import Flask, render_template, request, flash, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from os import path
import sqlite3

app = Flask(__name__)
DATABASE = "database.db"
app.config['SECRET_KEY'] = 'key'

def query_db(query, args=(), one=False, commit=False):
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    cursor.close()
    if commit:
        db.commit()
    db.close()
    #returns all the results unless one==True then it return just one result
    #it also checks that something came back and sends None if it is blank
    return (rv[0] if rv else None) if one else rv

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # attempt to find user by the email
        user = query_db(
            "SELECT id, email, password FROM user WHERE email = ?",
            (email, ),
            one=True
        )

        if user is not None:
            # the user was found
            # check the password hash in the database matches what the user entered
            if check_password_hash(user[2], password):
                flash('Logged in successfully!', category='success')
                # store the id of the logged in user
                session["user_id"] = user[0]
                session["cart"] = []
                # user now logged in redirect menu
                return redirect(url_for('menu'))
            else:
                # password was inocrrect
                flash('Incorrect password, try again.', category='error')
        else:
            # user was not found
            flash('Email does not exist.', category='error')

    return render_template("login.html")

#logout
@app.route('/logout')
def logout():
    session["user_id"] = None
    return redirect(url_for('login'))

#Sign Up
@app.route('/sign_up', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        print ("post to signup")
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # attempt to find user by the email
        existing_user = query_db(
            "SELECT email, password FROM user WHERE email = ?",
            (email, ),
            one=True
        )
        #error messages
        if existing_user:
            flash('Email already exists, Please',category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('first name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash("Password didn\'t match.", category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            query_db(
                "INSERT INTO user (email, password, first_name) VALUES (?, ?, ?)",
                (
                    email, 
                    generate_password_hash(password1),
                    first_name
                ),
                commit=True
            )
            user = query_db(
                "SELECT id FROM user WHERE email = ?",
                (email, ),
                one=True
            )
            session["user_id"] = user[0]
            session["cart"] = []
            flash('Account created', category='success')
            return redirect(url_for('menu'))

    return render_template("sign_up.html")

@app.route('/', methods=['GET', 'POST'])
def menu():
    if "cart" not in session:
        session['cart'] = []
    #connect and query
    sql = "SELECT * FROM item"
    menu = query_db(sql)
    return render_template("menu.html", menu=menu)

#displays item page by item id
@app.route('/item/<int:id>')
def item(id):
    sql = "SELECT * FROM item WHERE id = ?;"
    item = query_db(sql, args=(id,), one=True)
    return render_template("item.html", item=item)

#takes item from database
@app.route('/cart')
def cart():
    print(session["cart"])
    cart_name = []
    for id in session['cart']:
        sql = "SELECT name, price, id FROM item WHERE id = ?"
        item = query_db(sql, args=(id,), one=True)
        cart_name.append(item)

        #adds up total quantity
        # cursor = get_db().cursor()
        # count = "SELECT id, COUNT(*) as quantity FROM item GROUP BY id"
        # cursor.execute(count)
        # count = cursor.fetchall()
    return render_template("cart.html", cart_name=cart_name)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        return db

#adds item to cart
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    item_id = request.form.get("item_id")
    cartlist = session['cart']
    cartlist.append(item_id)
    session['cart'] = cartlist
    return redirect("/cart")

#delete items from session lists
@app.route("/delete", methods=["GET","POST"])
def delete():
    if request.method =="POST":
        print (session["cart"])
        id = request.form["id"]
        data = session["cart"]
        data.pop(int(id))
        session['cart'] = data
        #session["cart"].pop(int(id))
        print (session["cart"])
        print (id)
    return redirect('/cart')
    
if __name__ == '__main__':
    app.run(debug=True)