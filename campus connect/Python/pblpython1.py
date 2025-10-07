import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import sqlite3
import hashlib
import datetime

# ------------------- Database Setup -------------------
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
                content TEXT,
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

# ------------------- Helper Functions -------------------
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
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed))
    return c.fetchone()

def upload_note(user_id, subject, topic, content):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO notes (user_id, subject, topic, content, timestamp) VALUES (?, ?, ?, ?, ?)",
              (user_id, subject, topic, content, timestamp))
    conn.commit()
    messagebox.showinfo("Success", "Note uploaded successfully!")

def search_notes(keyword, text_area):
    c.execute("SELECT subject, topic, content, timestamp FROM notes WHERE content LIKE ?", ('%' + keyword + '%',))
    results = c.fetchall()
    text_area.delete('1.0', tk.END)
    if results:
        for note in results:
            result_text = f"Subject: {note[0]}\nTopic: {note[1]}\nDate: {note[3]}\nContent: {note[2]}\n{'-'*60}\n"
            text_area.insert(tk.END, result_text)
    else:
        text_area.insert(tk.END, "No notes found.\n")

def post_doubt(user_id, subject, question):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO doubts (user_id, subject, question, timestamp) VALUES (?, ?, ?, ?)",
              (user_id, subject, question, timestamp))
    conn.commit()
    messagebox.showinfo("Success", "Doubt posted successfully!")

def view_doubts(text_area):
    c.execute('''SELECT doubts.id, users.username, doubts.subject, doubts.question, doubts.timestamp 
                 FROM doubts JOIN users ON doubts.user_id = users.id 
                 ORDER BY doubts.timestamp DESC''')
    doubts = c.fetchall()
    text_area.delete('1.0', tk.END)
    if doubts:
        for d in doubts:
            text_area.insert(tk.END,
                             f"ID: {d[0]} | By: {d[1]} | Subject: {d[2]} | Date: {d[4]}\nQuestion: {d[3]}\n{'-'*60}\n")
    else:
        text_area.insert(tk.END, "No doubts posted yet.\n")

# ------------------- GUI -------------------
class CampusContactApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Campus Contact")
        self.user_id = None
        self.create_login_screen()

    def create_login_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        tk.Label(self.master, text="Campus Contact", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(self.master, text="Username:").grid(row=1, column=0, padx=10, pady=5)
        tk.Label(self.master, text="Password:").grid(row=2, column=0, padx=10, pady=5)

        self.username_entry = tk.Entry(self.master)
        self.password_entry = tk.Entry(self.master, show="*")
        self.username_entry.grid(row=1, column=1)
        self.password_entry.grid(row=2, column=1)

        tk.Button(self.master, text="Login", width=10, command=self.login).grid(row=3, column=0, pady=10)
        tk.Button(self.master, text="Register", width=10, command=self.register).grid(row=3, column=1, pady=10)

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username and password:
            register_user(username, password)
        else:
            messagebox.showerror("Error", "Please enter both username and password.")

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

        tk.Label(self.master, text="Welcome to Campus Contact!", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Button(self.master, text="Upload Note", width=20, command=self.upload_note_screen).pack(pady=5)
        tk.Button(self.master, text="Search Notes", width=20, command=self.search_notes_screen).pack(pady=5)
        tk.Button(self.master, text="Post Doubt", width=20, command=self.post_doubt_screen).pack(pady=5)
        tk.Button(self.master, text="View Doubts", width=20, command=self.view_doubts_screen).pack(pady=5)
        tk.Button(self.master, text="Logout", width=20, command=self.create_login_screen).pack(pady=10)

    def upload_note_screen(self):
        win = tk.Toplevel(self.master)
        win.title("Upload Note")

        tk.Label(win, text="Subject:").grid(row=0, column=0, padx=10, pady=5)
        tk.Label(win, text="Topic:").grid(row=1, column=0, padx=10, pady=5)
        tk.Label(win, text="Content:").grid(row=2, column=0, padx=10, pady=5)

        subject = tk.Entry(win)
        topic = tk.Entry(win)
        content = scrolledtext.ScrolledText(win, width=40, height=10)
        subject.grid(row=0, column=1)
        topic.grid(row=1, column=1)
        content.grid(row=2, column=1)

        def submit():
            if subject.get() and topic.get() and content.get('1.0', tk.END).strip():
                upload_note(self.user_id, subject.get(), topic.get(), content.get('1.0', tk.END).strip())
                win.destroy()
            else:
                messagebox.showerror("Error", "All fields required.")

        tk.Button(win, text="Upload", command=submit).grid(row=3, column=1, pady=10)

    def search_notes_screen(self):
        win = tk.Toplevel(self.master)
        win.title("Search Notes")

        tk.Label(win, text="Enter keyword:").pack(pady=5)
        keyword_entry = tk.Entry(win, width=40)
        keyword_entry.pack(pady=5)

        result_area = scrolledtext.ScrolledText(win, width=60, height=15)
        result_area.pack(pady=10)

        def search():
            if keyword_entry.get():
                search_notes(keyword_entry.get(), result_area)
            else:
                messagebox.showerror("Error", "Enter a keyword.")

        tk.Button(win, text="Search", command=search).pack(pady=5)

    def post_doubt_screen(self):
        win = tk.Toplevel(self.master)
        win.title("Post Doubt")

        tk.Label(win, text="Subject:").grid(row=0, column=0, padx=10, pady=5)
        tk.Label(win, text="Question:").grid(row=1, column=0, padx=10, pady=5)

        subject = tk.Entry(win)
        question = scrolledtext.ScrolledText(win, width=40, height=8)
        subject.grid(row=0, column=1)
        question.grid(row=1, column=1)

        def submit():
            if subject.get() and question.get('1.0', tk.END).strip():
                post_doubt(self.user_id, subject.get(), question.get('1.0', tk.END).strip())
                win.destroy()
            else:
                messagebox.showerror("Error", "All fields required.")

        tk.Button(win, text="Post", command=submit).grid(row=2, column=1, pady=10)

    def view_doubts_screen(self):
        win = tk.Toplevel(self.master)
        win.title("View Doubts")

        text_area = scrolledtext.ScrolledText(win, width=60, height=20)
        text_area.pack(pady=10)

        view_doubts(text_area)

# ------------------- Run App -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = CampusContactApp(root)
    root.mainloop()

