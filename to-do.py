import tkinter as tk
from tkinter import simpledialog
import os
import json
import sys


def get_save_path(filename):
    if getattr(sys, 'frozen', False):
        # Path where the .exe or .app is located
        application_path = os.path.dirname(sys.executable)
    else:
        # Development path
        application_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(application_path, filename)

FILE = get_save_path("save.json")

def add_task(text=None, checked=False):
    # Use text from entry if none provided (manual add)
    task_text = text if text is not None else entry.get().strip()
    
    if task_text:
        task_id = f"task_{len(cb_vars)}"
        var = tk.BooleanVar(value=checked) # Set initial state from load
        
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

def edit_task(checkbox, task_id):
    current_text = checkbox.cget("text")
    new_name = simpledialog.askstring("Edit Task", "Rename task:", initialvalue=current_text)
    if new_name and new_name != current_text:
        checkbox.config(text=new_name)


def save_tasks():
    # Convert UI variables into a serializable list
    data_to_save = []
    for tid, data in cb_vars.items():
        data_to_save.append({
            "text": data["cb"].cget("text"),
            "checked": data["var"].get()
        })
    
    with open(FILE, 'w') as f:
        json.dump(data_to_save, f)
    label.config(text="Task added and saved successfully!")

def load_tasks():
    if os.path.exists(FILE):
        try:
            with open(FILE, 'r') as f:
                tasks = json.load(f)
                for t in tasks:
                    add_task(text=t['text'], checked=t['checked'])
        except Exception as e:
            print(f"Error loading file: {e}")

def show_selected_tasks():
    selected = [data["cb"].cget("text") for tid, data in cb_vars.items() if data["var"].get()]
    label.config(text=f"Completed: {', '.join(selected) if selected else 'None'}")


root = tk.Tk()
root.title("Python To-Do List")
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


load_tasks()

root.mainloop()
