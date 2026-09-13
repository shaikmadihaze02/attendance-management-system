
import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import date


# =========================================================
# DATABASE
# =========================================================

connection = sqlite3.connect("attendance.db")
cursor = connection.cursor()

# Student table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
)
""")

# Attendance table
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT NOT NULL,
    attendance_date TEXT NOT NULL,
    status TEXT NOT NULL
)
""")

connection.commit()


# =========================================================
# ADD STUDENT
# =========================================================

def add_student():

    roll_no = roll_entry.get().strip()
    name = name_entry.get().strip()

    if roll_no == "" or name == "":
        messagebox.showwarning(
            "Warning",
            "Please enter Roll Number and Student Name."
        )
        return

    try:

        cursor.execute(
            "INSERT INTO students (roll_no, name) VALUES (?, ?)",
            (roll_no, name)
        )

        connection.commit()

        messagebox.showinfo(
            "Success",
            "Student added successfully!"
        )

        roll_entry.delete(0, tk.END)
        name_entry.delete(0, tk.END)

    except sqlite3.IntegrityError:

        messagebox.showerror(
            "Error",
            "This Roll Number already exists."
        )


# =========================================================
# MARK ATTENDANCE
# =========================================================

def mark_attendance(status):

    roll_no = roll_entry.get().strip()

    if roll_no == "":
        messagebox.showwarning(
            "Warning",
            "Please enter Roll Number."
        )
        return

    # Check whether student exists
    cursor.execute(
        "SELECT name FROM students WHERE roll_no = ?",
        (roll_no,)
    )

    student = cursor.fetchone()

    if student is None:

        messagebox.showerror(
            "Error",
            "Student not found. Please add the student first."
        )
        return

    student_name = student[0]

    today = str(date.today())

    # Check whether attendance is already marked
    cursor.execute(
        """
        SELECT * FROM attendance
        WHERE roll_no = ? AND attendance_date = ?
        """,
        (roll_no, today)
    )

    existing = cursor.fetchone()

    if existing:

        messagebox.showwarning(
            "Already Marked",
            "Attendance is already marked for this student today."
        )
        return

    # Save attendance
    cursor.execute(
        """
        INSERT INTO attendance
        (roll_no, attendance_date, status)
        VALUES (?, ?, ?)
        """,
        (roll_no, today, status)
    )

    connection.commit()

    messagebox.showinfo(
        "Attendance",
        f"{student_name} marked {status}."
    )

    roll_entry.delete(0, tk.END)


# =========================================================
# VIEW STUDENTS
# =========================================================

def view_students():

    window = tk.Toplevel(root)

    window.title("Student List")
    window.geometry("550x450")

    title = tk.Label(
        window,
        text="STUDENT LIST",
        font=("Arial", 18, "bold")
    )

    title.pack(pady=15)

    student_text = tk.Text(
        window,
        width=60,
        height=20,
        font=("Arial", 11)
    )

    student_text.pack(padx=10, pady=10)

    cursor.execute(
        "SELECT roll_no, name FROM students ORDER BY roll_no"
    )

    students = cursor.fetchall()

    if not students:

        student_text.insert(
            tk.END,
            "No students added yet."
        )

    else:

        student_text.insert(
            tk.END,
            "ROLL NUMBER\t\tNAME\n"
        )

        student_text.insert(
            tk.END,
            "-" * 50 + "\n"
        )

        for roll_no, name in students:

            student_text.insert(
                tk.END,
                f"{roll_no}\t\t{name}\n"
            )


# =========================================================
# ATTENDANCE REPORT
# =========================================================

def view_report():

    window = tk.Toplevel(root)

    window.title("Attendance Report")
    window.geometry("650x500")

    title = tk.Label(
        window,
        text="ATTENDANCE REPORT",
        font=("Arial", 18, "bold")
    )

    title.pack(pady=15)

    report_text = tk.Text(
        window,
        width=75,
        height=25,
        font=("Arial", 10)
    )

    report_text.pack(padx=10, pady=10)

    cursor.execute(
        "SELECT roll_no, name FROM students ORDER BY roll_no"
    )

    students = cursor.fetchall()

    if not students:

        report_text.insert(
            tk.END,
            "No students available."
        )

        return

    for roll_no, name in students:

        # Total attendance records
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM attendance
            WHERE roll_no = ?
            """,
            (roll_no,)
        )

        total = cursor.fetchone()[0]

        # Number of presents
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM attendance
            WHERE roll_no = ?
            AND status = 'Present'
            """,
            (roll_no,)
        )

        present = cursor.fetchone()[0]

        # Number of absents
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM attendance
            WHERE roll_no = ?
            AND status = 'Absent'
            """,
            (roll_no,)
        )

        absent = cursor.fetchone()[0]

        # Percentage
        if total > 0:

            percentage = (present / total) * 100

        else:

            percentage = 0

        report_text.insert(
            tk.END,
            f"Roll Number : {roll_no}\n"
            f"Name        : {name}\n"
            f"Present     : {present}\n"
            f"Absent      : {absent}\n"
            f"Total Days  : {total}\n"
            f"Percentage  : {percentage:.2f}%\n"
        )

        report_text.insert(
            tk.END,
            "-" * 60 + "\n"
        )


# =========================================================
# VIEW TODAY'S ATTENDANCE
# =========================================================

def today_attendance():

    window = tk.Toplevel(root)

    window.title("Today's Attendance")
    window.geometry("600x450")

    title = tk.Label(
        window,
        text="TODAY'S ATTENDANCE",
        font=("Arial", 18, "bold")
    )

    title.pack(pady=15)

    text = tk.Text(
        window,
        width=65,
        height=22,
        font=("Arial", 11)
    )

    text.pack(padx=10, pady=10)

    today = str(date.today())

    cursor.execute(
        """
        SELECT students.roll_no,
               students.name,
               attendance.status
        FROM students
        LEFT JOIN attendance
        ON students.roll_no = attendance.roll_no
        AND attendance.attendance_date = ?
        ORDER BY students.roll_no
        """,
        (today,)
    )

    records = cursor.fetchall()

    text.insert(
        tk.END,
        f"Date: {today}\n\n"
    )

    text.insert(
        tk.END,
        "ROLL NO\t\tNAME\t\tSTATUS\n"
    )

    text.insert(
        tk.END,
        "-" * 60 + "\n"
    )

    for roll_no, name, status in records:

        if status is None:
            status = "Not Marked"

        text.insert(
            tk.END,
            f"{roll_no}\t\t{name}\t\t{status}\n"
        )


# =========================================================
# MAIN WINDOW
# =========================================================

root = tk.Tk()

root.title("Attendance Management System")

root.geometry("550x650")

root.resizable(False, False)


# =========================================================
# TITLE
# =========================================================

title = tk.Label(
    root,
    text="ATTENDANCE MANAGEMENT SYSTEM",
    font=("Arial", 20, "bold")
)

title.pack(pady=25)


# =========================================================
# ROLL NUMBER
# =========================================================

roll_label = tk.Label(
    root,
    text="Roll Number",
    font=("Arial", 12)
)

roll_label.pack()

roll_entry = tk.Entry(
    root,
    width=35,
    font=("Arial", 12)
)

roll_entry.pack(pady=8)


# =========================================================
# STUDENT NAME
# =========================================================

name_label = tk.Label(
    root,
    text="Student Name",
    font=("Arial", 12)
)

name_label.pack()

name_entry = tk.Entry(
    root,
    width=35,
    font=("Arial", 12)
)

name_entry.pack(pady=8)


# =========================================================
# BUTTONS
# =========================================================

add_button = tk.Button(
    root,
    text="Add Student",
    width=30,
    font=("Arial", 12),
    command=add_student
)

add_button.pack(pady=10)


present_button = tk.Button(
    root,
    text="Mark Present",
    width=30,
    font=("Arial", 12),
    command=lambda: mark_attendance("Present")
)

present_button.pack(pady=5)


absent_button = tk.Button(
    root,
    text="Mark Absent",
    width=30,
    font=("Arial", 12),
    command=lambda: mark_attendance("Absent")
)

absent_button.pack(pady=5)


students_button = tk.Button(
    root,
    text="View Students",
    width=30,
    font=("Arial", 12),
    command=view_students
)

students_button.pack(pady=10)


today_button = tk.Button(
    root,
    text="Today's Attendance",
    width=30,
    font=("Arial", 12),
    command=today_attendance
)

today_button.pack(pady=5)


report_button = tk.Button(
    root,
    text="View Attendance Report",
    width=30,
    font=("Arial", 12),
    command=view_report
)

report_button.pack(pady=10)


# =========================================================
# RUN APPLICATION
# =========================================================

root.mainloop()


# Close database when application ends
connection.close()
