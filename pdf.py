from tkinter import *
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
# from PIL import ImageTk, Image
import sqlite3

window = Tk()
# background color
window["bg"] = "#fafafa"
# name
window.title("PDF Downloader")
# size
window.geometry("700x500")
import os

path = os.path.dirname(os.path.abspath(__file__))


def getElement(event):
  selection = event.widget.curselection()
  index = selection[0]
  value = event.widget.get(index)
  
  result.set(value)
  print(index,' -> ',value)

# open file dialog
def openFile():
    f_file_link.delete(0, END)
    window.filename = filedialog.askopenfilename(initialdir='/', title='choose file')
    if (len(window.filename) > 0):
        f_file_link.insert(0, window.filename)
        f_file_link.grid()
        # db_button.grid()
    
# connect to DB
def connectToDB():
    try:
        conn = sqlite3.connect(f'{path}/files.db')
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS files(
            name text,
            file_link text,
            insert_date timestamptz
        )""")
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        conn.close()

# insert file to DB
def insertFile():
    try:
        connectToDB()
        conn = sqlite3.connect(f'{path}/files.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO files VALUES(:name, :file_link, :insert_date)",
            {
                "name":  f_name.get(),
                "file_link": f_file_link.get(),
                "insert_date": datetime.now() 
            }
        )
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        #message about inserting
        if (len(f_file_link.get()) > 0):
            messagebox.showinfo(title="Message by db", message=f"{f_file_link.get()} insert to DB")
        else:
            if(len(f_file_link.get()) == 0 or len(f_name.get()) == 0):
                messagebox.showinfo(title="Message by db", message=f"EMPTY ROWS : {f_name_label['text']}, {button['text']}")

        f_name.delete(0, END)
        f_file_link.delete(0, END)
        conn.close()

# show files
def showFiles():
    # close_button['state'] = 'normal'
    global list_box
    list_box = Listbox(window)
    try:
        connectToDB()
        conn = sqlite3.connect(f'{path}/files.db')
        cur = conn.cursor()
        cur.execute("SELECT *, oid FROM files")
        files = cur.fetchall()
        # list_box = Listbox(window, listvariable=files)
        # list_box.grid(row=4, column=1, padx=40)
        if(len(files) == 0):
            messagebox.showinfo(title="INFO", message="NO RECORDS")
            return
        close_button['state'] = 'normal'
        info_button['state'] = 'disable'
        for file in files:
            list_box.insert(END, file[1])
            list_box.grid(row=4, column=1, padx=40, pady=40)
        # list_box.select_set(0)
        for i in list_box.curselection():
            print(list_box.get(i))
    except Exception as e:
        print(e)
    finally:
        # info_button['state'] = 'disable'
        conn.close()


def closeFiles():
    list_box.destroy()
    info_button['state'] = 'normal'
    close_button['state'] = 'disable'


# button for insert
db_button = Button(window, text="Add", command=lambda: insertFile())
db_button.grid(row=2, column=1, padx=20)


# inputs
f_name = Entry(window, width=30)
f_name.grid(row=0, column=1, padx=20)
f_file_link = Entry(window, width=30)
f_file_link.grid(row=1, column=1, padx=20)

# labels
f_name_label = Label(window, text="Name")
f_name_label.grid(row=0, column=0, padx=40)
button = Button(window, text="Choose file", command=openFile)
button.grid(row=1, column=0, padx=40)

# button for show files
info_button = Button(window, text="Show files", command=lambda: showFiles())
info_button.grid(row=3, column=0, padx=20)
close_button = Button(window, text="Close files", command=lambda: closeFiles(), state="disable")
close_button.grid(row=3, column=2, padx=20)

# result = StringVar()

# print(result)

# list_box
# list_box = tk.Listbox(root, listvariable=var2)
# list_box.grid(row = 0, column = 1)
# list_box.bind('<<ListboxSelect>>', getElement) #Select click

# List of files

# list_box = Listbox(window)

# window.bind("<Return>",exit_gui)

window.mainloop()
 