from flask import Flask, request,jsonify,send_from_directory,session
from bits.db import *
from bits.unzip import *
from contextlib import closing
#from wtforms import Form, TextField, PasswordField, BooleanField, validators

app = Flask(__name__)
app.secret_key = '123456'

app.config['MODEL_PATH'] = unzip_path


@app.route("/media/image/<path:p>",methods=['GET','POST'])
def retImage(p):
    return send_from_directory(unzip_path,os.path.join(p,'scene.gltf'),as_attachment=True)

@app.route("/api/upload/model", methods = ['GET', 'POST'])
def upload_model():
    try:
        model_info = request.get_json()
        print(model_info['filename'])
        con = databaseInit()
        # url = createURL(con, model_info)
        message = sendMessage(con, model_info)
        model_info,model_name = refine(message)
        print(model_info)
        print(model_name)
        return "{'code':'0',data:{'preview':'" + model_name +  "'}}"
    except Exception as e:
        return jsonify({'code':1, 'msg': '{}'.format(e)})
    


@app.route('/api/user/register', methods=['POST', 'GET'])
def register():
    try:
        #form = RegistrationForm(request.get_json())
        form = request.get_json()
        #print(form)
        #if request.method == 'POST' and form.validate():
        #if True:
        error,msg=registerUser(form)
        print(msg)
        if not error:
            session['logged_in'] = True
            session['username'] = form['username']
        else:
            return jsonify({'code':1,'msg':"{}".format(msg)})
        #return redirect(url_for('login'))
        data=getUserData(form['username'])
        print(data)
        print({'code':0,'data':"{}".format(data),'msg':"{}".format(msg)})
        return jsonify({'code':0,'data':"{}".format(data),'msg':"{}".format(msg)})

    except Exception as e:
        #return str(e)
        print("exception")
        print(e)
        return jsonify({'code':2,'msg':'Exception error : {}'.format(e)})


@app.route('/api/user/login', methods=['POST', 'GET'])
def login():
    try:
        error = None
        if request.method == 'POST':
            user_info = request.get_json()
            
            print(user_info)
            error,msg=dbLogin(user_info)
        
            if error:
                print({'code':1,'msg':"{}".format(msg)})
                return jsonify({'code':1,'msg':"{}".format(msg)})
            else:
                session['logged_in'] = True
                session['username'] = user_info['username']
                print("login success")
                data=getUserData(user_info['username'])
                print({'code':0,'data':"{}".format(data),'msg':"{}".format(msg)})
                return jsonify({'code':0,'data':"{}".format(data),'msg':"{}".format(msg)})
    except Exception as e:
        #return str(e)
        print("error")
        return jsonify({'code':4,'msg':"{}".format(e)})

@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    return jsonify({'code':0,'msg':"success"})

@app.route('/api/user/update/avatar')
def updateAvatar():
    try:
        form = request.get_json()
        error,msg=dbUpdateAvatar(form)
        if error:
            return jsonify({'code':1,'msg':"{}".format(msg)})
        else:           
            #return redirect(url_for('login'))
            data=getUserData(form['username'])
            print({'code':0,'data':"{}".format(data),'msg':"{}".format(msg)})
            return jsonify({'code':0,'data':"{}".format(data),'msg':"{}".format(msg)})

    except Exception as e:
         return jsonify({'code':4,'msg':"{}".format(e)})

        
@app.route('/api/user/update/passwd')
def updatePasswd():
    try:
        form = request.get_json()
        error,msg=dbUpdatePasswd(form)
        if error:
            return jsonify({'code':1,'msg':"{}".format(msg)})
        else:           
            #return redirect(url_for('login'))
            data=getUserData(form['username'])
            print({'code':0,'data':"{}".format(data),'msg':"{}".format(msg)})
            return jsonify({'code':0,'data':"{}".format(data),'msg':"{}".format(msg)})

    except Exception as e:
         return jsonify({'code':4,'msg':"{}".format(e)})

@app.route('/api/user/update/basic')
def updateBasic():
    try:
        form = request.get_json()
        error,msg=dbUpdateBasic(form)
        if error:
            return jsonify({'code':1,'msg':"{}".format(msg)})
        else:           
            #return redirect(url_for('login'))
            data=getUserData(form['username'])
            print({'code':0,'data':"{}".format(data),'msg':"{}".format(msg)})
            return jsonify({'code':0,'data':"{}".format(data),'msg':"{}".format(msg)})

    except Exception as e:
         return jsonify({'code':4,'msg':"{}".format(e)})

if __name__ == "__main__":
    con = databaseInit()
    app.run(debug=False)