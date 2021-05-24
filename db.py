# import mysql.connector
# import nltk 
# from . import object_parser as object_parser
# import re
# mydb = mysql.connector.connect(
#   host="localhost",
#   user="root",
#   password="linhchi",
#   charset='utf8',
#   port = 3306, 
#   database='scrapy'
# )
# mycursor = mydb.cursor()
# mycursor.execute("SELECT title,content,date,time FROM content ")
# myresult = mycursor.fetchmany(3)
# for x in myresult:
#     object_parser.getObject(x['content'],x['date'])

from tkinter import *
import tkinter.font
root = Tk()
root.title("P.E.T.A.R")
my_font = tkinter.font.Font(root,family="Comic Sans MS")
my_font2 = tkinter.font.Font(root,family="Copperplate Gothic Bold")
txt = "Lị chi"
txt = Label(root, text = "welcome to project petar",font=my_font)
# txt.grid(column = 0, row = 0)
print(txt)

