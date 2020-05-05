import mysql.connector
from flask import Flask
from flask import Flask, flash, redirect,send_file, render_template, request, session, abort
import os
import pandas as pd
import json
import fpdf
from zipfile import ZipFile 


app = Flask(__name__)
app.secret_key = "abc"  

#api for login page 
@app.route('/')
def loginPage():
   db = mysql.connector.connect(host="localhost",user="root",passwd="")
   cursor = db.cursor()
   cursor.execute("CREATE DATABASE IF NOT EXISTS Application")
   cursor.execute("create table IF NOT EXISTS Application.USER_DETAILS (userid varchar(50) PRIMARY KEY,password varchar(20),role varchar(20),status varchar(20))")
   cursor.execute("create table IF NOT EXISTS Application.Employee (employee_id varchar(50) PRIMARY KEY,employee_name varchar(20),department varchar(20),designation varchar(20),salary int,month varchar(20),address varchar(50),phoneno int,email_id varchar(50),reporting_manager varchar(50),invoice_no int,year int)")
   #cursor.execute("insert into Application.USER_DETAILS (userid,password,role,status) values('admin','admin','superadmin','active')")
   cursor.execute("INSERT INTO Application.USER_DETAILS (userid,password,role,status) VALUES ('admin','admin','superadmin','active') ON DUPLICATE KEY UPDATE userid='admin',password='admin',role='superadmin',status='active'")
   db.commit()
   db.close()
   if 'logged_in' not in session:
      return render_template('/login.html')
   else:
      return render_template('/home.html')

#api for handling login
@app.route('/login', methods=['POST'])
def handleLogin():
   db = mysql.connector.connect(host="localhost",user="root",passwd="")
   cursor = db.cursor()
   cursor.execute("SELECT count(*) FROM Application.USER_DETAILS WHERE status='active' and userid=%s AND password=%s",(str(request.form['username']),str(request.form['password'])))
   record = cursor.fetchone()
   if int(record[0])<1:
	      return render_template('/login.html',errorMessage="User is not Active. Please ask your admin to activate user id")
   else:
	cursor.execute("SELECT COUNT(*) FROM Application.USER_DETAILS WHERE userid=%s AND password=%s",(str(request.form['username']),str(request.form['password'])))
	record = cursor.fetchone()
	db.close()
	if int(record[0])>0:
	    session['logged_in'] = True
	    if str(request.form['username'])=='admin':
		return render_template('/home.html')
	else:
	    return render_template('/login.html',errorMessage="Invalid User Id & Password")

#api to invalisession['admin']=True
	    date session and logout
@app.route('/logout')
def logout():
	session.clear()
	return render_template('login.html',errorMessage="Logged Out Successfully")
