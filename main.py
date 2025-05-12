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
        self.cur.execute("SELECT name FROM sys.databases WHERE name = 'inventory'")
        db_exists = self.cur.fetchone()

        if not db_exists:
            self.cur.execute("CREATE DATABASE inventory")
            self.con.commit()
            print('* Database "inventory" created')
        else:
            print('* Database "inventory" already exists')


        # Switch to inventory DB
        self.con.close()
        self.con = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=ADMIN-PC\\SQLEXPRESS;'
            'DATABASE=inventory;'
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

        self.cur.execute("""
        IF OBJECT_ID('products', 'U') IS NULL
        CREATE TABLE products (
            product_id VARCHAR(20) PRIMARY KEY,
            product_name VARCHAR(50) NOT NULL,
            description VARCHAR(50) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            quantity INT NOT NULL
        )""")

        self.cur.execute("""
        IF OBJECT_ID('orders', 'U') IS NULL
        CREATE TABLE orders (
            order_id INT PRIMARY KEY,
            customer VARCHAR(20),
            date DATE,
            total_items INT,
            total_amount DECIMAL(10, 2),
            payment_status VARCHAR(20)
        )""")

        self.cur.execute("""
        IF OBJECT_ID('order_items', 'U') IS NULL
        CREATE TABLE order_items (
            order_item_id INT PRIMARY KEY,
            order_id INT,
            product_id VARCHAR(20),
            quantity INT NOT NULL,
            price DECIMAL(10, 2) NOT NULL
        )""")

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

