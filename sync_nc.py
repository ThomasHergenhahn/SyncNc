#!/usr/bin/env python

from tkinter import *
import socket
import sys, paramiko
import time
import string
import os
import threading, paramiko
from paramiko_shell import *

init_dir = "/home/thh/test/nctst_data"
state = "init_backup"
server_cmd = "/server_cmd.sh"

hostname = "192.168.178.23"
password = "__adid__"
username = "thh"
home_dieser_pc = "/home/thh/nc"
home_entfernter_pc = "/home/thh/nc"
data_dir_dieser_pc ="/var/nc_data"
data_dir_entfernter_pc ="/var/nc_data"
nc_dieser_pc = "/var/www/nextcloud"
nc_entfernter_pc = "/var/www/nextcloud"

def MainSync():
    global hostname
    global username
    global password
    global home_dieser_pc
    global home_entfernter_pc
    global data_dir_dieser_pc
    global data_dir_entfernter_pc
    global nc_dieser_pc
    global nc_entfernter_pc

    #commands = ['mkdir ' + home_entfernter_pc, 'whoami']
    pref = "/"
    dirs = home_entfernter_pc.split("/")
    cdDir = ""
    for dir in dirs:
        if dir != "":
            cdDir = cdDir + '/' + dir
            commands = ["mkdir " + cdDir, "cd " + cdDir]
            SendCmds(commands)
            #print (commands)
            #print('#################################################')

    commands = ['sudo -s', password, 'chown thh:thh ' + home_entfernter_pc, 'whoami']
    SendCmds(commands)
    write_server_cmd()
    SendCmdFile()

    connection = ssh(hostname, username, password)
    connection.SetState = False
    connection.openShell()

    vor_nc_entfernter_pc=''
    olddir = ''

    dirs = nc_entfernter_pc.split("/")
    for dir in dirs:
        vor_nc_entfernter_pc = vor_nc_entfernter_pc + olddir
        olddir=dir + '/'

    commands = ['sudo -s', '__adid__', 'chmod +x /home/thh/server_cmd.sh', 'sh /home/thh/server_cmd.sh',\
                'chown thh:thh /var/www/nextcloud-dirbkp.tar.gz', 'rm -R /home/thh/nc', 'mkdir /home/thh/nc',\
                'cp /var/www/nextcloud-dirbkp.tar.gz /home/thh/nc',\
                'chown thh:thh /home/thh/nc/nextcloud-dirbkp.tar.gz',\
                'cp /var/www/nextcloud-sqlbkp.bak /home/thh/nc',\
                'chown thh:thh /home/thh/nc/nextcloud-sqlbkp.bak',\
                'whoami']

    commands = ['sudo -s', '__adid__', \
                'chmod +x ' + home_entfernter_pc + '/server_cmd.sh', \
                'chown thh:thh ' + home_entfernter_pc + '/server_cmd.sh', \
                'sh ' + home_entfernter_pc + '/server_cmd.sh', \
                'chown thh:thh ' + nc_entfernter_pc + '/nextcloud-dirbkp.tar.gz', \
                #'rm -R ' + home_entfernter_pc, \
                #'mkdir ' + home_entfernter_pc, \
                'cp ' + nc_entfernter_pc + '/nextcloud-dirbkp.tar.gz ' + home_entfernter_pc, \
                'chown thh:thh ' + home_entfernter_pc + '/nextcloud-dirbkp.tar.gz', \
                'cp ' + nc_entfernter_pc + '/nextcloud-sqlbkp.bak ' + home_entfernter_pc, \
                'chown thh:thh ' + home_entfernter_pc + '/nextcloud-sqlbkp.bak', \
                'whoami']
    #commands = ['sudo -s', '__adid__', 'whoami']

    SendCmds(commands)
    GetResultFiles()

def SendCmds(commands):
    global hostname
    global username
    global password
    global home_dieser_pc
    global home_entfernter_pc
    global data_dir_dieser_pc
    global data_dir_entfernter_pc
    global nc_dieser_pc
    global nc_entfernter_pc

    connection = ssh(hostname, username, password)
    connection.SetState = False
    connection.openShell()

    for command in commands:
        while connection.strfound() == False:
            command = command
        print('command: ', command)
        connection.SetState = False
        connection.sendShell(command)

    connection.SetState = False
    while connection.strfound() == False:
        command = ""
    connection.closeConnection()

    """
    while True:
        command = input('$ ')
        command = ('ls -la')
        if command.startswith(" "):
            command = command[1:]
        connection.sendShell(command)
        print('Sende: ', command)
    """

def GetResultFiles():
    global hostname
    global password
    global username

    dest = "/home/thh/nc"
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.WarningPolicy)
        # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)

        sftp = ssh.open_sftp()
        sftp.get("/var/ncdata.tar.gz", dest + "/ncdata.tar.gz")
        sftp.get("/home/thh/nc/nextcloud-dirbkp.tar.gz", dest + "/nextcloud-dirbkp.tar.gz")
        sftp.get("/home/thh/nc/nextcloud-sqlbkp.bak", dest + "/nextcloud-sqlbkp.bak")
        sftp.close()
        ssh.close()
    except:
        print("Nicht alle Files vorhanden")

def SendCmdFile():
    global hostname
    global username
    global password
    global home_dieser_pc
    global home_entfernter_pc
    global data_dir_dieser_pc
    global data_dir_entfernter_pc
    global nc_dieser_pc
    global nc_entfernter_pc

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.WarningPolicy)
    ssh.connect(hostname, username=username, password=password)
    sftp = ssh.open_sftp()
    sftp.put(home_dieser_pc + '/server_cmd.sh', home_entfernter_pc + '/server_cmd.sh')
    sftp.close()
    ssh.close()

def write_server_cmd():
    global server_cmd

    if os.path.isfile(server_cmd):
        os.system("rm " + server_cmd)
    if os.path.isfile("/home/thh/nc/ncdata.tar.gz"):
        os.system("rm /home/thh/nc/ncdata.tar.gz")
    if os.path.isfile("/home/thh/nc/nextcloud-dirbkp.tar.gz"):
        os.system("rm /home/thh/nc/nextcloud-dirbkp.tar.gz")
    if os.path.isfile("/home/thh/nc/nextcloud-sqlbkp.bak"):
        os.system("rm /home/thh/nc/nextcloud-sqlbkp.bak")

    file = open(home_entfernter_pc + server_cmd, "w")
    file.write("#!bin/sh\n")
    file.write("rm /var/ncdata.tar.gz\n")
    file.write("rm -R /var/www/nextcloud-dirbkp\n")
    file.write("rm /var/www/nextcloud-dirbkp.tar.gz\n")
    file.write("rm /var/www/nextcloud-sqlbkp.bak\n")
    file.write("cd /var/www/nextcloud\n")
    file.write("sudo -u www-data php occ maintenance:mode --on\n")
    file.write("cd ..\n")
    file.write("rsync -Aax nextcloud/ nextcloud-dirbkp/\n")
    file.write("tar cfvz nextcloud-dirbkp.tar.gz nextcloud-dirbkp\n")
    file.write("mysqldump --lock-tables -h localhost -u nextcloud -pnextcloud nextcloud > nextcloud-sqlbkp.bak\n")
    file.write("cd /var\n")
    #file.write("tar cfvz ncdata.tar.gz nc_data\n")
    file.write("cd /var/www/nextcloud\n")
    file.write("sudo -u www-data php occ maintenance:mode --off\n")
    file.write("rm /home/thh/nc" + server_cmd + "\n")
    file.close()
    #os.system("chmod +x " + server_cmd)

def ReadParams():
    global hostname
    global username
    global password
    global home_dieser_pc
    global home_entfernter_pc
    global data_dir_dieser_pc
    global data_dir_entfernter_pc
    global nc_dieser_pc
    global nc_entfernter_pc

    if os.path.isfile(home_dieser_pc + "/sync_pers.txt"):
        file = open(home_dieser_pc + "/sync_pers.txt", "r")
        hostname = file.readline()
        if "\n" in hostname:
            hostname = hostname.replace("\n", "")
        username = file.readline()
        if "\n" in username:
            username = username.replace("\n", "")
        password = file.readline()
        if "\n" in password:
            password = password.replace("\n", "")

        home_dieser_pc = file.readline()
        if "\n" in home_dieser_pc:
            home_dieser_pc = home_dieser_pc.replace("\n", "")
        home_entfernter_pc = file.readline()
        if "\n" in home_entfernter_pc:
            home_entfernter_pc = home_entfernter_pc.replace("\n", "")
        data_dir_dieser_pc = file.readline()
        if "\n" in data_dir_dieser_pc:
            data_dir_dieser_pc = data_dir_dieser_pc.replace("\n", "")
        data_dir_entfernter_pc = file.readline()
        if "\n" in data_dir_entfernter_pc:
            data_dir_entfernter_pc = data_dir_entfernter_pc.replace("\n", "")
        nc_dieser_pc = file.readline()
        if "\n" in nc_dieser_pc:
            nc_dieser_pc = nc_dieser_pc.replace("\n", "")
        nc_entfernter_pc = file.readline()
        if "\n" in nc_entfernter_pc:
            nc_entfernter_pc = nc_entfernter_pc.replace("\n", "")

        file.close()

def StoreParams(hostname, username, password, home_dieser_pc, home_entfernter_pc, data_dir_dieser_pc, data_dir_entfernter_pc, nc_dieser_pc, nc_entfernter_pc):
    if not os.path.exists(home_dieser_pc):
        os.system("mkdir "+ home_dieser_pc )
    file = open(home_dieser_pc +"/sync_pers.txt", "w")
    file.write(hostname + "\n")
    file.write(username + "\n")
    file.write(password + "\n")
    file.write(home_dieser_pc + "\n")
    file.write(home_entfernter_pc + "\n")
    file.write(data_dir_dieser_pc + "\n")
    file.write(data_dir_entfernter_pc + "\n")
    file.write(nc_dieser_pc + "\n")
    file.write(nc_entfernter_pc + "\n")
    file.close()

    #GetResultFiles()
    MainSync()

class App:
  def __init__(self, master):
    global init_dir

    global hostname
    global username
    global password
    global home_dieser_pc
    global home_entfernter_pc
    global data_dir_dieser_pc
    global data_dir_entfernter_pc
    global nc_dieser_pc
    global nc_entfernter_pc

    ReadParams()
    frame = Frame(master)

    Label(root, text="Entfernter Host:             ", justify=LEFT, anchor=W).grid(row=0)
    Label(root, text="Entfernter Username:         ").grid(row=1)
    Label(root, text="Entfernters Passwort:        ").grid(row=2)
    Label(root, text="Home Dieser PC:              ").grid(row=3)
    Label(root, text="Home Entfernter PC:          ").grid(row=4)
    Label(root, text="Nc Daten Dieser PC:          ").grid(row=5)
    Label(root, text="Nc Daten Home Entfernter PC: ").grid(row=6)
    Label(root, text="Nc Dieser PC:                ").grid(row=7)
    Label(root, text="Nc Entfernter PC:            ").grid(row=8)
    Label(root, text="").grid(row=9)

    h = StringVar(root, value=hostname)
    self.e1 = Entry(root, textvariable=h)
    h = StringVar(root, value=username)
    self.e2 = Entry(root, textvariable=h)
    h = StringVar(root, value=password)
    self.e3 = Entry(root, textvariable=h)
    h = StringVar(root, value=home_dieser_pc)
    self.e4 = Entry(root, textvariable=h)
    h = StringVar(root, value=home_entfernter_pc)
    self.e5 = Entry(root, textvariable=h)
    h = StringVar(root, value=data_dir_dieser_pc)
    self.e6 = Entry(root, textvariable=h)
    h = StringVar(root, value=data_dir_entfernter_pc)
    self.e7 = Entry(root, textvariable=h)
    h = StringVar(root, value=nc_dieser_pc)
    self.e8 = Entry(root, textvariable=h)
    h = StringVar(root, value=nc_entfernter_pc)
    self.e9 = Entry(root, textvariable=h)

    self.b1 = Button(root, text="Save and QUIT", fg="red", command=frame.quit)
    self.b2 = Button(root, text="Save and Run", fg="green", command=self.StoreParamsInFile)

    #self.e1.pack(side=BOTTOM)
    #self.e2.pack(side=LEFT)

    self.e1.grid(row=0, column=1)
    self.e2.grid(row=1, column=1)
    self.e3.grid(row=2, column=1)
    self.e4.grid(row=3, column=1)
    self.e5.grid(row=4, column=1)
    self.e6.grid(row=5, column=1)
    self.e7.grid(row=6, column=1)
    self.e8.grid(row=7, column=1)
    self.e9.grid(row=8, column=1)
    self.b1.grid(row=10, column=0)
    self.b2.grid(row=10, column=1)

  def StoreParamsInFile(self):
      StoreParams(self.e1.get(), self.e2.get(), self.e3.get(), self.e4.get(), self.e5.get(), self.e6.get(), self.e7.get(), self.e8.get(), self.e9.get())

root = Tk()
app = App(root)
root.mainloop()

