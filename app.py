from flask import Flask, render_template,request,redirect,url_for,flash,jsonify
from flask.typing import TemplateFilterCallable
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import random
import string 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///shortner.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Shortner(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    long =db.Column(db.String(),nullable = False)
    short = db.Column(db.String(5), nullable = False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self)->str:
        return f"{self.sno} - {self.long} - {self.short}"

class UserSchema(ma.Schema):
    class Meta:
       fields = ("SNO", "long", "short", "date_created")

users_schema = UserSchema(many=True)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
       return ''.join(random.choice(chars) for _ in range(size))

@app.route('/', methods=['GET','POST'])
def home():
    if request.method=="POST":

        url_received = request.form["url"]
        urlindb = Shortner.query.filter_by(long=url_received).first()

        if urlindb:
            return "URL already Present in DB. <br> URL that is present is  : <br>" +  url_received

        else:    
            long = request.form['url']
            short=request.host_url+id_generator()
            shortner = Shortner(long = long, short = short)
            db.session.add(shortner)
            db.session.commit()
            d = dict(); 
            d['Website'] = shortner.long
            d['ShortURL']   = shortner.short
            return d
            
            
    return render_template('index.html')

@app.route('/<id_generator>')
def redirection(id_generator):
    short=request.host_url+id_generator
    shortner = Shortner.query.filter_by(short=short).first()
    if shortner:
        return redirect(shortner.long)
    else:
        return "URL NOT Present"
        
@app.route('/api', methods = ['GET'])
def users():
    all_users = Shortner.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)
    
if __name__ == "__main__":
    app.run(port=5000, debug=True) 