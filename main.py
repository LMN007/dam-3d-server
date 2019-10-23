from flask import Flask, request,jsonify,send_from_directory
from bits.db import *
from bits.unzip import *

app = Flask(__name__)
app.config['MODEL_PATH'] = unzip_path
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
    


if __name__ == "__main__":
    con = databaseInit()
    app.run(debug=True)