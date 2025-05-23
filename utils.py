# utils
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as mticker
import numpy as np
import matplotlib.pyplot as plt
def error(text):
    """Hiển thị hộp thoại lỗi và in ra console."""
    print(f"[!] {text}")
    messagebox.showerror("[ Lỗi ]", text)

def add_graphs(cur, frame):
    # Cấu hình chung
    plt.style.use("dark_background")
    for p in ['text.color','axes.labelcolor','xtick.color','ytick.color']:
        plt.rcParams[p] = 'white'

    figs = []

    # 1. Nam vs Nữ
    cur.execute("SELECT gender, COUNT(*) FROM employees GROUP BY gender;")
    labels, sizes = zip(*cur.fetchall())
    colors = [ "#c993c5", "#83C5BE"]  # Female, Male

    fig1 = plt.Figure(figsize=(4,2.5), dpi=100)
    ax1  = fig1.add_subplot()
    wedges, texts, autotexts = ax1.pie(
        sizes,
        labels=labels,
        autopct="%.0f%%",
        colors=colors,
        startangle=90,
        pctdistance=0.6,
        textprops=dict(color="white", weight="bold")
    )
    ax1.set_title("Male Female Ratio")
    fig1.tight_layout()
    figs.append(fig1)




# 2) Cơ cấu theo phòng ban (bar chart)
    cur.execute("SELECT department, COUNT(*) FROM employees GROUP BY department;")
    depts, counts = zip(*cur.fetchall())

    fig2 = plt.Figure(figsize=(4,2.5), dpi=100)
    ax2  = fig2.add_subplot()
    bars = ax2.bar(depts, counts, width=0.6, color="#FF66CC")

    # tiêu đề và nhãn
    ax2.set_title("Department")
    ax2.set_ylabel("Number of employees")

    # xoay nhãn trục X
    for lbl in ax2.get_xticklabels():
        lbl.set_rotation(45)
        lbl.set_ha('right')

    # thêm số liệu lên giữa mỗi thanh
    for bar, cnt in zip(bars, counts):
        x = bar.get_x() + bar.get_width()/2
        y = cnt * 0.5
        ax2.text(
            x, y,
            f"{cnt}",
            ha="center", va="center",
            color="white", fontweight="bold"
        )

    fig2.tight_layout()
    figs.append(fig2)

# 3) Chi phí lương theo phòng ban
    cur.execute("""
        SELECT e.department, SUM(p.net_salary) AS total_cost
        FROM payroll p
        JOIN employees e ON p.employee_id = e.employee_id
        GROUP BY e.department
        ORDER BY total_cost DESC;
    """)
    data = cur.fetchall()
    if data:
        depts, costs = zip(*data)
        costs = [float(c) for c in costs]   # chuyển Decimal → float
    else:
        depts, costs = [], []

    fig3 = plt.Figure(figsize=(4,2.5), dpi=100)
    ax3 = fig3.add_subplot()
    bars3 = ax3.barh(depts, costs)
    ax3.set_title("Salary costs by department")
    ax3.set_xlabel("Total salary (USD)")

    # Thêm nhãn số liệu
    max_cost = max(costs) if costs else 0.0
    offset   = max_cost * 0.01
    for bar in bars3:
        w = float(bar.get_width())
        y = bar.get_y() + bar.get_height()/2
        # trước đây: ax3.text(w + offset, y, f"{w:.0f}", va='center')
        # giờ đặt label bên trong, canh phải của text sát mép bar:
        ax3.text(w - offset, y, f"{w:.0f}",
                 va='center', ha='right',
                 color='white')
    fig3.tight_layout()

    figs.append(fig3)
    # 5) Tổng lương đã chi trả theo tháng
    cur.execute("""
        SELECT 
            payroll_year,
            MONTH(CAST(payroll_year AS VARCHAR(4)) + '-' + RIGHT('00'+CAST(payroll_month AS VARCHAR),2) + '-01') AS month,
            SUM(net_salary) AS total_payout
        FROM payroll
        GROUP BY payroll_year, payroll_month
        ORDER BY payroll_year, payroll_month;
    """)
    rows = cur.fetchall()
    months = list(range(1, 13))
    data_by_year = {}
    for year, m, total in rows:
        data_by_year.setdefault(year, {})[m] = float(total)

    fig5 = plt.Figure(figsize=(6, 2.5), dpi=100)
    ax5  = fig5.add_subplot()
    for year in sorted(data_by_year):
        ydata = [ data_by_year[year].get(m, 0) for m in months ]
        ax5.plot(months, ydata, marker='o', label=str(year))

    ax5.set_title("Total salary paid per month")
    ax5.set_xlabel("Month")
    ax5.set_ylabel("Total salary (USD)")

    # X-ticks là 1–12
    ax5.set_xticks(months)
    ax5.set_xticklabels([str(m) for m in months])

    # --- CHỈNH LẠI TRỤC Y ---
    from matplotlib.ticker import MultipleLocator
    # mỗi vạch trên trục Y cách nhau 5000 USD
    ax5.yaxis.set_major_locator(MultipleLocator(5000))

    # thêm lưới ngang để dễ đọc
    ax5.grid(True, axis='y', linestyle='--', alpha=0.3)

    # Đẩy legend ra ngoài
    leg = ax5.legend(title="YEAR", loc="upper left", bbox_to_anchor=(1.02, 1))

    # Nới lề để nhãn và legend không bị cắt
    fig5.subplots_adjust(bottom=0.25, right=0.75)
    fig5.tight_layout()

    figs.append(fig5)

# 6) Top 3 bonus theo từng tháng (1–3)
    cur.execute("""
            WITH latest_year AS (
                SELECT MAX(payroll_year) AS year FROM payroll
            ), ranked_bonus AS (
                SELECT 
                    p.payroll_month,
                    e.full_name,
                    p.bonus,
                    RANK() OVER (
                        PARTITION BY p.payroll_month 
                        ORDER BY p.bonus DESC
                    ) AS rk
                FROM payroll p
                JOIN employees e ON p.employee_id = e.employee_id
                JOIN latest_year y ON p.payroll_year = y.year
                WHERE p.payroll_month BETWEEN 1 AND 3
            )
            SELECT payroll_month, full_name, bonus
            FROM ranked_bonus
            WHERE rk <= 3
            ORDER BY payroll_month, rk;
        """)
    rows = cur.fetchall()  # [(1,'Alice',…), (1,'Bob',…), (1,'Cathy',…), (2,'Dan',…),(2,'Eve',…), …]

    # Gom dữ liệu
    data = {}
    for m, name, bonus in rows:
        data.setdefault(m, []).append((name, float(bonus)))

    months = sorted(data.keys())      # [1,2,3]
    n_months = len(months)
    n_per    = max(len(v) for v in data.values())  # =3

    # Tọa độ tâm cho mỗi nhóm tháng
    group_width = 0.8
    gap         = 0.4
    centers     = np.arange(n_months) * (group_width + gap)

    # Chiều rộng mỗi cột và offsets để chia đều trong nhóm
    bar_w   = group_width / n_per
    offsets = (np.arange(n_per) - (n_per-1)/2) * bar_w

    # Lấy danh sách tên duy nhất để phân màu
    unique_names = []
    for lst in data.values():
        for name,_ in lst:
            if name not in unique_names:
                unique_names.append(name)
    cmap = plt.get_cmap("tab10")
    color_map = {name: cmap(i) for i,name in enumerate(unique_names)}

    # Vẽ
    fig6 = plt.Figure(figsize=(4,2.5), dpi=100)
    ax6  = fig6.add_subplot()

    for i, m in enumerate(months):
        center = centers[i]
        for j, (name, bonus) in enumerate(data[m]):
            x = center + offsets[j]
            ax6.bar(x, bonus,
                    width=bar_w,
                    color=color_map[name],
                    label=name)
            ax6.text(x, bonus ,
                     f"{bonus:.0f}",
                     ha="center", va="bottom",
                     color="white", fontweight="bold", fontsize=6)

    # Đặt nhãn tháng
    ax6.set_xticks(centers)
    ax6.set_xticklabels([f"Month {m}" for m in months])
    # ax6.set_xlabel("Tháng")
    ax6.set_ylabel("Total bonus (USD)")
    ax6.set_title("Quarter 1 2025's top 3 bonus earners")

    # Loại bỏ trùng legend và hiển thị
    handles, labels = ax6.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax6.legend(by_label.values(), by_label.keys(),
               title="Employee Name", bbox_to_anchor=(1.02,1), loc="upper left")

    fig6.subplots_adjust(bottom=0.25, right=0.75)
    fig6.tight_layout()
    left_lim  = centers[0] - group_width/2 - 0.1
    right_lim = centers[-1] + group_width/2 + 0.1
    ax6.set_xlim(left_lim, right_lim)
    figs.append(fig6)

# 7) Hiển thị tất cả charts theo grid 2×4
    # 1) Đặt 2 hàng, 6 cột đều giãn nở
    for r in (0,1):
        frame.grid_rowconfigure(r, weight=1)
    for c in range(6):
        frame.grid_columnconfigure(c, weight=1)

    # 2) Lặp qua figs và đặt vào grid
    for idx, fig in enumerate(figs):
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        widget = canvas.get_tk_widget()

        if idx < 3:
            # Hàng trên: mỗi chart chiếm 2 cột
            col = idx * 2
            widget.grid(
                row=0, column=col, columnspan=2,
                sticky="nsew", padx=20, pady=20
            )
        else:
            # Hàng dưới: 2 chart chia đều, mỗi cái span 3 cột
            if idx == 3:
                # chart thứ 4 (idx=3): cột 0–2
                widget.grid(
                    row=1, column=0, columnspan=3,
                    sticky="nsew", padx=20, pady=20
                )
            else:  # idx == 4
                # chart thứ 5 (idx=4): cột 3–5
                widget.grid(
                    row=1, column=3, columnspan=3,
                    sticky="nsew", padx=20, pady=20
                )
