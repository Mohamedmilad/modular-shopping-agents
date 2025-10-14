import json
import tkinter as tk
import time
from tkinter import simpledialog
root = None
chat_box = None

def init_ui():
    global root, chat_box
    root = tk.Tk()
    root.title("AI Chat Agent")

    chat_box = tk.Text(root, wrap="word", state="normal", bg="#f8f8f8", fg="#222", font=("Consolas", 11))
    chat_box.pack(expand=True, fill="both", padx=10, pady=10)

def _to_displayable(text):
    """Force anything into readable text."""
    try:
        if isinstance(text, (dict, list)):
            return json.dumps(text, indent=2, ensure_ascii=False)
        elif not isinstance(text, str):
            return str(text)
        return text
    except Exception as e:
        return f"[Unrenderable content: {e}]"

def show_text(text, sender="ai", delay=15):
    """Show text with typing animation, safely converting any object."""
    global chat_box
    if chat_box is None:
        raise RuntimeError("UI not initialized. Call init_ui() first.")

    text = _to_displayable(text)
    prefix = f"{sender.upper()}: "

    chat_box.insert(tk.END, prefix)
    chat_box.see(tk.END)
    chat_box.update()

    for char in text:
        chat_box.insert(tk.END, char)
        chat_box.see(tk.END)
        chat_box.update()
        time.sleep(delay / 1000.0)

    chat_box.insert(tk.END, "\n\n")
    chat_box.see(tk.END)
    chat_box.update()

def get_input(prompt="Enter: "):
    """Simple blocking input window for single user entry."""
    global root
    inp = simpledialog.askstring("User Input", prompt)
    return inp

def start_ui_loop():
    root.mainloop()

def close_ui():
    if root:
        root.destroy()
