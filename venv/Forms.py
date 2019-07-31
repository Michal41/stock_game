from User import User
from flask_wtf import FlaskForm
from wtforms import StringField,validators,PasswordField,SubmitField
class Login_form(FlaskForm):
    user_name=StringField("Nazwa użytkownika",[validators.DataRequired(),validators.length(min=5,max=20)])
    password=PasswordField("Hasło",[validators.DataRequired(),validators.length(min=5,max=20)])
    submit=SubmitField("Zaloguj")
class Register_form(FlaskForm):
    email=StringField("Podaj E-mail",[validators.DataRequired(),validators.email()])
    user_name=StringField("Nazwa użytkownika",[validators.DataRequired(),validators.length(min=5,max=20)])
    password=PasswordField("Hasło",[validators.DataRequired(),validators.length(min=5,max=20)])
    confirm_password=PasswordField("Powtórz Hasło",[validators.DataRequired(),validators.EqualTo('password', message='Hasła nie są takie same')])
    submit=SubmitField("Zarejestruj")
    def validate_user_name(self,user_name):
        users_colection=User.users_collection()
        if users_colection.find_one({"user_name":user_name.data}):
            raise validators.ValidationError("Podana nazwa użytkownika jest zajęta ")

    def validate_email(self, email):
        users_colection = User.users_collection()
        if users_colection.find_one({"e-mail": email.data}):
            raise validators.ValidationError("Istnieje konto powiązane z tym adresem e-mail")

