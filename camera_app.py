import os
import time
import glob
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from picamera2 import Picamera2

def get_usb_mount_point():
    media_root = "/media/pi"
    if os.path.exists(media_root):
        for name in os.listdir(media_root):
            path = os.path.join(media_root, name)
            if os.path.ismount(path):
                return os.path.join(path, "CameraMedia")
    return os.path.join(os.getcwd(), "media")

save_dir = get_usb_mount_point()
os.makedirs(save_dir, exist_ok=True)

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pi Touch Camera")
        self.root.attributes('-fullscreen', True)

        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"format": "RGB888"}))
        self.picam2.start()

        self.icons = {
            "photo": ImageTk.PhotoImage(Image.open("icons/photo.png").resize((96, 96))),
            "record": ImageTk.PhotoImage(Image.open("icons/record.png").resize((96, 96))),
            "stop": ImageTk.PhotoImage(Image.open("icons/stop.png").resize((96, 96))),
            "gallery": ImageTk.PhotoImage(Image.open("icons/gallery.png").resize((96, 96))),
            "quit": ImageTk.PhotoImage(Image.open("icons/quit.png").resize((96, 96)))
        }

        self.canvas = tk.Label(root)
        self.canvas.pack(fill="both", expand=True)

        self.button_frame = tk.Frame(root, bg='black')
        self.button_frame.pack(side="bottom", fill="x")

        self.btn_photo = tk.Button(self.button_frame, image=self.icons["photo"], command=self.take_photo,
                                   bd=0, highlightthickness=0, relief="flat", bg="black", activebackground="black")
        self.btn_photo.pack(side="left", fill="x", expand=True)

        self.btn_gallery = tk.Button(self.button_frame, image=self.icons["gallery"], command=self.show_gallery,
                                     bd=0, highlightthickness=0, relief="flat", bg="black", activebackground="black")
        self.btn_gallery.pack(side="left", fill="x", expand=True)

        self.btn_quit = tk.Button(self.button_frame, image=self.icons["quit"], command=self.quit,
                                  bd=0, highlightthickness=0, relief="flat", bg="black", activebackground="black")
        self.btn_quit.pack(side="left", fill="x", expand=True)

        self.update_frame()

    def update_frame(self):
        frame = self.picam2.capture_array()
        img = Image.fromarray(frame)
        img = img.resize((self.root.winfo_width(), self.root.winfo_height() - 100))
        imgtk = ImageTk.PhotoImage(image=img)
        self.canvas.imgtk = imgtk
        self.canvas.configure(image=imgtk)
        self.current_frame = frame
        self.root.after(30, self.update_frame)

    def take_photo(self):
        countdown = tk.Toplevel(self.root)
        countdown.geometry("400x200+400+200")
        countdown.title("Countdown")
        label = tk.Label(countdown, text="3", font=("Arial", 72))
        label.pack(expand=True)

        def update_count(n):
            if n == 0:
                countdown.destroy()
                frame = self.picam2.capture_array()
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                folder = os.path.join(save_dir, time.strftime("%Y-%m-%d"))
                os.makedirs(folder, exist_ok=True)
                filename = os.path.join(folder, f"photo_{timestamp}.jpg")
                Image.fromarray(frame).save(filename)
                messagebox.showinfo("Photo Saved", f"Saved: {filename}")
            else:
                label.config(text=str(n))
                countdown.after(1000, update_count, n - 1)

        update_count(3)

    def show_gallery(self):
        images = sorted(glob.glob(os.path.join(save_dir, "**", "photo_*.jpg"), recursive=True))
        if not images:
            messagebox.showinfo("Gallery", "No photos found.")
            return

        gallery = tk.Toplevel(self.root)
        gallery.title("Gallery Viewer")
        gallery.geometry("800x480")

        img_label = tk.Label(gallery)
        img_label.pack(expand=True, fill="both")

        index = [0]

        def show_image(i):
            img = Image.open(images[i])
            img = img.resize((800, 480))
            imgtk = ImageTk.PhotoImage(img)
            img_label.imgtk = imgtk
            img_label.configure(image=imgtk)

        def next_img():
            index[0] = (index[0] + 1) % len(images)
            show_image(index[0])

        def prev_img():
            index[0] = (index[0] - 1) % len(images)
            show_image(index[0])

        btn_frame = tk.Frame(gallery)
        btn_frame.pack()
        tk.Button(btn_frame, text="⬅ Prev", font=("Arial", 20), command=prev_img).pack(side="left", expand=True)
        tk.Button(btn_frame, text="Next ➡", font=("Arial", 20), command=next_img).pack(side="left", expand=True)

        show_image(index[0])

    def quit(self):
        self.picam2.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
