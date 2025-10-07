import customtkinter as ctk
from tkinter import scrolledtext, messagebox, filedialog
import sqlite3
import hashlib
import datetime
import os

# ---------------- Database ----------------
conn = sqlite3.connect('campus_connect.db')
c = conn.cursor()

# Create tables
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
                file_path TEXT
            )''')
conn.commit()

# ---------------- Helpers ----------------
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

def upload_note(user_id, subject, topic, content, file_path=None):
    if not user_id:
        messagebox.showerror("Error", "User not logged in")
        return
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO notes (user_id, subject, topic, content, timestamp, file_path) VALUES (?, ?, ?, ?, ?, ?)",
              (user_id, subject, topic, content, timestamp, file_path))
    conn.commit()
    messagebox.showinfo("Success", "Note uploaded!")

def search_notes(keyword, text_area):
    c.execute("SELECT subject, topic, content, timestamp, file_path FROM notes WHERE content LIKE ?", ('%' + keyword + '%',))
    results = c.fetchall()
    text_area.delete('1.0', "end")
    if results:
        for note in results:
            file_text = f"File: {note[4]}" if note[4] else "File: None"
            text_area.insert("end", f"Subject: {note[0]}\nTopic: {note[1]}\nDate: {note[3]}\nContent: {note[2]}\n{file_text}\n{'-'*40}\n")
    else:
        text_area.insert("end", "No notes found.\n")

def open_file(path):
    if path and os.path.exists(path):
        os.startfile(path)
    else:
        messagebox.showerror("Error", "File not found")

# ---------------- App ----------------
class CampusConnectApp:
    def __init__(self, master):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.master = master
        self.master.title("Campus Connect")
        self.master.geometry("500x500")
        self.user_id = None
        self.login_screen()

    # --- Login/Register Screen ---
    def login_screen(self):
        for w in self.master.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.master, text="Campus Connect", font=("Arial", 24, "bold")).pack(pady=20)
        self.username = ctk.CTkEntry(self.master, placeholder_text="Username")
        self.username.pack(pady=10)
        self.password = ctk.CTkEntry(self.master, placeholder_text="Password", show="*")
        self.password.pack(pady=10)
        ctk.CTkButton(self.master, text="Login", command=self.login).pack(pady=10)
        ctk.CTkButton(self.master, text="Register", command=self.register).pack(pady=5)

    def register(self):
        if self.username.get() and self.password.get():
            register_user(self.username.get(), self.password.get())
        else:
            messagebox.showerror("Error", "Enter both fields.")

    def login(self):
        user = login_user(self.username.get(), self.password.get())
        if user:
            self.user_id = user[0]
            self.main_screen()
        else:
            messagebox.showerror("Error", "Invalid credentials.")

    # --- Main Screen ---
    def main_screen(self):
        for w in self.master.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.master, text=f"Welcome!", font=("Arial", 20, "bold")).pack(pady=20)
        ctk.CTkButton(self.master, text="Upload Note", width=200, command=self.upload_screen).pack(pady=10)
        ctk.CTkButton(self.master, text="Search Notes", width=200, command=self.search_screen).pack(pady=10)
        ctk.CTkButton(self.master, text="Logout", width=200, command=self.login_screen).pack(pady=20)

    # --- Upload Note ---
    def upload_screen(self):
        win = ctk.CTkToplevel(self.master)
        win.geometry("450x450")
        ctk.CTkLabel(win, text="Subject:").pack(pady=5)
        subject = ctk.CTkEntry(win)
        subject.pack(pady=5)
        ctk.CTkLabel(win, text="Topic:").pack(pady=5)
        topic = ctk.CTkEntry(win)
        topic.pack(pady=5)
        ctk.CTkLabel(win, text="Content:").pack(pady=5)
        content = scrolledtext.ScrolledText(win, width=40, height=8)
        content.pack(pady=5)

        file_path = ""

        def select_file():
            nonlocal file_path
            file_path = filedialog.askopenfilename(
                title="Select PDF or Image",
                filetypes=[("PDF files", "*.pdf"), ("Image files", "*.png;*.jpg;*.jpeg")]
            )
            if file_path:
                file_label.configure(text=file_path.split("/")[-1])

        ctk.CTkButton(win, text="Choose File (PDF/Image)", command=select_file).pack(pady=5)
        file_label = ctk.CTkLabel(win, text="No file selected")
        file_label.pack(pady=5)

        def submit():
            subj = subject.get()
            top = topic.get()
            cont = content.get("1.0", "end").strip()
            if subj and top and cont:
                upload_note(self.user_id, subj, top, cont, file_path)
                win.destroy()
            else:
                messagebox.showerror("Error", "All fields required.")

        ctk.CTkButton(win, text="Upload", command=submit).pack(pady=10)

    # --- Search Notes ---
    def search_screen(self):
        win = ctk.CTkToplevel(self.master)
        win.geometry("500x450")
        ctk.CTkLabel(win, text="Enter keyword:").pack(pady=5)
        keyword = ctk.CTkEntry(win, width=200)
        keyword.pack(pady=5)
        result = scrolledtext.ScrolledText(win, width=60, height=15)
        result.pack(pady=10)

        def search():
            if keyword.get():
                search_notes(keyword.get(), result)
            else:
                messagebox.showerror("Error", "Enter keyword.")

        ctk.CTkButton(win, text="Search", command=search).pack(pady=5)

# ---------------- Run App ----------------
if __name__ == "__main__":
    root = ctk.CTk()
    app = CampusConnectApp(root)
    root.mainloop()
