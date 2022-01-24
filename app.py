from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from flask_bcrypt import Bcrypt
#from flask_login import (LoginManager, UserMixin, current_user, login_required, login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, DateField, SelectMultipleField
from wtforms.validators import InputRequired, Length, ValidationError
from garmin import connect
from datetime import datetime
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, current_user, logout_user, login_user
from formaterOLT import *
from oltAPI import olt as OLT



app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///base.db"
app.config["SECRET_KEY"] = "DETTE ER en hemmelig nøkkel"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = "8976asfdih37rgbidsuof6g3Q2R79T89VGBAUSOP6F3EG83O7"
app.config['SEND_REGRISTER_EMAIL'] = False
app.config['SECURITY_TRACKABLE'] = True

"""loginM = LoginManager()
loginM.init_app(app)
loginM.login_view = "login"

@loginM.user_loader
def load_bruker(bruker_id):
    return Bruker.query.get(int(bruker_id))"""

roles = db.Table(
    "roles",
    db.Column("user_id", db.Integer, db.ForeignKey("bruker.id")),
    db.Column("rolle_id", db.Integer, db.ForeignKey("rolle.id"))
)

class Bruker(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    brukernavn = db.Column(db.String(50))
    password = db.Column(db.String(255), nullable=False)
    connect_pass = db.Column(db.String(80))
    connect_bruker = db.Column(db.String(80))
    olt_pass = db.Column(db.String(80))
    olt_bruker = db.Column(db.String(80))
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer)
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship("Rolle", secondary=roles, backref=db.backref("bruker", lazy="dynamic"))

class Rolle(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    beskrivelse = db.Column(db.String(255))

    def __str__(self) -> str:
        return self.name

class RegF(FlaskForm):
    brukernavn = StringField(validators=[InputRequired(), Length(6, 30)], render_kw={"placeholder":"Brukernavn"})
    password = PasswordField(validators=[InputRequired(), Length(6, 30)], render_kw={"placeholder":"password"})
    reg = SubmitField("Regristrer")

    def validate_brukernavn(self, brukernavn):
        if Bruker.query.filter_by(brukernavn=brukernavn.data).first():
            raise ValidationError(
                "Dette brukernavnet eksisterer allerede, bruk et annet"
            )

class LoggInnF(FlaskForm):
    brukernavn = StringField(validators=[InputRequired(), Length(6, 30)], render_kw={"placeholder":"Brukernavn"})
    password = PasswordField(validators=[InputRequired(), Length(6, 30)], render_kw={"placeholder":"password"})
    login = SubmitField("Logg Inn")

class infoF(FlaskForm):
    connect_pass = StringField(render_kw={"placeholder":"Connect password"})
    connect_bruker = StringField(render_kw={"placeholder":"Connect brukernavn"})
    olt_pass = StringField(render_kw={"placeholder":"OLT password"})
    olt_bruker = StringField(render_kw={"placeholder":"OLT brukernavn"})
    lagre = SubmitField("Lagre")

class kjørF(FlaskForm):
    dato_fra = DateField(label="Fra")
    dato_til = DateField(label="Til")
    kjør = SubmitField("Kjør")


def velgF(liste=[]):
    class vF(FlaskForm):
        pass
        #valg = SelectMultipleField(choices=[("a", "A"), ("b", "B")]) 
    ut = []
    for i in liste:
        #print(i, type(i))
        ut.append((i["activityId"], str(i["startTimeLocal"]).split(" ")[0]+" - "+str(i["activityName"])))
    vF.valg = SelectMultipleField(choices=ut)
    vF.kjør = SubmitField("Kjør")
    return vF()


class minadmin(ModelView):
    @login_required
    def is_accessible(self):
        return True #current_user.brukernavn == "adminn"

class minadminhjem(AdminIndexView):
    @login_required
    def is_accessible(self):
        return True

C = None
user_datestore = SQLAlchemyUserDatastore(db, Bruker, Rolle)
sec = Security(app, user_datestore)
admin = Admin(app, index_view=minadminhjem())
admin.add_view(minadmin(Bruker, db.session))
admin.add_view(minadmin(Rolle, db.session))




@app.route("/")
def hjem():
    #print(current_user.email)
    return render_template("hjem.html")

@app.route("/min_side", methods=["POST", "GET"])
@login_required
def min_side():
    form = infoF()
    if form.validate_on_submit():
        current_user.connect_pass = form.connect_pass.data
        current_user.connect_bruker = form.connect_bruker.data
        current_user.olt_pass = form.olt_pass.data
        current_user.olt_bruker = form.olt_bruker.data
        db.session.commit()
        global C
        C = connect(form.connect_user.data, form.connect_pass.data)
        print(current_user.olt_bruker)
        flash("Lagret brukernavn og password for OLT og for connect", "success")
    form.connect_pass.data = current_user.connect_pass
    form.connect_bruker.data = current_user.connect_bruker
    form.olt_pass.data = current_user.olt_pass
    form.olt_bruker.data = current_user.olt_bruker
    return render_template("minbruker.html", side="Min Side", bruker=current_user, form=form)

@app.route("/loggut", methods=["POST", "GET"])
@login_required
def loggut():
    logout_user()
    return redirect(url_for("login"))

@app.route("/loginn", methods=["POST", "GET"])
def login():
    form = LoggInnF()

    if form.validate_on_submit():
        b = Bruker.query.filter_by(brukernavn=form.brukernavn.data).first()
        if b:
            if bcrypt.check_password_hash(b.password, form.password.data):
                login_user(b)
                flash(f"Hello {b.brukernavn}", "success")
                return redirect(url_for("hjem"))
            else:
                flash("password stemmer ikke!", "danger")
        else:
            flash("Bruker finnes ikke!", "warning")

    return render_template("login.html", form=form)

@app.route("/reg", methods=["POST", "GET"])
def reg():
    form = RegF()

    if form.validate_on_submit():
        user_datestore.create_user(email=form.email.data, password=form.password.data)
        #db.session.add(Bruker(brukernavn=form.brukernavn.data, password=bcrypt.generate_password_hash(form.password.data)))
        db.session.commit()
        login_user(Bruker.query.filter_by(email=form.email.data).first())
        flash(f"Ny bruker laget. Hello {form.brukernavn.data}!", "success")

        return redirect(url_for('min_side'))

    return render_template("reg.html", form=form)

@app.route("/kjør", methods=["POST", "GET"])
@login_required
def kjør():
    if None in [current_user.connect_pass, current_user.connect_bruker, current_user.olt_pass, current_user.olt_bruker] or "" in [current_user.connect_pass, current_user.connect_bruker, current_user.olt_pass, current_user.olt_bruker]:
        flash("Man må ha regristret password og brukernavn for å kunne kjøre", "warning")
        return redirect("min_side")
    form = kjørF()
    #print([current_user.connect_pass, current_user.connect_bruker, current_user.olt_pass, current_user.olt_bruker])
    if form.validate_on_submit():
        global C
        if not C:
            print("Logger inn på Connect")
            C = connect(current_user.connect_bruker, current_user.connect_pass)
            print(form.dato_fra.data, form.dato_til.data)
        resultat = C.get_aktiv_mellom(form.dato_fra.data, form.dato_til.data)
        velg = velgF(liste=resultat)
        #print(resultat, type(resultat))
        return render_template("kjør.html", form=form, resultat=resultat, datetime=datetime, str=str, velg=velg)
    return render_template("kjør.html", form=form)

@app.route("/olt", methods=["GET", "POST"])
def olt():
    if request.method == "POST":
        print(request.form)
        resid = [i for i in [[i, x] for i, x in request.form.lists()] if i[0] == "valg"][0][1]
        global C
        if not C:
            C = connect(current_user.connect_bruker, current_user.connect_pass)
        res = [C.aktivitet(i) for i in resid]
        print(res)
        O = OLT(current_user.olt_bruker, current_user.olt_pass)
        for i in res:
            print(i["activityName"])
            for d in O.finn(i["summaryDTO"]["startTimeLocal"].split(" ")[0], i["summaryDTO"]["startTimeLocal"].split(" ")[0]):
                O.slett(d)
                pass
            #with open("test.json", "w") as f:
            #    json.dump(økt(gå_igjennom_økter(i, C.puls(i["activityId"]))), f)
            print(i["activityTypeDTO"]["typeKey"])
            if O.økt(økt(gå_igjennom_økter(i, C.puls(i["activityId"])))):
                flash("Økten er logget til OLT", "success")
                redirect("kjør")


    return "HEI"

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port="6060")
