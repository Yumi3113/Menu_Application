from pickle import TRUE
from flask import Flask, render_template, request, flash, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from os import path
import sqlite3

app = Flask(__name__)
DATABASE = "website/database.db"
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
                # user now logged in redirect home
                return redirect(url_for('home'))
            else:
                # password was inocrrect
                flash('Incorrect password, try again.', category='error')
        else:
            # user was not found
            flash('Email does not exist.', category='error')

    return render_template("login.html")


@app.route('/logout')
def logout():
    session["user_id"] = None
    return redirect(url_for('login'))

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

        if existing_user:
            flash('Email already exists.',category='error')
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
            flash('Account created', category='success')
            return redirect(url_for('home'))

    return render_template("sign_up.html")

@app.route('/')
def menu():
    #connect and query
    sql = "SELECT * FROM item"
    menu = query_db(sql)
    return render_template("menu.html", menu=menu)

@app.route('/item/<int:id>')
def item(id):
    sql = "SELECT * FROM item WHERE id = ?;"
    item = query_db(sql, args=(id,), one=True)
    return render_template("item.html", item=item)

if __name__ == '__main__':
    app.run(debug=True)