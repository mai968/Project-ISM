import pyodbc
from login import Login
from menu import Menu

class Main:
    def __init__(self):
        try:
            self.con = pyodbc.connect(
                'DRIVER={SQL Server};'
                'SERVER=ADMIN-PC\\SQLEXPRESS;'
                'DATABASE=master;'
                'Trusted_Connection=yes;',
                autocommit=True
            )

            print('* Connected to SQL Server')
            self.cur = self.con.cursor()
        except Exception as e:
            print('[!] Not connected to SQL Server:', e)
            return

        # Create DB if not exists
        # Check if DB exists
        self.cur.execute("SELECT name FROM sys.databases WHERE name = 'HRM'")
        db_exists = self.cur.fetchone()

        if not db_exists:
            self.cur.execute("CREATE DATABASE HRM")
            self.con.commit()
            print('* Database "HRM" created')
        else:
            print('* Database "HRM" already exists')


        # Switch to inventory DB
        self.con.close()
        self.con = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=ADMIN-PC\\SQLEXPRESS;'
            'DATABASE=HRM;'
            'Trusted_Connection=yes;'
        )
        self.cur = self.con.cursor()

        # Create tables if not exist
        self.cur.execute("""
        IF OBJECT_ID('users', 'U') IS NULL
        CREATE TABLE users (
            username VARCHAR(20) PRIMARY KEY,
            password VARCHAR(20) NOT NULL,
            account_type VARCHAR(10) NOT NULL
        )""")

         # ADMIN account = HR management


        # Tạo bảng employees
        self.cur.execute("""
        IF OBJECT_ID('employees', 'U') IS NULL
        CREATE TABLE employees (
            employee_id VARCHAR(10) PRIMARY KEY,
            full_name NVARCHAR(100),
            gender VARCHAR(10),
            date_of_birth DATE,
            department NVARCHAR(100),
            position NVARCHAR(100),
            date_joined DATE,
            status VARCHAR(20)
        )""")

        # Tạo bảng attendance
        self.cur.execute("""
        IF OBJECT_ID('attendance', 'U') IS NULL
        CREATE TABLE attendance (
            employee_id VARCHAR(15),
            date DATE,
            check_in TIME,
            check_out TIME,
            working_hours FLOAT,
            status VARCHAR(20),

        )""")

        # Tạo bảng leave_request
        self.cur.execute("""
        IF OBJECT_ID('leave_request', 'U') IS NULL
        CREATE TABLE leave_request (
            request_id VARCHAR(15) PRIMARY KEY,
            employee_id VARCHAR(15),
            start_date DATE,
            end_date DATE,
            leave_type VARCHAR(50),
            reason NVARCHAR(255),
            status VARCHAR(20),
        )""")

        # Tạo bảng payroll
        self.cur.execute("""
        IF OBJECT_ID('payroll', 'U') IS NULL
        CREATE TABLE payroll (
            payroll_id VARCHAR(15) PRIMARY KEY,
            employee_id VARCHAR(15),
            payroll_year INT,
            payroll_month INT,
            base_salary DECIMAL(18, 2),
            bonus DECIMAL(18, 2),
            deductions DECIMAL(18, 2),
            net_salary AS (base_salary + bonus - deductions) PERSISTED,
        )""")

        # Tạo bảng performance_reviews
        self.cur.execute("""
        IF OBJECT_ID('performance_reviews', 'U') IS NULL
        CREATE TABLE performance_reviews (
            review_id VARCHAR(15) PRIMARY KEY,
            employee_id VARCHAR(15),
            review_year INT,
            review_quarter INT,
            score FLOAT,
            reviewer NVARCHAR(225),
            feedback NVARCHAR(300),
        )""")

        print("* All HRM tables created or already exist.")

        self.con.commit()

        # Launch login
        self.login = Login(self.con)
        self.login.window.mainloop()

        if self.login.user:
            self.menu = Menu(self.con, self.login.user, self.login.window)
            self.menu.window.mainloop()

            if self.menu.logout:
                Main()

if __name__ == "__main__":
    m = Main()

