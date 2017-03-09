#Fun little project to play around with string hashing,
#salts, and general password stuff that I might have to
#use for real one day. Also fun because I tested SQL injection
#against it, which was thwarted by the .execute function
#(as opposed to building the string by hand with concatenation)
import hashlib
import sqlite3
import getpass
import random

DB_NAME = "data.db"

#handles adding of new user to database
#critically, salts and hashes their password
#before inserting it
def addNewUser(connection, username, password):
    salt = ""
    for i in range(0, 62): #random string of 63 bits
        salt += random.choice('01')

    password += salt

    m = hashlib.sha256() #probably more secure to use newer SHA family hashes
    m.update(password)

    password =  m.hexdigest()
    insert = "insert into login_info values(?,?,?)"
    connection.execute(insert, (username, password, salt))

    print "Welcome,", username

#returns the salt stored with a certain username
#in the login_info table
def getSaltByUname(connection, username):
    c = connection.cursor()

    username = (username, )
    statement = "select salt from login_info where username=?"
    for i in c.execute(statement, username): #don't actually need for loop but it's safer
        val = i

    return val[0]


#returns the hashed version of the string entered at account creation
def getPassByUName(connection, username):
    c = connection.cursor()

    username = (username, )
    statement = "select password from login_info where username=?"

    for i in c.execute(statement, username):
        val = i

    return val[0]

#checks if the password entered is correct for the user
#by adding the salt, hashing it
def checkLogin(connection, username, password):
    salt = getSaltByUname(connection, username) #should never fail, since we know the username is in there

    password += salt
    m = hashlib.sha256()
    m.update(password)

    password = m.hexdigest()

    if password == getPassByUName(connection, username):
        print "Wow, you're in!"
    else:
        print "Invalid password!"



#main driver/stub of code
def main():
    connection = sqlite3.connect(DB_NAME)

    username = raw_input("Enter your username (or desired username, if logging in for the first time): ")
    password = getpass.getpass("Enter password: ")

    c = connection.cursor()
    name_param = (username, )
    rows = 0
    for row in (c.execute("select * from login_info where username=?", name_param)):
        rows += 1

    if rows == 0:
        addNewUser(connection, username, password)
    else:
        checkLogin(connection, username, password)


    connection.commit()
    connection.close()

if __name__ == "__main__":
    main()
