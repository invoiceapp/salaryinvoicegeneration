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

#api to download invoice
@app.route('/download')
def download():
	return send_file("Invoice.zip", as_attachment=True)

#api to direct to reset password
@app.route('/forgetPassword')
def resetPassword():
	return render_template('forgetPassword.html')

#api to update password
@app.route('/updatePassword', methods=['POST'])
def updatePassword():
	try:
		print(str(request.form['password']),str(request.form['password1']))
		if str(request.form['password'])!=str(request.form['password1']):
			return render_template("forgetPassword.html",errorMessage="Password & confirm password must match")
		else:
			db = mysql.connector.connect(host="localhost",user="root",passwd="")
			cursor = db.cursor()
			cursor.execute("update Application.USER_DETAILS set password=%s where userid=%s",(str(request.form['password']).strip(),str(request.form['username']).strip()))
			db.commit()
		 	db.close()
			return render_template('login.html',message="Password reset Success. Please login with new password")
	except mysql.connector.Error as err:
		return render_template("forgetPassword.html",errorMessage="Password reset failed")

#method to redirect to fileupload page
@app.route('/fileUploadPage')
def fileUploadPage():
	return render_template('fileupload.html')

#method to get user list
@app.route('/getUserList')
def getUserList():
    if 'admin' not in session:
       return render_template('/accessDenied.html')
   
    db = mysql.connector.connect(host="localhost",user="root",passwd="")
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT userid,password,role,status FROM Application.USER_DETAILS")
    records = cursor.fetchall()
    db.close()
    return render_template('subuser.html',userList=records)

#method to update user
@app.route('/updateUser')
def updateUser():
    try:
	    print(request.args.get('userid'))
	    db = mysql.connector.connect(host="localhost",user="root",passwd="")
	    cursor = db.cursor()
	    cursor.execute("INSERT INTO Application.USER_DETAILS (userid,password,role,status) VALUES (%s,'admin',%s,'deactive') ON DUPLICATE KEY UPDATE userid=%s,role=%s,status=%s",(request.args.get('userid').strip(),request.args.get('role').strip(),request.args.get('userid').strip(),request.args.get('role').strip(),request.args.get('status').strip()))
	    db.commit()
	    db.close()

	    
    except Exception as e:
	print(e)
	return False
    
#method to delete user
@app.route('/removeUser')
def removeUser():
    try:
	    print(request.args.get('userid'))
	    db = mysql.connector.connect(host="localhost",user="root",passwd="")
	    cursor = db.cursor()
	    cursor.execute("delete from Application.USER_DETAILS where userid='"+str(request.args.get('userid'))+"'")
	    #cursor.execute("delete from Application.USER_DETAILS where userid=%s",)
	    db.commit()
	    db.close()
	    return True
    except Exception as e:
	print(e)
	return False

#method to get filtered user data

@app.route('/getFilteredUserData', methods=['GET','POST'])
def getFilteredUserData():
    flag=False
    queryOperator=" where "
    query="select * from Application.Employee" 
    if 'month' in request.form and str(request.form['month'])!='':
	query=query+" where month='"+str(request.form['month'])+"'"	
	flag=True
	print(flag)
    if 'year' in request.form and str(request.form['year'])!='':
	if flag:
		queryOperator=" and "		
	query=query+queryOperator+" year="+str(request.form['year'])+""
    print(query)	
    db = mysql.connector.connect(host="localhost",user="root",passwd="")
    cursor = db.cursor(dictionary=True)
    cursor.execute(query)
    records = cursor.fetchall()
    db.close()
    return render_template('userList.html',employeeList=records)
    
#method to handle file upload

@app.route('/handleUpload', methods=['POST'])			
def handleUpload():
	try:
		f = request.files['file']
		data_xls = pd.read_excel(f)
		jsonData= data_xls.to_json(orient='records')
		jsonData=json.loads(jsonData)
		validateFile(jsonData)
		for data in jsonData:
      			print(data['employee_id'])
			db = mysql.connector.connect(host="localhost",user="root",passwd="")
		    	cursor = db.cursor()
			cursor.execute("INSERT INTO Application.Employee (employee_id,employee_name,department,designation,salary,month,address,phoneno,email_id,reporting_manager,invoice_no,year)  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(data['employee_id'],data['employee_name'],data['department'],data['designation'],int(data['salary']),(data['month']),data['address'],int(data['phoneno']),data['email_id'],data['reporting_manager'],int(data['invoice_no']),int(data['year'])))
		    	db.commit()
		        db.close()
			pdf = fpdf.FPDF(format='letter') #pdf format
			pdf.add_page() #create new page
			pdf.set_font("Arial", size=12) # font and textsize
			pdf.cell(200, 10, txt="Invoice Report", ln=1, align="C")
			for key, value in data.items(): 
			   pdf.cell(200, 10, txt=str(key)+" : "+str(value), ln=1, align="L")
			pdf.output(str(data['month'])+"_"+str(data['employee_name'])+".pdf")
		with ZipFile('Invoice.zip','w') as zip:
		    for data in jsonData:
			zip.write(str(data['month'])+"_"+str(data['employee_name'])+".pdf")
			os.remove(str(data['month'])+"_"+str(data['employee_name'])+".pdf")
		    zip.close()

		#print(jsonData['jsonData'])
		return render_template('fileupload.html',message="File Uploaded Successfully & Data Saved")
	except mysql.connector.Error as err:
		return render_template('fileupload.html',errorMessage="Database Exception"+str(err))

	except Exception as e:
		print(e)
		return render_template('fileupload.html',errorMessage="Invalid file, Upload valid file in xls or xlsx format only")	


#method to validate uploaded file
def validateFile(jsonData):
	if 'employee_id' in jsonData and 'employee_name' in jsonData and 'department' in jsonData and 'designation' in jsonData and 'salary' in jsonData and 'month' in jsonData and 'address' in jsonData and 'phoneno' in jsonData and 'email_id' in jsonData	 and 'reporting_manager' in jsonData and 'invoice_no' in jsonData and 'year' in jsonData:
		return True
	else:
		return render_template('fileupload.html',errorMessage="Invalid file, all fields are not present in excel file")			

#api to fetch employee details
@app.route('/fetchEmployeeDetails')
def fetchEmployeeDetails():
  db = mysql.connector.connect(host="localhost",user="root",passwd="")
  cursor = db.cursor(dictionary=True)
  cursor.execute("SELECT * FROM Application.Employee")
  records = cursor.fetchall()
  db.close()
  return render_template('employeeList.html',employeeList=records)

#method to start the application
if __name__ == "__main__":
   session.clear()		
   app.secret_key = os.urandom(12)
   app.run(debug=True,host='localhost', port=5000)
   session.clear()
