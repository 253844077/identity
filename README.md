### 基于paddle的身份证识别
identity是一个基于paddle的中文身份证识别

### 安装
```shell script
conda create --name identity python=3.7 -y
```
```shell script
conda activate identity
```
```shell script
pip install -r requirement.txt -i https://mirror.baidu.com/pypi/simple --user
```
```shell script
conda install shapely -y
```
```shell script
python home.py
```

### 下载模型文件
identity-release

├──inference 

├────ch_ppocr_server_v2.0_det_infer

├────ch_ppocr_server_v2.0_rec_infer

├──home.py

...

链接：https://pan.baidu.com/s/1arP2DrjVZ0MkUavE4Fdm1g 
提取码：1342 

### 启动后的测试页面
http://localhost:8800/page

### api调用
POST form表单提交

请求
```
file_type   文件类型：file上传文件方式，url http链接的方式识别
side        正反面：front 正面，back背面
file        文件上传：如果file_type是file，则此字段必传
url         url方式：如果file_type是url，则此字段必传
```
正面响应
```json
{
    "errmsg": "success",
    "errno": 0,
    "result": {
        "birthday": "1990年11月12日",
        "gender": "女",
        "id": "42xxxxxxxxxxxxxxxxx3",
        "name": "徐无为",
        "nation": "汉"
    }
}
```
反面响应
```json
{
    "errmsg": "success",
    "errno": 0,
    "result": {
        "end_date": "2036.02.03",
        "sign": "北京中关村公安局",
        "start_date": "2016.02.03"
    }
}
```

errno错误码
```
0         参数正确进行识别
1001      file_type must be `file` or `url`.
1002      side must be `front` or `back`.
1000      other error.
1003      secret error.
```

### gpu调用
如果要使用paddlepaddle的gpu版本，可以在 https://www.paddlepaddle.org.cn/ 选择自己需要的版本。
修改Config.py文件的 `is_gpu=True`

### 配置
config.py
```
is_gpu=False            #使用gpu
rec_model_dir = "./inference/ch_ppocr_server_v2.0_rec_infer"  #文字识别模型
det_mode_dir = "./inference/ch_ppocr_server_v2.0_det_infer"   #detection模型
secret = None           #密码，None不使用密码，字符串既是密码
```