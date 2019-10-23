import zipfile
# import rarfile
import base64
import os
import re
import hashlib
import requests
import json
from bits.snapshot import *


target_format = ".gltf"
cache_path = "./cache"
unzip_path = "./unzipped"
headers = {'Content-Type': 'application/json'}


def lzw(message):
    model_name,model_path = base64toFiles(message['model'],message['name']+str(message['model_id']))
    files = os.listdir(model_path)
    flag = 3  # 0 - gltf     1 - obj     2 - fbx    3 - error
    convert_file = ""
    for f in files:
        format = f.split('.')[-1]
        if format == "gltf":
            flag = 0
            convert_file = f
            break
        elif format == 'obj':
            flag = 1
            convert_file = f
            break
        elif format == 'fbx':
            flag = 2
            convert_file = f
            break
    if flag == 3:
        print("3d model file not Found!")
        return None
    if flag == 2:
        data = {
            "src":os.path.abspath(os.path.join(model_path,convert_file).replace("\\","/")),
            "dst":os.path.abspath(os.path.join(unzip_path,model_name).replace("\\","/"))
        }
        sign = requests.post("http://127.0.0.1:5300/api/fbx2gltf",headers=headers,data=json.dumps(data))
    elif flag == 1:
        data = {
            "src":os.path.abspath(os.path.join(model_path,convert_file).replace("\\","/")),
            "dst":os.path.abspath(os.path.join(unzip_path,model_name).replace("\\","/"))
        }
        sign = requests.post("http://127.0.0.1:5300/api/obj2gltf",headers=headers,data=json.dumps(data))
    model_info = modelSnapshot('./bits/template.html',os.path.abspath(model_path),os.path.abspath(os.path.join(model_path,convert_file).replace("\\","/")))
    return model_info,os.path.join(unzip_path, model_name)


def base64toFiles(src_file_data,src_name):
    md5 = hashlib.md5()
    if os.path.exists(cache_path) is not True:
        os.mkdir(cache_path)
    if os.path.exists(unzip_path) is not True:
        os.mkdir(unzip_path)

    md5.update(src_name.encode("utf-8"))
    zip_name = md5.hexdigest()[:8]
    # print(zip_name)
    cache_zip = os.path.join(cache_path,zip_name+".zip")
    # print(src_file_data)
    with open(cache_zip,"wb") as f:
        f.write(base64.b64decode(src_file_data))

    zip = zipfile.ZipFile(cache_zip)
    model_path = os.path.join(unzip_path,zip_name)
    if os.path.exists(model_path) is not True:
        os.mkdir(model_path)
    zip.extractall(path=model_path)
    zip.close()
    os.remove(cache_zip)
    return zip_name,model_path


# lzw(message)
# driver.quit()