import time

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from blog.arch.forms import InstallForm, LoginForm, RecoverForm, ResetPasswordForm, TOTPForm
from blog.arch.models import User
from blog.core.extensions import db, mail
from blog.core.totp import verify_code

auth = Blueprint('auth', __name__)

RESET_TOKEN_MAX_AGE = 1800
PENDING_2FA_MAX_AGE = 300
PENDING_2FA_USER = 'pending_2fa_user_id'
PENDING_2FA_AT = 'pending_2fa_at'
PENDING_2FA_REMEMBER = 'pending_2fa_remember'


def _reset_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='password-reset')


def _clear_pending_2fa():
    session.pop(PENDING_2FA_USER, None)
    session.pop(PENDING_2FA_AT, None)
    session.pop(PENDING_2FA_REMEMBER, None)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.totp_enabled:
                session[PENDING_2FA_USER] = user.id
                session[PENDING_2FA_AT] = time.time()
                session[PENDING_2FA_REMEMBER] = bool(form.remember_me.data)
                return redirect(url_for('auth.verify_2fa'))
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('blog.index'))
        flash('Correo o contraseña inválidos.', 'danger')
    return render_template('auth/login.html', form=form)


@auth.route('/login/2fa', methods=['GET', 'POST'])
def verify_2fa():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    user_id = session.get(PENDING_2FA_USER)
    started = session.get(PENDING_2FA_AT, 0)
    if not user_id or time.time() - started > PENDING_2FA_MAX_AGE:
        _clear_pending_2fa()
        flash('La verificación en dos pasos ha expirado. Inicia sesión de nuevo.', 'warning')
        return redirect(url_for('auth.login'))
    user = db.session.get(User, user_id)
    if user is None or not user.totp_enabled:
        _clear_pending_2fa()
        return redirect(url_for('auth.login'))
    form = TOTPForm()
    if form.validate_on_submit():
        if verify_code(user.totp_secret, form.code.data):
            remember = session.get(PENDING_2FA_REMEMBER, False)
            _clear_pending_2fa()
            login_user(user, remember=remember)
            return redirect(url_for('blog.index'))
        flash('Código de verificación inválido.', 'danger')
    return render_template('auth/verify_2fa.html', form=form)


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
            try:
                mail.send_message(
                    'Recuperación de contraseña - microblog',
                    recipients=[user.email],
                    body=body,
                )
            except Exception:
                current_app.logger.exception('No se pudo enviar el correo de recuperación.')
                current_app.logger.info('Enlace de recuperación: %s', link)
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
