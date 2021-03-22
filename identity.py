import os
import sys
import re

import datetime

from config import Config

__dir__ = os.path.dirname(__file__)
sys.path.append(os.path.join(__dir__, ''))

from paddleocr import PaddleOCR

class Identity:
    def __init__(self):
        self.ocr_engine = PaddleOCR(use_gpu=Config.is_gpu
                               , use_angle_cls=True
                               , use_space_char=False
                               , rec_model_dir=Config.rec_model_dir
                               , det=Config.det_mode_dir)
    def front(self,path):
        result=self.ocr_engine.ocr(path,det=True,
                                rec=True,
                                cls=False)

        id=self.getId(result)
        name=self.getName(result)
        gender=self.getGender(id)
        nation=self.getNation(result)
        if nation in ["备"]:
            nation="畲"

        birthday=self.getBirthday(id)

        os.remove(path)

        return {"name":name,"gender":gender,"nation":nation,"birthday":birthday,"id":id}

    def back(self,path):
        result = self.ocr_engine.ocr(path, det=True,
                                     rec=True,
                                     cls=False)
        # for line in result:
        #     print(line)
        sign = self.getSign(result)

        (start_date,end_date)=self.getExpired(result)

        return {"sign":sign,"start_date":start_date,"end_date":end_date}

    def getExpired(self,result):
        time=None

        pos = None
        for idx in range(len(result)):
            line = result[idx]
            val = str(line[1][0])
            if not val.startswith("有效期限"):
                continue
            pos = line[0][1]
            if len(val) > 4:
                time = val[4:]
                break

        if pos is None:
            return (None,None)

        if time is None:
            min_pos = 200000000

            for line in result:
                val = str(line[1][0])
                if val.startswith("签发机关") or val.startswith("有效期限"):
                    continue

                if pos[0] > line[0][1][0]:
                    continue

                interval_pixel = abs(line[0][1][1] - pos[1])
                if interval_pixel < min_pos:
                    min_pos = interval_pixel
                    time = line[1][0]

        if time is None:
            return (None,None)

        result=time.replace("-","").replace(".","").replace("_","").replace("长期","")
        # print(result)
        if len(result)!=16 and len(result)!=8:
            return (None,None)

        if len(result)==16:
           return (result[0:4]+"."+result[4:6]+"."+result[6:8],result[8:12]+"."+result[12:14]+"."+result[14:])

        if len(result)==8:
            return (result[0:4]+"."+result[4:6]+"."+result[6:8],"长期")

        return (None,None)

    def getSign(self,result):
        pos = None
        for idx in range(len(result)):
            line = result[idx]
            val = str(line[1][0])
            if not val.startswith("签发机关"):
                continue
            pos = line[0][1]
            if len(val) > 4:
                return val[4:]

        if pos is None:
            return None

        min_pos = 200000000
        name = None
        for line in result:
            val = str(line[1][0])
            if val.startswith("签发机关") or val.startswith("有效期限"):
                continue

            if pos[0] > line[0][1][0]:
                continue

            interval_pixel = abs(line[0][1][1] - pos[1])
            if interval_pixel < min_pos:
                min_pos = interval_pixel
                name = line[1][0]
        return name

    def getName(self,result):
        pos=None
        for idx in range(len(result)):
            line=result[idx]
            val=str(line[1][0])
            if not val.startswith("姓名"):
                continue
            pos=line[0][1]
            if len(val)>2:
                return val[2:]

        if pos is None:
            return None

        min_pos=200000000
        name=None
        for line in result:
            val = str(line[1][0])
            if val.startswith("姓名") or val.startswith("性别") or val.startswith("民族") or val.startswith("住址")\
                    or val.startswith("公民身份号码"):
                continue

            if pos[0] > line[0][1][0]:
                continue

            interval_pixel=abs(line[0][1][1] - pos[1])
            if interval_pixel < min_pos:
                min_pos=interval_pixel
                name=line[1][0]
        return name

    def getGender(self,id):
        # id=self.getId(result)
        if id is None:
            return None
        if len(id)<15:
            return None

        if int(id[15]) % 2 == 1:
            return "男"
        else:
            return '女'

    def getNation(self,result):
        pos=None
        for idx in range(len(result)):
            line = result[idx]
            val = str(line[1][0])
            if not val.startswith("民族"):
                continue

            pos=line[0][1]

            if len(val) > 2:
                return val[2:]
        if pos is None:
            return None

        min_pos=200000000
        nation=None
        for line in result:
            val = str(line[1][0])
            if val.startswith("姓名") or val.startswith("性别") or val.startswith("民族") or val.startswith("住址") \
                    or val.startswith("公民身份号码"):
                continue

            if pos[0]>line[0][1][0]:
                continue

            interval_pixel=abs(line[0][1][1] - pos[1])
            if interval_pixel < min_pos:
                min_pos=interval_pixel
                nation=line[1][0]

        return nation

    def getBirthday(self,id):
        # id=self.getId(result)
        if id is None:
            return None

        year=id[6:10]
        month=id[10:12]
        day=id[12:14]

        return "%s年%d月%d日" % (year,int(month),int(day))

    def getAddress(self,result):
        pos1=None
        for line in result:
            val = str(line[1][0])
            if not val.startswith('出生'):
                continue

            pos1 = line[0][3]

        address=''

        for line in result:
            if pos1[0] > line[0][0][0]:
                continue
            if pos1[1] > line[0][0][1]:
                continue
            val = str(line[1][0])
            if re.findall("\d{15,}",val):
                continue

            address += val
        if address=='':
            return None
        return address

    def getId(self,result):
        for line in result:
            val = str(line[1][0])
            if not val.startswith("公民身份号码"):
                continue

            if len(val)>=6:
                id=str(val[6:])
                id = self.modify_id(id)
                if re.findall("\d{15,}",id):
                    if not self.check_id(id):
                        return None
                    return id

        for line in result:
            id = str(line[1][0])
            id = self.modify_id(id)
            if re.findall("\d{15,}",id):
                if not self.check_id(id):
                    return None
                return id

        return None
    def check_id(self,id):
        if len(id)<17:
            return False

        if len(id)==18:
            if not id[:-1].isdigit():
                return False

            fact = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
            sum = 0
            for i in range(17):
                sum += fact[i] * int(id[i])
            m = sum % 11
            chk = '10X98765432'
            if chk[m] != id[-1]:
                return False

        year = int(id[6:10])
        month = int(id[10:12])
        day = int(id[12:14])

        if not (year>=1890 and year<=datetime.datetime.now().year):
            return False

        if not (month>=1 and month<=12):
            return False

        if not (day>=1 and day<=31):
            return False

        return True

    def modify_id(self,id):
        id = id.replace("i", "1").replace("I", "")
        id = id.replace("z", "2").replace("Z", "2")
        id = id.replace("o", "0").replace("O", "0")
        return id.replace("x", "X")
