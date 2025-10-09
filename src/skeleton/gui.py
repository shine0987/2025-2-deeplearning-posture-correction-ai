import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
from pathlib import Path

# 경로에 있는 skeltonpose 모듈을 import하기 위해 sys.path를 조정
import sys
sys.path.append(str(Path(__file__).parent))

try:
    from skeltonpose import process_images_in_folder
except Exception as e:
    process_images_in_folder = None
    _IMPORT_ERROR = str(e)
else:
    _IMPORT_ERROR = None

class App:
    def __init__(self, master):
        self.master = master
        master.title('Skeleton Processor GUI')

        self.folder_var = tk.StringVar(value='labeling_test_images')
        tk.Label(master, text='이미지 폴더').grid(row=0, column=0, sticky='w')
        tk.Entry(master, textvariable=self.folder_var, width=50).grid(row=0, column=1)
        tk.Button(master, text='선택', command=self.browse).grid(row=0, column=2)

        self.auto_var = tk.BooleanVar(value=False)
        tk.Checkbutton(master, text='자동 임계값', variable=self.auto_var).grid(row=1, column=0, sticky='w')

        tk.Label(master, text='임계 k 값').grid(row=1, column=1, sticky='e')
        self.k_var = tk.DoubleVar(value=2.0)
        tk.Entry(master, textvariable=self.k_var, width=8).grid(row=1, column=2, sticky='w')

        self.adjust_var = tk.BooleanVar(value=False)
        tk.Checkbutton(master, text='이미지 재주석', variable=self.adjust_var).grid(row=2, column=0, sticky='w')

        tk.Label(master, text='결과 CSV').grid(row=3, column=0, sticky='w')
        self.result_var = tk.StringVar(value='skeleton_coords.csv')
        tk.Entry(master, textvariable=self.result_var, width=30).grid(row=3, column=1)

        tk.Button(master, text='실행', command=self.run).grid(row=4, column=0)
        tk.Button(master, text='종료', command=master.quit).grid(row=4, column=1)

        self.status = tk.StringVar(value='준비')
        tk.Label(master, textvariable=self.status).grid(row=5, column=0, columnspan=3, sticky='w')

        if _IMPORT_ERROR:
            messagebox.showerror('Import Error', f'Unable to import skeltonpose.py:\n{_IMPORT_ERROR}')

    def browse(self):
        d = filedialog.askdirectory(initialdir='.')
        if d:
            self.folder_var.set(d)

    def run(self):
        if process_images_in_folder is None:
            messagebox.showerror('Error', 'skeltonpose 모듈을 불러오지 못했습니다.')
            return
        folder = self.folder_var.get()
        result = self.result_var.get()
        auto = self.auto_var.get()
        k = float(self.k_var.get())
        adjust = self.adjust_var.get()

        def target():
            try:
                self.status.set('처리중...')
                process_images_in_folder(folder, output_csv=result, overwrite=True, backup_folder=None,
                                         auto_threshold=auto, threshold_method='mean_std', threshold_k=k, adjust_images=adjust)
                self.status.set('완료')
                messagebox.showinfo('완료', '처리가 완료되었습니다.')
            except Exception as e:
                self.status.set('오류')
                messagebox.showerror('오류', str(e))

        threading.Thread(target=target, daemon=True).start()

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
