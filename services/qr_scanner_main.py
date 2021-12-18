from imutils.video import VideoStream
from pyzbar import pyzbar
import cv2
import imutils
import time
import requests
from datetime import datetime
import os
import tkinter as tk
from PIL import Image, ImageTk

API_URL = 'http://52.76.27.252:3000/registrations/verify' 

vs = VideoStream(src=0).start()
time.sleep(2.0)
counter = 1
found = False
approved = './approved.wav'
rejected = './rejected.wav'

app = tk.Tk()
app.geometry("900x800")
app.title("RMIT QR code scanner")

h1 = tk.Label(app, text="RMIT QR code scanner")
h1.pack()

f2 = tk.Label(app, text="")
f2.pack()

f1 = tk.Label(app, text="")
f1.pack()

h3 = tk.Label(app, text="Last 5 scans:")
h3.pack()

h2 = tk.Label(app, text="")
h2.pack()

qrList = []


while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=400)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    frame = cv2.flip(frame, 1)
    barcodes = pyzbar.decode(frame)
    
    img2 = ImageTk.PhotoImage(Image.fromarray(frame))
    f2.config(image=img2)
    

    for barcode in barcodes:
        (x, y, w, h) = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
        
        response = requests.get(f'{API_URL}/{barcodeData}')
        data = response.json()
        valid = data['valid']
        name = data['name']
        type = data['type']
        id = data['id']
        print(data)
        

        now = datetime.now()

        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        print("Current Time =", current_time)
        
        text2 = f"TIME: {current_time} - DATA: {barcodeData} - VALID QR?: {valid}"
        text = f"{data['valid']}"
        print(text)
        cv2.putText(frame, text, (x - 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
        
        
        
        h1.configure(text=text2)
        h1.pack()
        msg = f'Name: {name} - id: {id}\n{type} - '
        if valid == 'Yes':
            msg += 'Welcome!'
            os.system("afplay " + approved)
        else:
            msg += 'Reject'
            os.system("afplay " + rejected)
            
        if len(qrList) > 5:
            qrList[0].forget()
            qrList.pop(0)
        qrList.append(tk.Label(app, text=msg))
        
        for qr in qrList:
            qr.pack()
        # h2.pack()
        
        # print(type(frame))
        img = ImageTk.PhotoImage(Image.fromarray(frame))
        f1.config(image=img)
        
        
        
        
        
        # cv2.imwrite(f"./frames/{current_time}.jpg", frame)
        found = True
    # frame = cv2.flip(frame, 1)

    # cv2.imshow("Barcode Scanner", frame)
    if found:
        time.sleep(1)
        
        found = False
        
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
        
    
    app.update()
        
        
    
        
        
# app.after(0, qr)
# app.mainloop()
    
print("cleaning up...")
    # csv.close()
cv2.destroyAllWindows()
vs.stop()
