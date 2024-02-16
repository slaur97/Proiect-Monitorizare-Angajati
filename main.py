import mysql.connector
import datetime
from datetime import date
from flask import Flask, request
import csv
import shutil
import time
import sys
import os
import json

# cale_salvare='C:/Users/Laurentiu/Desktop/TemaProiect/Tema'

from email.message import EmailMessage
import ssl 
import smtplib

class MailSender:
    password= "jdki mdhl bktf jvlx"
    email_sender='sogorlaurentiu@gmail.com'
    

    def send_email(self, email_destinatie, subiect, body):

        em=EmailMessage()
        em['From']=self.email_sender
        em['To']=email_destinatie
        em['Subject']=subiect
        em.set_content(body)

        context=ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
            smtp.login(self.email_sender,self.password)
            smtp.sendmail(self.email_sender,email_destinatie,em.as_string())

class mysql_connect:
        __host="127.0.0.1"
        __user="root"
        __password="Pasere123"
        __database="cladire"

        def __init__(self):
            self.database=mysql.connector.connect(
                host=self.__host,
                user=self.__user,
                password=self.__password,
                database=self.__database,
            )
            self.cursor=self.database.cursor()
        def selectQuery(self,query):
            self.database.commit()
            self.cursor.execute(query) 
            returnable=self.cursor.fetchall()
            return returnable
        def addQuery(self,query):
            self.cursor.execute(query)
            self.database.commit()
        def truncateAllTables(self):
            self.cursor.execute('TRUNCATE PERSOANE')
            self.cursor.execute('TRUNCATE ACCES')
mydb=mysql_connect()
try:
    if(sys.argv[1]=='1'):
        cale_salvare=sys.argv[2]
        shutil.copyfile(cale_salvare+'/input_files/Poarta1.txt', cale_salvare+'/intrari/Poarta1.txt')
        shutil.copyfile(cale_salvare+'/input_files/Poarta2.csv', cale_salvare+'/intrari/Poarta2.csv')
        class acces():
            def __init__(self, id_persoana,ora,sens,poarta):
                self.id_persoana=id_persoana
                self.ora=ora
                self.sens=sens
                self.poarta=poarta
            def citire_txt(self):
                with open(cale_salvare+'/intrari/poarta1.txt','r') as txtFile:
                    fisier=txtFile.readlines()
                    for element in fisier:
                            splitare=element.split(',')
                            splitare[-1]=splitare[-1].strip()
                            mydb.addQuery(f"""insert into acces values(Null,{splitare[0]},'{splitare[1][:-5]}','{splitare[2][:-1]}',1) """)
                        
            def citire_csv(self):
                with open(cale_salvare+'/intrari/poarta2.csv','r') as csvFile:
                    fisier=csv.reader(csvFile)
                    for element in fisier:
                        if(element[0]=='Id'):
                            continue
                        mydb.addQuery(f"""insert into acces values(Null,{element[0]},'{element[1][:-5]}','{element[2]}',2) """)
            def mutare_fisier(self,nume_fisier,extensie):
                locatie_actuala=f"{cale_salvare}/intrari/{nume_fisier}.{extensie}"
                destinatie=f"{cale_salvare}/backup_intrari/{nume_fisier}{date.today()}.{extensie}"
                shutil.move(locatie_actuala,destinatie)

        cladire=acces(1,1,1,1)
        try:
            cladire.citire_txt()
            cladire.citire_csv()
        except FileNotFoundError:
            print("Nu exista fisiere noi")
        try:
            cladire.mutare_fisier('Poarta1','txt')
            cladire.mutare_fisier('Poarta2','csv')
        except FileNotFoundError:
            print("nu exista fisiere de mutat")
except IndexError:
    print('loading...')

app=Flask(__name__)
time.sleep(3)
def creare_txt_chiulangii(json_):
    lista=[]
    data=datetime.datetime.now()
    data=data.strftime('%m-%d-%y') 
    locatie_salvare_fisier_txt=f"""{cale_salvare}/backup_intrari/{str(data)}_chiulangii.txt"""
    with open(locatie_salvare_fisier_txt,'w')as txtFile:
        for element in json_:
            lista.append(element['id'])
            lista.append(element['ore_lucrate'])
            txtFile.write(str(lista[0])+","+str(lista[1])+'\n')
            Mail=MailSender()
            Mail.send_email("laurentiu_sogor@yahoo.com", "chiulangiii", f"persoana cu id-ul {lista[0]} a lucrat doar {lista[1]} ore")
            time.sleep(3)
            lista.clear()
def creare_csv_chiulangii(json_):
    data=datetime.datetime.now()
    data=data.strftime('%m-%d-%y') 
    locatie_salvare_fisier_csv=f"""{cale_salvare}/backup_intrari/{str(data)}_chiulangii.csv"""   
    titlu=['id','ore_lucrate']
    with open(locatie_salvare_fisier_csv,'w',newline='') as csvfile:
        writer=csv.DictWriter(csvfile,fieldnames=titlu)
        writer.writeheader()
        writer.writerows(json_)
def angajati_sub_8ore_lucrate():
    json=[]
    data=mydb.selectQuery("select * from acces")
    print(data)
    for i in range(0,len(data)-1):
        for j in range(i+1,len(data)):
            if(data[i][1]==data[j][1]):
                ora1=data[i][2]
                ora2=data[j][2]
                diferenta=ora2-ora1
                ore_lucrate=str(diferenta)[:1]
                if(int(ore_lucrate)<8):
                    json.append({"id":data[i][1],"ore_lucrate":str(ore_lucrate)})
    creare_csv_chiulangii(json)
    creare_txt_chiulangii(json)
@app.route('/utilizator',methods=['POST'])
def inregistrare_persoane():
    fisier=request.get_json()
    mydb.addQuery(f"""insert into persoane values({fisier['Id']},'{fisier['Nume']}','{fisier['Prenume']}','{fisier['Companie']}',{fisier['IdManager']},'{fisier['Email']}')""")
    return "fisier returnat"
@app.route('/acces',methods=['POST'])
def introducere_json_baza_date():
    fisier=request.get_json()
    mydb.addQuery(f"""insert into acces values(Null,{fisier['idPersoana']},'{fisier['data'][:-5]}','{fisier['sens']}',{fisier['idPoarta']})""")
    time.sleep(2)
    return "intrare adaugata"



try:
    if(sys.argv[1]=='2'):
        if __name__=="__main__":
            app.run(debug=True)
except IndexError:
    print("index invalid")

try:
    if(sys.argv[1]=='3'):
        cale_salvare=sys.argv[2]
        data= data=datetime.datetime.now()  #daca este ora 20:00, adaugam in fisiere chiulangiii
        data=data.strftime("%H:%M:%S")
        if(int(str(data)[:2]))==15:
            print('loading..')
            time.sleep(3)
            angajati_sub_8ore_lucrate()
except IndexError:
    print("index invalid")

