import tkinter as tk

def create_window():
    # Create the main window
    window = tk.Tk()
    window.title("My Python Window")
    window.geometry("400x300")  # Set initial window size

    # Create a label widget
    label = tk.Label(window, text="Hello from my Python window!")
    label.pack(pady=20)  # Add some padding

    # Start the Tkinter event loop
    window.mainloop()

if __name__ == "__main__":
    create_window()