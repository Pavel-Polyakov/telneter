# Telneter
It's a light class for simplify using of Telnetlib for managing network devices. It works well with JunOS, EXOS and Cisco IOS devices.

# Using

To start using you can just import Executor and create instance with one parameter — hostname.
```
>>> from telneter import Executor
>>> ex = Executor('junos-router')
Password: 
>>> ex
Executor (hostname=junos-router,os=JUNOS,connected=True)
```
Executor has one main method — cmd, which returns unicode string with the result of the command
```
>>> model = ex.cmd('show version | match Model')
>>> print(model)
show version | match Model 
Model: mx960

{master}
user@junos-router> 
>>>
```
Also there some little and useful methods.

For example run_and_expect
```
>>> e.run_and_expect('show version', ['Cisco IOS', 'Extreme', 'JUNOS'], 5)
(1,
 <_sre.SRE_Match object; span=(270, 277), match=b'Extreme'>,
 b'show version\r\n\rSwitch      : 800399-00-12 1350N-43988 Rev 12.0 BootROM: 2.0.2.1    IMG: 15.5.3.4  \r\nVIM4-40G4X-1: 800402-00-06 1350N-43231 Rev 6.0\r\nPSU-1       : Internal PSU-1 800462-00-04 1337W-80058\r\nPSU-2       : Internal PSU-2 800462-00-04 1337W-80051\r\n\r\nImage   : Extreme')
```
Ctrl+C method
```
>>> ex.ctrlc()
```

Important thing — you should close connection strictly after using
```
>>> ex.close()
```
In previous example Username was got from bash variable and Password was requested. To purposes of automation is more useful to use separate Account instance which you can pass to constructor of the Executor. Of course you can use one Account to many instances of Executor.
```
>>> from telneter import Account
>>> a = Account()
Password: 
>>> ex = Executor('exos-switch', account=a)
>>> print(ex.cmd('show version | include Extreme'))
show version | include Extreme
Image   : ExtremeXOS version 15.5.3.4 v1553b4-patch1-5 by release-manager
exos-switch.4 # 
```
To use different username and/or password you can pass it to the constructor of Account object
```
>>> a = Account('user','pass')
>>> a
Account (username='user')
```

# Installation
Just install it with pip
   
```$ pip install telneter```
