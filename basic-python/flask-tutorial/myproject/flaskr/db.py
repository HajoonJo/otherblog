from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flaskr import db  # Import the SAME db instance
import click
from flask import current_app, g




def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
   

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


# SQLAlchemy.register_converter(
#    "timestamp", lambda v: datetime.fromisoformat(v.decode())
#)

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)