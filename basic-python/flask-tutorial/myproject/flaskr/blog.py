from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr import db  # <-- GOOD: Use the shared instance!
from flaskr.auth import login_required
from flaskr.models import Post, User

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    posts = Post.query.join(User, Post.author_id == User.id) \
        .add_columns(Post.id, Post.title, Post.body, Post.created, Post.author_id, User.username) \
        .order_by(Post.created.desc()).all()

    # Fetch all comments (if you have a Comment model)
    from flaskr.models import Comment
    comments = Comment.query.order_by(Comment.created.asc()).all()

    # Organize comments by post_id
    comments_by_post = {}
    for comment in comments:
        comments_by_post.setdefault(comment.post_id, []).append(comment)

    # Attach comments to each post
    posts_with_comments = []
    for post_tuple in posts:
        post = post_tuple[0] if isinstance(post_tuple, tuple) else post_tuple
        post_dict = {
            'id': post.id,
            'title': post.title,
            'body': post.body,
            'created': post.created,
            'author_id': post.author_id,
            'username': post_tuple.username if hasattr(post_tuple, 'username') else '',
            'comments': comments_by_post.get(post.id, [])
        }
        posts_with_comments.append(post_dict)

    return render_template('blog/index.html', posts=posts_with_comments)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            new_post = Post(title=title, body=body, author_id=g.user.id)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = Post.query.get(id)
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
    if check_author and post.author_id != g.user.id:
        abort(403, "You do not have permission to access this post.")
    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            post.title = title
            post.body = body
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('blog.index'))
