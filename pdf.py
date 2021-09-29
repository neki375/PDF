import os
import sqlite3
from tkinter import *
from datetime import datetime
from PIL import ImageTk, Image
from pdfrw import PdfWriter, PdfReader
from tkinter import ttk, filedialog, messagebox


path = os.path.dirname(os.path.abspath(__file__))
iconPath = os.path.join(path, "pdf.png")


window = Tk()
# background color
window["bg"] = "#2E2E2E"
# name
window.title("PDF Downloader")
# file icon
# window.iconphoto(False, PhotoImage(file=iconPath))
# window size
window.geometry("650x500")
window.resizable(False, False)
window.columnconfigure(1, weight=100)


# get element from Listbox
def getElement(event):
    try:
        selection = event.widget.curselection()
        index = selection[0]
        value = event.widget.get(index)
        result_name.set(value)
    except Exception as e:
        pass


# open file dialog
def openFile():
    f_file_link.delete(0, END)
    window.filename = filedialog.askopenfilename(
        initialdir='/', 
        title='Files', 
        filetypes=[
            ('pdf file', '.pdf'), 
            ('image files', ('.png', '.jpg'))
        ]
    )

    if (len(window.filename) > 0):
        f_file_link["state"] = "normal"
        f_file_link.insert(0, window.filename)
        f_file_link.grid()
    

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
    if (len(f_file_link.get()) > 0 and len(f_name.get()) > 0):
        try:
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
            messagebox.showinfo(title="Message by db", message=f"{f_file_link.get()} insert to DB")
            f_name.delete(0, END)
            f_file_link.delete(0, END)
            f_file_link["state"] = "disable"
            conn.close()
    else:
        messagebox.showinfo(title="Message by db", message="Fill in all the fields")


# show files
def showFiles():
    global list_names
    global list_label
    global list_id_label
    global list_id
    global f_id
    global f_id_label
    # ids list
    list_id = Listbox(window, bg="#2E2E2E")
    list_id.config(width=4)
    # filenames list
    list_names = Listbox(window, bg="#2E2E2E", fg="white")
    list_names.config(width=50)
    try:
        conn = sqlite3.connect(f'{path}/files.db')
        cur = conn.cursor()
        cur.execute("SELECT *, oid FROM files")
        files = cur.fetchall()

        if(len(files) == 0):
            messagebox.showinfo(title="INFO", message="NO RECORDS")
            return

        # label for id
        f_id_label = Label(window, text="Write ID", bg="#2E2E2E", fg="white")
        f_id_label.grid(row=3, column=1, padx=(0, 170))
        # input for id
        f_id = Entry(window, width=6)
        f_id.grid(row=3, column=1, sticky=W)
        # rows name from db
        list_label = Label(window, text="FILENAME", bg="#7E7E7E", fg="white")
        list_label.config(width=50)
        list_label.grid(row=4, column=1)
        # rows id from db
        list_id_label = Label(window, text="ID", bg="#7E7E7E", fg="white")
        list_id_label.config(width=4)
        list_id_label.grid(row=4, column=0, sticky=E)

        close_button['state'] = 'normal'
        info_button['state'] = 'disable'
        download_button['state'] = 'normal'
        delete_button['state'] = 'normal'

        for file in files:
            list_names.insert(END, file[1])
            list_names.grid(row=5, column=1, sticky=E)
            list_id.insert(END, file[3])
            list_id.grid(row=5, column=0, sticky=E)

        list_id.configure(state=DISABLED)

        # get value from LB
        list_names.bind('<<ListboxSelect>>', getElement)

    except Exception as e:
        print(e)
    finally:
        conn.close()

def delete():
    oid = f_id.get()
    if not oid:
        messagebox.showinfo(title="INFO", message=f"Id not filled")
        # return
    else:
        try:
            conn = sqlite3.connect(f'{path}/files.db')
            cur = conn.cursor()
            cur.execute("DELETE FROM files WHERE oid=%s"%(oid))
            conn.commit()

        except Exception as e:
            print(e)
        finally:
            conn.close()
            messagebox.showinfo(title="INFO", message=f"Record with id={oid} deleted")
            closeFiles()


def closeFiles():
    list_names.destroy()
    list_id.destroy()
    f_id.destroy()
    list_label["text"] = ""
    list_label["bg"] = "#2E2E2E"
    list_id_label["text"] = ""
    list_id_label["bg"] = "#2E2E2E"
    f_id_label["text"] = ""
    f_id_label["bg"] = "#2E2E2E"
    info_button['state'] = 'normal'
    close_button['state'] = 'disable'
    download_button['state'] = 'disable'
    delete_button['state'] = 'disable'


# download file
def download():
    file_name = result_name.get().split("/")[-1].split(".")[0]
    window.filename = filedialog.asksaveasfile(
        initialfile=file_name, 
        title='Files', 
        filetypes=[
            ('pdf file', '.pdf'), 
            ('image files', ('.png', '.jpg'))
        ]
    )

    if window.filename:
        save_path = window.filename.name
        file_format = window.filename.name.split("/")[-1].split(".")[-1]
        if file_format == "pdf":
            # for pdf
            writer = PdfWriter()
            reader = PdfReader(result_name.get())
            writer.addpage(reader.pages[0])
            writer.write(save_path)
        elif file_format == "png":
            # for png
            img = Image.open(result_name.get())
            img.save(save_path)

        messagebox.showinfo(title="INFO", message=f"Download is complete")
        closeFiles()
  

# inputs
f_name = Entry(window, width=30)
f_name.grid(row=0, column=1, padx=20, pady=(50, 0))
f_file_link = Entry(window, width=30, state="disable")
f_file_link.grid(row=1, column=1, padx=20)

# labels
root_label = Label(window, text="Fill in inputs", font=("Helvetica", 14), bg="#2E2E2E", fg="white")
root_label.grid(row=0, column=1, padx=40)
f_name_label = Label(window, text="Name", bg="#2E2E2E", fg="white")
f_name_label.grid(row=0, column=0, padx=40, pady=(50, 0))


#button for choose files
button = Button(window, bg="#FFFFFF", border=0, text="Choose file", command=openFile)
button.grid(row=1, column=0, padx=40)

# button for insert
db_button = Button(window, bg="#FFFFFF", border=0, text="Insert", command=lambda: insertFile())
db_button.grid(row=1, column=2)

# button for show files
info_button = Button(window, bg="#FFFFFF", border=0, text="Show files", command=lambda: showFiles())
info_button.grid(row=3, column=0, padx=20)

# button for close
close_button = Button(window, bg="#FFFFFF", border=0, text="Close files", command=lambda: closeFiles(), state="disable")
close_button.grid(row=3, column=2, padx=20)

# button for download
download_button = Button(window, bg="#FFFFFF", border=0, text="Download", command=lambda: download(), state="disable")
download_button.grid(row=3, column=1, padx=20, pady=20, sticky=E)

# button for delete by id
delete_button = Button(window, bg="#FFFFFF", border=0, text="Delete", command=lambda: delete(), state="disable")
delete_button.grid(row=3, column=1)

# name from lb
result_name = StringVar()

# create table if not exists
connectToDB()


if __name__ == "__main__":
    window.mainloop()
 