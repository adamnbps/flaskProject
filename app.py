from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)
app.secret_key = 'the random string'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subtitle = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),
        nullable=False)
    category = db.relationship('Category', backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return '<Post %r>' % self.title


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return '<Category %r>' % self.name

@app.route('/')
def get_all_posts():  # put application's code here
    posts = Post.query.all()
    return render_template("index.html", posts=posts)


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def display_post(post_id):
    if request.method == "GET":
        fetched_post = Post.query.get(post_id)
        return render_template("/post.html", post=fetched_post)


@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    if request.method == "GET":
        fetched_post = Post.query.get(post_id)
        categories = Category.query.all()
        return render_template("/edit-post.html", post=fetched_post, categories=categories)

    else:
        fetched_post = Post.query.get(post_id)
        category = request.form["category"]
        fetched_category = Category.query.filter_by(name=category).first()
        if fetched_category is None:
            fetched_category = Category(name=category)
        fetched_post.title = request.form["title"]
        fetched_post.subtitle = request.form["subtitle"]
        fetched_post.body = request.form["body"]
        fetched_post.category = fetched_category
        db.session.commit()
        return redirect(url_for("display_post", post_id=post_id))

@app.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
def delete_post(post_id):
    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted from database.","info")
    return redirect(url_for("get_all_posts"))

@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    if request.method == "GET":
        categories = Category.query.all()
        return render_template("/add-post.html", categories=categories)
    else:
        category = request.form["category"]
        fetched_category = Category.query.filter_by(name=category).first()
        if fetched_category is None:
            fetched_category = Category(name=category)
        post = Post(
            title=request.form["title"],
            subtitle=request.form["subtitle"],
            body=request.form["body"],
            category=fetched_category
        )
        db.session.add(post)
        db.session.commit()
        flash("Post added to database.", "info")
        return redirect(url_for("get_all_posts"))

@app.route('/contact')
def contact():
    return render_template("/contact.html")

@app.route('/edit-category', methods=['GET', 'POST'])
def edit_category():
    if request.method == "GET":
        categories = Category.query.all()
        return render_template("/edit-category.html", categories=categories)
    else:
        category = request.form["category_id"]
        fetched_category = Category.query.get(category)
        if fetched_category is None:
            fetched_category = Category(name=category)
        fetched_category.name = request.form["title"]
        db.session.commit()
        categories = Category.query.all()
        return render_template("/edit-category.html", categories=categories)


if __name__ == '__main__':
    app.run()
