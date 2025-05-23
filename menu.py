import tkinter
from tkinter import ttk , messagebox
from datetime import date
import customtkinter as ctk
from PIL import Image

from utils import error , add_graphs

class Menu():
    """Represents a menu for the HR management system."""

    def __init__(self, con, user, login_win):
        # Set window theme as dark
        ctk.set_default_color_theme("dark-blue")
        ctk.set_appearance_mode("dark")
        # ctk.deactivate_automatic_dpi_awareness()
        self.login_win = login_win
        self.window =  ctk.CTkToplevel(self.login_win)
        self.window.protocol("WM_DELETE_WINDOW", exit)
        self.con = con
        self.cur = con.cursor()
        self.user = user
        self.font = 'Century Gothic'
        self.make_window()

    def make_window(self):
        # Center window
        width, height = 1350, 740
        sw, sh = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
        x, y = (sw - width)//2, (sh - height)//2
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        if self.login_win:
            self.login_win.withdraw()
        self.make_panel()


    def make_panel(self):
        """ Create side panel or navigation panel"""
        side_panel = ctk.CTkFrame(self.window, corner_radius=0, width=250)
        side_panel.pack(fill="y", side="left")

        section_functions = {
            "dashboard": self.dashboard,
            "employees": self.employees,
            "attendance": self.attendance,
            "payroll": self.payroll,
            # "shop": self.shop,
            # "history": self.history,
            "logout": self.logout
        }

        # Add buttons for different sections in the side panel
        if self.user[2] == 'ADMIN':
            sections = ["dashboard", "employees", "attendance", "payroll", "logout"]
        else:
            sections = ["dashboard", "attendance", "logout"]

        for section in sections:
            img = ctk.CTkImage(Image.open(f"./imgs/{section}.png").resize((30,30)),size=(30,30))
            button = ctk.CTkButton(side_panel, text=section.title(), image= img, anchor="w", font=(self.font, 18),fg_color="transparent", hover_color="#212121", command=section_functions[section])
            button.pack(padx=50,pady=50)

        self.frame = ctk.CTkFrame(self.window, corner_radius=0 ,fg_color="#1a1a1a")
        self.frame.pack(fill="both", expand=True)
        self.dashboard()

    def set_title(self, title):
        """
        Sets the title of the user interface window.
        Args:
            title (str): The title to set for the window.
        """
        try:
            self.frame.forget()
            self.frame = ctk.CTkFrame(self.window, corner_radius=0 ,fg_color="#1a1a1a")
            self.frame.pack(fill="both", expand=True)

        except:
            pass
        self.window.title(title)
        heading = ctk.CTkLabel(self.frame, text=title, anchor="center", font=(self.font, 33) )
        heading.pack()


    def dashboard(self):
        # 1) Window title
        self.set_title("Dashboard")
 
        # 2) KPI cards
        self.cur.execute("SELECT COUNT(*) FROM employees;")
        total = self.cur.fetchone()[0]
        self.cur.execute("SELECT COUNT(*) FROM employees WHERE status='Active';")
        active = self.cur.fetchone()[0]
        self.cur.execute("SELECT COUNT(*) FROM employees WHERE status='Resigned';")
        resigned = self.cur.fetchone()[0]
        rate = (resigned/total) if total else 0
 
        kpi_frame = ctk.CTkFrame(self.frame)
        kpi_frame.pack(fill="x", padx=20, pady=(20,10))
        cards = [
            ("Total number of employees", total,       "#AEC6CF", "#2F4F4F"),  # Pastel Blue + Slate Gray
            ("Number of employees working", active,     "#77DD77", "#006400"),  # Pastel Green + Dark Green
            ("Number of employees leaving", resigned, "#FFB7CE", "#DC143C"),  # Pastel Pink + Crimson
            ("Employee turnover rate", f"{rate:.0%}", "#FDFD96", "#DAA520")  # Pastel Yellow + Goldenrod
        ]
 
        # Mỗi cột sẽ giãn đều
        for i in range(len(cards)):
            kpi_frame.grid_columnconfigure(i, weight=1)
 
        for i,(lbl,val,bg_color,fg_color) in enumerate(cards):
            card = ctk.CTkFrame(kpi_frame, fg_color=bg_color, corner_radius=10)
            # sticky="nsew" để card tự giãn cả chiều ngang và dọc
            card.grid(row=0, column=i, sticky="nsew", padx=10, pady=5)
 
            # Giãn label ở trong card để căn giữa
            ctk.CTkLabel(card,
                         text=val,
                         font=(self.font, 30),
                         text_color=fg_color).pack(expand=True)
            ctk.CTkLabel(card,
                         text=lbl,
                         font=(self.font, 15),
                         text_color=fg_color).pack(pady=(0,5), expand=True)
 
 
 
    # 3) Charts area: grid 2x3
        graph_frame = ctk.CTkFrame(self.frame)
        graph_frame.pack(fill="both", expand=True, padx=20, pady=20)
        add_graphs(self.cur, graph_frame)
 

    def employees(self):
        """ Displays the employees section of the user interface. """
        self.set_title("Employees")
        if self.user[2] == 'ADMIN':
            add_button = ctk.CTkButton(self.frame, width=50, command=self.add_button, text="Add Item", fg_color="#007fff", font=(self.font , 20))
            add_button.place(x=50,y=50)
        self.make_table(("Employee ID", "Name", "Gender" ,"DateBirth", 
                         "Department", "Position", "DateJoined", "Status"), 
                        130,
                        "employees")

    def attendance(self):
        """ Displays the attendance section of the user interface. """
        self.set_title("Attendance")
        self.make_table(("Employee ID", "Date", "Check in", "Check out", "Working hours", "Status"), 170 ,"attendance")

    def payroll(self):
        """ Displays all the payroll placed in the system."""
        self.set_title("Payroll")
        headings = ("Payroll Id", "Employee ID", "Payroll year", "Payroll month", "Base salary", "Bonus", "Deductions", "Net Salary")
        self.make_table(headings, 130, "payroll")


    def add_button(self):
        """Displays entry fields inside the main frame to add a new employee."""

        # Xóa nội dung cũ trong self.frame
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Tiêu đề
        title = ctk.CTkLabel(self.frame, text="Add New Employee", font=(self.font, 22, 'bold'))
        title.pack(pady=10)

        # Các field
        self.product_entries = {}
        items = ["Employee ID", "Name", "Gender", "DateBirth", 
                 "Department", "Position", "DateJoined", "Status"]

        for label_text in items:
            label = ctk.CTkLabel(self.frame, text=label_text, font=(self.font, 16))
            label.pack(pady=(8, 0))

            entry = ctk.CTkEntry(self.frame, placeholder_text=label_text, width=400, height=35)
            entry.pack(pady=4)
            self.product_entries[label_text] = entry

        # Nút Add
        add_btn = ctk.CTkButton(self.frame, text="Add Employee", command=self.add_emp, width=300, height=40, font=(self.font, 18))
        add_btn.pack(pady=10)


    def add_emp(self):
        """Creates a new employee in the system by registering the provided details in the SQL Server."""

        e_id = self.product_entries['Employee ID'].get().strip()
        name = self.product_entries['Name'].get().strip()
        gender = self.product_entries['Gender'].get().strip()
        dob = self.product_entries['DateBirth'].get().strip()
        dept = self.product_entries['Department'].get().strip()
        position = self.product_entries['Position'].get().strip()
        date_joined = self.product_entries['DateJoined'].get().strip()
        status = self.product_entries['Status'].get().strip()

        
            # Kiểm tra ID đã tồn tại chưa
        self.cur.execute("SELECT * FROM employees WHERE employee_id = ?", (e_id,))
        existing = self.cur.fetchall()

        if existing:
            messagebox.showerror("ERROR", "Employee ID already exists.")
            return

        if len(position) > 50:
            messagebox.showerror("ERROR", "Position must be less than 50 characters.")
            return

            # Thêm vào cơ sở dữ liệu
        self.cur.execute(
                """
                INSERT INTO employees 
                (employee_id, full_name, gender, date_of_birth, department, position, date_joined, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (e_id, name, gender, dob, dept, position, date_joined, status)
            )
        self.con.commit()
        messagebox.showinfo("Success", "Employee added successfully!")

            # Đóng form
        self.topwin.destroy()

            # Cập nhật lại bảng hiển thị nếu có
        self.tree.delete(*self.tree.get_children())
        self.render_table("employees")


           

    def fill_labels(self, choice):
        """ Fills labels with data of a particular item chosen by user"""
        self.cur.execute(f"SELECT quantity, price  FROM products WHERE product_name='{choice}';")
        fetch = self.cur.fetchall()[0]
        self.spin_var = ctk.IntVar(value=1)
        x = 250
        try:
            self.price_label.place_forget()
            self.quantity_label.place_forget()
            self.spinbox.place_forget()
        except:
            pass

        self.quantity_label = ctk.CTkLabel(self.win_frame, text=fetch[0], font=(self.font, 20))
        self.quantity_label.place(x=x,y=100)
        self.price_label = ctk.CTkLabel(self.win_frame, text=fetch[1], font=(self.font, 20))
        self.price_label.place(x=x,y=160)

        style = ttk.Style()
        style.configure("TSpinbox", fieldbackground="#343638", foreground="white", background="#343638")

        self.spinbox = ttk.Spinbox(self.win_frame, from_=1, to=fetch[0], textvariable=self.spin_var, style="TSpinbox")
        self.spinbox.place(x=x ,y=220)

        
    def logout(self):
        """
        Logout the current user: close the dashboard window and return to login screen.
        """
        # Close the dashboard window
        self.window.destroy()
        try:
            # If login window was passed in, show it again
            if self.login_win:
                self.login_win.deiconify()
                return
        except:
            pass
        # Otherwise, launch a fresh login window
        from login import Login
        login = Login(self.con)
        login.window.mainloop()

    def make_table(self, col, width, table=None, height=600):
        """Create a tkinter treeview table with specified columns, column widths, and optional data source table.

            Args:
                col (tuple): Tuple of column names.
                width (list): List of column widths.
                table (str, optional): Name of the table. Defaults to None.
                height (int, optional): Height of the table. Defaults to 600.
            """
        tableframe = ctk.CTkScrollableFrame(self.frame, width=1000,height=height)
        tableframe.place(x=1070, y=100, anchor=tkinter.NE )
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                            background="#2a2d2e",
                            foreground="white",
                            rowheight=25,
                            fieldbackground="#343638",
                            bordercolor="#343638",
                            borderwidth=0)
        style.map('Treeview', background=[('selected', '#007fff')])

        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        style.map("Treeview.Heading",
                    background=[('active', '#3484F0')])
        self.tree = ttk.Treeview(tableframe, columns=col,
        selectmode="browse", height=100)

        for i, value in enumerate(col):
            print(value, "=", i)
            if value == 'Price':
                w = 300
            else:
                w = 0 if i==0 else width
            self.tree.column(f'#{i}', stretch=tkinter.NO, minwidth=30, width=w)
            self.tree.heading(value, text=value, anchor=tkinter.W)


        self.tree.grid(row=1, column=0, sticky="W")
        self.tree.pack(fill="both", expand=True)
        if table:
            self.render_table(table)

    def render_table(self, table=None, items=None, query=None):
        """Render data from the database table into a Tkinter TreeView."""
        print(f"[INFO] Rendering table: {table}, query: {bool(query)}, items: {bool(items)}")

        if query:
            self.cur.execute(query)
            items = self.cur.fetchall()
        elif table:
            self.cur.execute(f"SELECT * FROM {table};")
            items = self.cur.fetchall()
        elif items is None:
            print("❗ Không có dữ liệu để hiển thị")
            return

        for i in items:
            if table == "employees":
                values = (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7])
            elif table == "attendance":
                values = (i[0], i[1], i[2], i[3], i[4], i[5])
            elif table == "payroll":
                values = (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7])
            else:
                values = tuple(i)

            existing_item = None
            for item in self.tree.get_children():
                if self.tree.item(item, 'values')[0] == values[0]:
                    existing_item = item
                    break

            if existing_item:
                self.tree.item(existing_item, values=values)
            else:
                self.tree.insert('', 'end', values=values)

