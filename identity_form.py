from flask_wtf import FlaskForm
from wtforms import StringField,FileField
from wtforms.validators import DataRequired,AnyOf

class IdentityForm(FlaskForm):
    file_type = StringField('file_type',validators=[DataRequired(),AnyOf(['file','url'])])
    side = StringField("side",validators=[DataRequired(),AnyOf('front','back')])
    file = FileField('file')
    url = StringField("url")
    secret = StringField("secret")