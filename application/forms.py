from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, URL, Optional, ValidationError
from wtforms.fields.html5 import DateField


class URLForm(FlaskForm):
    current_url = StringField('Current URL', validators=[DataRequired(), URL(message="This is not a valid URL")])
    register_url = StringField('New URL', validators=[DataRequired(), URL(message="This is not a valid URL")])
    # entry_date = DateField('Entry date', validators=[DataRequired()])
    # end_date = DateField('End date', validators=[Optional(strip_whitespace=True)])
    def validate(self):
        if not super().validate():
            return False
        result = True
        if self.current_url.data == self.register_url.data:
            self.register_url.errors.append('The new URL cannot be the same as the current URL')
            result = False

        return result



