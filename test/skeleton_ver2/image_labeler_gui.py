import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import shutil
import cv2
import numpy as np
from PIL import Image, ImageTk
import argparse
import sys


def safe_imread(path: Path):
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
        if data.size == 0:
            return None
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None


class ImageLabeler(tk.Tk):
    def __init__(self, input_folder: str, output_folder: str, mode: str = 'copy', normal_name: str = 'normal', abnormal_name: str = 'abnormal'):
        super().__init__()
        self.title('Image Labeler')
        self.geometry('1000x800')

        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.mode = mode.lower()
        if self.mode not in ('copy', 'move'):
            self.mode = 'copy'
        self.normal_folder = self.output_folder / normal_name
        self.abnormal_folder = self.output_folder / abnormal_name
        # create folders
        self.normal_folder.mkdir(parents=True, exist_ok=True)
        self.abnormal_folder.mkdir(parents=True, exist_ok=True)

        self.image_paths = sorted([p for p in self.input_folder.iterdir() if p.suffix.lower() in ['.jpg', '.jpeg', '.png']])
        if not self.image_paths:
            messagebox.showinfo('Info', f'No images found in {self.input_folder}')
            self.destroy()
            return

        self.index = 0
        self.history = []  # list of tuples (src_dst)

        # UI
        self.lbl_filename = tk.Label(self, text='')
        self.lbl_filename.pack(anchor='nw')

        self.canvas = tk.Canvas(self, bg='black')
        self.canvas.pack(fill='both', expand=True)

        frame = tk.Frame(self)
        frame.pack(fill='x', side='bottom')

        btn_normal = tk.Button(frame, text='Normal (N)', command=self.mark_normal)
        btn_normal.pack(side='left', padx=5, pady=5)
        btn_abnormal = tk.Button(frame, text='Abnormal (A)', command=self.mark_abnormal)
        btn_abnormal.pack(side='left', padx=5, pady=5)
        btn_skip = tk.Button(frame, text='Skip (S)', command=self.next_image)
        btn_skip.pack(side='left', padx=5, pady=5)
        btn_undo = tk.Button(frame, text='Undo (U)', command=self.undo)
        btn_undo.pack(side='left', padx=5, pady=5)
        btn_quit = tk.Button(frame, text='Quit (Q)', command=self.on_quit)
        btn_quit.pack(side='right', padx=5, pady=5)

        self.status = tk.Label(self, text='')
        self.status.pack(anchor='sw')

        # bindings
        self.bind('<n>', lambda e: self.mark_normal())
        self.bind('<a>', lambda e: self.mark_abnormal())
        self.bind('<s>', lambda e: self.next_image())
        self.bind('<u>', lambda e: self.undo())
        self.bind('<q>', lambda e: self.on_quit())

        self.photo_image = None
        self.show_image()

    def show_image(self):
        if self.index < 0:
            self.index = 0
        if self.index >= len(self.image_paths):
            messagebox.showinfo('Done', 'All images processed')
            self.on_quit()
            return

        p = self.image_paths[self.index]
        self.lbl_filename.config(text=f'[{self.index+1}/{len(self.image_paths)}] {p.name}')

        img = safe_imread(p)
        if img is None:
            self.canvas.delete('all')
            self.canvas.create_text(10, 10, anchor='nw', text='Failed to load image', fill='white')
            return

        # convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w = img.shape[:2]

        # fit to canvas size
        canvas_w = max(self.winfo_width(), 640)
        canvas_h = max(self.winfo_height(), 480)
        scale = min(canvas_w / w, (canvas_h - 100) / h, 1.0)
        new_w = int(w * scale)
        new_h = int(h * scale)
        img_pil = Image.fromarray(img).resize((new_w, new_h), Image.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(img_pil)

        self.canvas.delete('all')
        self.canvas.create_image(canvas_w//2, (canvas_h-100)//2, image=self.photo_image, anchor='center')
        self.update_status()

    def update_status(self):
        normal_count = len(list(self.normal_folder.iterdir()))
        abnormal_count = len(list(self.abnormal_folder.iterdir()))
        remaining = len(self.image_paths) - self.index
        self.status.config(text=f'Normal: {normal_count}  Abnormal: {abnormal_count}  Remaining: {remaining}')

    def move_current(self, dest_folder: Path):
        src = self.image_paths[self.index]
        dest = dest_folder / src.name
        # avoid overwrite
        if dest.exists():
            stem = src.stem
            ext = src.suffix
            i = 1
            while dest.exists():
                dest = dest_folder / f"{stem}_{i}{ext}"
                i += 1
        try:
            if self.mode == 'copy':
                shutil.copy2(str(src), str(dest))
            else:
                shutil.move(str(src), str(dest))
            self.history.append((src, dest))
            # if moved, remove from list; if copied, still remove to avoid reprocessing
            del self.image_paths[self.index]
            # do not increment index: next image occupies same index
            self.show_image()
        except Exception as e:
            messagebox.showerror('Error', f'Failed to copy/move file: {e}')

    def mark_normal(self):
        self.move_current(self.normal_folder)
        self.update_status()

    def mark_abnormal(self):
        self.move_current(self.abnormal_folder)
        self.update_status()

    def next_image(self):
        self.index += 1
        if self.index >= len(self.image_paths):
            messagebox.showinfo('Done', 'All images processed')
            self.on_quit()
            return
        self.show_image()

    def undo(self):
        if not self.history:
            messagebox.showinfo('Undo', 'Nothing to undo')
            return
        src, dest = self.history.pop()
        try:
            # move back
            shutil.move(str(dest), str(src))
            # insert back into list at current index
            self.image_paths.insert(self.index, src)
            self.show_image()
            self.update_status()
        except Exception as e:
            messagebox.showerror('Error', f'Undo failed: {e}')

    def on_quit(self):
        self.destroy()


def main():
    parser = argparse.ArgumentParser(description='Simple image labeling GUI (normal/abnormal)')
    parser.add_argument('--input', default='labeling_test_images', help='input folder')
    parser.add_argument('--out', default='labeled', help='output base folder (will create normal/abnormal subfolders)')
    parser.add_argument('--mode', default='copy', choices=['copy','move'], help='operation mode: copy (default) or move')
    parser.add_argument('--normal', default='normal', help='normal subfolder name')
    parser.add_argument('--abnormal', default='abnormal', help='abnormal subfolder name')
    args = parser.parse_args()

    app = ImageLabeler(args.input, args.out, mode=args.mode, normal_name=args.normal, abnormal_name=args.abnormal)
    app.mainloop()


if __name__ == '__main__':
    main()
