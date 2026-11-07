from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired, MultipleFileField
from wtforms import (
    BooleanField,
    EmailField,
    PasswordField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, EqualTo, Length, Optional, Regexp

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RecoverForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Length(max=120)])
    submit = SubmitField('Recover Password')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class InstallForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=20)])
    email = EmailField('Email', validators=[DataRequired(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Install')


class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Añadir')

class TagForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Añadir')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    content = CKEditorField('Content', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    tags = SelectMultipleField('Tags', coerce=int, validators=[Optional()])
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')

class PageForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    content = CKEditorField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')

class GalleryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Submit')

class ExternalLinkForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    url = StringField('URL', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Submit')

class UploadForm(FlaskForm):
    file = StringField('File', validators=[DataRequired()])
    submit = SubmitField('Upload')

class UploadImageForm(FlaskForm):
    image = MultipleFileField('Images', validators=[FileRequired(), FileAllowed({'png', 'jpg', 'jpeg', 'gif', 'webp'}, 'Formato de imagen no permitido.')])
    submit = SubmitField('Subir imágenes')

class ImageForm(FlaskForm):
    image = StringField('Image', validators=[DataRequired()])
    submit = SubmitField('Submit')

class UploadVideoForm(FlaskForm):
    video = StringField('Video', validators=[DataRequired()])
    submit = SubmitField('Upload')

class VideoForm(FlaskForm):
    video = StringField('Video', validators=[DataRequired()])
    submit = SubmitField('Submit')

class DatabaseForm(FlaskForm):
    hostname = StringField('Hostname', validators=[DataRequired(), Length(max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired()])
    database_name = StringField('Database Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Submit')

class AdminForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    email = EmailField('Email', validators=[DataRequired(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=20)])
    email = EmailField('Email', validators=[DataRequired(), Length(max=120)])
    submit = SubmitField('Guardar')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Cambiar contraseña')

class TOTPForm(FlaskForm):
    code = StringField('Code', validators=[
        DataRequired(),
        Regexp(r'^\d{6}$', message='Introduce un código de 6 dígitos.'),
    ])
    submit = SubmitField('Verificar')

class TwoFactorDisableForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    code = StringField('Code', validators=[
        DataRequired(),
        Regexp(r'^\d{6}$', message='Introduce un código de 6 dígitos.'),
    ])
    submit = SubmitField('Desactivar')
