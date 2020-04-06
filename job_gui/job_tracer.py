from tkinter import *

from utils.utils import update_jobs_status
from utils.utils import read_all_experiments
from utils.utils import save_all_experiments

import subprocess
import yaml
import os

from utils.utils import load_cluster_info

WINDOW_TITLE = 'Job tracer'
WINDOW_WIDTH = 1500
ENTRY_HEIGHT = 50
JOB_INFO_X = 280
LABELS_X = 250
RUN_COLOR = 'green'
DONE_COLOR = 'black'
FONT = 'ArialBlack 14'
OUTPUT_BUTTON_POSITION = 600
BUTTON_X_SHIFT = 100
BUTTON_WIDTH = 100
BUTTON_SEPARATOR = 10
REFRESH_X = 800


class ClusterRunnerGUI:
    def __init__(self):


        cluster_info = load_cluster_info()
        self.login = cluster_info['login']
        self.user = cluster_info['user']
        self.local_storage = cluster_info['local_storage_path']

        self.root=Tk()
        self.root.title('Jobs tracer')
        frame=Frame(self.root,width=1300,height=1300)
        frame.pack(expand=True, fill=BOTH) #.grid(row=0,column=0)
        self.canvas=Canvas(frame,bg='#FFFFFF',width=WINDOW_WIDTH,height=100*ENTRY_HEIGHT,scrollregion=(0,0,1500,1500))
        hbar=Scrollbar(frame,orient=HORIZONTAL)
        hbar.pack(side=BOTTOM,fill=X)
        hbar.config(command=self.canvas.xview)
        vbar=Scrollbar(frame,orient=VERTICAL)
        vbar.pack(side=RIGHT,fill=Y)
        vbar.config(command=self.canvas.yview)
        self.canvas.config(width=1000,height=800)
        self.canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.pack(side=LEFT,expand=True,fill=BOTH)
        update_jobs_status(self.login, self.user)
        self.plot_labels()
        self.plot_experiments()
        self.root.mainloop()

    def refresh(self):
        self.clear_canvas()
        update_jobs_status(self.login, self.user)
        self.plot_labels()
        self.plot_experiments()

    def plot_experiments(self):
        all_experiments = read_all_experiments()
        for idx, job_id in enumerate(all_experiments):
            self.plot_job(job_id, all_experiments[job_id], idx+1)

    def clear_canvas(self):
        self.canvas.delete('all')

    def plot_labels(self):
        self.canvas.create_text(LABELS_X + 30, 15,
                                fill=DONE_COLOR, font=FONT,
                                text='JOB_ID | STATUS | TIME | LIMIT | NAME')
        refreshBTN = self.canvas.create_rectangle(REFRESH_X, BUTTON_SEPARATOR, REFRESH_X + BUTTON_WIDTH, ENTRY_HEIGHT - BUTTON_SEPARATOR,
                                                 fill="grey80", outline="grey60")
        refreshTXT = self.canvas.create_text(REFRESH_X + BUTTON_WIDTH//2, ENTRY_HEIGHT//2, text="Refresh", font=FONT)
        self.canvas.tag_bind(refreshBTN, "<Button-1>",
                             func=lambda _: self.refresh())
        self.canvas.tag_bind(refreshTXT, "<Button-1>",
                             func=lambda _: self.refresh())

    def plot_job(self, job_id, job_info, position):
        y_position = position*ENTRY_HEIGHT
        job_color = DONE_COLOR if job_info['status'] == 'D' else RUN_COLOR

        text_to_show = f'{job_id} | '
        text_to_show += job_info['status'] + ' | '
        text_to_show += job_info['time'] + ' | '
        text_to_show += job_info['time_limit'] + ' | '
        if 'name' in job_info:
            text_to_show += job_info['name']
        else:
            text_to_show += '[no name]'
        self.canvas.create_text(JOB_INFO_X, y_position+ENTRY_HEIGHT//2,
                                     fill=job_color, font=FONT,  text=text_to_show)

        def show_remote(file, login, local_storage):
            remote_out = subprocess.run(f'ssh {login} cat {file}', shell=True, capture_output=True, encoding='utf-8')
            local_output = os.path.join(local_storage, 'current_out.out')
            with open(local_output, 'w') as file:
                file.write(remote_out.stdout)
            subprocess.run(f'gedit {local_output}', shell=True, capture_output=True)

        def kill(login, job_id):
            subprocess.run(f'ssh {login} scancel {job_id}', shell=True, capture_output=True, encoding='utf-8')
            print(f'ssh {login} scancel {job_id}')
            self.refresh()

        def delete_job(job_id):
            all_experiments = read_all_experiments()
            del all_experiments[job_id]
            save_all_experiments(all_experiments)
            self.refresh()

        if 'remote_output' in job_info:
            buttonOUT = self.canvas.create_rectangle(OUTPUT_BUTTON_POSITION + BUTTON_SEPARATOR, y_position + BUTTON_SEPARATOR,
                                                    OUTPUT_BUTTON_POSITION + BUTTON_WIDTH - BUTTON_SEPARATOR, y_position + ENTRY_HEIGHT - BUTTON_SEPARATOR,
                                                    fill="grey80", outline="grey60")
            buttonOUT_TXT = self.canvas.create_text(OUTPUT_BUTTON_POSITION + BUTTON_WIDTH//2, y_position + ENTRY_HEIGHT // 2,
                                                text="Output", font=FONT)
            self.canvas.tag_bind(buttonOUT, "<Button-1>", func=lambda _: show_remote(job_info['remote_output'], self.login, self.local_storage))
            self.canvas.tag_bind(buttonOUT_TXT, "<Button-1>", func=lambda _: show_remote(job_info['remote_output'], self.login, self.local_storage))

        if 'remote_error' in job_info:

            buttonERR = self.canvas.create_rectangle(OUTPUT_BUTTON_POSITION + BUTTON_X_SHIFT + BUTTON_SEPARATOR, y_position + BUTTON_SEPARATOR,
                                                    OUTPUT_BUTTON_POSITION + BUTTON_X_SHIFT + BUTTON_WIDTH - BUTTON_SEPARATOR, y_position + ENTRY_HEIGHT - BUTTON_SEPARATOR,
                                                    fill="grey80", outline="grey60")
            buttonERR_TXT = self.canvas.create_text(OUTPUT_BUTTON_POSITION + BUTTON_X_SHIFT + BUTTON_WIDTH//2, y_position + ENTRY_HEIGHT // 2,
                                                text="Error", font=FONT)
            self.canvas.tag_bind(buttonERR, "<Button-1>",
                                 func=lambda _: show_remote(job_info['remote_error'], self.login, self.local_storage))
            self.canvas.tag_bind(buttonERR_TXT, "<Button-1>",
                                 func=lambda _: show_remote(job_info['remote_error'], self.login, self.local_storage))

        if job_info['status'] != 'D':

            buttonKILL = self.canvas.create_rectangle(OUTPUT_BUTTON_POSITION + 2*BUTTON_X_SHIFT + BUTTON_SEPARATOR,
                                                     y_position + BUTTON_SEPARATOR,
                                                     OUTPUT_BUTTON_POSITION + 2*BUTTON_X_SHIFT + BUTTON_WIDTH - BUTTON_SEPARATOR,
                                                     y_position + ENTRY_HEIGHT - BUTTON_SEPARATOR,
                                                     fill="grey80", outline="grey60")
            buttonKILL_TXT = self.canvas.create_text(OUTPUT_BUTTON_POSITION + 2*BUTTON_X_SHIFT + BUTTON_WIDTH // 2,
                                                    y_position + ENTRY_HEIGHT // 2,
                                                    text="Kill", font=FONT)
            self.canvas.tag_bind(buttonKILL, "<Button-1>",
                                 func=lambda _: kill(self.login, job_id))
            self.canvas.tag_bind(buttonKILL_TXT, "<Button-1>",
                                 func=lambda _: kill(self.login, job_id))

        buttonDEL = self.canvas.create_rectangle(OUTPUT_BUTTON_POSITION + 3 * BUTTON_X_SHIFT + BUTTON_SEPARATOR,
                                                  y_position + BUTTON_SEPARATOR,
                                                  OUTPUT_BUTTON_POSITION + 3 * BUTTON_X_SHIFT + BUTTON_WIDTH - BUTTON_SEPARATOR,
                                                  y_position + ENTRY_HEIGHT - BUTTON_SEPARATOR,
                                                  fill="grey80", outline="grey60")
        buttonDEL_TXT = self.canvas.create_text(OUTPUT_BUTTON_POSITION + 3 * BUTTON_X_SHIFT + BUTTON_WIDTH // 2,
                                                 y_position + ENTRY_HEIGHT // 2,
                                                 text="Delete", font=FONT)
        self.canvas.tag_bind(buttonDEL, "<Button-1>",
                             func=lambda _: delete_job(job_id))
        self.canvas.tag_bind(buttonDEL_TXT, "<Button-1>",
                             func=lambda _: delete_job(job_id))