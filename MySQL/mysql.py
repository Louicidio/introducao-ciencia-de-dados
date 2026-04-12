import mysql.connector

cnx = mysql.connector.connect(user='root', 
                              password='Luis74411!',
                              host='127.0.0.1',
                              database='Jotair')
cnx.close()