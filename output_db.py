  
#! /usr/bin/python3
# -*- coding: utf-8 -*-

# import underthesea
import re

import mysql.connector
# from . import neo4j_util as neo4j
# import neo4j_util as 
f = open('test.txt', 'w+', encoding='utf-8')
FEMALE = [r"(n|N)ữ",
          r"(n|N)ữ" ]
MALE = [r"(n|N)am", "nam giới"]
AGE = [r"[0-9]{1,3}\s{1,6}(tuổi|tuổi)"]
BN_RANGE = [r"CA BỆNH\s{1,6}[0-9]{1,3} - [0-9]{1,3}",
        r"Bệnh nhân\s[0-9]{1,3} - [0-9]{1,3}",
         r"Bệnh nhân số\s{1,6}[0-9]{1,3} - [0-9]{1,3}",
         r"CA BỆNH\s{1,6}[0-9]{1,3} - [0-9]{1,3}",
         r"Bệnh nhân \s[0-9]{1,3} - [0-9]{1,3}",
         r"Bệnh nhân số\s{1,6}[0-9]{1,3} - [0-9]{1,3}",
       ]
BNre = [r"CA BỆNH\s{0,2}[0-9]{1,4}",
        r"Bệnh nhân\s[0-9]{1,4}",
        r"Bệnh nhân số\s{1,6}[0-9]{1,4}",
        r"BN\s{0,2}[0-9]{1,4}",
        r"CA BỆNH\s{0,2}[0-9]{1,4}",
        r"bệnh nhân\s[0-9]{1,4}"

       ]
FLIGHT_RE= [r"(c|C)huyến bay\s{0,6}[A-Z]{1,4}\s?[0-9]{2,8}"]
NATIONLATY_RE = ["quốc tịch(.{0,1}[A-Z]\w{1,7}){1,3}",
                "quốc tịch(.{0,1}\w{1,7}){1,3}",
                "công dân(.{0,1}[A-Z]\w{1,7}){1,3}",
                "công dân(.{0,1}\w{1,7}){1,3}",
                ]
ORIGIN = [r"(địa\s{1,2}chỉ|trú)\s{1,2}(tại|ở)\s{1,2}(\s|\w|,|TP.)*([A-Z]\w{1,})",
r"(địa chỉ|trú|quê) (tại|ở)?(\s(phường|quận|thị xã|thị trấn|tỉnh|Thành phố)?(\s?\w{1,4}){1,3})"]
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
        result = re.search(i, text,flags)
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

def getBNid(text):
    BNs=[]
    for i in BNre:
        result = re.search(i, text)
        if result:
            text_include = re.findall(i, text)
            for bn in text_include:
                BNs.append(re.findall(r"[0-9]{1,3}", bn)[0])
    return ["BN"+BNid for BNid in BNs]


def preprocessIDBN(text):
    BNs=[]
    for i in BNre:
        result = re.search(i, text)
        if result:
            text_include = re.findall(i, text)
            for bn in text_include:
                text = text.replace(bn,"BN"+str(re.findall(r"[0-9]{1,3}", bn)[0]))

    text = text.replace("TP. ", "thành phố ")
    return text


def seperateSentences(text):
    sentences = []
    for sentence in text.split('.'):
        sentences += sentence.split(";")
    return sentences
def getRelation(text):
    BNids = getBNid(text)
    # for BNid in BNids:
    #     neo4j.createBN(BNid,None, None, None, None, None, None, None, None)
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




def getNationlaty(text):
    for i in NATIONLATY_RE:
        result = re.search(i, text, flags)
        if result:
            match_obj_country = re.search("([A-Z]\w{1,7}.{0,1}){1,3}",result.group(0))
            if match_obj_country:
                return match_obj_country.group(0)
            else:
                return result.group(0)

def getOrigin(text):
    for i in ORIGIN:
        result = re.search(i, text, flags)
        if result:
            return result.group(0)

def getFlight(text):
    for i in FLIGHT_RE:
        result = re.search(i, text)
        if result:
            return result.group(0)
    return None
def getNumberSit(text):
    for i in NUMBERSIT:
        result = re.search(i, text)
        if result:
            return result.group(0)
    return None

def process(text, date=None):
    BNid_main = None
    for sentence in seperateSentences(text):
        print("#"*32)
        print("Sentences:",sentence)
        f.write("\n")
        f.writelines("#"*32)
        f.write("\nSentences: "+sentence)
        BNids = getBNid(sentence)
        if len(BNids) != 0:
            BNid_main = BNids[0]
        print(BNid_main)
        f.write("\n"+BNid_main)
        # if date:
        #     # neo4j.updateBN(BNid_main, "date", date)
        sex = getSex(sentence)
        if sex != None:
            # neo4j.updateBN(BNid_main, "sex", sex)
            print("Sex:",sex)
            f.write("\nSex:"+sex)
        age = getAge(sentence)
        if age != None:
            # neo4j.updateBN(BNid_main, "age", age)
            print("Age:",age)
            f.write("\n Age:" +age)
        flight = getFlight(sentence)
        if flight != None:
            # neo4j.createTranspotation(BNid_main, flight)
            print("Flight:",flight)
            f.write("\n Flight:"+flight)
            numbersit = getNumberSit(sentence)
            if numbersit != None:
                # neo4j.updateBN(BNid_main, "number_sit", numbersit)
                print("Numbersit:",numbersit)
                f.write("\n Numbersit:"+numbersit)
                # neo4j.createConnectPTVT(BNid_main, numbersit, flight)
        nationlaty = getNationlaty(sentence)
        if nationlaty != None:
            # neo4j.updateBN(BNid_main, "nationlaty", nationlaty)
            print("Nation:",nationlaty)
            f.write("\n Nation:"+nationlaty)
        origin = getOrigin(sentence)
        if origin != None:
            # neo4j.updateBN(BNid_main, "origin", origin)
            print("Origin:",origin)
            f.write("\nOrigin:"+origin)
        status = getStatus(sentence)
        if status != None:
            # neo4j.updateBN(BNid_main, "status", status)
            print("Status:",status)
            f.write("\n Status: "+status)

def getObject(text, date=None):
    try:
        text = preprocessIDBN(text)
        getRelation(text)
        process(text, date)
    except Exception as e:
        print("Error: ",e)

if __name__ == '__main__':
    # text = """CA BỆNH 2827 (BN2827) ghi nhận tại tỉnh Khánh Hòa: Bệnh nhân nam, 37 tuổi, quốc tịch Ấn Độ, là chuyên gia. Bệnh nhân từ Ấn Độ quá cảnh Dubai, Hàn Quốc, sau đó nhập cảnh Sân bay Cam Ranh trên chuyến bay OZ773 ngày 20/4/2021 và được cách ly ngay sau khi nhập cảnh tại tỉnh Khánh Hòa. Kết quả xét nghiệm ngày 22/4/2021 dương tính với SARS-CoV-2. Hiện bệnh nhân được cách ly, điều trị tại Bệnh viện Bệnh nhiệt đới tỉnh Khánh Hòa."""
    # text = text + u"Thành phố Hà Nội "
    text = """ 
      THÔNG BÁO VỀ 4 CA MẮC MỚI (BN2911-2914)Trong đó có 03 ca ghi nhận trong nước tại Hà Nội (1), Hưng Yên (2) và 01 ca được cách ly ngay sau khi nhập cảnh tại Quảng Trị. Cụ thể:- CA BỆNH 2911 (BN2911) ghi nhận tại Hà Nội: Bệnh nhân nam, 28 tuổi, địa chỉ tại xã Việt Hùng, huyện Đông Anh, thành phố Hà Nội, là F1 của BN2899. Ngày 22/04, bệnh nhân đi ăn liên hoan cùng BN2899 tại thị trấn Vĩnh Trụ, Lý Nhân, Hà Nam. Ngày 29/04, bệnh nhân có kết quả dương tính với SARS-CoV-2. Hiện bệnh nhân đang được cách ly điều trị tại bệnh viện Bệnh nhiệt đới Trung ương cơ sở Đông Anh.- CA BỆNH 2912 (BN2912) ghi nhận tại Hưng Yên: Bệnh nhân nữ, 02 tuổi, địa chỉ tại xã Tiên Tiến, huyện Phù Cừ, tỉnh Hưng Yên, là F1 của BN2899. Bệnh nhân có tiếp xúc gần với BN2899 ngày 22/4 tại xã Đạo Lý, huyện Lý Nhân, tỉnh Hà Nam. Ngày 29/04, bệnh nhân có kết quả dương tính với SARS-CoV-2. Hiện bệnh nhân đang được cách ly điều trị tại bệnh viện Bệnh nhiệt đới Trung ương cơ sở Đông Anh.- CA BỆNH 2913 (BN2913) ghi nhận tại Hưng Yên: Bệnh nhân nữ, 58 tuổi, địa chỉ tại xã Tiên Tiến, huyện Phù Cừ, tỉnh Hưng Yên, là bà nội của BN2912. Bệnh nhân thường xuyên tiếp xúc gần với BN2912. Ngày 29/04, bệnh nhân có kết quả dương tính với SARS-CoV-2. Hiện bệnh nhân đang được cách ly điều trị tại bệnh viện Bệnh nhiệt đới Trung ương cơ sở Đông Anh.- CA BỆNH 2914 (BN2914) cách ly ngay sau nhập cảnh tại Quảng Trị: Bệnh nhân nữ, 34 tuổi, có địa chỉ tại quận Cẩm Lệ, thành phố Đà Nẵng. Ngày 27/4/2021, bệnh nhân trên từ nước ngoài nhập cảnh cửa khẩu Lao Bảo và được cách ly ngay sau khi nhập cảnh tại tỉnh Quảng Trị. Kết quả xét nghiệm ngày 29/4/2021 dương tính với SARS-CoV-2. Hiện bệnh nhân được cách ly, điều trị tại Bệnh viện các bệnh Phổi tỉnh Quảng Trị.
# """
    text1 = "CA BỆNH"
    text2 = "CA BỆNH"
    print(text1 +", " + text2)
    print(text1 == text2)
#     getObject(text,"21/3")
    # print(text)
    # print(BNre)
   
    
    # mydb = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     password="linhchi",
    #     charset='utf8',
    #     port = 3306, 
    #     database='scrapy'
    # )
    # mycursor = mydb.cursor()
    # mycursor.execute("SELECT title,content,date,time FROM content ")
    # myresult = mycursor.fetchmany(1)
    # for x in myresult:
    #     getObject(x[1])
    f.close()