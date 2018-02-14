import threading, paramiko

StrEnd = False
cnt=0
cnt1=0

class ssh:
    shell = None
    client = None
    transport = None

    def __init__(self, address, username, password):
        print("Connecting to server on ip", str(address) + ".")
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        self.client.connect(address, username=username, password=password, look_for_keys=False)
        self.transport = paramiko.Transport((address, 22))
        self.transport.connect(username=username, password=password)

        thread = threading.Thread(target=self.process)
        thread.daemon = True
        thread.start()

    def SetState(self, state):
        global StrEnd
        StrEnd = state


    def closeConnection(self):
        if (self.client != None):
            self.client.close()
            self.transport.close()

    def openShell(self):
        self.shell = self.client.invoke_shell()

    def sendShell(self, command):
        if (self.shell):
            self.shell.send(command + "\n")
        else:
            print("Shell not opened.")

    def process(self):
        #global connection
        global cnt1
        global StrEnd

        while True:
            # Print data when available
            if self.shell != None and self.shell.recv_ready():
                alldata = self.shell.recv(1024)
                while self.shell.recv_ready():
                    alldata += self.shell.recv(1024)
                strdata = str(alldata, "utf8")
                strdata.replace('\r', '')
                cnt1 = cnt1 +1
                print(strdata, end="")
                if (strdata.endswith("$ ") or ("Passwort" in strdata and strdata.endswith(": ") or ("root@" in strdata and strdata.endswith("# ")) )):
                    print("\n$ ", end="")
                    #print ("cnt1: ", cnt1)
                    cnt1 = 0
                    StrEnd = True

    def strfound(self):
        global StrEnd
        global cnt
        if (StrEnd == True):
            StrEnd = False
            cnt = cnt +1
            #print("true", cnt)
            return (True)
        else:
            return (False)
