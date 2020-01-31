'''Name: Naveen Sokke Nagarajappa
   ID:   1001768613              '''

""" References used
https://www.youtube.com/watch?v=VMP1oQOxfM0
https://www.youtube.com/watch?v=JrWHyqonGj8
https://www.youtube.com/watch?v=_FVvlJDQTxk&list=PLhTjy8cBISErYuLZUvVOYsR1giva2payF&index=4
https://www.youtube.com/watch?v=Iu8_IpztiOU
http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html
https://docs.python.org/2/library/socket.html
https://stackoverflow.com/questions/667640/how-to-tell-if-a-connection-is-dead-in-python
https://stackoverflow.com/questions/3998742/how-can-i-dynamically-change-the-color-of-a-button-in-tkinter
https://effbot.org/tkinterbook/button.htm#when-to-use
https://codereview.stackexchange.com/questions/214788/socket-chat-room-made-with-tkinter-python
https://www.reddit.com/r/learnpython/comments/6z2x97/socket_python_3_file_transfer_over_tcp/
https://github.com/schedutron/CPAP/blob/master/Chap5/chat_serv.py
https://github.com/schedutron/CPAP/blob/master/Chap5/chat_clnt_GUI.py
http://www.effbot.org/tkinterbook/pack.htm#patterns
"""

"""Script for file transfer client with Tkinter GUI."""
import socket
import threading
import tkinter as tk
import os
import time
import sys
import random

# Change this path if you have a different directory
PATH = "D:/Study/1st Sem/Distributed Systems/Lab3/Client3"


def monitor(CLIENT):
    """Monitors shared folder for any new files. if new files found send it to Server"""
    print("Monitoring started")
    before = dict([(f, None) for f in os.listdir(PATH)])
    while True:
        if disconnected_flag.get() == "Y":
            close_all(CLIENT)
        time.sleep(3)
        after = dict([(f, None) for f in os.listdir(PATH)])
        added = [f for f in after if not f in before]
        removed = [f for f in before if not f in after]

        if received_file.get() in added:
            print(received_file.get())
            added.remove(received_file.get())
            received_file.set("")
        if received_file.get() in removed:
            print(received_file.get())
            removed.remove(received_file.get())
            received_file.set("")
        for file in added:
            print("Added", end=': ')
            print(added)
            f_send = PATH + "/" + str(file)
            CLIENT.send(("ADDED" + str(file)).encode('utf8'))
            print(f_send)
            f = open(f_send, "rb")
            data = f.read(BUFSIZ)
            while data:
                print(data)
                CLIENT.send(data)
                data = f.read(BUFSIZ)
            print(data)
            f.close()

        for file in removed:
            print("Removed", end=': ')
            print(removed)
            operation.set("REMOVED" + str(file))
            CLIENT.send(("REMOVED" + str(file)).encode('utf8'))
            print(file)
            # removed.remove(file)

        before = after


def receive(CLIENT):
    """Waiting for server to send any files and downloads file when it is available"""
    print("Receiving messages started")
    while True:
        if disconnected_flag.get() == "Y":
            close_all(CLIENT)
        print("Waiting for message")
        data = CLIENT.recv(BUFSIZ).decode('utf8')
        print("Received data" + data)
        print(operation.get())
        print("[:7]" + operation.get()[:7])

        if operation.get()[:7] == "REMOVED":
            agree, disagree = 0, 0
            file = operation.get()[7:]
            print("Received data for agreement" + data)
            while (data[:5] == "AGREE" or data[:8] == "DISAGREE"):
                if data[:5] == "AGREE":
                    agree += 1
                else:
                    disagree += 1
                data = CLIENT.recv(BUFSIZ).decode('utf8')
            print(data[13:])
            print("agrees : " + str(agree))
            num_peers = int(data[13:]) - 1
            print("agrees : " + str(num_peers))
            if agree == num_peers:
                print("all agreed to remove file")
                msg.insert(tk.END, "All " + str(num_peers) + " agreed to delete the file, confirming the delete\n")
                CLIENT.send("CONFIRM".encode())
            else:
                print(str(agree) + "clients agreed to remove file")
                CLIENT.send("NOT-CONFIRM".encode())
                f = open(PATH + "/" + file, 'wb')
                print("restoring file " + file)
                msg.insert(tk.END, "Only " + str(num_peers) + " agreed to delete the file, so aborting the delete\n")
                while True:
                    # get file bytes
                    data = CLIENT.recv(BUFSIZ)
                    # write bytes on file
                    print(data)
                    print(len(data))
                    f.write(data)
                    if (len(data) < BUFSIZ):
                        break
                f.close()
                msg.insert(tk.END, "Restored the deleted file" + received_file.get() + "\n")
            operation.set("")

        if data[:5] == "ADDED":
            received_file.set(data[5:])
            msg.insert(tk.END, "new file " + data[5:] + " available and getting downloaded to" + PATH + "\n")
            f = open(PATH + "/" + data[5:], 'wb')
            while data:
                # get file bytes
                data = CLIENT.recv(BUFSIZ)
                # write bytes on file
                f.write(data)
                if (len(data) < BUFSIZ):
                    break
            f.close()

        elif data[:7] == "REMOVED":
            received_file.set(data[7:])
            f_remv = PATH + "/" + data[7:]
            msg.insert(tk.END, "file " + data[7:] + " has been removed  need to give consent " + PATH + "\n")

            time.sleep(3)
            if random.random() > 0.75:
                print("sending vote not to remove file")
                CLIENT.send("DISAGREE".encode())
                msg.insert(tk.END, "Voted 'NO' to delete the file\n")
            else:
                print("sending vote remove file")
                CLIENT.send("AGREE".encode())
                msg.insert(tk.END, "Voted 'YES' to delete the file\n")

        elif data[:7] == "CONFIRM":
            print("all agreed to remove file, delete the file ")
            msg.insert(tk.END, "All agreed to delete the file, file is deleted\n")
            if os.path.exists(f_remv):
                os.remove(f_remv)
            else:
                print("The file does not exist")
        elif data[:11] == "NOT-CONFIRM":
            msg.insert(tk.END, "Everyone did not agree to delete the file, file delete aborted\n")
            print("did not agree to remove file, de ")


def connect():
    """Checking user name and connecting to the server"""
    print("connecting to server")
    CLIENT = socket.socket()

    try:
        CLIENT.connect(ADDR)
        connected = "YES"
    except socket.error:
        msg.insert(tk.END, "connection error : make sure server is running, IP and port# are correct\n")
        connected = "NOT"

    user_name = str(entry_username.get())

    if connected == "YES" and user_name and not user_name.isspace():
        print("sending username")
        CLIENT.send(user_name.encode())
        connected = CLIENT.recv(BUFSIZ).decode()
    else:
        connected = "NO"
        print("User name is empty")

    if connected == "Y":
        msg.insert(tk.END, "You are connected as " + user_name + "\n")
        msg.insert(tk.END, "Your shared folder is \n" + PATH + "\n")

        connect_button.configure(text="Disconnect", fg="Blue", command=disconnect)

        if disconnected_flag.get() == "N":
            disconnected_flag.set("1")

        threading.Thread(target=monitor, args=(CLIENT,)).start()

        threading.Thread(target=receive, args=(CLIENT,)).start()

    elif connected == "NO":
        msg.insert(tk.END, "User name cannot be empty\n")

    elif connected == "N":
        msg.insert(tk.END, "user name '" + user_name + "'already exists please try another name\n")


def disconnect():
    """handling disconnection to server."""
    print("Disconnected from server")
    if disconnected_flag.get() == "1":
        disconnected_flag.set("Y")

    CLIENT.close()

    # Button
    connect_button.configure(text="Connect", fg="Blue", command=connect)

    msg.insert(tk.END, "You are not connected to server\n")


def close_all(CLIENT):
    """This function is to be called when the window is closed."""
    CLIENT.send("EXIT_CONNECTION".encode('utf8'))
    disconnected_flag.set("N")
    sys.exit(0)


# ----Now comes the sockets part----
HOST = "127.0.0.1"
PORT = 7777
BUFSIZ = 1024
ADDR = (HOST, PORT)
CLIENT = socket.socket()

# below is the code for GUI.
window = tk.Tk()
window.title("Client")

frame = tk.Frame(window)

received_file = tk.StringVar()
disconnected_flag = tk.StringVar()
operation = tk.StringVar()

disconnected_flag.set("N")

prompt = tk.Label(text="Enter a user Name")
prompt.pack(side=tk.TOP)

entry_username = tk.Entry(window)
entry_username.pack(side=tk.TOP)

connect_button = tk.Button(window)
connect_button.pack()

scrollbar = tk.Scrollbar(frame)  # To navigate through past messages.
# Following will contain the messages.
msg = tk.Listbox(frame, height=50, width=100, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
msg.pack(side=tk.LEFT, fill=tk.BOTH)
msg.pack()
frame.pack()

msg.insert(tk.END, "Client started...\n")

threading.Thread(target=disconnect).start()

# Starts GUI execution.
tk.mainloop()
import socket
import threading
import tkinter as tk
import os
import time
import sys


""" References used
https://www.youtube.com/watch?v=VMP1oQOxfM0
https://www.youtube.com/watch?v=JrWHyqonGj8
https://www.youtube.com/watch?v=_FVvlJDQTxk&list=PLhTjy8cBISErYuLZUvVOYsR1giva2payF&index=4
https://www.youtube.com/watch?v=Iu8_IpztiOU
http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html
https://docs.python.org/2/library/socket.html
https://stackoverflow.com/questions/667640/how-to-tell-if-a-connection-is-dead-in-python
https://stackoverflow.com/questions/3998742/how-can-i-dynamically-change-the-color-of-a-button-in-tkinter
https://effbot.org/tkinterbook/button.htm#when-to-use
https://codereview.stackexchange.com/questions/214788/socket-chat-room-made-with-tkinter-python
https://www.reddit.com/r/learnpython/comments/6z2x97/socket_python_3_file_transfer_over_tcp/
https://github.com/schedutron/CPAP/blob/master/Chap5/chat_serv.py
https://github.com/schedutron/CPAP/blob/master/Chap5/chat_clnt_GUI.py
http://www.effbot.org/tkinterbook/pack.htm#patterns
http://effbot.org/tkinterbook/entry.htm#Tkinter.Entry.delete-method
"""

"""Script for file transfer client with Tkinter GUI."""

# Change this FILE if you have a different file name
FILE = "D:\\Study\\1st Sem\\Distributed Systems\\Lab2\\Client1\\Text.txt"


def monitor(CLIENT):
    """Monitors shared text file for any modifications. if the file is modified files found send it to Server"""
    modtime_sleep = os.stat(FILE).st_mtime_ns
    received_file.set(modtime_sleep)
    while True:
        try:
            if disconnected_flag.get() == "Y":
                disconnected_flag.set("N")
                close_all(CLIENT)
            time.sleep(3)
            modtime = os.stat(FILE).st_mtime_ns
            if int(received_file.get()) > modtime_sleep:
                modtime_sleep = int(received_file.get())
            if modtime != modtime_sleep:
                msg.insert(tk.END, FILE + " has been updated, update notification sent to server\n")
                CLIENT.send("Y".encode('utf8'))
                f = open(FILE, "rb")
                data = f.read(BUFSIZ)
                while data:
                    CLIENT.send(data)
                    data = f.read(BUFSIZ)
                f.close()
                msg.insert(tk.END, "Updated file has been sent to server\n")
                modtime_sleep = modtime
        except:
            close_all(CLIENT)
            break

def receive(CLIENT):
    """Waiting for server to send notification of updates to to the file and downloads file when it is available"""
    while True:
        try:
            if disconnected_flag.get() == "Y":
                disconnected_flag.set("N")
                close_all(CLIENT)
            data = CLIENT.recv(BUFSIZ).decode('utf8')
            if data == "Y":
                msg.insert(tk.END, FILE + " file updated version is available\n")
                f = open(FILE, 'wb')
                while True:
                    # get file bytes
                    data = CLIENT.recv(BUFSIZ)
                    # write bytes on file
                    f.write(data)
                    if len(data) <= BUFSIZ:
                        break
                        print("Closing file1")
                f.close()
                msg.insert(tk.END, "The file got updated\n")
                received_file.set(os.stat(FILE).st_mtime_ns)
        except:
            close_all(CLIENT)
            break



def connect():
    """Checking user name and connecting to the server"""
    CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        CLIENT.connect(ADDR)
    except socket.error:
        msg.insert(tk.END, "connection error : make sure server is running, IP and port# are correct\n")
        exit(0)

    user_name = str(entry_username.get())

    CLIENT.send(user_name.encode())

    connected = CLIENT.recv(BUFSIZ).decode()

    if connected == "Y":
        msg.insert(tk.END, "you are connected as " + user_name + "\n")
        msg.insert(tk.END, "if you change the file " + FILE + " it will be update to all\n")

        connect_button.configure(text="Disconnect", fg="Blue", command=disconnect)

        if disconnected_flag.get() == "N":
            disconnected_flag.set("1")

        threading.Thread(target=monitor, args=(CLIENT,)).start()

        threading.Thread(target=receive, args=(CLIENT,)).start()

    else:
        msg.insert(tk.END, "user name '" + user_name + "'already exists please try another name\n")


def disconnect():
    """handling disconnection to server."""
    if disconnected_flag.get() == "1":
        disconnected_flag.set("Y")

    CLIENT.close()

    # Button
    connect_button.configure(text="Connect", fg="Blue", command=connect)

    msg.insert(tk.END, "You are not connected to server\n")


def close_all(CLIENT):
    """This function is to be called when the window is closed."""
    CLIENT.send("EXIT_CONNECTION".encode('utf8'))
    sys.exit(0)

def on_closing():
    """This function is to be called when the window is closed."""
    disconnected_flag.set("Y")
    #disconnect()
    window.destroy()
    sys.exit(0)
    #window.destroy()

# ----Now comes the sockets part----
HOST = "127.0.0.1"
PORT = 7777
BUFSIZ = 1024
ADDR = (HOST, PORT)
CLIENT = socket.socket()

# below is the code for GUI.
window = tk.Tk()
window.title("Client")

frame = tk.Frame(window)

received_file = tk.StringVar()
disconnected_flag = tk.StringVar()

disconnected_flag.set("N")

prompt = tk.Label(text="Enter a user Name")
prompt.pack(side=tk.TOP)

entry_username = tk.Entry(window)
entry_username.pack(side=tk.TOP)

connect_button = tk.Button(window)
connect_button.pack()

scrollbar = tk.Scrollbar(frame)  # To navigate through past messages.
# Following will contain the messages.
msg = tk.Listbox(frame, height=50, width=100, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
msg.pack(side=tk.LEFT, fill=tk.BOTH)
msg.pack()
frame.pack()

msg.insert(tk.END, "Client started...\n")

threading.Thread(target=disconnect).start()

window.protocol("WM_DELETE_WINDOW", on_closing)
# Starts GUI execution.
tk.mainloop()
sys.exit(0)
