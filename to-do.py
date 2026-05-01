import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import json
import sys
import urllib.request
import webbrowser
import ssl

# --- CONFIG ---
CURRENT_VERSION = "v1.0.0" 
REPO_OWNER = "mystylemur"
REPO_NAME = "TodoList"

def get_save_path(filename):
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(application_path, filename)

FILE = get_save_path("save.json")

# --- EASY UPDATE CHECK ---
def check_for_updates():
    """Checks GitHub for a new version and offers a browser download."""
    # Ensure this URL is exactly as written below (api.github.com/repos/...)
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
    
    try:
        # GitHub requires a User-Agent header or it may reject the connection
        req = urllib.request.Request(url, headers={'User-Agent': 'Python-Urllib-App'})
        context = ssl._create_unverified_context() # Helps with macOS SSL issues
        
        with urllib.request.urlopen(req, context=context, timeout=5) as response:
            data = json.loads(response.read().decode())
            latest_version = data.get("tag_name", "")
            release_url = data.get("html_url", "")

            if latest_version and latest_version != CURRENT_VERSION:
                if messagebox.askyesno("Update Available", 
                    f"A new version ({latest_version}) is available!\n\nWould you like to open the download page?"):
                    webbrowser.open(release_url)
    except Exception as e:
        # If the internet is down or DNS fails, we skip silently to keep the app working
        print(f"Update check skipped: {e}")

# --- CORE APP LOGIC ---
def add_task(text=None, checked=False):
    task_text = text if text is not None else entry.get().strip()
    if task_text:
        task_id = f"task_{len(cb_vars)}"
        var = tk.BooleanVar(value=checked)
        frame = tk.Frame(tasks_container)
        frame.pack(fill='x', padx=10, pady=2)
        
        cb = tk.Checkbutton(frame, text=task_text, variable=var, command=save_tasks)
        cb.pack(side='left')
        
        tk.Button(frame, text="X", fg="red", command=lambda: delete_task(frame, task_id)).pack(side='right')
        tk.Button(frame, text="Edit", command=lambda: edit_task(cb)).pack(side='right', padx=2)
        
        cb_vars[task_id] = {"var": var, "cb": cb}
        entry.delete(0, tk.END)
        save_tasks()

def delete_task(frame, task_id):
    frame.destroy()
    cb_vars.pop(task_id, None)
    save_tasks()

def edit_task(checkbox):
    new_name = simpledialog.askstring("Edit", "Rename task:", initialvalue=checkbox.cget("text"))
    if new_name:
        checkbox.config(text=new_name)
        save_tasks()

def save_tasks():
    data = [{"text": d["cb"].cget("text"), "checked": d["var"].get()} for d in cb_vars.values()]
    with open(FILE, 'w') as f:
        json.dump(data, f)

def load_tasks():
    if os.path.exists(FILE):
        try:
            with open(FILE, 'r') as f:
                for t in json.load(f):
                    add_task(t['text'], t['checked'])
        except: pass

# --- UI SETUP ---
root = tk.Tk()
root.title(f"To-Do {CURRENT_VERSION}")
root.geometry("400x500")

cb_vars = {}
tk.Label(root, text="To-Do List", font=("Arial", 16, "bold")).pack(pady=10)

entry = tk.Entry(root, width=30)
entry.pack(pady=5)
entry.bind('<Return>', lambda e: add_task())

tk.Button(root, text="Add Task", command=add_task, bg="lightgrey").pack(pady=5)

tasks_container = tk.Frame(root)
tasks_container.pack(fill='both', expand=True)

load_tasks()

# Start the update check 1 second after opening to keep the app snappy
root.after(1000, check_for_updates)

root.mainloop()
