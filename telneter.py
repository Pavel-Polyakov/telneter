import telnetlib
import getpass
import time


class Account(object):
    def __init__(self, username=None, password=None):
        self.username = username or getpass.getuser()
        self.password = password or getpass.getpass()

    def __repr__(self):
        return 'Account (username="{}", password="{}")'.\
                format(self.username, '*'*len(self.password))


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
        self.run_and_expect(self.account.username, self.prompt_password, 10)
        response = self.run_and_expect(self.account.password,
                                       [self.prompt_id_extreme,
                                        self.prompt_id_juniper,
                                        self.prompt_failed_login] + self.prompt_all,
                                       10)
        if response[0] == 0:
            self.__initialize_exos()
        elif response[0] == 1:
            self.__initialize_junos()
        elif response[0] == 2:
            self.close()
            raise ValueError("Failed login")
        else:
            response = self.run_and_expect("show version",
                                           [b"(M|m)ore"]+self.prompt_all, 10)
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
        self.ctrlc()
        self.run("terminal length 0")

    def __initialize_exos(self):
        self.connected = True
        self.os = "EXOS"
        self.run('disable clipaging')
        time.sleep(1)

    def __initialize_junos(self):
        self.connected = True
        self.os = "JUNOS"
        self.run(self.eol)
        self.run("cli")
        self.run("set cli screen-length 0")

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
        self.read_all()
        output = self.run_and_expect(command, prompt)[-1]
        return output.decode('utf8', errors='replace')

    def expect(self, expect, timer=30):
        if isinstance(expect, list):
            cleaned = [self.__convert_to_bytes(x) for x in expect]
        else:
            cleaned = [self.__convert_to_bytes(expect)]
        return self._tn.expect(cleaned, timer)

    def run(self, command):
        self._tn.write(self.__convert_to_bytes(command)+self.eol)

    def run_and_expect(self, command, expect, timer=30):
        self.run(command)
        return self.expect(expect, timer)

    def read_all(self):
        return self._tn.read_very_eager()

    def ctrlc(self):
        self.run(b"\x03")

    @staticmethod
    def __convert_to_bytes(value):
        result = None
        if isinstance(value, str):
            result = value.encode('utf8')
        elif isinstance(value, (float, int, )):
            result = str(value).encode('utf8')
        elif isinstance(value, bytes):
            result = value
        else:
            result = bytes(value)
        return result

    def __repr__(self):
        return 'Executor (hostname="{}", os="{}", connected={})'.\
                format(self.hostname, self.os, self.connected)
