from flask import Flask, request, g, Flask, current_app, jsonify
from flask_sqlalchemy import SQLAlchemy
import jwtForApp
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:626626@127.0.0.1:3306/marriagesystem'
app.config["SQLALCHEMY_TRACE_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "marriage_system"
app.config['SQLALCHEMY_ECHO'] = True


# 跨域支持
def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
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
                return {"code": 200, "message": "登录成功", "data": {"token": _token}}
            else:
                return {"code": 501, "message": "密码错误"}
        else:
            return {"code": 502, "message": "用户不存在"}


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
            _add_user = CipherTable(_username, _password)
            db.session.add(_add_user)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)
            # db.session.commit()
            return {"code": 200, "message": "注册成功"}
        else:
            return {"code": 501, "message": "用户名已存在"}


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

        if _baseinfo is not None:
            """
            _baseinfo是FilterInfo类的一个实例化对象，并不能与string类型进行拼接
             XXXprint("entry" + _baseinfo)是一个错误写法XXX
             会导致BaseException，由于get_base_info是由login_required进行装饰
             所以会return code 402
            """
            return jsonify({"code": 200, "message": "请求成功", "data": _baseinfo.to_dict()})
        else:
            return {"code": 501, "message": "请先完善用户信息"}
    elif request.method == 'POST':
        return "use method GET"


# 基本资料-post向后端发送资料
@app.route('/personal/createbaseinfo', methods=['get', 'post'])
@jwtForApp.login_required
def create_base_info():
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
        return {"code": 200, "message": "基础信息完善成功"}


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
        FilterInfo.query.filter(FilterInfo.id == 3).update(_add_baseinfo.to_dict())
        db.session.commit()
        return {"code": 200, "message": "基础信息修改成功"}


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
    _filter = FilterInfo("柳非烟", "女", "本科", "北京", "江苏", "10000", "未婚", "汉族", "城市规划", "无", "无", "无")
    db.session.add(_filter)
    db.session.commit()
    print(_filter)
    return "ok"


if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', debug=True)
