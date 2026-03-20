from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hrm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- LOGIN REQUIRED DECORATOR ----------------

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

# ---------------- MODELS ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    role = db.Column(db.String(100))

class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100))
    reason = db.Column(db.String(200))
    status = db.Column(db.String(50), default="Pending")

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer)
    status = db.Column(db.String(50))

# ---------------- AUTH ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()

        if user:
            session['user'] = user.username
            return redirect('/')
        else:
            return "Invalid Username or Password"

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')
#-----------------HIRING------------------
@app.route('/hire', methods=['GET','POST'])
def hire():
    if request.method == 'POST':
        # store data (you can connect DB later)
        return redirect('/hiring-process')
    return render_template('hire.html')


@app.route('/hiring-process')
def hiring_process():
    return render_template('hiring_process.html')
# ---------------- DASHBOARD ----------------

@app.route('/')
@login_required
def dashboard():
    return render_template('index.html')


@app.route('/api/dashboard')
@login_required
def dashboard_data():
    return jsonify({
        "total": Employee.query.count(),
        "present": Attendance.query.filter_by(status="Present").count(),
        "leave": Leave.query.count()
    })

# ---------------- EMPLOYEE ----------------

@app.route('/employees')
@login_required
def employees():
    data = Employee.query.all()
    return render_template('employees.html', employees=data)


@app.route('/add_employee', methods=['POST'])
@login_required
def add_employee():
    db.session.add(Employee(
        name=request.form['name'],
        role=request.form['role']
    ))
    db.session.commit()
    return redirect(url_for('employees'))

# ---------------- SEARCH ----------------

@app.route('/search')
@login_required
def search():
    keyword = request.args.get('q')
    results = Employee.query.filter(Employee.name.like(f"%{keyword}%")).all()
    return render_template('employees.html', employees=results)

# ---------------- LEAVE ----------------

@app.route('/leave')
@login_required
def leave_page():
    leaves = Leave.query.all()
    return render_template('leave.html', leaves=leaves)


@app.route('/apply_leave', methods=['POST'])
@login_required
def apply_leave():
    db.session.add(Leave(
        employee_name=request.form['name'],
        reason=request.form['reason']
    ))
    db.session.commit()
    return redirect(url_for('leave_page'))


@app.route('/approve_leave/<int:id>')
@login_required
def approve_leave(id):
    leave = Leave.query.get(id)
    if leave:
        leave.status = "Approved"
        db.session.commit()
    return redirect(url_for('leave_page'))

# ---------------- ATTENDANCE ----------------

@app.route('/attendance')
@login_required
def attendance_page():
    data = Attendance.query.all()
    return render_template('attendance.html', records=data)


@app.route('/mark_attendance', methods=['POST'])
@login_required
def mark_attendance():
    db.session.add(Attendance(
        employee_id=request.form['emp_id'],
        status=request.form['status']
    ))
    db.session.commit()
    return redirect(url_for('attendance_page'))

# ---------------- RUN ----------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Create default user (first time only)
        if not User.query.filter_by(username="admin").first():
            db.session.add(User(username="admin", password="admin"))
            db.session.commit()

    app.run(debug=True)