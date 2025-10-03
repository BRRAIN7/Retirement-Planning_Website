import mysql.connector

SessionInformation=mysql.connector.connect(host="localhost",user="root",passwd="",database="SessionInformation")
mycursor =SessionInformation.cursor()

