import sqlite3
from tkinter import Menu
from flask import Blueprint, render_template
from flask_login import current_user

views = Blueprint('views', __name__)
DATABASE="website/database.db"


@views.route('/')
def home():
    #connect and query
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    sql = "SELECT * FROM item"
    cursor.execute(sql)
    menu = cursor.fetchall()
    print(menu)
    db.close()
    return render_template("home.html", user=current_user,menu=menu)

@views.route('item/<int:id>')
def item(id):
    return f"this is the item page for id {id}"