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
    prompt_login = r"login"
    prompt_password = r"assword"
    prompt_id_extreme = r"ExtremeXOS"
    prompt_id_juniper = r"JUNOS"
    prompt_ios = [r".*#$"]
    prompt_exos = [r".*# $"]
    prompt_junos = [r".*> $", r".*% $"]
    prompt_all = [r".*> $", r".*# $", r".*% $", r".*#$"]
    prompt_failed_login = r"Login incorrect"

    def __init__(self, hostname, account=None, connect=True):
        self.hostname = hostname
        self.account = account or Account()
        self.connected = False
        self._tn = None
        self.os = None
        self.eol = "\r\n"
        if connect:
            self.connect()

    def connect(self):
        self._tn = telnetlib.Telnet(self.hostname)
        self._tn.read_until(self.prompt_login, 10)
        self._tn.write(self.account.username+"\n")
        self._tn.expect([self.prompt_password], 10)
        self._tn.write(self.account.password+"\n")
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
            self._tn.write("show version\r\n")
            response = self._tn.expect([r"(M|m)ore"]+self.prompt_all, 10)
            if "Cisco IOS" in response[-1]:
                self.__initialize_ios()
            else:
                self.close()
                raise ValueError("Enexpected device")

    def close(self):
        self.connected = False
        self._tn.close()

    def __initialize_ios(self):
        self.connected = True
        self.os = "IOS"
        self._tn.write("\x03")
        self._tn.write("terminal length 0\r\n")
        self._tn.read_very_eager()

    def __initialize_exos(self):
        self.connected = True
        self.os = "EXOS"
        self._tn.write("disable clipaging\r\n")
        self._tn.read_very_eager()

    def __initialize_junos(self):
        self.connected = True
        self.os = "JUNOS"
        self._tn.write("cli\r\n")
        self._tn.read_very_eager()

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
        self._tn.write(command+self.eol)
        output = self._tn.expect(prompt, 30)[-1]
        return output

    def __repr__(self):
        return "Executor (hostname={},os={},connected={})".\
                format(self.hostname, self.os, self.connected)
