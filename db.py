import mysql.connector
import nltk 

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="linhchi",
  charset='utf8',
  port = 3306, 
  database='scrapy'
)
mycursor = mydb.cursor()
mycursor.execute("SELECT title,content,date,time FROM content WHERE title LIKE '%covid%'")
myresult = mycursor.fetchmany(5)
for x in myresult:
  tokens = [t for t in x[1].split()] 
  freq = nltk.FreqDist(tokens) 
  for key,val in freq.items(): 
    print (str(key) + ':' + str(val))

