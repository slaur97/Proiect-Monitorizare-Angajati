import os
import time
import shutil
import datetime
import mysql.connector
import csv 
import requests
import threading 
import json

class mysqlconn:
    __host="localhost"
    __user="root"
    __password="Pasere123"
    __database="cladire"

    def __init__(self):
        self.database=mysql.connector.connect(
            host=self.__host,
            user=self.__user,
            password=self.__password,
            database=self.__database,
            auth_plugin='mysql_native_password'
        )
        self.cursor=self.database.cursor()
    
    def selectQuery(self,query):
        self.database.commit()
        self.cursor.execute(query)
        returnable=self.cursor.fetchall()
        return returnable
    
    def truncateAllTables(self):
        self.cursor.execute('TRUNCATE PERSOANE')
        self.cursor.execute('TRUNCATE ACCES')
        # self.database.commit()


filesPath='C:/Users/Laurentiu/Desktop/TemaProiect/Tema/'
mydb=mysqlconn()

def compare(persJsonObj,persTupple):
    ok=True
    if(persJsonObj['Nume']!=persTupple[1]):
        ok=False
    if(persJsonObj['Prenume']!=persTupple[2]):
        ok=False
    if(persJsonObj['Companie']!=persTupple[3]):
        ok=False
    if(persJsonObj['IdManager']!=persTupple[4]):
        ok=False
    if(persJsonObj['Email']!=persTupple[5]):
        ok=False
    return ok

def compare_access(accessJsonObj,accessTuple):
    if(accessJsonObj['data'][:-5]!=accessTuple[2].strftime('%Y-%m-%dT%H:%M:%S')):
        return False
    if(accessJsonObj['sens']!=accessTuple[3]):
        return False
    if(accessJsonObj['idPersoana']!=accessTuple[1]):
        return False
    if(accessJsonObj['idPoarta']!=accessTuple[4]):
        return False
    return True

def run_test_one():
    testPassed=0
    os.system(f'python main.py 1 "{filesPath}"')
    time.sleep(1)

    # shutil.copyfile('C:/Users/Laurentiu/Desktop/TemaProiect/Tema/input_files/Poarta1.txt','C:/Users/Laurentiu/Desktop/TemaProiect/Tema/intrari/Poarta1.txt')
    # time.sleep(2)

    if 'Poarta1.txt' not in os.listdir(filesPath+'/intrari'):
        print("PASSED Test 1.1")
        testPassed+=1
    else:
        print("FAILED Test 1.1")

    if f'Poarta1{datetime.date.today()}.txt' in os.listdir(filesPath+'/backup_intrari'):
        testPassed+=1
        print("PASSED Test 1.2")
    else:
        print("FAILED Test 1.2")

    # shutil.copyfile('C:/Users/Laurentiu/Desktop/TemaProiect/Tema/input_files/Poarta2.csv','C:/Users/Laurentiu/Desktop/TemaProiect/Tema/intrari/Poarta2.csv')
    # time.sleep(2)

    if 'Poarta2.csv' not in os.listdir(filesPath+'/intrari'):
        testPassed+=1
        print("PASSED Test 1.3")
    else:
        print("FAILED Test 1.3")

    if f'Poarta2{datetime.date.today()}.csv' in os.listdir(filesPath+'/backup_intrari'):
        testPassed+=1
        print("PASSED Test 1.4")
    else:
        print("FAILED Test 1.4")
    
    dbResults=mydb.selectQuery('select * from acces')
    ok=True
    with open(filesPath+'input_files/Poarta1.txt','r') as txtFile:
        txt=txtFile.readlines()
        lenOfTxt=len(txt)
        try:
            for i,line in enumerate(txt):
                if(dbResults[i][2].strftime('%Y-%m-%dT%H:%M:%S')!=line.split(',')[1][:-5]):
                    ok=False

        except IndexError:
            print('Nu a inserat corect in baza (txt)!')

    with open(filesPath+'input_files/Poarta2.csv','r') as csvFile:
        continut=csv.reader(csvFile)
        next(continut)
        try:
            for i,line in enumerate(continut):
                if(dbResults[lenOfTxt+i][2].strftime('%Y-%m-%dT%H:%M:%S')!=line[1][:-5]):
                    ok=False
        except IndexError:
            print('Nu a inserat corect in baza (csv)')
    if ok==True:
        testPassed+=1
        print("PASSED Test 1.5")
    else:
        print("FAILED Test 1.5")

    return testPassed

def start_server():
    os.system(f'python "C:/Users/Laurentiu/Desktop/TemaProiect/Tema/main.py" 2')


def send_signup_request():
    with open(r'C:\Users\Laurentiu\Desktop\TemaProiect\Tema\input_files\utilizatori.json','r') as jsonFile:
        data=json.load(jsonFile)
        time.sleep(5)
        for person in data:
            response=requests.post('http://127.0.0.1:5000/utilizator',json=person)
            if response.status_code!=200:
                print("Eroare la inregistrare utilizator!")
        time.sleep(2)
        utilizatori=mydb.selectQuery("SELECT * FROM persoane;")
        print(utilizatori)
        ok=True
        print(len(data))
        for poz in range(len(data)):
            print((data[poz]))
            print(utilizatori[poz])
            if(compare(data[poz],utilizatori[poz])==False):
                ok=False
                break
        if(ok):
            print('Test 2.1 passed!')
        else:
            print('Test 2.1 failed!')


def send_access_request():
     with open(r'C:\Users\Laurentiu\Desktop\TemaProiect\Tema\input_files\acces.json','r') as jsonFile:
        acces=json.load(jsonFile)
        for object in acces:
            response=requests.post('http://127.0.0.1:5000/acces',json=object)
        intrari=mydb.selectQuery("SELECT * FROM acces where Poarta=3")
        print(intrari)
        ok=True
        try:
            for poz in range(len(acces)):
                if(compare_access(acces[poz],intrari[poz])==False):
                    ok=False
                    break
        except IndexError:
            print('Nu toate intrarile au fost inserate!')
            ok=False
        if(ok==True):
             print('Test 2.2 passed!')
        else:
             print('Test 2.2 failed!')

def test_2_aux():
    send_signup_request()
    send_access_request() 
    
             

def run_test_two():
    t1=threading.Thread(target=start_server)
    t2=threading.Thread(target=test_2_aux)
    t1.start()
    t2.start()

def run_test_three():
    os.system(f'python main.py 3 "{filesPath}"')

# run_test_one()
# run_test_two()
# run_test_three()


# mydb.truncateAllTables()