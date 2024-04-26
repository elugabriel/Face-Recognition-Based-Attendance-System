import tkinter as tk
from subprocess import run

class FaceRecognitionApp:
    def __init__(self, master):
        self.master = master
        master.geometry("1200x600")  # Use master instead of self.win

        master.title("Face Recognition App")

        self.capture_button = tk.Button(master, text="Capture Image", command=self.capture_image)
        self.capture_button.pack()

        self.process_button = tk.Button(master, text="Process Image", command=self.process_image)
        self.process_button.pack()

        self.login_button = tk.Button(master, text="Login", command=self.login)
        self.login_button.pack()

        self.view_attendance_button = tk.Button(master, text="View Attendance", command=self.view_attendance)
        self.view_attendance_button.pack()

    def capture_image(self):
        run(["python", "get_faces_from_camera_tkinter.py"])

    def process_image(self):
        run(["python", "features_extraction_to_csv.py"])

    def login(self):
        run(["python", "attendance_taker.py"])

    def view_attendance(self):
        run(["python", "app.py"])

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()
