from flask import Flask, render_template,request, flash, session , redirect , url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,IntegerField,TextAreaField
from wtforms.validators import DataRequired,Email 
from flask_mail import Mail,Message
from flask_sqlalchemy import SQLAlchemy
from threading import Thread
import os
basedir=os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config['SECRET_KEY']="sachin"
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///' + os.path.join(basedir,'data.sqlite')

app.config['MAIL_SERVER'] ='smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

app.config['MAIL_SUBJECT_PREFIX'] = 'Query about '
app.config['MAIL_SENDER'] = 'Admin <ss100429@gmail.com>'

app.config['ADMIN'] = os.environ.get('ADMIN')

bootstrap=Bootstrap(app)
db= SQLAlchemy(app)
mail=Mail(app)

def send_mail_async(app,msg):
    with app.app_context():
        mail.send(msg)

def send_mail(subject,recv,template,**kwargs):
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + subject, sender = app.config['MAIL_SENDER'] , recipients = [recv] )
    msg.body = render_template (template + '.txt',**kwargs)
    msg.html = render_template (template + '.html',**kwargs)
    thrd = Thread(target=send_mail_async,args=[app,msg])
    thrd.start()
    return thrd

class User(db.Model):
    __tablename__ = 'Users'
    id= db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(60),unique=False,index=True)
    email = db.Column(db.String(60),unique=False,index=True)
    subject = db.Column(db.String(60),unique=False,index=True)
    message = db.Column(db.String(260),unique=False,index=True)
    def __repr__(self):
        return '< User %r>' % self.email
        
class myform(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(),Email()])
    sub = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET','POST'])
def index():
    form = myform()
    if form.validate_on_submit():
        user = User(name=form.name.data,email=form.email.data,subject=form.sub.data,message=form.message.data)
        db.session.add(user)
        db.session.commit()
        send_mail(user.subject,app.config['ADMIN'],'mail/new_user',user=user)
        flash('Thank You for Contacting Us!!')
        return redirect(url_for('index'))
    return render_template('index.html',form=form)
 
