import re
# from . import neo4j_util as neo4j
# import neo4j_util as neo4j

f = open('out.json', 'w+', encoding='utf-8')

FEMALE = [r"(n|N)ữ"]
MALE = [r"(n|N)am", "nam giới"]
AGE = [r"[0-9]{1,3}\s{1,6}tuổi"]
BN_RANGE = [r"CA BỆNH\s{1,6}[0-9]{1,4} - [0-9]{1,4}",
        r"Bệnh nhân\s[0-9]{1,4} - [0-9]{1,4}",
         r"Bệnh nhân số\s{1,6}[0-9]{1,4} - [0-9]{1,4}"
       ]
BNre = [r"CA BỆNH\s{1,6}[0-9]{1,4}",
        r"(b|B)ệnh nhân\s[0-9]{1,4}",
         r"(b|B)ệnh nhân số\s{1,6}[0-9]{1,4}",
        r"BN\s{0,2}[0-9]{1,4}"
       ]
FLIGHT_RE= [r"(c|C)huyến bay\s{0,6}[A-Z]{1,4}\s?[0-9]{2,8}"]
NATIONLATY_RE = ["quốc tịch(.{0,1}[A-Z]\w{1,7}){1,3}",
                "quốc tịch(.{0,1}\w{1,7}){1,3}"]
ORIGIN = [r"(địa\s{1,2}chỉ|trú)\s{1,2}(tại|ở)\s{1,2}(\s|\w|,|TP.)*([A-Z]\w{1,})",
r"(địa chỉ|trú|quê) (tại|ở)?(\s(phường|quận|thị xã|thị trấn|tỉnh|thành phố)?(\s?\w{1,4}){1,3})"]
NUMBERSIT = ["số ghế [0-9]{1,8}[A-Z]{1,4}\s?"]
flags=re.I|re.U
DEATH = [r"(đã)?\s{1,3}(chết|khuất|ngoẻo|tử vong|mất)",
        r"(đã)\s{1,3}(khuất|mất)"
]
NEGATIVE_COVID = [r"(đã)?\s{1,3}(khỏi bệnh)"
]
def getBNid(text):
    BNs=[]
    for i in BNre:
        result = re.search(i, text)
        if result:
            text_include = re.findall(i, text)
            for bn in text_include:
                BNs.append(re.findall(r"[0-9]{1,3}", bn)[0])
    return ["BN"+BNid for BNid in BNs]
def seperateSentences(text):
    sentences = []
    for sentence in text.split('.'):
        sentences += sentence.split(";")
    return sentences

def getRelation(text):
    #lấy id của tất cả các bệnh nhân
    BNids = getBNid(text)
        # Nếu mà id nhỏ hơn 2, nghĩa là chỉ có 1 bệnh nhân => trả về None là không có relation nào
    if len(BNids) < 2:
        return
    BNid_main = BNids[0]
#tách câu ra, nếu mà ít hơn 4 câu
    for sentence in seperateSentences(text):
        if len(sentence) < 4:
            continue
        # lấy id của tất cả bệnh nhân
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
                    # neo4j.createConnect(BNid1, relation, BNid2)
text = """Tại cuộc họp Ban Chỉ đạo Phòng, chống COVID-19 TP. Đà Nẵng vào chiều 10/5, Bí thư Thành ủy Đà Nẵng Nguyễn Văn Quảng cho biết, cả hệ thống chính trị Thành phố đang vào cuộc với quyết tâm cao để phòng, chống dịch COVID-19 và bước đầu đã cho những kết quả khả quan. Ông Nguyễn Văn Quảng khẳng định, hoàn toàn không có chuyện cách ly, phong tỏa toàn thành phố như tin đồn.
heo Bí thư Thành ủy Nguyễn Văn Quảng, công tác giám sát, điều tra dịch tễ là hết sức quan trọng. Đặc biệt, việc khai thác thông tin nhanh chóng, kịp thời, kỹ lưỡng có vai trò quyết định đến hiệu quả phòng, chống dịch của cả hệ thống chính trị. Bí thư Thành ủy Đà Nẵng đề nghị các đơn vị, địa phương thực hiện điều tra dịch tễ kỹ càng, nhanh nhất, sớm nhất có thể để có được bản thông tin đi lại, tiếp xúc của bệnh nhân, từ đó áp dụng các biện pháp y tế phù hợp đối với những trường hợp liên quan.
Tại cuộc họp, Chủ tịch UBND Thành phố Lê Trung Chinh cho biết, tại Đà Nẵng các trường hợp F1 trở thành F0 đang tiếp tục tăng, gây áp lực cho các địa phương trong việc thực hiện biện pháp cách ly y tế tập trung. Ông Lê Trung Chính đề nghị các địa phương bố trí lực lượng, có phương án cụ thể, rõ ràng, bảo đảm cách ly y tế đối với các F1 an toàn, không để xảy ra tình trạng lây nhiễm chéo trong khu cách ly.
Bên cạnh đó, chủ động tổ chức, rà soát kỹ lưỡng các F1, F2, mạnh dạn đề xuất thành phố các biện pháp cách ly, xét nghiệm cần thiết đối với những trường hợp có nguy cơ nhưng chưa nhận định được là F1 hay F2, F3.
Tính từ ngày 3/5 đến chiều 10/5, Đà Nẵng ghi nhận 53 ca mắc COVID-19. Hiện nay, việc truy vết các ca F1 được các đơn vị, địa phương tiếp tục thực hiện với tinh thần chủ động, quyết liệt, thần tốc, không để sót đối tượng."""
print(seperateSentences(text))