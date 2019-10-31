import sqlite3
import os
import time
import gc
import re
import base64
from fuzzywuzzy import fuzz
import hashlib
from passlib.hash import sha256_crypt


def createURL(con, model_dict):
    sql = "select max(model_ID) from model;"
    try:
        c = con.cursor()
        c.execute(sql)
        con.commit()
    except Exception as e:
        print(e)
    else:
        id = c.fetchall()[0][0] + 1
        print(id)

        model_dict['owner'] = "wsh"
        owner = model_dict['owner']
        name = model_dict['name'].split(".")[0]
        folderName = name + str(id)
        sha1 = hashlib.sha1()
        sha1.update(folderName.encode('utf-8'))
        hashcode = sha1.hexdigest()
        url = r'assets/models' + '/' + owner
        if os.path.exists(url):
            print("The path is exist!")
        else:
            os.makedirs(url)
        return url


def sendMessage(con, model_info,user):
    sql = "select max(model_ID) from model;"
    try:
        c = con.cursor()
        c.execute(sql)
        con.commit()
    except Exception as e:
        print(e)
        raise e
    message = {}
    temp = c.fetchall()[0][0]
    if temp is None or type(temp) is None:
        model_id = 1
    else:
        model_id = temp + 1
    a = "5"
    model_base64 = model_info['model']
    message['format'] = model_info['filename'].split(".")[-1]
    model_name = model_info['filename'].split(".")[0]
    # model_name = model_info['filename'][0:len(model_info['filename'])-len(message['format']-1)]
    message['user'] = user
    message['name'] = model_name
    message['model_id'] = model_id
    message['model'] = model_base64
    message['render_config'] = model_info['render_config']
    return message

# 创建name和type表


def createModelsTable(con):
    sql = "create table model (model_ID INTEGER PRIMARY KEY AUTOINCREMENT, "\
        "model_name varchar(20),"\
        "type_name varchar(20),"\
        "publish_time TEXT,"\
        "num_triangles INTEGER,"\
        "num_vertices INTEGER,"\
        "animated INTEGER,"\
        "owner_ID INTEGER,"\
        "url varchar(50));"
    try:
        c = con.cursor()
        c.execute(sql)
        con.commit()
    except Exception as e:
        print(e)
    else:
        print("Create table model success!")

# 建立Tag表


def createTagTable(con):

    sql = "create table tag (model_ID INTEGER," \
        "tag_name varchar(100),"\
        "FOREIGN KEY(model_ID) REFERENCES model(model_ID));"
    try:
        c = con.cursor()
        c.execute(sql)
        con.commit()
    except Exception as e:
        print(e)
    else:
        print("Create table tag success!")


def insertModel(con, model_dict, model_add_dict, user, url):
    model_name = model_dict['name'].split('.')[0]
    type_name = model_dict['catalog']
    publish_time = time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    num_triangles = model_add_dict['triangles']
    num_vertices = model_add_dict['vertices']
    animated = 0
    owner = user
    tags = model_dict['tags']
    sql = "insert into model values (NULL," \
        "'" + model_name + "',"  \
        "'" + type_name + "',"\
        "'" + publish_time + "',"\
        "" + str(num_triangles) + ","\
        "" + str(num_vertices) + ","\
        "" + str(animated) + ","\
        "'" + owner + "',"\
        "'" + url + "');"
    try:
        c1 = con.cursor()
        c1.execute(sql)
        con.commit()
        sql_2 = "select model_ID from model where publish_time = '" + publish_time + "';"
        try:
            c2 = con.cursor()
            c2.execute(sql_2)
            con.commit()
        except Exception as e:
            print(e)
        else:
            model_id = c2.fetchall()[0][0]
            model_dict['model_ID'] = model_id
            # url = r'./models/' + owner + '/' + str(model_id)

            for tag in tags:
                insertTag(con, model_id, tag)
            sql_3 = "insert into user_product values(NULL, '"+ owner+"'," + str(model_id) + ")"
            try:
                c3 = con.cursor()
                c3.execute(sql_3)
                con.commit()
            except Exception as e:
                print(e)
            else:
                print("Insert into user_product success")
    except Exception as e:
        print(e)
    else:
        print("Insert Success!")


def selectNameFromModel(con):
    sql = "select model_ID, model_name from model"
    try:
        c = con.cursor()
        c.execute(sql)
        con.commit()
    except Exception as e:
        print(e)
    else:
        return c.fetchall()


def fuzzyName(con, name_list, input_name):
    fuzzy_dict = {}
    fuzzy_sorted = {}
    for name in name_list:
        fuzzy_dict[name[0]] = fuzz.ratio(name[1], input_name)
    models_list = []
    count = 0
    for k in sorted(fuzzy_dict, key=fuzzy_dict.__getitem__, reverse=True):
        fuzzy_sorted[k] = fuzzy_dict[k]
        tmp = fromIdGetMessage(con, k)
        if tmp is None:
            continue
        models_list.append(tmp)
        count = count+1
        if count >= 8:
            break
    # print(models_list)
    return models_list

# 根据id获取模型全部信息


def fromIdGetMessage(con, id):
    sql = "select * from model where model_ID = " + str(id) + ";"
    try:
        c = con.cursor()
        c.execute(sql)
        con.commit()
    except Exception as e:
        print(e)
    else:
        model_tuple = (c.fetchall())
        if len(model_tuple):
            return tuple2json(con, model_tuple[0])
        else:
            return None

# 将模型信息包装为JSON
def getUserModelIds(con, user):
    sql = "select * from user_product where username='{}';".format(user)
    c = con.cursor()
    c.execute(sql)
    con.commit()
    result = (c.fetchall())
    modelids = []
    for entry in result:
        modelids.append(int(entry[2]))
    return modelids

def getUserModels(con, user):
    res = []
    for id in getUserModelIds(con, user):
        tmp = fromIdGetMessage(con, id)
        if tmp is None:
            continue
        res.append(tmp)
    return res

def getModelsbyCategory(con, catelog):
    sql = "select * from model where type_name='{}' limit 8".format(catelog)
    c = con.cursor()
    c.execute(sql)
    con.commit()
    result = (c.fetchall())
    models = []
    for entry in result:
        models.append(tuple2json(con, entry))
    return models

def getModelsbyCategories(con, catelogs):
    res = {}
    for catelog in catelogs:
        res[catelog] = getModelsbyCategory(con, catelog)
    return res

def tuple2json(con, model_tuple):
    # print(model_tuple)
    model_json = {}
    model_json['url'] = '/' + model_tuple[8]
    model_json['name'] = model_tuple[1]
    model_json['publish'] = model_tuple[3]
    model_json['catalog'] = model_tuple[2]
    model_json['num_triangles'] = model_tuple[4]
    model_json['num_vertices'] = model_tuple[5]
    model_json['tags'] = fromIdGetTag(con, model_tuple[0])
    model_json['comments'] = []
    if model_tuple[6] == 0:
        model_json['animated'] = False
    else:
        model_json['animated'] = True
    model_json['owner'] = getUserData(model_tuple[7]) #model_tuple[7]
    # print(model_json)
    return(model_json)


def fromTagGetName(con, tag_name):
    sql = "select model_ID from tag where tag_name = '" + tag_name + "';"
    try:
        c = con.cursor()
        c.execute(sql)
        con.commit()
    except Exception as e:
        print(e)
    else:
        model_list = []
        for id in c.fetchall():
            tmp = fromIdGetMessage(con, id)
            if tmp is None:
                continue
            model_list.append(tmp)
        return model_list


def fromIdGetTag(con, id):
    sql = "select tag_name from tag where model_ID = " + str(id) + ";"
    try:
        c = con.cursor()
        count = c.execute(sql)
        con.commit()
    except Exception as e:
        print(e)
    else:
        tag_list = []
        for tag in count.fetchall():
            tag_list.append(tag[0])
        return tag_list


def insertTag(con, id, tag):
    if(len(isExistInTag(con, id, tag)) != 0):
        print("The tag:" + tag + " of " + str(id) + " has already exists!")
    else:
        sql = "insert into tag values(" + str(id) + ", '" + tag + "')"
        try:
            c = con.cursor()
            c.execute(sql)
            con.commit()
        except Exception as e:
            print(e)
        else:
            print("Insert " + tag + " success!")


def isExistInTag(con, id, tag):
    sql = "select * from tag where model_ID =  " + \
        str(id) + " and tag_name = '" + tag + "';"
    try:
        c = con.cursor()
        c.execute(sql)
        con.commit()
    except Exception as e:
        print(e)
    else:
        return c.fetchall()

############################################################分割线################################################
# 通过标签查询模型


def fromNameGetTag(con, model_name):
    #id = len(selectID(model_name))
    sql = "select tag_name from tag where model_name =  '" + model_name + "';"
    try:
        c = con.cursor()
        c.execute(sql)
        con.commit()
    except Exception as e:
        print(e)
    else:
        return c.fetchall()


def registerUser(form):
    #print("in function")
    print(form)
    error = False
    msg = ''
    username = form['username']
    nickname = form['nickname']
    location = form['location']
    introduction = form['introduction']
    biography = form['biography']
    email = form['email']
    avatar = form['avatar']
    if not os.path.exists("assets/avatars"):
        os.makedirs("assets/avatars")
    avatarPATH = "assets/avatars/{}.png".format(username)
    f = open(avatarPATH, 'wb')
    data = base64.b64decode(avatar)
    f.write(data)
    f.close()
    avatar = avatarPATH
    #print(str(form['password']))
    password = sha256_crypt.encrypt(str(form['password']))  # encode paassword
    db = databaseInit()
    cur = db.cursor()
    x = cur.execute(
        'SELECT * FROM user WHERE username = ?', [username])
    queryRes = x.fetchall()
    if len(queryRes) != 0:
        error = True
        msg = 'That username is already taken, please choose another'
        #flash("That username is already taken, please choose another")
        #return render_template('register.html', form=form)
    elif not re.findall('^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$',email) and not email=='':
        error = True
        msg = 'Please use the right format of the email'
    else:
        cur.execute("INSERT INTO user (username, nickname, password, location, introduction, biography, email, avatar) VALUES(?,?,?,?,?,?,?,?)", [
                    username, nickname, password, location, introduction, biography, email, avatar])
        db.commit()
        #flash("Thanks for registering!")
        cur.close()
        db.close()
        gc.collect()      # collect garbage
        msg = 'succeed in registering'
    #print(msg)
    return error, msg


def dbLogin(form):
    username = form['username']
    password = form['password']
    error = False
    msg = ""
    db = databaseInit()
    cur = db.cursor()
    passwd_hash_tuple = cur.execute('SELECT password FROM user WHERE username=?', [username]).fetchone()   # return a tuple
    if not passwd_hash_tuple:
        error=True
        msg = 'Invalid username'
    elif not (sha256_crypt.verify(str(password), passwd_hash_tuple[0])):
        error=True
        msg = 'Invalid password'
    else:
        msg='login success'
    db.commit()
    cur.close()
    db.close()
    gc.collect()           
    return error, msg


def dbUpdateAvatar(form):
    error = False
    msg = ''
    username = form['username']
    avatar = form['avatar']
    avatarPATH = "assets/avatars/{}.png".format(username)
    f = open(avatarPATH, 'wb')
    data = base64.b64decode(avatar)
    f.write(data)
    f.close()
    msg = 'succeed in updating avatar'
    return error, msg


def dbUpdatePasswd(form):
    error = False
    msg = ''
    username = form['username']

    password = sha256_crypt.encrypt(str(form['password']))  # encode paassword
    db = databaseInit()
    cur = db.cursor()
    x = cur.execute(
        'SELECT * FROM user WHERE username = ?', [username])
    queryRes = x.fetchall()
    passwd_hash_tuple = cur.execute(
        'SELECT password FROM user WHERE username=?', [username]).fetchone()
    if len(queryRes) != 0:
        error = True
        msg = 'No such user!'
    elif (sha256_crypt.verify(str(password), passwd_hash_tuple[0])):
        error = True
        msg = 'You should not use the same password'
    else:
        cur.execute("UPDATE user SET password = ? WHERE username = ?", [
                    password, username])
        db.commit()
        cur.close()
        db.close()
        gc.collect()      # collect garbage
        msg = 'succeed in updating password'
    return error, msg


def dbUpdateBasic(form):
    error = False
    msg = ''
    username = form['username']
    location = form['location']
    introduction = form['introduction']
    biography = form['biography']
    email = form['email']

    db = databaseInit()
    cur = db.cursor()
    cur.execute("UPDATE user SET location = ?, introduction = ?, biography = ?, email = ? WHERE username = ?", [
                location, introduction, biography, email, username])
    db.commit()
    cur.close()
    db.close()
    gc.collect()      # collect garbage

    if not re.findall('^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$',email) and not email=='':
        error = True
        msg = 'Please use the right format of the email'
        return error,msg
    msg = 'succeed in updating basic info'
    return error, msg


def getUserData(username):
    db = databaseInit()
    cur = db.cursor()
    x = cur.execute(
        'SELECT * FROM user WHERE username = ?', [username])
    userTuple = x.fetchall()

    u = cur.execute(
        'select model_ID,url from model where model_ID in (select modelID from user_product where username = ?)', [username])
    URL = u.fetchall()
    modelURL = []
    for each in URL:
        modelURL.append(str(each[1]))
    #print(modelURL)
    #read the avatar
    avatarPATH = "assets/avatars/{}.png".format(username)
    # f = open(avatarPATH, 'rb')
    # data=f.read()
    # avatar = base64.b64encode(data)
    # f.close()
    userJson = {}
    userJson['username'] = str(username)
    userJson['nickname'] = userTuple[0][1]
    userJson['biography'] = userTuple[0][5]
    userJson['owned_models'] = modelURL
    userJson['location'] = userTuple[0][3]
    userJson['introduction'] = userTuple[0][4]
    userJson['collections'] = ""
    userJson['email'] = userTuple[0][6]
    userJson['avatar'] = avatarPATH
    # print(userJson)
    return userJson


def databaseInit(flag=False):
    con = sqlite3.connect('database/models.db')
    if flag:
        createModelsTable(con)
        createTagTable(con)
    # model_dict = {
    #     'url': '/JSON',  #
    #     'name': 'zzpdl.gltf',   #
    #     'publish': 'time',
    #     #'comments': [],
    #     'catalog': 'Human',
    #     'num_triangles': 100,  #
    #     'num_vertices': 150,  #
    #     'tags': ['kami', 'sama'],
    #     'animated': False,   #
    #     'render_config': 'string',
    #     'owner': 'string'
    # }
    return con