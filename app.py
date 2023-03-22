from flask import Flask, request, g, Flask, current_app, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import imgUpload
from werkzeug.utils import secure_filename

import jwtForApp
import os
from os import path

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:626626@127.0.0.1:3306/marriagesystem'
app.config["SQLALCHEMY_TRACE_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "marriage_system"
app.config['SQLALCHEMY_ECHO'] = True
# app.config["BASE_DIR"] = path.abspath(path.dirname(__file__))
BASE_DIR = path.abspath(path.dirname(__file__))
app.config["MEDIA_PATH"] = path.join(BASE_DIR, "static", "img")
# 图片上传路径

"""
3.18更新状态码
"""

"""
在请求头header中设置了了自定义的token字段，所以跨域请求就认为这是一个复杂的请求，他就会先进行预校验，
也就是我们说的Options请求，等Options请求成功之后它才会进行post或者get请求，所以在发送Options请求的时候要校验请求头，
我们的后台之前的设置的是resp.setheaders(Access-Control-Allow-Headers:'*')；
前端预请求成功之后的POST请求默认带有content-type的请求头，所以要将这个也加入到验证中去，
一旦自己设置了自定义请求头那么在服务端就不能统一放行设置为*,
这样是不会通过校验的，所以如果自己有添加多个自定义的请求头那么在后端要一一列出来不能用*代替。
"""


# 跨域支持
def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = 'token,content-type'
    return resp


app.after_request(after_request)

db = SQLAlchemy(app)


# 密码表
class CipherTable(db.Model):
    __tablename__ = 'ciphertable'
    uuid = db.Column(db.Integer, primary_key=True)
    username = db.Column('username', db.String(20), unique=True)
    password = db.Column(db.Integer, index=True)

    # __table_args__ = (
    #     db.UniqueConstraint("username", name='unique_username'),
    # )

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

    # def verify_password(self, password) -> bool:
    #     if self.password == password:
    #         return True
    #     else:
    #         return False


# 展示信息表
class DisplayInfo(db.Model):
    __tablename__ = 'displayinfo'
    id = db.Column(db.Integer, primary_key=True)
    # 唯一约束需要在数据库表中设置
    username = db.Column('username', db.String(32), unique=True)
    constellation = db.Column(db.String(32))
    image = db.Column(db.String(32), unique=True)
    favorbook = db.Column(db.String(32))
    favorsong = db.Column(db.String(32))
    favormovie = db.Column(db.String(32))
    monologue = db.Column(db.String(255))
    tel = db.Column(db.String(255), unique=True)
    specialty = db.Column(db.String(32))

    def __init__(self, username, constellation, image, favorbook, favorsong, favormovie, monologue, tel, specialty):
        self.username = username
        self.constellation = constellation
        self.image = image
        self.favorbook = favorbook
        self.favorsong = favorsong
        self.favormovie = favormovie
        self.monologue = monologue
        self.tel = tel
        self.specialty = specialty

    def __repr__(self):
        return '<tel %r>' % self.tel

    def to_dict(self):
        return {
            "username": self.username,
            "constellation": self.constellation,
            # "image": self.image,
            "favorbook": self.favorbook,
            "favorsong": self.favorsong,
            "favormovie": self.favormovie,
            "monologue": self.monologue,
            "tel": self.tel,
            "specialty": self.specialty,
        }


# 筛选信息表
class FilterInfo(db.Model):
    __tablename__ = 'filterinfo'
    id = db.Column(db.Integer, primary_key=True)
    # 唯一约束需要在数据库表中设置
    username = db.Column('username', db.String(32), unique=True)
    gender = db.Column(db.String(32))
    edubackground = db.Column(db.String(32))
    workprovince = db.Column(db.String(32))
    nativeprovince = db.Column(db.String(32))
    salary = db.Column(db.String(32))
    marital = db.Column(db.String(32))
    nationality = db.Column(db.String(32))
    occupation = db.Column(db.String(32))
    houseornot = db.Column(db.String(32))
    carornot = db.Column(db.String(32))
    drinkornot = db.Column(db.String(32))

    def __init__(self, username, gender, edubackground, workprovince, nativeprovince, salary, marital, nationality,
                 occupation, houseornot, carornot, drinkornot):
        self.username = username
        self.gender = gender
        self.edubackground = edubackground
        self.workprovince = workprovince
        self.nativeprovince = nativeprovince
        self.salary = salary
        self.marital = marital
        self.nationality = nationality
        self.occupation = occupation
        self.houseornot = houseornot
        self.carornot = carornot
        self.drinkornot = drinkornot

    def __repr__(self):
        return '<nationality %r>' % self.gender

    # 对数据模型添加处理方法to_dict，模型字段处理成list，将查询结果直接引用该方法
    def to_dict(self):
        return {
            "username": self.username,
            "gender": self.gender,
            "edubackground": self.edubackground,
            "workprovince": self.workprovince,
            "nativeprovince": self.nativeprovince,
            "salary": self.salary,
            "marital": self.marital,
            "nationality": self.nationality,
            "occupation": self.occupation,
            "houseornot": self.houseornot,
            "carornot": self.carornot,
            "drinkornot": self.drinkornot,
        }


# 择偶条件表
# 择偶条件表也需要在密码表生成列时同时生成
class MatingCondition(db.Model):
    __tablename__ = 'matingcondition'
    id = db.Column(db.Integer, primary_key=True)
    # 唯一约束需要在数据库表中设置
    username = db.Column('username', db.String(32), unique=True)
    gender = db.Column(db.String(32))
    edubackground = db.Column(db.String(32))
    workprovince = db.Column(db.String(32))
    nativeprovince = db.Column(db.String(32))
    salary = db.Column(db.String(32))
    marital = db.Column(db.String(32))
    nationality = db.Column(db.String(32))
    occupation = db.Column(db.String(32))
    houseornot = db.Column(db.String(32))
    carornot = db.Column(db.String(32))
    drinkornot = db.Column(db.String(32))

    def __init__(self, username, gender, edubackground, workprovince, nativeprovince, salary, marital, nationality,
                 occupation, houseornot, carornot, drinkornot):
        self.username = username
        self.gender = gender
        self.edubackground = edubackground
        self.workprovince = workprovince
        self.nativeprovince = nativeprovince
        self.salary = salary
        self.marital = marital
        self.nationality = nationality
        self.occupation = occupation
        self.houseornot = houseornot
        self.carornot = carornot
        self.drinkornot = drinkornot

    def __repr__(self):
        return '<gender %r>' % self.gender

    def to_dict(self):
        return {
            "username": self.username,
            "gender": self.gender,
            "edubackground": self.edubackground,
            "workprovince": self.workprovince,
            "nativeprovince": self.nativeprovince,
            "salary": self.salary,
            "marital": self.marital,
            "nationality": self.nationality,
            "occupation": self.occupation,
            "houseornot": self.houseornot,
            "carornot": self.carornot,
            "drinkornot": self.drinkornot,
        }


# 装饰器-在处理请求之前验证token
@app.before_request
def authentication():
    jwtForApp.jwt_authentication()


# 登录
@app.route('/login', methods=['get', 'post'])
def login():  # put application's code here

    # cipher1 = CipherTable('周行云', 232523)
    # db.session.add(cipher1)
    # db.session.commit()
    if request.method == 'GET':  # 请求方式是get
        return "use method POST"
    elif request.method == 'POST':
        _username = request.form.get('username', type=str)  # form取post方式参数
        _password = request.form.get('password', type=str)

        # print(_username, _password)

        _user = CipherTable.query.filter_by(username=_username).first()
        if _user is not None:
            if _user.password == _password:
                _token = jwtForApp.create_token(_username, _password)
                return {"code": 6200, "message": "登录成功", "data": {"token": _token}}
            else:
                return {"code": 6501, "message": "密码错误"}
        else:
            return {"code": 6502, "message": "用户不存在"}


# 注册
@app.route('/signup', methods=['get', 'post'])
def sign_up():
    if request.method == 'GET':  # 请求方式是get
        return "use method POST"
    elif request.method == 'POST':
        _username = request.form.get('username', type=str)  # form取post方式参数
        _password = request.form.get('password', type=str)

        _user = CipherTable.query.filter_by(username=_username).first()
        # 添加新用户
        if _user is None:
            """
            注册成功时在所有包含username的表建立默认行
            之后的提交数据改用update方法更新数据即可
            设置用户初始头像为默认头像default.png
            """

            _add_user = CipherTable(_username, _password)
            _add_baseinfo = FilterInfo(_username, "_gender", "_edubackground", "_workprovince", "_nativeprovince",
                                       "_salary",
                                       "_marital", "_nationality", "_occupation", "_houseornot", "_carornot",
                                       "_drinkornot")
            _add_displayinfo = DisplayInfo(_username, "_constellation", "default.png", "_favorbook", "_favorsong",
                                           "_favormovie", "_monologue", "_tel", "_specialty")
            _add_matingcondition = MatingCondition(_username, "_gender", "_edubackground", "_workprovince",
                                                   "_nativeprovince",
                                                   "_salary",
                                                   "_marital", "_nationality", "_occupation", "_houseornot",
                                                   "_carornot",
                                                   "_drinkornot")
            db.session.add(_add_user)
            db.session.add(_add_baseinfo)
            db.session.add(_add_displayinfo)
            db.session.add(_add_matingcondition)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)
            # db.session.commit()
            return {"code": 6200, "message": "注册成功"}
        else:
            return {"code": 6501, "message": "用户名已存在"}


# ##个人中心

# 基本资料-get获取后端资料
@app.route('/personal/getbaseinfo', methods=['get', 'post'])
@jwtForApp.login_required
def get_base_info():
    if request.method == 'GET':  # 请求方式是get
        """
        _name = request.args.get('name')  # args取get方式参数
        _hobby = request.args.getlist('hobby')  # getlist取一键多值类型的参数
        """

        # username从token中解析出来，不需要从前端加参数
        _username = g.username
        # print("out out" + _username)
        """
        方式1: 等值过滤器 关键字实参设置字段值  返回BaseQuery对象
        User.query.filter_by(id=4).all()

        方式2: 复杂过滤器  参数为比较运算/函数引用等  返回BaseQuery对象
        User.query.filter(User.id == 4).first()
        """

        # 等值过滤器filter_by
        _baseinfo = FilterInfo.query.filter(FilterInfo.username == _username).first()

        if _baseinfo.gender != "_gender":
            """
            _baseinfo是FilterInfo类的一个实例化对象，并不能与string类型进行拼接
             XXXprint("entry" + _baseinfo)是一个错误写法XXX
             会导致BaseException，由于get_base_info是由login_required进行装饰
             所以会return code 402
            """
            return jsonify({"code": 6200, "message": "请求成功", "data": _baseinfo.to_dict()})
        else:
            return {"code": 6501, "message": "请先完善用户信息"}
    elif request.method == 'POST':
        return "use method GET"


# 基本资料-post向后端发送资料
@app.route('/personal/createbaseinfo', methods=['get', 'post'])
@jwtForApp.login_required
def create_base_info():
    """
    XXXXXXXXXXX 3.19更新注册时创建默认行后便不再使用此接口 XXXXXXXXXXXXXXX
    """
    if request.method == 'GET':
        return "use method post"
    elif request.method == 'POST':
        # 前端调用该接口即在无详细信息的情况下，故无需判断是否存在重复用户名
        # username从token中解析出来，不需要从前端加参数
        _username = g.username
        _gender = request.form.get('gender', type=str)
        _edubackground = request.form.get('edubackground', type=str)
        _workprovince = request.form.get('workprovince', type=str)
        _nativeprovince = request.form.get('nativeprovince', type=str)
        _salary = request.form.get('salary', type=str)
        _marital = request.form.get('marital', type=str)
        _nationality = request.form.get('nationality', type=str)
        _occupation = request.form.get('occupation', type=str)
        _houseornot = request.form.get('houseornot', type=str)
        _carornot = request.form.get('carornot', type=str)
        _drinkornot = request.form.get('drinkornot', type=str)

        _add_baseinfo = FilterInfo(_username, _gender, _edubackground, _workprovince, _nativeprovince, _salary,
                                   _marital, _nationality, _occupation, _houseornot, _carornot, _drinkornot)
        db.session.add(_add_baseinfo)
        db.session.commit()
        return {"code": 6200, "message": "基础信息完善成功"}


# 基本资料-post更新基本资料
@app.route('/personal/updatebaseinfo', methods=['get', 'post'])
@jwtForApp.login_required
def update_base_info():
    if request.method == 'GET':
        return "use method post"
    elif request.method == 'POST':
        _username = g.username
        _gender = request.form.get('gender', type=str)
        _edubackground = request.form.get('edubackground', type=str)
        _workprovince = request.form.get('workprovince', type=str)
        _nativeprovince = request.form.get('nativeprovince', type=str)
        _salary = request.form.get('salary', type=str)
        _marital = request.form.get('marital', type=str)
        _nationality = request.form.get('nationality', type=str)
        _occupation = request.form.get('occupation', type=str)
        _houseornot = request.form.get('houseornot', type=str)
        _carornot = request.form.get('carornot', type=str)
        _drinkornot = request.form.get('drinkornot', type=str)

        _add_baseinfo = FilterInfo(_username, _gender, _edubackground, _workprovince, _nativeprovince, _salary,
                                   _marital, _nationality, _occupation, _houseornot, _carornot, _drinkornot)

        # 应用模型对象转换为list的函数整体更新
        FilterInfo.query.filter(FilterInfo.username == _username).update(_add_baseinfo.to_dict())
        db.session.commit()
        return {"code": 6200, "message": "基础信息修改成功"}


# 基本资料-上传单个图片（头像）
@app.route('/personal/imgupload', methods=['post'])
@jwtForApp.login_required
def img_upload():
    _username = g.username
    _file = request.files.get("file")

    # 在更新之前删除原来头像

    # 保存图片的同时返回唯一文件名
    filename = imgUpload.img_upload(_file)
    # print(filename)

    DisplayInfo.query.filter(DisplayInfo.username == _username).update({'image': filename})
    db.session.commit()
    return {"code": 6200, "message": _file.filename + " √"}


# 基本资料-获取单个图片（头像）
"""
3.20取消getimg的token验证，改变为根据用户名进行查询的接口，
用于用户获取自己的头像以及其他用户获取该用户的头像
"""


@app.route('/personal/imgget', methods=['get'])
# @jwtForApp.login_required
def img_get():
    # _username = g.username
    _username = request.args.get("username")
    # print(_username)
    # print(type(_username))
    # 从配置文件中读出文件储存路径
    _media_path = current_app.config['MEDIA_PATH']

    # 根据用户名查找对应头像（文件名）
    display_info = DisplayInfo.query.filter(DisplayInfo.username == _username).first()
    # print(type(display_info.image))
    if display_info is not None:
        _img_filename = display_info.image

        # 拼接图片路径
        _img_path = path.join(_media_path, _img_filename)

        # 按照二进制方式打开文件，读到的内容为二进制文件流
        try:
            with open(_img_path, 'rb') as bfile:
                bimg = bfile.read()
        except FileNotFoundError:
            return None, 404
        resp = make_response(bimg)
        resp.headers['Content-Type'] = 'image/png'
        # resp.headers['response-Type'] = 'blob'
        return resp
    else:
        return {"code": 6501, "message": "用户不存在"}


# 详细资料-get获取后端资料
@app.route('/personal/getdisplayinfo', methods=['get'])
@jwtForApp.login_required
def get_display_info():
    _username = g.username
    _display_info = DisplayInfo.query.filter(DisplayInfo.username == _username).first()

    if _display_info.constellation != "_constellation":
        return jsonify({"code": 6200, "message": "请求成功", "data": _display_info.to_dict()})
    else:
        return {"code": 6501, "message": "请先完善详细信息"}


# 详细资料-更新后端资料
@app.route('/personal/updatedisplayinfo', methods=['post'])
@jwtForApp.login_required
def update_display_info():
    _username = g.username
    _constellation = request.form.get('constellation', type=str)
    # _image调用其他接口
    _favorbook = request.form.get('favorbook', type=str)
    _favorsong = request.form.get('favorsong', type=str)
    _favormovie = request.form.get('favormovie', type=str)
    _monologue = request.form.get('monologue', type=str)
    _tel = request.form.get('tel', type=str)
    _specialty = request.form.get('specialty', type=str)
    # 先将image取出来，同新数据一同放入新的对象
    _image_object = DisplayInfo.query.filter(DisplayInfo.username == _username).first()

    _display_info = DisplayInfo(_username, _constellation, _image_object.image, _favorbook, _favorsong, _favormovie,
                                _monologue, _tel,
                                _specialty)
    DisplayInfo.query.filter(DisplayInfo.username == _username).update(_display_info.to_dict())
    db.session.commit()
    if _display_info.constellation != "_constellation":
        return jsonify({"code": 6200, "message": "详细信息更新成功"})
    else:
        return {"code": 6501, "message": "详细信息不完整"}


# 择偶条件-get获取后端资料
@app.route('/personal/getmatingcondition', methods=['get'])
@jwtForApp.login_required
def get_mating_condition():
    _username = g.username
    _mating_condition = MatingCondition.query.filter(MatingCondition.username == _username).first()
    if _mating_condition.gender != "_gender":
        return jsonify({"code": 6200, "message": "请求成功", "data": _mating_condition.to_dict()})
    else:
        return {"code": 6501, "message": "请先完善择偶条件"}


# 择偶条件-更新后端资料
@app.route('/personal/updatematingcondition', methods=['post'])
@jwtForApp.login_required
def update_mating_condition():
    _username = g.username
    _gender = request.form.get('gender', type=str)
    _edubackground = request.form.get('edubackground', type=str)
    _workprovince = request.form.get('workprovince', type=str)
    _nativeprovince = request.form.get('nativeprovince', type=str)
    _salary = request.form.get('salary', type=str)
    _marital = request.form.get('marital', type=str)
    _nationality = request.form.get('nationality', type=str)
    _occupation = request.form.get('occupation', type=str)
    _houseornot = request.form.get('houseornot', type=str)
    _carornot = request.form.get('carornot', type=str)
    _drinkornot = request.form.get('drinkornot', type=str)

    _add_matingcondition = MatingCondition(_username, _gender, _edubackground, _workprovince, _nativeprovince, _salary,
                                           _marital, _nationality, _occupation, _houseornot, _carornot, _drinkornot)

    # 应用模型对象转换为list的函数整体更新
    MatingCondition.query.filter(MatingCondition.username == _username).update(_add_matingcondition.to_dict())
    db.session.commit()
    return {"code": 6200, "message": "基础信息修改成功"}


@app.route('/imgtest', methods=['post'])
def img_test():
    import base64
    file = request.files.get("file")

    # print(request.files['file'])
    # print(file.filename)
    # basepath = path.abspath(path.dirname(__file__))
    # upload_path = path.join(basepath, 'static', 'uploads', file.filename)
    # file.save(upload_path)
    filename = imgUpload.img_upload(file)
    print(filename)
    # DisplayInfo.query.filter(DisplayInfo.username == _username).update({'image': filename})
    return {"code": 6200, "message": filename}


# 在需要登陆权限的页面启用token验证-login_requried
@app.route('/main', methods=['get', 'post'])
@jwtForApp.login_required
def main():
    # 利用g（globle）可以取出login_required中从token中解析出来的username
    username = g.username
    return username


# 测试新建模型类与mysql的链接
@app.route('/testsql', methods=['get', 'post'])
def testsql():
    # display = DisplayInfo("柳非烟", "双鱼", "../..", "巴黎圣母院", "难忘今宵", "《肖申克的救赎》", "独白", "13533353335","唱歌")
    # _filter = FilterInfo("柳非烟", "女", "本科", "北京", "江苏", "10000", "未婚", "汉族", "城市规划", "无", "无", "无")
    _mating = MatingCondition("杨过", "男", "本科", "北京", "江苏", "10000", "未婚", "汉族", "城市规划", "无", "无",
                              "无")
    db.session.add(_mating)
    db.session.commit()
    print(_mating)
    return "ok"


if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', debug=True)
