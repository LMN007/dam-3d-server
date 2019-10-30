import zipfile
import hashlib
import requests
from bits.snapshot import *
import json
target_format = ".gltf"
cache_path = "./cache"
unzip_path = "./assets/models"
headers = {'Content-Type': 'application/json'}

# message = {
#     "model":"",
#     "name":"",
#     "model_id":"",
# }
# with open("./Dilophosaurus.zip","rb") as f:
#     message['model'] = base64.b64encode(f.read())
# message['name'] = "Dilophosaurus.zip"
# message['model_id'] = "1"


def refine(message):
    model_name,model_path = base64toFiles(message['model'],message['name']+str(message['model_id']))
    files = os.listdir(model_path)
    flag = 3  # 0 - gltf     1 - obj     2 - fbx    3 - error
    convert_file = ""
    ok = False
    for f in files:
        format = f.split('.')[-1]
        if format == "gltf":
            flag = 0
            convert_file = f
            ok = True
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
        res = json.loads(bytes.decode(sign.content))
        ok = res['ok']
        convert_file = res['converted']
    elif flag == 1:
        data = {
            "src":os.path.abspath(os.path.join(model_path,convert_file).replace("\\","/")),
            "dst":os.path.abspath(os.path.join(unzip_path,model_name).replace("\\","/"))
        }
        sign = requests.post("http://127.0.0.1:5300/api/obj2gltf",headers=headers,data=json.dumps(data))
        res = json.loads(bytes.decode(sign.content))
        ok = res['ok']
        convert_file = res['converted']
    if ok:
        model_info = modelSnapshot(os.path.abspath('./bits/template.html'),os.path.abspath(model_path),"../"+os.path.join(model_path,convert_file).replace("\\","/"))
    else:
        return None
    return model_info,model_name, model_path




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