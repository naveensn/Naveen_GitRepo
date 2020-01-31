
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

# Change this path if you have a different directory
PATH = "D:/Study/1st Sem/Distrubuted Systems/Lab1/Client1"


def monitor(CLIENT):
    """Monitors shared folder for any new files. if new files found send it to Server"""
    before = dict ([(f, None) for f in os.listdir(PATH)])
    while True:
        if disconnected_flag.get() == "Y":
            close_all(CLIENT)
        time.sleep(1)
        after = dict([(f, None) for f in os.listdir(PATH)])
        added = [f for f in after if not f in before]
        if received_file.get() in added:
            added.remove(received_file.get())
        for i in range(0, len(added)):
            f_send = PATH + "/" + str(added[i])
            CLIENT.send(("Y"+str(added[i])).encode('utf8'))
            print(f_send)
            f = open(f_send, "rb")
            data = f.read(BUFSIZ)
            while data:
                print(data)
                CLIENT.send(data)
                data = f.read(BUFSIZ)
            print(data)
        before = after


def receive(CLIENT):
    """Waiting for server to send any files and downloads file when it is available"""
    while True:
        if disconnected_flag.get() == "Y":
            close_all(CLIENT)
        data = CLIENT.recv(BUFSIZ).decode('utf8')

        if data[:1] == "Y":
            received_file.set(data[1:])
            msg.insert(tk.END, "new file " + data[1:] + " available and getting downloaded to" + PATH + "\n" )
            f = open(PATH + "/" + data[1:], 'wb')
            while data:
                # get file bytes
                data = CLIENT.recv(BUFSIZ)
                # write bytes on file
                f.write(data)
                if (len(data) <= BUFSIZ):
                    break
            f.close()


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
        msg.insert(tk.END, "to upload the files please put the files in \n" + user_name + "\n")

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