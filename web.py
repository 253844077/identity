import os
import tempfile

from flask import Flask, request, render_template
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename

from config import Config
from identity import Identity
from identity_form import IdentityForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "ADn4fgcR1o89tpKRnfuIVRmQUHBsBkRKMpcC8EqAkNkilnDZ42HlNj"
app.config['UPLOAD_FOLDER'] = "/tmp"
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

    if side == 'front':
        if file_type=='url':
            return {"errno":0,"errmsg":"success","result":identitier.front(url)}
        else:
            tmpdir = tempfile.gettempdir()
            filename=secure_filename(file.filename)
            file_path = os.path.join(tmpdir, filename)
            file.save(file_path)
            return {"errno":0,"errmsg":"success","result":identitier.front(file_path)}
    elif side == 'back':
        if file_type == 'url':
            return {"errno":0,"errmsg":"success","result":identitier.back(url)}
        else:
            tmpdir = tempfile.gettempdir()
            filename = secure_filename(file.filename)
            file_path = os.path.join(tmpdir, filename)
            file.save(file_path)
            return {"errno":0,"errmsg":"success","result":identitier.back(file_path)}

    return {'errno': 1000, 'errmsg':'other error.'}

# if __name__ == '__main__':
#     app.run(port=8800)