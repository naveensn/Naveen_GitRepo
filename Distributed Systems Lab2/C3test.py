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
    """Monitors shared folder for new files or deleted files. and sends info to Server"""
    before = dict ([(f, None) for f in os.listdir(PATH)])
    while True:
        if disconnected_flag.get() == "Y":
            close_all(CLIENT)
        time.sleep(3)
        after = dict([(f, None) for f in os.listdir(PATH)])
        added = [f for f in after if not f in before]
        removed = [f for f in before if not f in after]

        if received_file.get() in added:
            added.remove(received_file.get())
            received_file.set("")
        if received_file.get() in removed:
            removed.remove(received_file.get())
            received_file.set("")
        for file in added:
            f_send = PATH + "/" + str(file)
            CLIENT.send(("ADDED"+str(file)).encode('utf8'))
            f = open(f_send, "rb")
            data = f.read(BUFSIZ)
            while data:
                CLIENT.send(data)
                data = f.read(BUFSIZ)
            f.close()

        for file in removed:
            operation.set("REMOVED"+str(file))
            CLIENT.send(("REMOVED"+str(file)).encode('utf8'))
        before = after


def receive(CLIENT):
    """Waiting for any messages/files from servers"""
    while True:
        if disconnected_flag.get() == "Y":
            close_all(CLIENT)
        data = CLIENT.recv(BUFSIZ).decode('utf8')

        if operation.get()[:7] == "REMOVED":
            agree, disagree = 0, 0
            file = operation.get()[7:]
            while data[:5] == "AGREE" or data[:8] == "DISAGREE":
                if data[:5] == "AGREE":
                    agree += 1
                else:
                    disagree += 1
                data = CLIENT.recv(BUFSIZ).decode('utf8')
            num_peers = int(data[13:]) - 1
            if agree == num_peers:
                msg.insert(tk.END, "All " + str(num_peers) + " peers agreed to delete the file\n")
                CLIENT.send("CONFIRM".encode())
            else:
                CLIENT.send("NOT-CONFIRM".encode())
                received_file.set(file)
                f = open(PATH + "/" + file, 'wb')
                msg.insert(tk.END, "Only " + str(num_peers) + " peer agreed to delete the file, aborting the delete\n")
                while True:
                    # get file bytes
                    data = CLIENT.recv(BUFSIZ)
                    # write bytes on file
                    f.write(data)
                    if (len(data) < BUFSIZ):
                        break
                f.close()
                msg.insert(tk.END, "Restored the deleted file" + received_file.get() + "\n")
            operation.set("")

        if data[:5] == "ADDED":
            received_file.set(data[5:])
            msg.insert(tk.END, "new file " + data[5:] + " available and getting downloaded to" + PATH + "\n" )
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
            msg.insert(tk.END, "file " + data[7:] + " has been removed  need to give consent " + PATH + "\n" )

            time.sleep(3)
            if random.random() > 0.75:
                CLIENT.send("DISAGREE".encode())
                msg.insert(tk.END, "Voted 'NO' to delete the file\n")
            else:
                CLIENT.send("AGREE".encode())
                msg.insert(tk.END, "Voted 'YES' to delete the file\n")

        elif data[:7] == "CONFIRM":
            msg.insert(tk.END, "All clients agreed to delete the file, file is deleted\n")
            if os.path.exists(f_remv):
                os.remove(f_remv)
            else:
                print("The file does not exist")
        elif data[:11] == "NOT-CONFIRM":
            msg.insert(tk.END, "Everyone did not agree to delete the file, file delete aborted\n")



def connect():
    """Checking user name and connecting to the server"""
    CLIENT = socket.socket()

    try:
        CLIENT.connect(ADDR)
        connected = "YES"
    except socket.error:
        msg.insert(tk.END, "connection error : make sure server is running, IP and port# are correct\n")
        connected = "NOT"

    user_name = str(entry_username.get())

    if connected == "YES" and user_name and not user_name.isspace():
        CLIENT.send(user_name.encode())
        connected = CLIENT.recv(BUFSIZ).decode()
    else:
        connected = "NO"

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