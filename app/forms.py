'''
HTML Forms for gathering data
'''

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired

class PetForm(FlaskForm):
    ''' Web Form for creating a Pet '''
    name = StringField('Name', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int)
    available = BooleanField('Available')
    submit = SubmitField('Create Pet')

class CategoryForm(FlaskForm):
    ''' Web Form for creating a Category '''
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Create Category')
