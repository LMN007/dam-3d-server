from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash,current_app,jsonify,send_from_directory
from bits.db import *
from bits.unzip import *
import os
import sqlite3
from contextlib import closing
import gc
from wtforms import Form, TextField, PasswordField, BooleanField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key = '123456'

app.config.update(
    DATABASE = 'database/models.db',
    DEBUG=True,
)

# app.config['MODEL_PATH'] = unzip_path

def connect_db():
    return sqlite3.connect(app.config['DATAPATH'])

def get_db():
    db = connect_db()
    cur = db.cursor()
    return db,cur

@app.route("/media/image/<path:p>",methods=['GET','POST'])
def retImage(p):
    return send_from_directory(unzip_path,os.path.join(p,'scene.gltf'),as_attachment=True)



@app.route("/api/upload/model", methods = ['GET', 'POST'])
def upload_model():
    try:
        model_info = request.get_json()
        # print(type(model_info))
        print(model_info['filename'])
        con = databaseInit()
        url = createURL(con, model_info)
        message = sendMessage(con, model_info)
        # print("message: {}".format(message))
        # with open("./a_simple_pokeball.zip","rb") as f:
        #     message['model'] = base64.b64encode(f.read())
        model_info,model_name = refine(message)
        print(model_info)
        print(model_name)
        return "{'code':'0',data:{'preview':'" + model_name +  "'}}"
    except Exception as e:
        print(e)
        return jsonify({'code':1, 'msg': '{}'.format(e)})
    


class RegistrationForm(Form):
    username = TextField('username', [validators.Length(min=2, max=20)])
    nickname = TextField('nickname', [validators.length(min=2,max=20)])
    location = TextField('location')
    introduction = TextField('introduction', [validators.length(max=128)])
    biography = TextField('biography', [validators.length(max=265)])
    avatar = TextField('avatar')
    email = TextField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message='Passwords must match.')])
    confirm = PasswordField('Password Again')



@app.route('/api/user/register', methods=['POST', 'GET'])
def register():
    try:
        #form = RegistrationForm(request.get_json())
        form = request.get_json()
        #if request.method == 'POST' and form.validate():
        if True:
            '''
            username = form.username.data
            nickname=form.nickname.data
            location=form.location.data
            introduction=form.introduction.data
            biography=form.biography.data
            email = form.email.data
            avatar=form.avatar.data
            password = sha256_crypt.encrypt(str(form.password.data))    #encode paassword
            '''
            username=form['username']
            nickname=form['nickname']
            location=form['location']
            introduction=form['introduction']
            biography=form['biography']
            email = form['email']
            avatar=form['avatar']
            password = sha256_crypt.encrypt(str(form['password']))    #encode paassword

            #db, cur = get_db()
            db = databaseInit()
            cur = db.cursor()

            x = cur.execute(
                'SELECT * FROM user WHERE username = ?', [username])

            babab = x.fetchall()
            if len(babab) != 0:
                print(babab, len(babab))
                #flash("That username is already taken, please choose another")
                #return render_template('register.html', form=form)
                return jsonify({'code':2,'msg':"That username is already taken, please choose another"})
            else:
                cur.execute("INSERT INTO user (username, nickname, password, location, introduction, biography, email, avatar) VALUES(?,?,?,?,?,?,?,?)", [
                            username, nickname, password, location, introduction, biography, email, avatar])
                db.commit()

                flash("Thanks for registering!")

                cur.close()
                db.close()
                gc.collect()      # collect garbage

                session['logged_in'] = True
                session['username'] = username

                #return redirect(url_for('login'))
                return jsonify({'code':0,'msg':"success"})

        #return render_template('register.html', form=form)
        return jsonify({'code':3,'msg':"invalidate"})

    except Exception as e:
        #return str(e)
        return jsonify({'code':10,'msg':'{}'.format(e)})


@app.route('/api/user/login', methods=['POST', 'GET'])
def login():
    try:
        error = None
        if request.method == 'POST':
            '''
            username = request.form['username']
            password = request.form['password']
            '''
            user_info = request.get_json()
            print(user_info)
            username=user_info['username']
            password=user_info['password']
            print(username+'&'+password)

            #db, cur = get_db()
            db = databaseInit()
            cur = db.cursor()

            passwd_hash_tuple = cur.execute(
                'SELECT password FROM user WHERE username=?', [username]).fetchone()   # return a tuple

            if not passwd_hash_tuple:
                error = 'Invalid username'

            elif not (sha256_crypt.verify(password, passwd_hash_tuple[0])):
                error = 'Invalid password'
            else:
                #flash('Hey %s, you are in' % username)
                session['logged_in'] = True
                session['username'] = username
                #return redirect(url_for('test'))
                return jsonify({'code':0,'msg':"success"})

        gc.collect()
        #return render_template('login.html', error=error)
        return jsonify({'code':3,'data':'{}'.format(error),'msg':"failure"})

    except Exception as e:
        #return str(e)
        return jsonify({'code':4,'msg':"{}".format(e)})

@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    flash("You have logged out")
    #return redirect(url_for('test'))
    return jsonify({'code':0,'msg':"success"})


if __name__ == "__main__":
    con = databaseInit()
    app.run(port=5000,debug=True)