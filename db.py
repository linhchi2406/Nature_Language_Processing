import mysql.connector
import nltk 
from . import object_parser as object_parser
import re
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
myresult = mycursor.fetchmany(3)
for x in myresult:
    object_parser.getObject(x['content'],x['date'])
      
