from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, EmailField, PasswordField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length

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
    submit = SubmitField('Submit')

class TagForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')

class PageForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')

class GalleryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ExternalLinkForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    url = StringField('URL', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Submit')

class UploadForm(FlaskForm):
    file = StringField('File', validators=[DataRequired()])
    submit = SubmitField('Upload')

class UploadImageForm(FlaskForm):
    image = StringField('Image', validators=[DataRequired()])
    submit = SubmitField('Upload')

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