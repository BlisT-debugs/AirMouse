import tkinter as tk
from threading import Thread
from gesture_controller import HandGestureController

controller = HandGestureController()

def start_controller():
    Thread(target=controller.start, daemon=True).start()

def main():
    root = tk.Tk()
    root.title("Hand Mouse Controller")

    label = tk.Label(root, text="Control Mouse with Your Hand", font=("Arial", 14))
    label.pack(pady=10)

    start_btn = tk.Button(root, text="Start Control", command=start_controller, font=("Arial", 12), width=20)
    start_btn.pack(pady=10)

    exit_btn = tk.Button(root, text="Exit", command=root.destroy, font=("Arial", 12), width=20)
    exit_btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
