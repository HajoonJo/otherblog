from flask import Blueprint, g, redirect, render_template, request, url_for, flash, abort
from flaskr.auth import login_required

from flaskr import db  # <-- GOOD: Use the shared instance!
bp = Blueprint('comment', __name__, url_prefix='/comment')

from flaskr.models import Comment

@bp.route('/create/<int:post_id>', methods=('POST',))
@login_required
def create(post_id):
    body = request.form['body']
    if not body:
        flash('Comment cannot be empty.')
    else:
        new_comment = Comment(body=body, author_id=g.user.id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
    return redirect(url_for('blog.index'))

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    comment = Comment.query.get_or_404(id)
    if comment.author_id != g.user.id:
        abort(403)
    if request.method == 'POST':
        body = request.form['body']
        if not body:
            flash('Comment cannot be empty.')
        else:
            comment.body = body
            db.session.commit()
            return redirect(url_for('blog.index'))
    return render_template('comment/edit.html', comment=comment)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    comment = Comment.query.get_or_404(id)
    if comment.author_id != g.user.id:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('blog.index'))