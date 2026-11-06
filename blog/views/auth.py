from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from blog.arch.forms import InstallForm, LoginForm, RecoverForm, ResetPasswordForm
from blog.arch.models import User
from blog.core.extensions import db, mail

auth = Blueprint('auth', __name__)

RESET_TOKEN_MAX_AGE = 1800


def _reset_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='password-reset')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('blog.index'))
        flash('Correo o contraseña inválidos.', 'danger')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('blog.index'))


@auth.route('/recover', methods=['GET', 'POST'])
def recover():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    form = RecoverForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = _reset_serializer().dumps(user.email)
            link = url_for('auth.reset_password', token=token, _external=True)
            body = f'Para restablecer tu contraseña visita: {link}'
            if current_app.config.get('DEBUG'):
                current_app.logger.info(body)
            else:
                mail.send_message(
                    'Recuperación de contraseña - microblog',
                    recipients=[user.email],
                    body=body,
                )
        flash('Si el correo está registrado, enviamos un enlace de recuperación.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/recovery.html', form=form)


@auth.route('/recover/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = _reset_serializer().loads(token, max_age=RESET_TOKEN_MAX_AGE)
    except (BadSignature, SignatureExpired):
        flash('El enlace de recuperación no es válido o ha expirado.', 'danger')
        return redirect(url_for('auth.recover'))
    user = User.query.filter_by(email=email).first()
    if user is None:
        flash('El enlace de recuperación no es válido.', 'danger')
        return redirect(url_for('auth.recover'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Contraseña actualizada. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset.html', form=form)


@auth.route('/install', methods=['GET', 'POST'])
def install():
    if User.query.first() is not None:
        return redirect(url_for('auth.login'))
    form = InstallForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Administrador creado. Inicia sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/install.html', form=form)
