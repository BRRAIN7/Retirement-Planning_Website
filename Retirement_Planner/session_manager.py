import mysql.connector

SessionInformation=mysql.connector.connect(host="localhost",user="root",passwd="Brrain7@mysql",database="SessionInformation")
mycursor =SessionInformation.cursor()

mycursor.execute("desc retirement_plans")
for i in mycursor:
    print(i)