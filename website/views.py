from ast import arg
import sqlite3
from tkinter import Menu
from flask import Blueprint, render_template, g
from flask_login import current_user

views = Blueprint('views', __name__)
DATABASE="website/database.db"

def query_db(query, args=(), one=False):
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    cursor.close()
    db.close()
    #returns all the results unless one==True then it return just one result
    #it also checks that something came back and sends None if it is blank
    return (rv[0] if rv else None) if one else rv

@views.route('/')
def home():
    #connect and query
    sql = "SELECT * FROM item"
    menu = query_db(sql)
    return render_template("home.html", user=current_user,menu=menu)

@views.route('item/<int:id>')
def item(id):
    
    return f"this is the item page for id {id}"