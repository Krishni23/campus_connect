import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import sqlite3
import hashlib
import datetime
import os
import shutil

# Create folder for storing uploaded PDFs
if not os.path.exists('uploaded_notes'):
    os.makedirs('uploaded_notes')

# Database setup
conn = sqlite3.connect('campus_contact.db')
c = conn.cursor()

# Create tables if not exist
c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subject TEXT,
                topic TEXT,
                filename TEXT,
                timestamp TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS doubts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subject TEXT,
                question TEXT,
                timestamp TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )''')

conn.commit()

# Functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    try:
        hashed = hash_password(password)
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        messagebox.showinfo("Success", "Registration successful!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists.")

def login_user(username, password):
    hashed = hash_password(password)
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed))
    return c.fetchone()

def upload_pdf_note(user_id, subject, topic):
    file_path = filedialog.askopenfilename(
        title="Select PDF file",
        filetypes=(("PDF Files", "*.pdf"),)
    )
    if not file_path:
        messagebox.showerror("Error", "No file selected.")
        return

    filename = os.path.basename(file_path)
    dest_path = os.path.join('uploaded_notes', filename)

    # Avoid overwriting by renaming if file exists
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(dest_path):
        filename = f"{base}_{counter}{ext}"
        dest_path = os.path.join('uploaded_notes', filename)
        counter += 1

    shutil.copy(file_path, dest_path)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO notes (user_id, subject, topic, filename, timestamp) VALUES (?, ?, ?, ?, ?)",
              (user_id, subject, topic, filename, timestamp))
    conn.commit()
    messagebox.showinfo("Success", f"{filename} uploaded successfully.")

def search_notes(keyword, text_area):
    c.execute("SELECT subject, topic, filename, timestamp FROM notes WHERE subject LIKE ? OR topic LIKE ?",
              ('%' + keyword + '%', '%' + keyword + '%'))
    results = c.fetchall()
    text_area.delete('1.0', tk.END)
    if results:
        for note in results:
            note_text = f"Subject: {note[0]}\nTopic: {note[1]}\nFile: {note[2]}\nUploaded on: {note[3]}\n{'-'*50}\n"
            text_area.insert(tk.END, note_text)
    else:
        text_area.insert(tk.END, "No notes found.")

def post_doubt(user_id, subject, question):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO doubts (user_id, subject, question, timestamp) VALUES (?, ?, ?, ?)",
              (user_id, subject, question, timestamp))
    conn.commit()
    messagebox.showinfo("Success", "Doubt posted.")

def view_doubts(text_area):
    c.execute("SELECT doubts.id, users.username, subject, question, timestamp FROM doubts JOIN users ON doubts.user_id = users.id ORDER BY timestamp DESC")
    doubts = c.fetchall()
    text_area.delete('1.0', tk.END)
    for doubt in doubts:
        doubt_text = f"ID: {doubt[0]}\nBy: {doubt[1]}\nSubject: {doubt[2]}\nDate: {doubt[4]}\nQuestion: {doubt[3]}\n{'-'*50}\n"
        text_area.insert(tk.END, doubt_text)

# GUI Class
class CampusContactApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Campus Contact")
        self.user_id = None
        self.create_login_screen()

    def create_login_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        tk.Label(self.master, text="Username:").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.master, text="Password:").grid(row=1, column=0, padx=10, pady=10)

        self.username_entry = tk.Entry(self.master)
        self.password_entry = tk.Entry(self.master, show="*")

        self.username_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.master, text="Login", command=self.login).grid(row=2, column=0, pady=10)
        tk.Button(self.master, text="Register", command=self.register).grid(row=2, column=1, pady=10)

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username and password:
            register_user(username, password)
        else:
            messagebox.showerror("Error", "Please enter both fields.")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = login_user(username, password)
        if user:
            self.user_id = user[0]
            self.create_main_screen()
        else:
            messagebox.showerror("Error", "Invalid credentials.")

    def create_main_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        tk.Label(self.master, text="Welcome to Campus Contact!").pack(pady=10)

        tk.Button(self.master, text="Upload Note (PDF)", command=self.upload_note_screen).pack(pady=5)
        tk.Button(self.master, text="Search Notes", command=self.search_notes_screen).pack(pady=5)
        tk.Button(self.master, text="Post Doubt", command=self.post_doubt_screen).pack(pady=5)
        tk.Button(self.master, text="View Doubts", command=self.view_doubts_screen).pack(pady=5)
        tk.Button(self.master, text="Logout", command=self.create_login_screen).pack(pady=10)

    def upload_note_screen(self):
        window = tk.Toplevel(self.master)
        window.title("Upload Note (PDF)")

        tk.Label(window, text="Subject:").grid(row=0, column=0, padx=10, pady=5)
        tk.Label(window, text="Topic:").grid(row=1, column=0, padx=10, pady=5)

        subject_entry = tk.Entry(window)
        topic_entry = tk.Entry(window)

        subject_entry.grid(row=0, column=1)
        topic_entry.grid(row=1, column=1)

        def submit_pdf():
            subject = subject_entry.get()
            topic = topic_entry.get()
            if subject and topic:
                upload_pdf_note(self.user_id, subject, topic)
                window.destroy()
            else:
                messagebox.showerror("Error", "Subject and Topic are required.")

        tk.Button(window, text="Upload PDF", command=submit_pdf).grid(row=2, column=1, pady=10)

    def search_notes_screen(self):
        window = tk.Toplevel(self.master)
        window.title("Search Notes")

        tk.Label(window, text="Enter keyword:").pack(pady=5)
        keyword_entry = tk.Entry(window, width=40)
        keyword_entry.pack(pady=5)

        result_area = scrolledtext.ScrolledText(window, width=60, height=15)
        result_area.pack(pady=10)

        def search():
            keyword = keyword_entry.get()
            if keyword:
                search_notes(keyword, result_area)
            else:
                messagebox.showerror("Error", "Please enter a keyword.")

        tk.Button(window, text="Search", command=search).pack(pady=5)

    def post_doubt_screen(self):
        window = tk.Toplevel(self.master)
        window.title("Post Doubt")

        tk.Label(window, text="Subject:").grid(row=0, column=0, padx=10, pady=5)
        tk.Label(window, text="Question:").grid(row=1, column=0, padx=10, pady=5)

        subject_entry = tk.Entry(window)
        question_text = scrolledtext.ScrolledText(window, width=40, height=8)

        subject_entry.grid(row=0, column=1)
        question_text.grid(row=1, column=1)

        def submit_doubt():
            subject = subject_entry.get()
            question = question_text.get('1.0', tk.END).strip()
            if subject and question:
                post_doubt(self.user_id, subject, question)
                window.destroy()
            else:
                messagebox.showerror("Error", "All fields are required.")

        tk.Button(window, text="Post", command=submit_doubt).grid(row=2, column=1, pady=10)

    def view_doubts_screen(self):
        window = tk.Toplevel(self.master)
        window.title("View Doubts")

        result_area = scrolledtext.ScrolledText(window, width=60, height=20)
        result_area.pack(pady=10)

        view_doubts(result_area)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = CampusContactApp(root)
    root.mainloop()