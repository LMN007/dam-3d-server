from flask import Flask, request, render_template, jsonify
import os, sys
from bits.db import *
from bits.unzip import *

app = Flask(__name__)

@app.route("/api/upload/model", methods = ['GET', 'POST'])
def upload_model():
    model_info = request.get_json()
    print(type(model_info))
    print(model_info['filename'])
    # con = databaseInit()
    url = createURL(con, model_info)
    message = sendMessage(con, model_info)
    # with open("./a_simple_pokeball.zip","rb") as f:
    #     message['model'] = base64.b64encode(f.read())
    model_new,path = lzw(message)
    return "{}"
    
#
# if __name__ == "__main__":
#     con = databaseInit()
#     app.run(debug=True)