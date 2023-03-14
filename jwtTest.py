from flask import g, request, Flask, current_app, jsonify
from jwt import exceptions
import jwt
import functools
import datetime

app = Flask(__name__)

# 处理中文编码
app.config['JSON_AS_ASCII'] = False


# 跨域支持
def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


app.after_request(after_request)

# 构造header
headers = {
    'typ': 'jwt',
    'alg': 'HS256'
}

# 密钥
SALT = 'iv%i6xo7l8_t9bf_u!8#g#m*)*+ej@bek6)(@u3kh*42+unjv='


def create_token(username, password):
    # 构造payload
    payload = {
        'username': username,
        'password': password,  # 自定义用户ID
        # 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)  # 超时时间
    }
    # python3中Python3的str 默认不是bytes，所以不能decode，只能先encode转为bytes，再decode
    # python2的str 默认是bytes，所以能decode
    result = jwt.encode(payload=payload, key=SALT, algorithm="HS256", headers=headers)
    return result


def verify_jwt(token, secret=None):
    """
    检验jwt
    :param token: jwt
    :param secret: 密钥
    :return: dict: payload
    """
    if not secret:
        secret = current_app.config['JWT_SECRET']

    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except exceptions.ExpiredSignatureError:  # 'token已失效'
        return 1
    except jwt.DecodeError:  # 'token认证失败'
        return 2
    except jwt.InvalidTokenError:  # '非法的token'
        return 3


def login_required(f):
    '让装饰器装饰的函数属性不会变 -- name属性'
    '第1种方法,使用functools模块的wraps装饰内部函数'

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            if g.username == 1:
                return {'code': 401, 'message': 'token已失效'}, 401
            elif g.username == 2:
                return {'code': 401, 'message': 'token认证失败'}, 401
            elif g.username == 2:
                return {'code': 401, 'message': '非法的token'}, 401
            else:
                return f(*args, **kwargs)
        except BaseException as e:
            return {'code': 401, 'message': '请先登录认证.'}, 401

    '第2种方法,在返回内部函数之前,先修改wrapper的name属性'
    # wrapper.__name__ = f.__name__
    return wrapper


@app.before_request
def jwt_authentication():
    """
    1.获取请求头Authorization中的token
    2.判断是否以 Bearer开头
    3.使用jwt模块进行校验
    4.判断校验结果,成功就提取token中的载荷信息,赋值给g对象保存
    """
    _token = request.headers.get('token')
    # if auth and auth.startswith('Bearer '):
    #     "提取token 0-6 被Bearer和空格占用 取下标7以后的所有字符"
    #     token = auth[7:]
    #     "校验token"
    g.username = None
    try:
        "判断token的校验结果"
        payload = jwt.decode(_token, SALT, algorithms=['HS256'])
        "获取载荷中的信息赋值给g对象"
        g.username = payload.get('username')
    except exceptions.ExpiredSignatureError:  # 'token已失效'
        g.username = 1
    except jwt.DecodeError:  # 'token认证失败'
        g.username = 2
    except jwt.InvalidTokenError:  # '非法的token'
        g.username = 3


@app.route('/')
def hello_world():
    return "ok"


# 登录
@app.route('/api/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        type_ = data.get("type")
        if type_ == 'login':
            username = data.get("username")
            password = data.get("password")
            # 验证账号密码，正确则返回token，用于后续接口权限验证
            if username == "root" and password == "123456":
                token = create_token(username, password)
                return {"code": 200, "message": "success", "data": {"token": token}}
            else:
                return {"code": 501, "message": "登陆失败"}
        else:
            return {"code": 201, "message": "type is false"}

    elif request.method == 'GET':
        return {"code": 202, "message": "get is nothing"}
    else:
        return {"code": 203, "message": "'not support other method'"}


# 测试接口
@app.route('/api/test', methods=['GET', 'POST'])
@login_required
def submit_test_info_():
    username = g.username
    return username


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8090, debug=True)
