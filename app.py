import pandas as pd
from flask import Flask, render_template, request,jsonify
from math import sin, cos, sqrt, atan2, radians
from time import gmtime, strftime
import pyodbc
import csv
import time
import json
from datetime import datetime

app = Flask(__name__)
app.config.from_pyfile('config.py')


server = ""
database = ""
username = ""
password = ""

cnxn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
    + server
    + ";DATABASE="
    + database
    + ";UID="
    + username
    + ";PWD="
    + password
)
cursor = cnxn.cursor()



@app.route('/student', methods=['GET', 'POST'])
def student():
    return render_template('StudentPage.html',main="mainpage")


@app.route('/teacher', methods=['GET', 'POST'])
def teacher():
    return render_template('TeacherPage.html',main="mainpage")

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return render_template('AdminPage.html',main="mainpage")


@app.route('/teacherform', methods=['GET', 'POST'])
def teacherform():
    return render_template('teacherform.html',main="mainpage")

@app.route('/adminform', methods=['GET', 'POST'])
def adminform():
    return render_template('adminform.html',main="mainpage")


@app.route('/studentform', methods=['GET', 'POST'])
def studentform():
    return render_template('studentform.html',main="mainpage")


@app.route('/savedetails', methods=['GET'])
def savedetails():
    msg = ""
    name = request.args.get('name')
    userid = request.args.get('userid')
    now = datetime.now()
    qry = "Insert into projectDB..Users(Userid,Name) Values(?,?)"
    cursor.execute(qry,userid,name)
    cursor.commit()
    msg="Inserted Successfully"
    if userid=='T':
        return render_template('TeacherPage.html')
    elif userid=='S':
        return render_template('StudentPage.html')
    else:
        return render_template('AdminPage.html')


@app.route('/insertquestion', methods=['GET'])
def insertquestion():
    msg = ""
    question = request.args.get('question')
    now = datetime.now()
    chekqry="SELECT TOP 1 * FROM ProjectDB..games "
    cursor.execute(chekqry)
    res = cursor.fetchall()
    if not res:
        qry = "insert into projectDB..games(QuestionId, Question) values ('1',?)"
        cursor.execute(qry,question)
    else:
        qry = "insert into projectDB..games(QuestionId, Question,createddate) values ((select  max(coalesce(QuestionId,0))+1 from projectDB..games),?,?)"
        cursor.execute(qry, question, now.strftime("%d/%m/%Y %H:%M:%S"))
    cursor.commit()
    msg="Inserted Successfully"
    return render_template('TeacherPage.html',msg=msg)


@app.route('/startgame', methods=['POST'])
def startgame():
    now = datetime.now()
    output = request.get_json()
    jsonreslt = json.loads(output)
    if jsonreslt['st'] == "start":
        qry2 = "update projectDB..games set createdDate=?  where questionid =1"
        cursor.execute(qry2, now.strftime("%d/%m/%Y %H:%M:%S"))
        cursor.commit()
    qry1 = "select QuestionId,Question from projectDB..games where questionid = (select max(QuestionId) from  projectDB..games ) and answer is null"
    cursor.execute(qry1)
    result = cursor.fetchall()
    dict = {}
    if result:
        dict["qnsid"] = result[0][0]
        dict["qns"] = result[0][1]
    return (dict)


@app.route('/fetchnamedetails', methods=['POST'])
def fetchnamedetails():
    qry2 = "select name,userid from projectDB..users "
    cursor.execute(qry2)
    result2 = cursor.fetchall()
    dict={}
    if result2:
        dict["user1"] = result2[0][0]+","+result2[0][1]
        dict["user2"] = result2[1][0]+","+result2[1][1]
    return (dict)



@app.route('/fetchansweranddate', methods=['POST'])
def fetchansweranddate():
    now = datetime.now()
    qry1 = "select answer  from projectDB..games where score is null and answer is not null "
    cursor.execute(qry1)
    result1 = cursor.fetchall()
    qry2 = "select name,userid from projectDB..users "
    cursor.execute(qry2)
    result2 = cursor.fetchall()
    qry3 = "SELECT CONVERT(Char(19), createddate ,20)  AS datetime from projectDB..games where questionID=1 "
    cursor.execute(qry3)
    result3 = cursor.fetchall()
    dict={}
    if result1:
        dict["ans"] = result1[0][0]
    if result2:
        dict["user1"] = result2[0][0]+","+result2[0][1]
        dict["user2"] = result2[1][0]+","+result2[1][1]
    if result3:
        dict["starttime"]=result3[0][0]
    return (dict)



@app.route('/fetchanswersadmin', methods=['POST'])
def fetchanswersadmin():
    now = datetime.now()
    qry1 = "select question,answer,score  from projectDB..games where score is not null "
    cursor.execute(qry1)
    result1 = cursor.fetchall()
    qry2 = "select name,userid from projectDB..users where userid in ('T','S')"
    cursor.execute(qry2)
    result2 = cursor.fetchall()
    qry3 = "SELECT CONVERT(Char(19), createddate ,20)  AS datetime from projectDB..games where questionID=1 "
    cursor.execute(qry3)
    result3 = cursor.fetchall()
    reslt1list=[]
    for row in result1:
        reslt1list.append([x for x in row])
    dict={}
    if result1:
        dict["qnsansscore"] = reslt1list
    if result2:
        dict["user1"] = result2[0][0]+","+result2[0][1]
        dict["user2"] = result2[1][0]+","+result2[1][1]
    if result3:
        dict["starttime"]=result3[0][0]
    return (dict)


@app.route('/saveanswer', methods=['POST'])
def saveanswer():
    output = request.get_json()
    jsonreslt = json.loads(output)
    now = datetime.now()
    qry2 = "update projectDB..games set answer=?  where questionid = (select max(QuestionId) from  projectDB..games) and answer is null"
    cursor.execute(qry2, jsonreslt['answer'])
    cursor.commit()
    return "Updated Successfully"


@app.route('/viewscore', methods=['POST'])
def viewscore():
    qry2 = "select questionid, score from projectDB..games where questionid = (select max(QuestionId) from  projectDB..games) and score is not null"
    cursor.execute(qry2)
    result3 = cursor.fetchone()
    if result3:
        return "Score for Question "+result3[0]+" is "+result3[1]
    return ""


@app.route('/saveanswers', methods=['POST'])
def saveanswers():
    msg = ""
    output = request.get_json()
    print(output)
    print(type(output))
    jsonreslt = json.loads(output)
    now = datetime.now()
    qry1 = "select QuestionId,Question from projectDB..games where questionid = ?"
    cursor.execute(qry1,int(jsonreslt['qnsno'])+1)
    result = cursor.fetchall()
    qry2 = "update projectDB..games set answerid = ?,answer=?,submittedDate=? where questionID=?"
    cursor.execute(qry2,jsonreslt['qnsno'],jsonreslt['ans'],now.strftime("%d/%m/%Y %H:%M:%S"),jsonreslt['qnsno'])
    cursor.commit()
    if(result):
        return render_template('AnswerQuestions.html',question=result[0])
    else:
        return render_template('AnswerQuestions.html')


@app.route('/viewandscoreans', methods=['GET'])
def viewandscoreans():
    score = request.args.get('score')
    now = datetime.now()
    if(score):
        qry2 = "update projectDB..games set score=?  where score is null and answer is not null"
        cursor.execute(qry2, score)
        cursor.commit()
    return render_template('TeacherPage.html')





if __name__ == "__main__":
    app.run(host="0.0.0.0")
