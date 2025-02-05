import torch
from diffusers import StableDiffusionPipeline
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from tkinter.filedialog import askopenfilename, asksaveasfilename
import pathlib
import sys
import io
from contextlib import redirect_stdout
from threading import Thread
import random
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

window_title = "txt2img v1"

img_pil = Image.open("default_img.png")

class IORedirector(object):
    def __init__(self,text_area):
        self.text_area = text_area

class StdoutRedirector(IORedirector):
    def write(self,str):
        txt_console.insert("1.0", str+"\n")
        sys.__stdout__.write(str)

class StderrRedirector(IORedirector):
    def write(self,str):
        txt_console.insert("1.0", str+"\n")
        sys.__stdout__.write(str)

def get_multi_writer(streams):
    writer = type('obj', (object,), {})
    writer.write = lambda s: [stream.write(s) for stream in streams]
    return writer

def catch_output(func, args, kwargs):
    streams = [sys.stderr, io.StringIO()]
    with redirect_stdout(get_multi_writer(streams)):
        func(*args, **kwargs)
    return streams[1].getvalue()

def open_txt_file():
    filepath = askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not filepath:
        return
    txt_edit.delete("1.0", tk.END)
    with open(filepath, mode="r", encoding="utf-8") as input_file:
        text = input_file.read()
        txt_edit.insert(tk.END, text)
    window.title(f"{window_title} - {filepath}")

def save_txt_file():
    filepath = asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if not filepath:
        return
    with open(filepath, mode="w", encoding="utf-8") as output_file:
        text = txt_edit.get("1.0", tk.END)
        output_file.write(text)
    window.title(f"{window_title} - {filepath}")

def open_img_file():
    filepath = askopenfilename(
        filetypes=[("Image Files", "*.png"), ("All Files", "*.*")]
    )
    if not filepath:
        return

    img = Image.open(filepath)
    img = ImageTk.PhotoImage(img)
    img_panel.image = img
    img_panel.config(image=img)
    window.title(f"{window_title} - {filepath}")

def save_img_file():
    filepath = asksaveasfilename(
        title="last_img_"+str(seed),
        defaultextension=".png",
        filetypes=[("Image Files", "*.png"), ("All Files", "*.*")],
    )
    if not filepath:
        return
    img_pil.save(filepath)
    window.title(f"{window_title} - {filepath}")

def open_model_file():
    filepath = askopenfilename(
        filetypes=[("Model Files", "*.safetensors"), ("All Files", "*.*")]
    )
    if not filepath:
        return
    path = pathlib.Path(filepath)
    secondparent = path.parent.parent
    print(str(path.relative_to(secondparent)))
    txt_model.delete(0,tk.END)
    txt_model.insert(0,str(path.relative_to(secondparent)))
    window.title(f"{window_title} - {filepath}")

def show_advanced_options():
    if(btn_show_advanced_options['text'] == "Show advanced"):
        lbl_width.grid(row=7, column=0, sticky="ew", padx=5)
        txt_width.grid(row=8, column=0, sticky="ew", padx=5)
        lbl_height.grid(row=9, column=0, sticky="ew", padx=5)
        txt_height.grid(row=10, column=0, sticky="ew", padx=5)
        lbl_steps.grid(row=11, column=0, sticky="ew", padx=5)
        txt_steps.grid(row=12, column=0, sticky="ew", padx=5)
        lbl_model.grid(row=13, column=0, sticky="ew", padx=5)
        txt_model.grid(row=14, column=0, sticky="ew", padx=5)
        lbl_seed.grid(row=15, column=0, sticky="ew", padx=5)
        txt_seed.grid(row=16, column=0, sticky="ew", padx=5)
        lbl_seed_random.grid(row=17, column=0, sticky="ew", padx=5)
        chk_seed_random.grid(row=18, column=0, sticky="ew", padx=5)
        lbl_negative_prompt.grid(row=19, column=0, sticky="ew", padx=5)
        txt_negative_prompt.grid(row=20, column=0, sticky="ew", padx=5)
        btn_show_advanced_options.config(text="Hide advanced")
    else:
        lbl_width.grid_forget()
        txt_width.grid_forget()
        lbl_height.grid_forget()
        txt_height.grid_forget()
        lbl_steps.grid_forget()
        txt_steps.grid_forget()
        lbl_model.grid_forget()
        txt_model.grid_forget()
        lbl_seed.grid_forget()
        txt_seed.grid_forget()
        lbl_seed_random.grid_forget()
        chk_seed_random.grid_forget()
        lbl_negative_prompt.grid_forget()
        txt_negative_prompt.grid_forget()
        btn_show_advanced_options.config(text="Show advanced")

window = tk.Tk()
window.title(window_title)
window.resizable(width=True, height=True)

window.rowconfigure(0, minsize=400, weight=1)
window.columnconfigure(1, minsize=400, weight=1)

width = 512
height = 512
steps = 30
model_path = "models/realismByStableYogi_sd15V9.safetensors"
seed = 1337

img = img_pil.resize((width, height))
img = ImageTk.PhotoImage(img)

frm_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
frm_txt = tk.Frame(window, relief=tk.RAISED, bd=2)
frm_panel = tk.Frame(window, relief=tk.RAISED, bd=2)
frm_progress = ttk.Progressbar(window, mode="indeterminate", orient=tk.HORIZONTAL)

txt_edit = tk.Text(frm_txt, wrap=tk.WORD, undo=True, maxundo=-1)
txt_console = tk.Text(frm_txt, wrap=tk.WORD, undo=True, maxundo=-1, background="grey")

img_panel = tk.Label(frm_panel, image=img)
img_panel.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

# img_panel.image = img
# txt_edit.insert(tk.END, "Beautiful photo of a happy woman looking into image with text 'v1'.")
txt_edit.insert(tk.END, "Happy woman using personal computer in a futuristic environment.")


lbl_seed_random = tk.Label(frm_buttons, text="Randomize seed on generate:", anchor="w")

music_is_checked = tk.IntVar()

pygame.mixer.init()

sound = pygame.mixer.Sound("music.opus")

def chk_music_clicked(music_is_checked):
    music_is_checked = music_is_checked.get()
    print(music_is_checked)
    if(music_is_checked == 1):
        pygame.mixer.unpause()
    else:
        pygame.mixer.pause()
        
        
chk_music = tk.Checkbutton(frm_buttons, text="Music", onvalue=1, offvalue=0, variable=music_is_checked, command=lambda:chk_music_clicked(music_is_checked), state='active')
chk_music.select()
sound.play(-1)

chk_music.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

btn_open_txt_file = tk.Button(frm_buttons, text="Load txt", command=open_txt_file)
btn_save_txt_file = tk.Button(frm_buttons, text="Save txt", command=save_txt_file)

btn_open_txt_file.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
btn_save_txt_file.grid(row=2, column=0, sticky="ew", padx=5)

btn_open_img_file = tk.Button(frm_buttons, text="Load img", command=open_img_file)
btn_save_img_file = tk.Button(frm_buttons, text="Save img", command=save_img_file)

btn_open_img_file.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
btn_save_img_file.grid(row=4, column=0, sticky="ew", padx=5)

btn_open_model_file = tk.Button(frm_buttons, text="Load model", command=open_model_file)
btn_open_model_file.grid(row=5, column=0, sticky="ew", padx=5, pady=5)

btn_show_advanced_options = tk.Button(frm_buttons, text="Show advanced", command=show_advanced_options)
btn_show_advanced_options.grid(row=6, column=0, sticky="ew", padx=5, pady=5)

lbl_width = tk.Label(frm_buttons, text="Img width:", anchor="w")
lbl_height = tk.Label(frm_buttons, text="Img height:", anchor="w")
lbl_steps = tk.Label(frm_buttons, text="Steps:", anchor="w")

txt_width = tk.Entry(frm_buttons)
txt_width.delete(0,tk.END)
txt_width.insert(0,width)

txt_height = tk.Entry(frm_buttons)
txt_height.delete(0,tk.END)
txt_height.insert(0,height)

txt_steps = tk.Entry(frm_buttons)
txt_steps.delete(0,tk.END)
txt_steps.insert(0,steps)

lbl_model = tk.Label(frm_buttons, text="Model:", anchor="w")

txt_model = tk.Entry(frm_buttons)
txt_model.delete(0,tk.END)
txt_model.insert(0,model_path)

lbl_seed = tk.Label(frm_buttons, text="Seed:", anchor="w")

txt_seed = tk.Entry(frm_buttons)
txt_seed.delete(0,tk.END)
txt_seed.insert(0,seed)

lbl_seed_random = tk.Label(frm_buttons, text="Randomize seed on generate:", anchor="w")

seed_rng_is_checked = tk.IntVar()

def chk_seed_random_clicked(seed_rng_is_checked):
    seed_rng_is_checked = seed_rng_is_checked.get()

chk_seed_random = tk.Checkbutton(frm_buttons, onvalue=1, offvalue=0, variable=seed_rng_is_checked, command=lambda:chk_seed_random_clicked(seed_rng_is_checked), state='active')
chk_seed_random.select()

lbl_negative_prompt = tk.Label(frm_buttons, text="Negative prompt:", anchor="w")

txt_negative_prompt = tk.Entry(frm_buttons)
txt_negative_prompt.delete(0,tk.END)
txt_negative_prompt.insert(0,"NSFW")


def gen_thread():
    frm_progress.grid(row=1, column=0, sticky="nsew", columnspan=3)
    frm_progress.start()
    t1=Thread(target=gen_imgs, args=[seed_rng_is_checked]) 
    t1.daemon = True
    t1.start() 

def gen_imgs(seed_rng_is_checked):
    sys.stdout = StdoutRedirector( txt_console )
    sys.stderr = StderrRedirector( txt_console )
    seed_rng_is_checked = seed_rng_is_checked.get()
    if(seed_rng_is_checked == 1):
        txt_seed.delete(0,tk.END)
        txt_seed.insert(0,random.randint(0,9999))
    seed = int(txt_seed.get())
    print("\nSeed: " + str(seed) + "\n")

    model_path = str(txt_model.get())
    pipe = StableDiffusionPipeline.from_single_file(model_path, )
    width = int(txt_width.get())
    height = int(txt_height.get())
    steps = int(txt_steps.get())
    prompt = str(txt_edit.get("1.0", tk.END))
    print("\nPositive prompt:\n" + prompt + "\n")
    negative_prompt = str(txt_negative_prompt.get())
    if(negative_prompt):
        print("\nNegative prompt:\n" + negative_prompt + "\n")
    
    # for x in range(10):
    generator = torch.manual_seed(seed)
    img = pipe(prompt, negative_prompt=negative_prompt, num_inference_steps=steps, width=width, height=height, generator=generator).images[0]
    img.save("last_img_"+str(seed)+".png")
    
    # img = pipe(prompt, negative_prompt=negative_prompt, num_inference_steps=steps, width=width, height=height, generator=generator).images[0]
    # img_panel.image = image_grid(imgs, rows, cols)
    img = ImageTk.PhotoImage(img)
    img_panel.image = img
    img_panel.config(image=img)
    frm_progress.stop()
    frm_progress.grid_forget()

    # To stop redirecting stdout:
    sys.stdout = sys.__stdout__
    # To stop redirecting stderr:
    sys.stderr = sys.__stderr__

btn_gen_image = tk.Button(frm_panel, text="Generate", command=gen_thread)
btn_gen_image.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

frm_buttons.grid(row=0, column=0, sticky="ns")
frm_txt.grid(row=0, column=1, sticky="nsew")
frm_panel.grid(row=0, column=2, sticky="nsew")

txt_edit.grid(row=0, column=0, sticky="nsew")
txt_console.grid(row=1, column=0, sticky="nsew")

window.mainloop()
