import os
import subprocess
import sys
from tkinter import messagebox
from auth import c

# ------------------- Search Notes -------------------
def search_notes(keyword):
    """
    Search notes based on keyword in Topic, Subject, Content, or attached file name.
    Returns a list of matching notes.
    """
    c.execute("""
        SELECT id, subject, topic, content, timestamp, file_path
        FROM notes
        WHERE topic LIKE ? OR subject LIKE ? OR content LIKE ? OR file_path LIKE ?
        ORDER BY timestamp DESC
    """, ('%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%'))
    return c.fetchall()

# ------------------- Open Attached File -------------------
def open_file(path: str):
    """
    Open attached PDF or image file.
    """
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", "File not found.")
        return
    try:
        if sys.platform.startswith('win'):
            os.startfile(path)
        elif sys.platform.startswith('darwin'):
            subprocess.call(['open', path])
        else:
            subprocess.call(['xdg-open', path])
    except Exception as e:
        messagebox.showerror("Error", f"Cannot open file: {e}")
