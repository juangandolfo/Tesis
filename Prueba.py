import tkinter as tk

def show_non_blocking_message(title, message):
    popup = tk.Toplevel()  # Create a new window
    popup.title(title)
    popup.geometry("200x100")

    label = tk.Label(popup, text=message, wraplength=180)
    label.pack(pady=10)

    ok_button = tk.Button(popup, text="OK", command=popup.destroy)
    ok_button.pack(pady=5)

# Example usage
root = tk.Tk()
root.withdraw()  # Hide the root window

show_non_blocking_message("Info", "This won't block the flow")
print("This message prints immediately")  # Flow continues without waiting

root.mainloop()