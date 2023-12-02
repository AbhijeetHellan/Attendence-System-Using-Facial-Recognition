import face_recognition
import numpy as np
from datetime import datetime
import os
import cv2
import keyboard
import pyautogui
import customtkinter as cstk
import tkinter as tk
from tkinter import filedialog, PhotoImage

path = "ImagesAttendance"
marked_students = r"marked_students"
attend_csv_path = r"Attendance.csv"

# GUI Initialization
cstk.set_appearance_mode("dark")
cstk.set_default_color_theme("blue")
root = cstk.CTk()
root.geometry("1920x1080")
root.title("Attendance System")

# Global variables
images = []  # img to numpy array
global image_names
global filesz
global encodeListKnown
encodeListKnown = []
filesz = tuple()
image_names = []  # stores people's names
mylist = os.listdir(path)  # lists all the images in dir
savedImg = []
global attend_dict
attend_dict = {}
print(mylist)
global del_names, del_ind
del_names = []
del_ind = []


# accessing images in folder
def access():
    global images, image_names
    for cl in mylist:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        image_names.append(os.path.splitext(cl)[0])  # root path of name [0] ext path [1]
    print(image_names)


# Train the face recognition system
def train_faces():
    global encodeListKnown
    encodeListKnown.clear()  # Clear existing face encodings
    access()  # Get the names of images

    for image in images:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(image)[0]
        encodeListKnown.append(encode)

    tk.messagebox.showinfo("Success", "Images trained successfully!")


# Create the needed variables
def clean():
    for f in os.listdir(marked_students):
        os.remove(fr"{marked_students}\{f}")


# Save the captured image
def save_img(imagesz, nami):
    savedImg = os.listdir(marked_students)
    if nami not in savedImg:
        cv2.imwrite(rf"{marked_students}+\{nami}.jpg", imagesz)


# Mark attendance into the CSV file for a new name
def markAttendance(name, new_id=None):
    print(name, "attended")

    with open("Attendance.csv", 'r+') as f:
        myDataList = f.readlines()  # reads every line in the attendance list

        for line in myDataList:
            line = line.strip()
            entry = line.split(',')
            attend_dict[entry[0]] = entry[1:]

        if name not in attend_dict.keys():
            now = datetime.now()
            dtString = now.strftime("%I:%M %p")  # I - 12 hr format(), minute, pm or am
            if new_id is None:
                new_id = pyautogui.prompt(f"Renter ID for {name}", title="Enter Details")
            attend_dict[name] = [new_id, dtString, "Present"]  # writes ID, entry time, and status
            with open("Attendance.csv", 'a') as reg_file:
                reg_file.write(f"{name},{new_id},,\n")  # Add name and ID to CSV during registration

        elif name in attend_dict.keys():
            now = datetime.now()
            dtString = now.strftime("%I:%M %p")  # I - 12 hr format(), minute, pm or am
            attend_dict[name][1] = dtString  # updates entry time
            attend_dict[name][2] = "Present"  # updates status


# Mark attendance
def attendance():
    ff = open("Attendance.csv", 'w+')
    try:
        ff.writelines("NAME,ID,ENTRY,STATUS")
        ff.writelines("\n")
        del attend_dict['NAME']
        del attend_dict['UNKNOWN']
    except KeyError:
        print()

    for i in attend_dict.keys():
        if len(attend_dict[i]) >= 3:  # Check if there are at least three elements in the list
            ss = ""  # Reset the ss variable for each iteration
            ss += i
            new_id = attend_dict[i][0]
            entryy = attend_dict[i][1]
            status = attend_dict[i][2]

            ss += "," + new_id + "," + entryy + "," + status
            ff.writelines(ss)
            ff.writelines("\n")

    ff.close()
    os.startfile(r"Attendance.csv")


# Webcam scan function
def webcam_scan():
    if not encodeListKnown:
        tk.messagebox.showinfo("Warning", "Train images first before marking attendance.")
        return
    cap = cv2.VideoCapture(0)  # starts video capture through webcam

    while True:
        success, img = cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        cv2.putText(img, f'Number of faces detected: {len(facesCurFrame)}', (100, 450), cv2.FONT_HERSHEY_COMPLEX, 1,
                    (255, 0, 255), 2)

        for encodeFace, FaceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=0.5)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = image_names[matchIndex].upper()
                y1, x2, y2, x1 = FaceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

                cv2.rectangle(img, (x1 - 20, y1 - 20), (x2 + 20, y2 + 20), (255, 255, 0), 2)
                cv2.rectangle(img, (x1 - 20, y2 - 15), (x2 + 20, y2 + 20), (255, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 - 14, y2 + 14), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 2)
                save_img(img, name)
                markAttendance(name)

            else:
                name = "UNKNOWN"
                y1, x2, y2, x1 = FaceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

                cv2.rectangle(img, (x1 - 20, y1 - 20), (x2 + 20, y2 + 20), (255, 255, 0), 2)
                cv2.rectangle(img, (x1 - 20, y2 - 15), (x2 + 20, y2 + 20), (255, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 - 14, y2 + 14), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 2)

        cv2.imshow('webcam', img)
        cv2.waitKey(1)

        if keyboard.is_pressed('q'):
            print("i quit!!")
            cv2.destroyWindow('webcam')
            break


# Save the captured image
def save_img(imagesz, nami):
    savedImg = os.listdir(marked_students)
    if nami not in savedImg:
        cv2.imwrite(rf"{marked_students}+\{nami}.jpg", imagesz)


# Mark attendance into the CSV file for a new name
def markAttendance(name, new_id=None):
    print(name, "attended")

    with open("Attendance.csv", 'r+') as f:
        myDataList = f.readlines()  # reads every line in the attendance list

        for line in myDataList:
            line = line.strip()
            entry = line.split(',')
            attend_dict[entry[0]] = entry[1:]

        if name not in attend_dict.keys():
            now = datetime.now()
            dtString = now.strftime("%I:%M %p")  # I - 12 hr format(), minute, pm or am
            if new_id is None:
                new_id = pyautogui.prompt(f"Renter ID for {name}", title="Enter Details")
            attend_dict[name] = [new_id, dtString, "Present"]  # writes ID, entry time, and status
            with open("Attendance.csv", 'a') as reg_file:
                reg_file.write(f"{name},{new_id},,\n")  # Add name and ID to CSV during registration

        elif name in attend_dict.keys():
            now = datetime.now()
            dtString = now.strftime("%I:%M %p")  # I - 12 hr format(), minute, pm or am
            attend_dict[name][1] = dtString  # updates entry time
            attend_dict[name][2] = "Present"  # updates status


# Add a new student to the database
def add_to_database():
    new_name = pyautogui.prompt('Enter Name', title="Enter Details")
    new_id = pyautogui.prompt('Enter ID', title="Enter Details")

    if new_name in del_names:
        loc = del_ind[del_names.index(new_name)]
        image_names[loc] = new_name

        new_filename = f"{new_name}.jpg"
        tk.messagebox.showinfo("Alert", "Look at the Camera in 3 sec!")
        result, new_img = cv2.VideoCapture(0).read()
        cv2.imwrite(fr"ImagesAttendance\{new_filename}", new_img)
        cv2.imshow("New Image", new_img)
        cv2.waitKey(0)
        cv2.destroyWindow('New Image')

    else:
        new_filename = f"{new_name}.jpg"
        tk.messagebox.showinfo("Alert", "Look at the Camera in 3 sec!")
        result, new_img = cv2.VideoCapture(0).read()
        cv2.imwrite(fr"ImagesAttendance\{new_filename}", new_img)
        cv2.imshow("New Image", new_img)
        cv2.waitKey(0)
        cv2.destroyWindow('New Image')

        images.append(cv2.imread(fr'ImagesAttendance\{new_filename}'))
        image_names.append(new_name)
        print(new_name)
        encodeListKnown.append(face_recognition.face_encodings(images[-1])[0])

        # Add the new_id to the ID column in the CSV file
        markAttendance(new_name, new_id)


# Delete a student from the database
def delete_from_database():
    L1 = image_names
    L2 = []
    li2 = os.listdir(r"ImagesAttendance")
    filesz = filedialog.askopenfilenames(title="Select Student",
                                         filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*")))
    print("Selected files:", filesz)
    for xx in filesz:
        os.remove(xx)
        xx = os.path.splitext(xx[xx.find('nce') + 4:])[0]
        del_ind.append(L1.index(xx))
        del_names.append(image_names[L1.index(xx)])
        image_names[L1.index(xx)] = "unknown"
        print("removed : ", xx)

    set_dif = []
    for x in li2:
        L2.append(os.path.splitext(x)[0])
    set_dif = list(set(L1).symmetric_difference(set(L2)))
    set_dif = list(filter(lambda t: t != "unknown", set_dif))
    removed_names = ""
    for j in set_dif:
        removed_names += j + " , "
    tk.messagebox.showinfo("showinfo", f"Deregistered = {len(set_dif)}\n{removed_names}\nClose the Window")


# Open the deregistration window
def deregister():
    root1 = tk.Toplevel()
    root1.geometry("550x720")
    root1.title("Delete")
    image2 = PhotoImage(file=r"C:\Games\Project\Face_Recognition-main\icons and background\remove.png")
    bg1label = tk.Label(root1, image=image2, width=512, height=600)
    bg1label.pack()
    button9 = tk.Button(root1, text="Select Student", command=delete_from_database, width=512, pady=5)
    button9.pack()
    root1.mainloop()


# Open the marked students folder
def show():
    os.startfile(r"marked_students")


# Open the database folder
def database():
    os.startfile(r"ImagesAttendance")


# GUI Initialization
imag = tk.PhotoImage(
    file=r"C:\Games\Project\Face_Recognition-main\icons and background\wp8047222-blue-tech-wallpapers.png")

frame = cstk.CTkFrame(master=root)
frame.pack(padx=60, pady=20, fill="both", expand=True)

label = cstk.CTkLabel(master=frame, text="ATTENDANCE SYSTEM", font=("Roboto", 40, "bold"), compound="left")
label.pack(pady=12, padx=10)

bglabel = cstk.CTkLabel(master=frame, image=imag, text="", width=1080, height=1080)
bglabel.pack()

button1 = cstk.CTkButton(master=frame, text="Mark Attendance", command=webcam_scan, height=120, width=350,
                         font=("Times New Roman", 38, "bold"))
button1.place(relx=0.3, rely=0.3, anchor="e")

button2 = cstk.CTkButton(master=frame, text="Train", command=train_faces, height=120, width=350,
                         font=("Times New Roman", 38, "bold"))
button2.place(relx=0.7, rely=0.55, anchor="w")

button3 = cstk.CTkButton(master=frame, text="Registered Students", command=database, height=120, width=350,
                         font=("Times New Roman", 38, "bold"))
button3.place(relx=0.7, rely=0.3, anchor="w")

button4 = cstk.CTkButton(master=frame, text="Register", command=add_to_database, height=120, width=350,
                         font=("Times New Roman", 38, "bold"))
button4.place(relx=0.3, rely=0.82, anchor="e")

button5 = cstk.CTkButton(master=frame, text="Deregister", command=deregister, height=120, width=350,
                         font=("Times New Roman", 38, "bold"))
button5.place(relx=0.7, rely=0.82, anchor="w")

button6 = cstk.CTkButton(master=frame, text="Open Attendance", command=attendance, height=120, width=350,
                         font=("Times New Roman", 38, "bold"))
button6.place(relx=0.3, rely=0.55, anchor="e")

root.mainloop()
