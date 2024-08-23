from flask import Flask, render_template, request, redirect, url_for, g, session, flash
import os
from markupsafe import Markup
import sqlite3
from werkzeug.security import check_password_hash

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("/home/tbui123/blog.db")
    return g.db

def index():
    return render_template("index.html")

def blog_posts():
    db = get_db()
    results = db.execute("SELECT rowid, title, content FROM posts ORDER BY created DESC").fetchall()
    data = []
    for r in results:
        data.append({ "pid": r[0], "title": r[1], "content": r[2] })
    return render_template("posts.html", post_data=data)


def view():
    pid = request.args.get("pid")
    db = get_db()
    result = db.execute("SELECT rowid, title, content FROM posts WHERE rowid=?", (pid)).fetchone()
    return render_template("view.html", data={ "pid": result[0], "title": result[1], "content": result[2] })

def create():
    user_id = session.get("user_id")
    if user_id == None:
        return redirect(url_for("login"))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        #include user_id with INSERT
        #fill database with new title and content
        return redirect(url_for("posts"))

    return render_template("create.html")

def logout():
    if request.method == 'POST':
        session.clear()
    return render_template("index.html")
    

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        query = "SELECT password, rowid FROM users WHERE username=?"
        #hashed_password = db.execute(query, (username,)).fetchone()[0]
        row = db.execute(query, (username,)).fetchone()
        if not row == None:
            hashed_password = row[0]
            rowid = row[1]
            if check_password_hash(hashed_password, password):
                session.clear()
                session['user_id'] = rowid
                flash("Successfully logged in")
                return redirect(url_for("index"))

        flash("Username or password invalid")
        return redirect(url_for("login"))

    return render_template("login.html")

#app = Flask(__name__, template_folder="/home/tbui123/mysite/templates/", static_folder="/home/tbui123/mysite/static/")
app = Flask(__name__)
app.config.from_mapping(SECRET_KEY='dev')
app.add_url_rule("/", "index", index)
app.add_url_rule("/posts", "posts", blog_posts)
app.add_url_rule("/posts/view", "view", view)
app.add_url_rule("/posts/create", "create", create, methods=['GET', 'POST'])
app.add_url_rule("/users/login", "login", login, methods=['GET', 'POST'])
app.add_url_rule("/users/logout", "logout", logout, methods=['POST'])
#app.run()

