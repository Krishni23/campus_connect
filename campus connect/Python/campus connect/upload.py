import shutil, os, datetime
from tkinter import messagebox
from auth import conn, c

# Copy selected file to uploads folder
def copy_to_uploads(src_path: str) -> str:
    if not src_path:
        return None
    try:
        base = os.path.basename(src_path)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        dest_name = f"{timestamp}_{base}"
        dest_path = os.path.join("uploads", dest_name)
        shutil.copy2(src_path, dest_path)
        return dest_path
    except Exception as e:
        messagebox.showerror("Error", f"File copy failed: {e}")
        return None

# Upload note with optional file
def upload_note(user_id, subject, topic, content, selected_file=None):
    if not user_id:
        messagebox.showerror("Error", "User not logged in")
        return
    file_path = copy_to_uploads(selected_file)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO notes (user_id, subject, topic, content, timestamp, file_path) VALUES (?, ?, ?, ?, ?, ?)",
              (user_id, subject, topic, content, timestamp, file_path))
    conn.commit()
    messagebox.showinfo("Success", "Note uploaded successfully!")
