from flask import Flask,render_template,request,redirect
import MySQLdb,csv,urllib2
import tablib
import os



app = Flask(__name__)

ROOT = os.path.dirname(os.path.abspath(__file__))
dataset = tablib.Dataset()

mydb = MySQLdb.connect(host="localhost", user="hacker", passwd="xyz_zyx")

cursor = mydb.cursor()
DATABASE_NAME = "employeeattendance"
cursor.execute("SHOW DATABASES")

check = False
for x in cursor:
    print(x)
    if x == (DATABASE_NAME,):
        check = True
        mydb = MySQLdb.connect(host="localhost", user="hacker", passwd="xyz_zyx", db=DATABASE_NAME)
        cursor=mydb.cursor()
        break
if not check:
    cursor.execute("CREATE DATABASE " + DATABASE_NAME)
    mydb = MySQLdb.connect(host="localhost", user="hacker", passwd="xyz_zyx", db=DATABASE_NAME)
    cursor=mydb.cursor()
    cursor.execute("CREATE TABLE tbl_attendance (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), attendance VARCHAR(255))")
    cursor.execute("CREATE TABLE admin (username VARCHAR(255) PRIMARY KEY, password VARCHAR(255)")
    cursor.execute("CREATE TABLE employee (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255)")


@app.route('/',methods=["GET","POST"])
def index():
    if request.method=="POST":
        username = str(request.form['username'])
        password = str(request.form['password'])
        print(username, password)
        cursor = mydb.cursor()
        cursor.execute('INSERT INTO admin (username,password)VALUES(%s,%s)', (username, password))
        cursor.close()
        mydb.commit()
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login_form.html")

@app.route('/register')
def register():
    return render_template("register_form.html")


@app.route('/employee',methods=["GET","POST"])
def enter_employee():
    if request.method=="POST":
        username = str(request.form['username'])
        password = str(request.form['password'])
        cursor = mydb.cursor()
        cursor.execute('SELECT username, password FROM admin WHERE username=%s',[username])
        user=cursor.fetchone()
        cursor.close()
        mydb.commit()
        if user[1]==password:
            return render_template("enter_employee.html")
        else: return "failed"

@app.route('/employee/create', methods=["GET", "POST"])
def create():
    employee_name = str(request.args.get('employee_name', ""))
    cursor = mydb.cursor()
    cursor.execute('INSERT INTO employee (name)VALUES(%s)', [employee_name])
    mydb.commit()
    cursor.close()
    return render_template("enter_employee.html")

@app.route('/employee/export', methods=["GET", "POST"])
def export():
    cursor = mydb.cursor()
    cursor.execute('SELECT * FROM employee')
    res = cursor.fetchall()
    with open('output.csv', 'w') as fileout:
        writer = csv.writer(fileout)
        writer.writerows(res)
    mydb.commit()
    cursor.close()
    
    return redirect('http://3.16.75.43/Attendance/output.csv')

@app.route('/employee/show_attendence', methods=["GET", "POST"])
def show_attendence():
    if request.method == 'POST':
        target = os.path.join(ROOT, 'temp/')

        if not os.path.isdir(target):
            os.mkdir(target)
        file = request.files['file']
        filename = file.filename
        destination ='/var/www/html/Attendance/temp/temp.csv'
        file.save(destination)
        with open(destination, 'r') as f:
            dataset.csv = f.read()
            r = csv.DictReader(f)
            print(dataset.csv)
        for x in dataset:
            val = (x[1], x[2])
            sql = "INSERT INTO tbl_attendance(name,attendance) VALUES (%s, %s)"
            cursor.execute(sql, val)
            mydb.commit()
        return render_template('table.html', dataset=dataset)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
