import tkinter as tk
from tkinter import simpledialog, messagebox
import os
import json
import sys
import urllib.request
import webbrowser # To open the download page

# --- UPDATE CONFIGURATION ---
CURRENT_VERSION = "v1.0.0"  # Change this as you release new versions
REPO_OWNER = "mystylemur"
REPO_NAME = "TodoList"

def check_for_updates():
    """Checks GitHub for a newer release and asks to update."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
    try:
        # Request latest release info from GitHub API
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            latest_version = data.get("tag_name", "")
            release_url = data.get("html_url", "")

            # If the version on GitHub is different from our current one
            if latest_version and latest_version != CURRENT_VERSION:
                answer = messagebox.askyesno(
                    "Update Available", 
                    f"A new version ({latest_version}) is available!\n\nDo you want to go to the download page?"
                )
                if answer:
                    webbrowser.open(release_url)
    except Exception as e:
        print(f"Update check failed: {e}")

# --- REST OF YOUR ORIGINAL FUNCTIONS ---

def get_save_path(filename):
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(application_path, filename)

FILE = get_save_path("save.json")

def add_task(text=None, checked=False):
    task_text = text if text is not None else entry.get().strip()
    if task_text:
        task_id = f"task_{len(cb_vars)}"
        var = tk.BooleanVar(value=checked)
        task_frame = tk.Frame(tasks_container)
        task_frame.pack(fill='x', padx=10, pady=2)
        cb = tk.Checkbutton(task_frame, text=task_text, variable=var)
        cb.pack(side='left')
        del_btn = tk.Button(task_frame, text="X", fg="red", 
                             command=lambda: delete_task(task_frame, task_id))
        del_btn.pack(side='right', padx=2)
        edit_btn = tk.Button(task_frame, text="Edit", 
                             command=lambda: edit_task(cb, task_id))
        edit_btn.pack(side='right', padx=2)
        cb_vars[task_id] = {"var": var, "cb": cb}
        entry.delete(0, tk.END)
        save_tasks()

def delete_task(frame, task_id):
    frame.destroy()
    if task_id in cb_vars:
        cb_vars.pop(task_id)
    save_tasks()

def edit_task(checkbox, task_id):
    current_text = checkbox.cget("text")
    new_name = simpledialog.askstring("Edit Task", "Rename task:", initialvalue=current_text)
    if new_name and new_name != current_text:
        checkbox.config(text=new_name)
        save_tasks()

def save_tasks():
    data_to_save = [{"text": d["cb"].cget("text"), "checked": d["var"].get()} for d in cb_vars.values()]
    with open(FILE, 'w') as f:
        json.dump(data_to_save, f)
    label.config(text="Tasks saved!")

def load_tasks():
    if os.path.exists(FILE):
        try:
            with open(FILE, 'r') as f:
                tasks = json.load(f)
                for t in tasks:
                    add_task(text=t['text'], checked=t['checked'])
        except Exception:
            pass

def show_selected_tasks():
    selected = [data["cb"].cget("text") for tid, data in cb_vars.items() if data["var"].get()]
    label.config(text=f"Completed: {', '.join(selected) if selected else 'None'}")

# --- MAIN APP SETUP ---
root = tk.Tk()
root.title(f"Python To-Do List ({CURRENT_VERSION})")
root.geometry("500x500")

cb_vars = {} 
label = tk.Label(root, text='Add a task below', wraplength=250)
label.pack(pady=10)

entry = tk.Entry(root, width=25)
entry.pack(pady=5)
entry.focus_set()
entry.bind('<Return>', lambda e: add_task())

btn_add = tk.Button(root, text="Add Task", command=add_task)
btn_add.pack(pady=5)

tk.Label(root, text="My Tasks", font=("Arial", 12, "bold")).pack(pady=5)

tasks_container = tk.Frame(root)
tasks_container.pack(fill='both', expand=True)

btn_check = tk.Button(root, text="Show Completed", command=show_selected_tasks)
btn_check.pack(side="bottom", pady=20)

# Run initial tasks
load_tasks()

# Check for updates on startup
root.after(1000, check_for_updates) 

root.mainloop()
