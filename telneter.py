import telnetlib
import getpass
import time


class Account(object):
    def __init__(self, username=None, password=None):
        self.username = username or getpass.getuser()
        self.password = password or getpass.getpass()

    def __repr__(self):
        return "Account (username={})".format(self.username)


class Executor(object):
    prompt_login = b"login"
    prompt_password = b"assword"
    prompt_id_extreme = b"ExtremeXOS"
    prompt_id_juniper = b"JUNOS"
    prompt_ios = [b".*#$"]
    prompt_exos = [b".*# $"]
    prompt_junos = [b".*> $", b".*% $"]
    prompt_all = [b".*> $", b".*# $", b".*% $", b".*#$"]
    prompt_failed_login = b"Login incorrect"

    def __init__(self, hostname, account=None, connect=True):
        self.hostname = hostname
        self.account = account or Account()
        self.connected = False
        self._tn = None
        self.os = None
        self.eol = b"\r\n"
        if connect:
            self.connect()

    def connect(self):
        self._tn = telnetlib.Telnet(self.hostname)
        self._tn.read_until(self.prompt_login, 10)
        self._tn.write((self.account.username+"\n").encode('utf8'))
        self._tn.expect([self.prompt_password], 10)
        self._tn.write((self.account.password+"\n").encode('utf8'))
        response = self._tn.expect([self.prompt_id_extreme,       # 0
                                    self.prompt_id_juniper,       # 1
                                    self.prompt_failed_login,     # 2
                                    ]+self.prompt_all, 10)
        if response[0] == 0:
            self.__initialize_exos()
        elif response[0] == 1:
            self.__initialize_junos()
        elif response[0] == 2:
            self.close()
            raise ValueError("Failed login")
        else:
            self._tn.write(b"show version\r\n")
            response = self._tn.expect([b"(M|m)ore"]+self.prompt_all, 10)
            if b"Cisco IOS" in response[-1]:
                self.__initialize_ios()
            else:
                self.close()
                raise ValueError("Enexpected device")

    def close(self):
        self.connected = False
        self.os = None
        self._tn.close()

    def __initialize_ios(self):
        self.connected = True
        self.os = "IOS"
        self._tn.write(b"\x03")
        self._tn.write(b"terminal length 0\r\n")

    def __initialize_exos(self):
        self.connected = True
        self.os = "EXOS"
        self._tn.write(b"disable clipaging\r\n")

    def __initialize_junos(self):
        self.connected = True
        self.os = "JUNOS"
        self._tn.write(self.eol)
        self._tn.write(b"cli\r\n")
        self._tn.write(b"set cli screen-length 0\r\n")

    def cmd(self, command):
        if self.os == "JUNOS":
            prompt = self.prompt_junos
        elif self.os == "EXOS":
            prompt = self.prompt_exos
        elif self.os == "IOS":
            prompt = self.prompt_ios
        else:
            prompt = self.prompt_all

        time.sleep(1)
        self._tn.read_very_eager()
        self._tn.write(command.encode('utf8')+self.eol)
        output = self._tn.expect(prompt, 30)[-1]
        return output.decode('utf8', errors='replace')

    def __repr__(self):
        return "Executor (hostname={},os={},connected={})".\
                format(self.hostname, self.os, self.connected)
