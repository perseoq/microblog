import click
from flask.cli import with_appcontext

from blog.arch.models import User
from blog.core.extensions import db


@click.command('seed-admin')
@click.option('--username', prompt=True)
@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
@with_appcontext
def seed_admin(username, email, password):
    if User.query.filter_by(email=email).first():
        click.echo('Ya existe un usuario con ese correo.')
        return
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f'Administrador {username} creado.')
