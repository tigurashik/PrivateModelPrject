from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import random
import string

app = Flask(__name__)

# Функция для connect PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        dbname="kapinosa2",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    return conn

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Routes

# Отображение и добавление служащих
@app.route('/employee', methods=['GET', 'POST'])
def show_employee():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        payment_method = request.form['payment_method']
        rate = request.form['rate']
        salary_type = request.form['salary_type']
        cur.execute("""
            INSERT INTO employee (name, address, payment_method, rate, salary_type)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, address, payment_method, rate, salary_type))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('show_employee'))
    else:
        cur.execute('SELECT * FROM employee;')
        employees = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('employee.html', employees=employees)

# Удаление служащего
@app.route('/employee/delete/<int:id>')
def delete_employee(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM employee WHERE id_employee = %s;', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('show_employee'))

# Назначение служащего администратором
@app.route('/employee/promote/<int:id>')
def promote_employee(id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Получаем имя служащего
    cur.execute('SELECT name FROM employee WHERE id_employee = %s;', (id,))
    employee = cur.fetchone()
    if employee:
        name = employee[0]
        # Генерируем случайный пароль
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        # Уровень доступа по умолчанию
        access_rights = 'Неполный доступ'
        # Добавляем запись в таблицу administrator
        cur.execute("""
            INSERT INTO administrator (name, access_rights, password)
            VALUES (%s, %s, %s);
        """, (name, access_rights, password))
        conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('show_employee'))

# Отображение администраторов
@app.route('/administrator')
def show_administrator():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM administrator;')
    administrators = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('administrator.html', administrators=administrators)

# Удаление администратора
@app.route('/administrator/delete/<int:id>')
def delete_administrator(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM administrator WHERE id_administrator = %s;', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('show_administrator'))


# Отображение и добавление заказов
@app.route('/orders', methods=['GET', 'POST'])
def show_orders():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        sales_volume = request.form['sales_volume']
        date = request.form['date']
        employee_id = request.form['employee_id']
        cur.execute("""
            INSERT INTO orders (sales_volume, date, employee_id)
            VALUES (%s, %s, %s)
        """, (sales_volume, date, employee_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('show_orders'))
    else:
        cur.execute('''
            SELECT orders.id_order, employee.name, orders.sales_volume, orders.date
            FROM orders
            JOIN employee ON orders.employee_id = employee.id_employee
            ORDER BY orders.date DESC;
        ''')
        orders = cur.fetchall()
        cur.execute('SELECT id_employee, name FROM employee;')
        employees = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('orders.html', orders=orders, employees=employees)

# Удаление заказа
@app.route('/orders/delete/<int:id>')
def delete_order(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM orders WHERE id_order = %s;', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('show_orders'))

# Отображение и добавление зарплат
@app.route('/salary', methods=['GET', 'POST'])
def show_salary():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        accrual_date = request.form['accrual_date']
        employee_id = request.form['employee_id']
        amount = request.form['amount']
        cur.execute("""
            INSERT INTO salary (accrual_date, employee_id, amount)
            VALUES (%s, %s, %s)
        """, (accrual_date, employee_id, amount))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('show_salary'))
    else:
        cur.execute('''
            SELECT salary.id_salary, employee.name, employee.id_employee, salary.accrual_date, salary.amount
            FROM salary
            JOIN employee ON salary.employee_id = employee.id_employee
            ORDER BY salary.accrual_date DESC;
        ''')
        salaries = cur.fetchall()
        cur.execute('SELECT id_employee, name FROM employee;')
        employees = cur.fetchall()
        cur.execute('''
            SELECT employee.id_employee, employee.name, SUM(salary.amount)
            FROM salary
            JOIN employee ON salary.employee_id = employee.id_employee
            GROUP BY employee.id_employee, employee.name;
        ''')
        total_salaries = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('salary.html', salaries=salaries, employees=employees, total_salaries=total_salaries)

# Удаление записи о зарплате
@app.route('/salary/delete/<int:id>')
def delete_salary(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM salary WHERE id_salary = %s;', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('show_salary'))

# Отображение и изменение комиссий
@app.route('/commission', methods=['GET', 'POST'])
def show_commission():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        new_percentage = request.form['percentage']
        cur.execute('SELECT * FROM commission WHERE employee_id = %s;', (employee_id,))
        commission = cur.fetchone()
        if commission:
            cur.execute('UPDATE commission SET percentage = %s WHERE employee_id = %s;',
                        (new_percentage, employee_id))
        else:
            cur.execute("""
                INSERT INTO commission (percentage, sales_volume, employee_id)
                VALUES (%s, 0, %s);
            """, (new_percentage, employee_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('show_commission'))
    else:
        cur.execute('''
            SELECT e.id_employee, e.name, COALESCE(c.percentage, 0), COALESCE(SUM(o.sales_volume), 0)
            FROM employee e
            LEFT JOIN commission c ON e.id_employee = c.employee_id
            LEFT JOIN orders o ON e.id_employee = o.employee_id
            GROUP BY e.id_employee, e.name, c.percentage;
        ''')
        commissions = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('commission.html', commissions=commissions)

# Отображение и добавление записей учета рабочего времени
@app.route('/time_tracking', methods=['GET', 'POST'])
def show_time_tracking():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        date = request.form['date']
        hours_worked = request.form['hours_worked']
        rate = request.form['rate']
        employee_id = request.form['employee_id']
        cur.execute("""
            INSERT INTO time_tracking (date, hours_worked, rate, employee_id)
            VALUES (%s, %s, %s, %s)
        """, (date, hours_worked, rate, employee_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('show_time_tracking'))
    else:
        cur.execute('''
            SELECT tt.id_tracking, tt.date, tt.hours_worked, tt.rate, e.name
            FROM time_tracking tt
            JOIN employee e ON tt.employee_id = e.id_employee
            ORDER BY tt.date DESC;
        ''')
        time_trackings = cur.fetchall()
        cur.execute('SELECT id_employee, name FROM employee;')
        employees = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('time_tracking.html', time_trackings=time_trackings, employees=employees)

# Удаление записи учета рабочего времени
@app.route('/time_tracking/delete/<int:id>')
def delete_time_tracking(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM time_tracking WHERE id_tracking = %s;', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('show_time_tracking'))

# Отображение и запрос отпусков
@app.route('/leave', methods=['GET', 'POST'])
def show_leave():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        start_date = request.form['start_date']
        number_of_days = int(request.form['number_of_days'])
        cur.execute("""
            INSERT INTO leave (start_date, number_of_days, employee_id)
            VALUES (%s, %s, %s)
        """, (start_date, number_of_days, employee_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('show_leave'))
    else:
        cur.execute('''
            SELECT e.id_employee, e.name, 14 - COALESCE(SUM(l.number_of_days), 0) AS remaining_days
            FROM employee e
            LEFT JOIN leave l ON e.id_employee = l.employee_id
            GROUP BY e.id_employee, e.name;
        ''')
        leaves = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('leave.html', leaves=leaves)

if __name__ == '__main__':
    app.run(debug=True)
