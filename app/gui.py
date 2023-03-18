from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, Label, messagebox

import cv2 
import numpy as np
import torch
import serial

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

userlist = { 'Email': 'david5512@gmail.com', 'Password': '123456'}
class_id_list = []
ser = serial.Serial()

MODEL_PATH = 'exp9/weights/best.pt'
model = torch.hub.load('ultralytics/yolov5', 'custom', path = MODEL_PATH, force_reload=True)
model.conf = 0.33

def loginfunc():
    if entry_1.get() == userlist.get("Email") :
        if entry_2.get() == userlist.get("Password"):
            make_welcome_page()
    if len(entry_1.get()) != 0 and len(entry_2.get()) != 0 :
        if entry_1.get() not in userlist.get("Email"):
            messagebox.showerror("error","電子郵件或密碼有錯")

    if len(entry_1.get()) == 0 :
        messagebox.showwarning("warning","電子郵件或密碼不能為空!")
    elif len(entry_2.get()) == 0 :
        messagebox.showwarning("warning","電子郵件或密碼不能為空!")

def logoutfunc():
    make_login_page()

window = Tk()
window.title("犬隻智能健康系統")


def make_login_page():
    window.geometry("1024x768")
    window.configure(bg = "#FFFFFF")
    canvas3.place_forget()
    clear_entry()
    canvas.place(x = 0,y = 0)

def make_welcome_page():
    window.geometry("1024x768")
    window.configure(bg = "#5D5FEF")
    canvas.place_forget()
    canvas2.place(x = 0, y = 0)
    window.after(3000, make_main_page)

def make_main_page():
    window.geometry("832x480")
    window.configure(bg = "#FFFFFF")
    canvas2.place_forget()
    canvas3.place(x = 0, y = 0)

def clear_entry():
    entry_1.delete(0, 'end')
    entry_2.delete(0, 'end')

def read_weight():
    if(ser.isOpen()):
        line = ser.readline()   # read a byte
        line_read = (line.decode('utf-8'))
        if (len(line_read) != 0):
            try:
                weight = float(line_read)
                if(weight >= 0):
                    if(weight == -0.0):
                        weight = 0.0
                elif(weight < 0):
                    weight = 0.0
            except:
                weight = 0.0
            dog_weight.configure(text=weight)
        
        elif (len(line_read) == 0):
            weight = 0.0
            dog_weight.configure(text=weight)

def port_open():
    try:
        ser.port = 'COM3'            #設定埠號
        ser.baudrate = 9600     #設定波特率
        ser.bytesize = 8        #設定資料位
        ser.stopbits = 1        #設定停止位
        ser.parity = "N"        #設定校驗位
        ser.open()              #開啟串列埠,要找到對的串列埠號才會成功
        ser.timeout = 1
        print("體重感測器開啟成功")
    except:
        print("體重感測器開啟失敗")
    
def mutidetect(class_id_list):
    if 'constipation' in class_id_list:
        if 'constipation' in class_id_list and 'healthy' in class_id_list and 'diarrhea' in class_id_list:
            description.configure(text="便祕，健康，腹瀉")
        elif 'constipation' in class_id_list and 'healthy' in class_id_list:
            description.configure(text="便祕，健康")
        elif 'constipation' in class_id_list and 'diarrhea' in class_id_list:
            description.configure(text="便祕，腹瀉")
        else:
            description.configure(text="乾燥、硬、容易碎裂的糞便。")
            advise.configure(text="糞便太過乾燥，平時要注意狗狗喝水的狀況。")
    elif 'healthy' in class_id_list:
        if 'healthy' in class_id_list and 'diarrhea' in class_id_list:
            description.configure(text="很有水份的，快要不成形的糞便")
            advise.configure(text="常見的糞便不須過多擔心，主要是澱粉類比例太多，也可能消化吸收不好，建議給予益生菌可以幫助許多。")
        else:
            description.configure(text="成形良好、撿起來不會留印痕的糞便")
            advise.configure(text="形狀和乾濕度都可以說是完美的狀態，代表腸道是健康的。請繼續維持。")
    elif 'diarrhea' in class_id_list:
            description.configure(text="水樣狀腹瀉")
            advise.configure(text="明顯就是一種病狀了，可能，寄生蟲，或者病毒感染。建議就醫。")



def StreamOpenCV():
    cap = cv2.VideoCapture(0)
    port_open()

    while(cap.isOpened()):
        ret,frame = cap.read()
        # Make detections 
        results = model(frame)
        cv2.imshow('object detection', np.squeeze(results.render()))

        # getclass
        class_id_list = []

        results_in_panda = results.pandas().xyxy[0]
        class_id_list = results_in_panda['name'].tolist()

        if(len(class_id_list) != 0):
            mutidetect(class_id_list)
        elif(len(class_id_list) == 0):
            description.configure(text="未偵測到糞便")
            advise.configure(text="未偵測到糞便")
            
        if cv2.waitKey(10) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            description.configure(text="尚未開始偵測")
            advise.configure(text="尚未開始偵測")
            
    
        read_weight()
        dog_weight.update()
        
        

canvas = Canvas(
    window,
    bg = "#FFFFFF",
    height = 768,
    width = 1024,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    canvas,
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_1 clicked"),
    relief="flat"
)
button_1.place(
    x=597.0,
    y=561.0,
    width=71.0,
    height=69.0
)

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    canvas,
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_2 clicked"),
    relief="flat"
)
button_2.place(
    x=714.0,
    y=552.0,
    width=72.0,
    height=91.0
)

button_image_3 = PhotoImage(
    file=relative_to_assets("button_3.png"))
button_3 = Button(
    canvas,
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_3 clicked"),
    relief="flat"
)
button_3.place(
    x=828.0,
    y=556.0,
    width=83.0,
    height=82.0
)

canvas.create_text(
    681.0,
    62.0,
    anchor="nw",
    text="Sign in",
    fill="#000000",
    font=("Candara", 48 * -1)
)

canvas.create_text(
    570.0,
    184.0,
    anchor="nw",
    text="Email",
    fill="#000000",
    font=("Candara", 24 * -1)
)

canvas.create_text(
    570.0,
    342.0,
    anchor="nw",
    text="Password",
    fill="#000000",
    font=("Candara", 24 * -1)
)

button_image_4 = PhotoImage(
    file=relative_to_assets("button_4.png"))
button_4 = Button(
    canvas,
    image=button_image_4,
    borderwidth=0,
    highlightthickness=0,
    command=loginfunc,
    relief="flat"
)
button_4.place(
    x=642.0,
    y=676.0,
    width=212.0,
    height=69.0
)

entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    756.0,
    250.5,
    image=entry_image_1
)
entry_1 = Entry(
    canvas,
    bd=0,
    bg="#C4C4C4",
    highlightthickness=0,
    font = ("Inter", 16)
)
entry_1.place(
    x=591.5,
    y=216.0,
    width=329.0,
    height=67.0
)

entry_image_2 = PhotoImage(
    file=relative_to_assets("entry_2.png"))
entry_bg_2 = canvas.create_image(
    756.0,
    409.5,
    image=entry_image_2
)
entry_2 = Entry(
    canvas,
    bd=0,
    bg="#C4C4C4",
    highlightthickness=0,
    font = ("Inter", 16),
    show="*"
)
entry_2.place(
    x=591.5,
    y=375.0,
    width=329.0,
    height=67.0
)

canvas.create_text(
    630.0,
    487.0,
    anchor="nw",
    text="Other login methods",
    fill="#000000",
    font=("Inter", 24 * -1)
)

image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    248.0,
    384.0,
    image=image_image_1
)

# welcome_page

canvas2 = Canvas(
    window,
    bg = "#5D5FEF",
    height = 768,
    width = 1024,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas2.create_text(
    123.0,
    337.0,
    anchor="nw",
    text="歡迎使用犬隻智能健康系統",
    fill="#FFFFFF",
    font=("Microsoft JhengHei UI", 64 * -1, "bold")
)


# main_page

canvas3 = Canvas(
    window,
    bg = "#FFFFFF",
    height = 480,
    width = 832,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

button_image_5 = PhotoImage(
    file=relative_to_assets("button_5.png"))
button_5 = Button(
    canvas3,
    image=button_image_5,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: window.destroy(),
    relief="flat"
)
button_5.place(
    x=525.0,
    y=366.0,
    width=145.0,
    height=47.193397521972656
)

button_image_6 = PhotoImage(
    file=relative_to_assets("button_6.png"))
button_6 = Button(
    canvas3,
    image=button_image_6,
    borderwidth=0,
    highlightthickness=0,
    command= logoutfunc,
    relief="flat"
)
button_6.place(
    x=343.0,
    y=366.0,
    width=145.0,
    height=47.193397521972656
)

button_image_7 = PhotoImage(
    file=relative_to_assets("button_7.png"))
button_7 = Button(
    canvas3,
    image=button_image_7,
    borderwidth=0,
    highlightthickness=0,
    command=StreamOpenCV,
    relief="flat"
)
button_7.place(
    x=161.0,
    y=366.0,
    width=145.0,
    height=47.193397521972656
)

canvas3.create_rectangle(
    65.0,
    63.0,
    384.0,
    166.0,
    fill="#E5E5E5",
    outline="")

canvas3.create_rectangle(
    448.0,
    63.0,
    767.0,
    166.0,
    fill="#E5E5E5",
    outline="")

canvas3.create_rectangle(
    65.0,
    199.0,
    384.0,
    302.0,
    fill="#E5E5E5",
    outline="")

canvas3.create_rectangle(
    448.0,
    199.0,
    767.0,
    302.0,
    fill="#E5E5E5",
    outline="")

canvas3.create_text(
    75.0,
    72.0,
    anchor="nw",
    text="愛犬姓名",
    fill="#1862F0",
    font=("Microsoft JhengHei UI", 20 * -1)
)

canvas3.create_text(
    462.0,
    70.0,
    anchor="nw",
    text="愛犬體重",
    fill="#1862F0",
    font=("Microsoft JhengHei UI", 20 * -1)
)

canvas3.create_text(
    75.0,
    206.0,
    anchor="nw",
    text="糞便敘述",
    fill="#1862F0",
    font=("Microsoft JhengHei UI", 20 * -1)
)

canvas3.create_text(
    462.0,
    206.0,
    anchor="nw",
    text="建議",
    fill="#1862F0",
    font=("Microsoft JhengHei UI", 20 * -1)
)

dog_name = Label(canvas3, font=("Microsoft JhengHei UI", 32), bg="#E5E5E5", text= "Jason")
dog_name.place(
    x=155.0,
    y=95.0,
    anchor="nw"
)

description = Label(canvas3, font=("Microsoft JhengHei UI", 12), bg="#E5E5E5", text="尚未開始偵測")
description.place(
    x=72.0,
    y=231.0,
    anchor="nw"
)

advise = Label(canvas3, font=("Microsoft JhengHei UI", 12), bg="#E5E5E5", text="尚未開始偵測", wraplength=300, justify="left")
advise.place(
    x=460.0,
    y=230.0,
    anchor="nw"
)

dog_weight = Label(canvas3, font=("Microsoft JhengHei UI", 36), bg="#E5E5E5", text="0.0")
dog_weight.place(
    x=568.0,
    y=92.0,
    anchor="nw"
)

canvas3.create_text(
    721.0,
    128.0,
    anchor="nw",
    text="kg",
    fill="#000000",
    font=("Inter Medium", 24 * -1)
)

description.update()
advise.update()

make_login_page()

window.resizable(False, False)
window.mainloop()
