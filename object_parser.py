#! /usr/bin/python3
# -*- coding: utf-8 -*-
# import underthesea
import re
import mysql.connector
# from underthesea import ner

f = open('out.txt', 'w+', encoding='utf-8')

FEMALE = [r"(n|N)ữ"]
MALE = [r"(n|N)am", "nam giới"]
AGE = [r"[0-9]{1,3}\s{1,6}tuổi"]
BN_RANGE = [r"CA BỆNH\s{1,6}[0-9]{1,4} - [0-9]{1,4}",
        r"Bệnh nhân\s[0-9]{1,4} - [0-9]{1,4}",
         r"Bệnh nhân số\s{1,6}[0-9]{1,4} - [0-9]{1,4}"
       ]
BNre = [r"CA BỆNH\s{0,2}[0-9]{1,4}",
        r"bệnh nhân\s[0-9]{1,4}",
        r"bệnh nhân số\s{1,6}[0-9]{1,4}",
          r"BN\s{0,2}[0-9]{1,4}"
       ]
FLIGHT_RE= [r"(c|C)huyến bay\s{0,6}[A-Z]{1,4}\s?[0-9]{2,8}"]
NATIONLATY_RE = ["quốc tịch(.{0,1}[A-Z]\w{1,7}){1,3}",
                "quốc tịch(.{0,1}\w{1,7}){1,3}",
                "công dân(.{0,1}[A-Z]\w{1,7}){1,3}",
                "công dân(.{0,1}\w{1,7}){1,3}",
                ]
ORIGIN = [r"(địa chỉ|trú|quê) (tại|ở)?(\s(phường|quận|thị xã|thị trấn|tỉnh|thành phố)?(\s?\w{1,20}){1,3})"]

NUMBERSIT = ["số ghế [0-9]{1,8}[A-Z]{1,4}\s?"]
flags=re.I|re.U
DEATH = [r"(đã)?\s{0,3}(chết|khuất|ngoẻo|tử vong|mất)"
]
NEGATIVE_COVID = [r"(đã)?\s{0,3}(khỏi bệnh)"
]

def getStatus(text):
    for i in NEGATIVE_COVID:
        result = re.search(i, text,flags)
    if result:
        return "negative"
    for i in DEATH:
        result = re.search(i, text,flags)
    if result:
        return "death"
    return None

def getSex(text):
    for i in FEMALE:
        result = re.search(i, text)
        if result:
            return "female"
    for i in MALE:
        result = re.search(i, text)
        if result:
            return "male"
    return None

def getAge(text):

    for i in AGE:
        result = re.search(i, text)
        if result:
            return re.findall(i, text)[0]
    return None

def BNrange(text):

    BNids = None
    for i in BN_RANGE:
        result = re.search(i, text)
        if result:
            BNids = re.findall(i, text)[0]
            ids = re.findall(r"[0-9]{1,4}", BNids)
            return(ids)
            break
        return None
# lấy id của các của bệnh nhân
def getBNid(text):
    BNs=[]
    for i in BNre:
        result = re.search(i, text)
        if result:
            text_include = re.findall(i, text)
            for bn in text_include:
                BNs.append(re.findall(r"[0-9]{1,4}", bn)[0])
    return ["BN"+BNid for BNid in BNs]

# chuyển file text thành định dạng BN và thành phố
def preprocessIDBN(text):
    BNs=[]
    for i in BNre:
        result = re.search(i, text)
        if result:
            text_include = re.findall(i, text)
            for bn in text_include:
                text = text.replace(bn,"BN"+str(re.findall(r"[0-9]{1,4}", bn)[0]))

    text = text.replace("TP. ", "thành phố ")
    return text

# tách đoạn văn thành các đoạn sau dấu chấm và dấu chấm phẩy
def seperateSentences(text):
    sentences = []
    for sentence in text.split('.'):
        sentences += sentence.split(";")
    return sentences
#Lấy mối quan hệ của các bệnh nhân
def getRelation(text):
    BNids = getBNid(text)
    # for BNid in BNids:
        # neo4j.createBN(BNid,None, None, None, None, None, None, None, None)
    if len(BNids) < 2:
        return
    BNid_main = BNids[0]

    for sentence in seperateSentences(text):
        if len(sentence) < 4:
            continue
        BNids = getBNid(sentence)
        if len(BNids) < 2:
            continue
        else:
            for i in range(len(BNids)-1):
                BNid1 = BNids[i]
                BNid2 = BNids[i+1]
                if BNid1 == BNid2:
                    continue
                else:
                    sub = text[text.rfind(BNid1)+len(BNid1):text.find(BNid2)]
                    print(sub)
                    f.write("\n"+sub)
                    if "," in sub:
                        BNid1 = BNid_main
                    else:
                        BNid_main = BNid1
                    relation = sub[sub.rfind(",")+1:]
                    if relation == None:
                        relation = sub[sub.rfind("(")+1:]
                    if relation == None:
                        relation = sub
                    print("Relation:",BNid1, relation, BNid2)
                    f.write("\nRelation: "+BNid1)
                    f.write(relation)
                    f.write(BNid2)
                    # neo4j.createConnect(BNid1, relation, BNid2)

#Lấy quốc tịch của bệnh nhân
def getNationlaty(text):
    for i in NATIONLATY_RE:
        result = re.search(i, text, flags)
        if result:
            match_obj_country = re.search("([A-Z]\w{1,7}.{0,1}){1,4}",result.group(0))
            if match_obj_country:
                return match_obj_country.group(0)
            else:
                return result.group(0)
#Lấy thông tin về địa chỉ của bệnh nhân
def getOrigin(text):
    for i in ORIGIN:
        result = re.search(i, text, flags)
        if result:
            return result.group(0)
#Thông tin về chuyến bay
def getFlight(text):
    for i in FLIGHT_RE:
        result = re.search(i, text)
        if result:
            return result.group(0)
    return None
#Thông tin về số ghế
def getNumberSit(text):
    for i in NUMBERSIT:
        result = re.search(i, text)
        if result:
            return result.group(0)
    return None
#Tách các thực thể 
def process(text, date=None):
    BNid_main = None
    for sentence in seperateSentences(text):
        f.write("\n")
        f.writelines("#"*32)
        print("#"*32)
        f.write("\nSentences: "+sentence)
        print("Sentences:",sentence)
        #Lấy id của bệnh nhân
        BNids = getBNid(sentence)
        if len(BNids) != 0:
            BNid_main = BNids[0]
            # in ra mã bệnh nhân
        if BNid_main:
            f.write("\n"+BNid_main)
            print(BNid_main)
        if date:
            f.write("\n")
            f.write(date)
            # neo4j.updateBN(BNid_main, "date", date)
        sex = getSex(sentence)
        if sex != None:
            f.write("\nSex:"+sex)

            # neo4j.updateBN(BNid_main, "sex", sex)
            print("Sex:",sex)
        age = getAge(sentence)
        if age != None:
            # neo4j.updateBN(BNid_main, "age", age)
            f.write("\n Age:" +age)
            print("Age:",age)
        flight = getFlight(sentence)
        if flight != None:
            f.write("\n Flight:"+flight)
            # neo4j.createTranspotation(BNid_main, flight)
            print("Flight:",flight)
            numbersit = getNumberSit(sentence)
            if numbersit != None:
                f.write("\n Numbersit:"+numbersit)
                # neo4j.updateBN(BNid_main, "number_sit", numbersit)
                print("Numbersit:",numbersit)
                # neo4j.createConnectPTVT(BNid_main, numbersit, flight)
        nationlaty = getNationlaty(sentence)
        if nationlaty != None:
            f.write("\n Nation:"+nationlaty)
            # neo4j.updateBN(BNid_main, "nationlaty", nationlaty)
            print("Nation:",nationlaty)
        origin = getOrigin(sentence)
        if origin != None:
            f.write("\nOrigin:"+origin)
            # neo4j.updateBN(BNid_main, "origin", origin)
            print("Origin:",origin)
        status = getStatus(sentence)
        if status != None:
            f.write("\n Status: "+status)
            # neo4j.updateBN(BNid_main, "status", status)
            print("Status:",status)

def getObject(text, date=None):
    try:
        #chuyển về đúng định dạng câu văn
        text = preprocessIDBN(text)
        #Xem xét các quan hệ của bệnh nhân
        # getRelation(text)
        #Lấy các thông tin của bệnh nhân
        process(text, date)
    except Exception as e:
        print("Error: ",e)

if __name__ == '__main__':
#     text = """ 
 
# - CA BỆNH 2825  ghi nhận tại Thành phố Đà Nẵng: Bệnh nhân nam, 37 tuổi, công dân VN, địa chỉ tại quận Hoàng Mai, Thành phố Hà Nội. Ngày 08/4/2021, bệnh nhân từ Nhật Bản nhập cảnh Sân bay Quốc tế Đà Nẵng trên chuyến bay VJ8679 và được cách ly ngay sau khi nhập cảnh tại Thành phố Đà Nẵng. Kết quả xét nghiệm ngày 22/4/2021 dương tính với SARS-CoV-2. Hiện bệnh nhân được cách ly, điều trị tại Bệnh viện Phổi Đà Nẵng.
 
# - CA BỆNH 2826 (BN2826) ghi nhận tại tỉnh Bà Rịa - Vũng Tàu: Bệnh nhân nam, 50 tuổi, quốc tịch Philippnes, là thuyền viên trên tàu di chuyển từ Trung Quốc đến tỉnh Bà Rịa - Vũng Tàu ngày 18/4/2021. Đây là trường hợp được cách ly ngay trên tàu tại khu vực neo đậu Cảng vụ hàng hải Vũng Tàu. Kết quả xét nghiệm ngày 22/4/2021 dương tính với SARS-CoV-2. Hiện bệnh nhân được cách ly, điều trị tại Trung tâm Y tế huyện Long Điền.
 
# - CA BỆNH 2827 (BN2827) ghi nhận tại tỉnh Khánh Hòa: Bệnh nhân nam, 37 tuổi, quốc tịch Ấn Độ, là chuyên gia. Bệnh nhân từ Ấn Độ quá cảnh Dubai, Hàn Quốc, sau đó nhập cảnh Sân bay Cam Ranh trên chuyến bay OZ773 ngày 20/4/2021 và được cách ly ngay sau khi nhập cảnh tại tỉnh Khánh Hòa. Kết quả xét nghiệm ngày 22/4/2021 dương tính với SARS-CoV-2. Hiện bệnh nhân được cách ly, điều trị tại Bệnh viện Bệnh nhiệt đới tỉnh Khánh Hòa.
 
# - CA BỆNH 2828 (BN2828) ghi nhận tại tỉnh An Giang: Bệnh nhân nam, 23 tuổi, công dân Việt Nam, địa chỉ tại huyện An Phú, tỉnh An giang. Ngày 20/4/2021 bệnh nhân trên từ nước ngoài nhập cảnh tại Cửa khẩu Long Bình và được cách ly ngay sau khi nhập cảnh tại tỉnh An Giang. Kết quả xét nghiệm ngày 22/4/2021 dương tính với SARS-CoV-2. Hiện bệnh nhân được cách ly, điều trị tại Trung tâm y tế huyện An Phú, tỉnh An Giang.
 
# - CA BỆNH 2829 (BN2829) ghi nhận tại tỉnh Khánh Hòa: Bệnh nhân nữ, 23 tuổi, công dân Việt Nam, địa chỉ tại huyện Long Điền, tỉnh Bà Rịa - Vũng Tàu. Bệnh nhân từ Nga nhập cảnh Sân bay Cam Ranh trên chuyến bay VN62 ngày 18/4/2021 và được cách ly ngay sau khi nhập cảnh tại tỉnh Khánh Hòa. Kết quả xét nghiệm ngày 22/4/2021 dương tính với SARS-CoV-2. Hiện bệnh nhân được cách ly, điều trị tại Bệnh viện Bệnh nhiệt đới tỉnh Khánh Hòa.
 
# - CA BỆNH 2830 (BN2830) ghi nhận tại Thành phố Hồ Chí Minh: Bệnh nhân nữ, 27 tuổi, công dân Việt Nam, địa chỉ tại quận Hoàn Kiếm, Thành phố Hà Nội. Ngày 21/4/2021, bệnh nhân từ Nhật Bản nhập cảnh Sân bay Tân Sơn Nhất trên chuyến bay JL759 và được cách ly ngay sau khi nhập cảnh tại Thành phố Hồ Chí Minh. Kết quả xét nghiệm ngày 22/4/2021 dương tính với SARS-CoV-2. Hiện bệnh nhân được cách ly, điều trị tại Bệnh viện Dã chiến Củ Chi.
# """
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="linhchi",
        charset='utf8',
        port = 3306, 
        database='scrapy'
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT title,content,date,time FROM content ")
    myresult = mycursor.fetchall()
    for x in myresult:
        getObject(x[1])
    # getObject(text)
    f.close()