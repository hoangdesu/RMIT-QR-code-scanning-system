from ctypes import alignment
from tkinter.constants import BOTH, BOTTOM, CENTER, DISABLED, LEFT, NW, RAISED, RIGHT, SUNKEN, TOP
from imutils.video import VideoStream
from pyzbar import pyzbar
import cv2
import imutils
import time
import requests
from datetime import datetime, date
import os
import tkinter as tk
from tkinter import Label, ttk
from PIL import Image, ImageTk

API_URL = 'http://52.76.27.252:3000/registrations/verify' 

def main():
    # system variables
    qrFound = False
    totalPeopleScanned = 0
    # start_time = 0
    
    
    # VideoStream
    vs = VideoStream(src=0).start()
    time.sleep(2.0) 
    
    # GUI
    app = tk.Tk()
    scr_width, scr_height = 1200, 700
    x_shift, y_shift = 100, 50
    geo_str = f"{scr_width}x{scr_height}+{x_shift}+{y_shift}"
    app.geometry(geo_str)
    app.title("RMIT QR code scanning system")
    
    # audio
    approved = './approved.wav'
    rejected = './rejected.wav'
    
    # ---- top frame ---
    topFrame = tk.LabelFrame(app, padx=20, pady=10)
    timeFontTuple = ("Roboto", 15, "normal")
    dateTimeLbl = tk.Label(topFrame, text="", padx=10, bg="#080230", fg="#eff0e1", font=timeFontTuple)
    logo_bytecode = Image.open('./assets/rmit_logo.png').resize((2560//20, 900//20))
    logo_img = ImageTk.PhotoImage(logo_bytecode)   
    logo = tk.Label(topFrame, image=logo_img)
    
    logo.pack(side=LEFT)
    tk.Label(topFrame, text="QR SCANNING SYSTEM", padx=20).pack(side=LEFT)
    # timeLbl.pack(side=RIGHT)
    dateTimeLbl.pack(side=RIGHT)
    topFrame.pack(fill='x')
    
    # bottom frame
    bottomFrame = tk.LabelFrame(app)
    bottomFrame.pack(fill='x')
    
    
    # --- camera frame (right) ---
    cameraFrame = tk.LabelFrame(bottomFrame)
    cameraFrame.pack(side=RIGHT, padx=5, pady=10)
    liveCamLbl = tk.Label(cameraFrame, padx=50, pady=50)
    scanQR_img = ImageTk.PhotoImage(Image.open('./assets/scanQR.jpeg').resize((450, 252)))
    capturedCamLbl = tk.Label(cameraFrame, image=scanQR_img, padx=50, pady=50)
    
    tk.Label(cameraFrame, text="Live 🔴").pack()
    liveCamLbl.pack()
    tk.Label(cameraFrame, text="Last captured").pack()
    capturedCamLbl.pack()
    
    
    # --- info frame (left) ---
    infoFrame = tk.LabelFrame(bottomFrame)
    # tk.Label(infoFrame, text="INFORMATION", pady=10, bg="pink").pack(fill='x')
    infoFrame.pack(fill='x', padx=5, pady=10)
    infoFrameFontLeft = ("Roboto", 20, "normal")
    infoFrameFontRight = ("Roboto", 26, "bold")
    
    # name container
    infoFrame1 = tk.Frame(infoFrame)
    infoFrame1.pack(fill='x')
    lbl1 = tk.Label(infoFrame1, text="Name", width=10, font=infoFrameFontLeft)
    lbl1.pack(side=LEFT, padx=10, pady=15)
    nameLabel = tk.Label(infoFrame1, width=30, bg="white", font=infoFrameFontRight, text="", pady=5)
    nameLabel.pack(fill='x', padx=10, pady=15)  
    
    # id container
    infoFrame2 = tk.Frame(infoFrame)
    infoFrame2.pack(fill='x')
    lbl2 = tk.Label(infoFrame2, text="ID", width=10, font=infoFrameFontLeft)
    lbl2.pack(side=LEFT, padx=10, pady=15)
    idLabel = tk.Label(infoFrame2, width=30, bg="white", font=infoFrameFontRight, text="", pady=5)
    idLabel.pack(fill='x', padx=10, pady=15)
    
    # role container
    infoFrame3 = tk.Frame(infoFrame)
    infoFrame3.pack(fill='x')
    lbl3 = tk.Label(infoFrame3, text="Role", width=10, font=infoFrameFontLeft)
    lbl3.pack(side=LEFT, padx=10, pady=15)
    roleLabel = tk.Label(infoFrame3, width=30, bg="white", font=infoFrameFontRight, text="", pady=5)
    roleLabel.pack(fill='x', padx=10, pady=15)  
    
    # scan status
    scanStatusLabel = tk.Label(infoFrame, width=30, bg="#fff", fg="#000", font=infoFrameFontRight, text="Scan your QR...", pady=10)
    scanStatusLabel.pack(fill='x')
    
    
    # statistic frame (below)
    statsFrame = tk.LabelFrame(bottomFrame)
    statsFrame.pack(fill='x', padx=5)
    
    # list box
    listboxFrame = tk.Frame(statsFrame, padx=10, pady=10)
    tk.Label(listboxFrame, text="Past QR scans", font=("Roboto", 15, "normal"), pady=4).pack()
    listboxFrame.pack(side=LEFT)
    listbox = tk.Listbox(listboxFrame, width=35)
    listbox.pack(padx=30, pady=5)
    def exportToCsv():
        if listbox.size() > 0:
            now_now = datetime.now()
            current_time_now = now_now.strftime("%Y-%m-%d - %H-%M-%S")
            with open(f'./exports/{current_time_now}.csv', 'w') as file:
                for i in range(listbox.size()):
                    file.write(listbox.get(i) + '\n')
                listbox.config(highlightthickness=1, highlightbackground='blue', highlightcolor='blue')
                file.close()
            print(f'File has been exported to ./exports/{current_time_now}')
    tk.Button(listboxFrame, text="Export to csv", command=exportToCsv).pack()
    
    
    # total number scan
    totalNumberScanFrame = tk.Frame(statsFrame, padx=80, pady=10)
    tk.Label(totalNumberScanFrame, text="Total people scanned", font=("Roboto", 15, "normal"), pady=8).pack(expand=True)
    totalPeopleScannedLbl = tk.Label(totalNumberScanFrame, text=str(totalPeopleScanned), font=("Roboto", 50, "normal"), pady=20)
    totalPeopleScannedLbl.pack(expand=True)
    totalNumberScanFrame.pack(side=RIGHT)
    
    # credits
    creditLbl = tk.Label(app, text="Copyright © RMIT University Vietnam. All rights reserved.", padx=20, pady=10, cursor='hand2')
    def creditClickHandler(event):
        smallWindow = tk.Toplevel(app)
        smallWindow.geometry('500x100+200+200')
        tk.Label(smallWindow, text="Author: Hoang Nguyen<hoangdesu@gmail.com>\nhoangdesu.com\nfacebook.com/Hoangdayo\ngithub.com/hoangdesu").pack()

    creditLbl.bind('<Button-1>', creditClickHandler)
    creditLbl.pack()
    
    # program main loop
    while True:
        now = datetime.now()
        current_time = now.strftime("%Y/%m/%d - %H:%M:%S")
        dateTimeLbl.config(text=current_time)
        
        # read and process a video frame then decode
        frame = vs.read()
        frame = imutils.resize(frame, width=450)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.flip(frame, 1)
        barcodes = pyzbar.decode(frame)
        
        # create an Tk image object from frame (numpy's ndarray)
        liveCam_img = ImageTk.PhotoImage(Image.fromarray(frame))
        liveCamLbl.config(image=liveCam_img)
        
        # if len(barcodes) > 0:
        for barcode in barcodes:
            # draw a rect around barcode found
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            
            # get request, verify QR
            response = requests.get(f'{API_URL}/{barcodeData}')
            data = response.json()
            valid = data['valid']
            name = data['name']
            role = data['type']
            id = data['id']
            print(data)
            
            # process image for captured frame
            qrText = f"{current_time}:  {valid}"
            cv2.putText(frame, qrText, (x - 10, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            captured_frame = ImageTk.PhotoImage(Image.fromarray(frame))
            
            # update new data to UI
            capturedCamLbl.config(image=captured_frame)
            nameLabel.config(text=name)
            idLabel.config(text=id)
            roleLabel.config(text=role)
            
            totalPeopleScanned += 1
            totalPeopleScannedLbl.config(text=totalPeopleScanned)
            
            # need to change this to boolean!
            if valid == 'Yes':
                scanStatusLabel.config(bg="#5ccf23", fg="#fff", text="Approved ✅")
                os.system("afplay " + approved)
            else:
                scanStatusLabel.config(bg="#cf0e1b", text="Rejected ❌")
                os.system("afplay " + rejected)
                
            
            listbox.insert(0, f'{current_time}: {name}, {id}, {role}')
            qrFound = True
            # start_time = time.time()
            
            
                
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        
        # delay 1s to avoid sending multiple requests
        if qrFound:
            time.sleep(1)
            qrFound = False
            
        # reset the system to idle mode if time exceeds a certain amount
        # print(time.time() - start_time )
        # if time.time() - start_time > 3:
        #     scanStatusLabel.config(bg="#fff", fg="#000", text="Scan your QR...")
        #     capturedCamLbl.config(image=scanQR_img)
        #     nameLabel.config(text="")
        #     idLabel.config(text="")
        #     roleLabel.config(text="")
        #     start_time = time.time()
            
            
            
        app.update()
        
        
        
    print("cleaning up...")
        # csv.close()
    cv2.destroyAllWindows()
    vs.stop()
    
    


if __name__ == '__main__':    
    main()