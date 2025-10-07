import customtkinter as ctk
from tkinter import scrolledtext, filedialog, messagebox
from auth import register_user, login_user
from upload import upload_note
from search import search_notes, open_file
import os

class CampusConnectApp:
    def __init__(self, master):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.master = master
        self.master.title("Campus Connect")
        self.master.geometry("600x520")
        self.user_id = None
        self.username = None
        self.login_screen()

    # ----------------- Login/Register -----------------
    def login_screen(self):
        for w in self.master.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.master, text="Campus Connect", font=("Arial", 28, "bold")).pack(pady=20)
        self.username_entry = ctk.CTkEntry(self.master, placeholder_text="Username", width=300)
        self.username_entry.pack(pady=5)
        self.password_entry = ctk.CTkEntry(self.master, placeholder_text="Password", show="*", width=300)
        self.password_entry.pack(pady=5)

        ctk.CTkButton(self.master, text="Login", width=120, command=self.login).pack(pady=10)
        ctk.CTkButton(self.master, text="Register", width=120, command=self.register).pack(pady=5)

    def register(self):
        user = self.username_entry.get().strip()
        pwd = self.password_entry.get().strip()
        if user and pwd:
            if register_user(user, pwd):
                messagebox.showinfo("Success", "Registration successful!")
            else:
                messagebox.showerror("Error", "Username already exists.")
        else:
            messagebox.showerror("Error", "Enter both fields.")

    def login(self):
        user = self.username_entry.get().strip()
        pwd = self.password_entry.get().strip()
        record = login_user(user, pwd)
        if record:
            self.user_id = record[0]
            self.username = user
            self.main_screen()
        else:
            messagebox.showerror("Error", "Invalid credentials.")

    # ----------------- Main Menu -----------------
    def main_screen(self):
        for w in self.master.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.master, text=f"Welcome, {self.username}", font=("Arial", 20, "bold")).pack(pady=20)
        ctk.CTkButton(self.master, text="Upload Note", width=200, command=self.upload_screen).pack(pady=10)
        ctk.CTkButton(self.master, text="Search Notes", width=200, command=self.search_screen).pack(pady=10)
        ctk.CTkButton(self.master, text="Logout", width=200, fg_color="#d9534f", command=self.login_screen).pack(pady=20)

    # ----------------- Upload Note -----------------
    def upload_screen(self):
        win = ctk.CTkToplevel(self.master)
        win.title("Upload Note")
        win.geometry("500x500")

        subject = ctk.CTkEntry(win, placeholder_text="Subject", width=400)
        subject.pack(pady=5)
        topic = ctk.CTkEntry(win, placeholder_text="Topic", width=400)
        topic.pack(pady=5)
        content_text = scrolledtext.ScrolledText(win, width=50, height=10)
        content_text.pack(pady=10)

        selected = {"path": None}

        # Label to show selected file
        file_label = ctk.CTkLabel(win, text="No file selected", anchor="w")
        file_label.pack(pady=4)

        def choose_file():
            path = filedialog.askopenfilename(
                title="Select PDF or Image",
                filetypes=[("PDF files", "*.pdf"), ("Image files", "*.png;*.jpg;*.jpeg")]
            )
            if path:
                selected["path"] = path
                file_label.configure(text=f"Attached: {os.path.basename(path)}")

        ctk.CTkButton(win, text="Choose File", command=choose_file).pack(pady=5)

        def submit_note():
            s = subject.get()
            t = topic.get()
            c = content_text.get("1.0", "end").strip()
            f = selected["path"]
            if s and t:
                upload_note(self.user_id, s, t, c, f)
                win.destroy()
            else:
                messagebox.showerror("Error", "Subject and Topic are required.")

        ctk.CTkButton(win, text="Upload", command=submit_note).pack(pady=10)

    # ----------------- Search Notes -----------------
    def search_screen(self):
        win = ctk.CTkToplevel(self.master)
        win.title("Search Notes")
        win.geometry("700x500")

        keyword = ctk.CTkEntry(win, placeholder_text="Enter keyword", width=300)
        keyword.pack(pady=10)
        result_frame = ctk.CTkScrollableFrame(win, width=650, height=400)
        result_frame.pack()

        def perform_search():
            for w in result_frame.winfo_children():
                w.destroy()
            results = search_notes(keyword.get())
            if not results:
                ctk.CTkLabel(result_frame, text="No results found").pack(pady=10)
                return
            for row in results:
                subject, topic, content, ts, file_path = row[1], row[2], row[3], row[4], row[5]
                frame = ctk.CTkFrame(result_frame)
                frame.pack(fill="x", pady=5, padx=5)
                ctk.CTkLabel(frame, text=f"{subject} - {topic}", font=("Arial", 14, "bold")).pack(anchor="w", padx=5)
                ctk.CTkLabel(frame, text=f"Date: {ts}", font=("Arial", 10)).pack(anchor="w", padx=5)
                if content:
                    ctk.CTkLabel(frame, text=content[:200] + "...", wraplength=620, justify="left").pack(anchor="w", padx=5)
                if file_path:
                    ctk.CTkLabel(frame, text=f"Attached file: {os.path.basename(file_path)}").pack(anchor="w", padx=5)
                    ctk.CTkButton(frame, text="Open File", command=lambda p=file_path: open_file(p)).pack(anchor="e", padx=5, pady=5)

        ctk.CTkButton(win, text="Search", command=perform_search).pack(pady=5)


if __name__ == "__main__":
    root = ctk.CTk()
    app = CampusConnectApp(root)
    root.mainloop()
