import os
import random
import tempfile

from flask import Flask, request, render_template
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename

from config import Config
from identity import Identity
from identity_form import IdentityForm

import requests

app = Flask(__name__)
app.config["SECRET_KEY"] = "ADn4fgcR1o89tpKRnfuIVRmQUHBsBkRKMpcC8EqAkNkilnDZ42HlNj"
# app.config['UPLOAD_FOLDER'] = "/tmp"
identitier=Identity()

@app.route("/page")
def page():
    return render_template('page.html')

@app.route("/identity",methods=['GET','POST'])
def identity():
    form = IdentityForm(CombinedMultiDict([request.form, request.files]))

    if Config.secret is not None and Config.secret!=form.secret:
        return {'errno': 1003, 'errmsg': 'secret error.'}

    file_type=form.file_type.data
    side = form.side.data
    file = form.file.data
    url = form.url.data

    if file_type not in ['file','url']:
        return {'errno': 1001, 'errmsg': 'file_type must be `file` or `url`.'}

    if side not in ['front','back']:
        return {'errno': 1002, 'errmsg': 'side must be `front` or `back`.'}

    tmpdir = tempfile.gettempdir()

    if file_type == 'url':
        if url.lower().startswith("http"):
            if url.lower().endswith(".png"):
                ext = "png"
            elif url.lower().endswith(".jpeg") or url.lower().endswith(".jpg"):
                ext = "jpg"
            else:
                return {'errno': 1004, 'errmsg': 'not support image type.'}
            filename = generate_random_str(24) + "." + ext
            file_path = os.path.join(tmpdir, filename)

            res = requests.get(url)
            with open(file_path, "wb") as f:
                f.write(res.content)
        else:
            file_path = url
    else:
        filename = secure_filename(file.filename)
        file_path = os.path.join(tmpdir, filename)
        file.save(file_path)

    try:
        if side == 'front':
            return {"errno":0,"errmsg":"success","result":identitier.front(file_path)}
        elif side == 'back':
            return {"errno":0,"errmsg":"success","result":identitier.back(file_path)}
    except:
        return {'errno': 1005, 'errmsg':'identification error.'}

    return {'errno': 1000, 'errmsg':'other error.'}

def generate_random_str(randomlength=16):
  """
  生成一个指定长度的随机字符串
  """
  random_str = ''
  base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
  length = len(base_str) - 1
  for i in range(randomlength):
    random_str += base_str[random.randint(0, length)]
  return random_str

# if __name__ == '__main__':
#     app.run(port=8800)