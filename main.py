import tkinter as tk
from threading import Thread
from gesture_controller import HandGestureController

def run_hand_controller():
    controller = HandGestureController()
    controller.start()

def main():
    root = tk.Tk()
    root.title("Hand Gesture Mouse Controller")
    root.geometry("360x240")  
    root.resizable(False, False)

    label = tk.Label(root, text="Control your mouse with hand gestures!", font=("Helvetica", 14))
    label.pack(pady=20)

    start_btn = tk.Button(root, text="Start Hand Control", font=("Helvetica", 12), width=25, command=lambda: Thread(target=run_hand_controller, daemon=True).start())
    start_btn.pack(pady=10)

    exit_btn = tk.Button(root, text="Exit", font=("Helvetica", 12), width=25, command=root.destroy)
    exit_btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
