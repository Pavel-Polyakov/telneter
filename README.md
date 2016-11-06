# Telneter
It's a light class for simplify using of Telnetlib for managing network devices. It works well with JunOS, EXOS and Cisco IOS devices.

# Using

To start using you can just import Executor and create instance with one parameter — hostname.
```
>>> from telneter import Executor
>>> ex = Executor('junos-router')
... Password: 
>>> ex
... Executor (hostname=m9-r0,os=JUNOS,connected=True)
```
Executor has one method — cmd, which returns unicode string with the result of the command
```
>>> model = ex.cmd('show version | match Model')
>>> print(model)
... show version | match Model 
... Model: mx960
... 
... {master}
... user@junos-router> 
>>>
```
You should close connection strictly after using
```
>>> ex.close()
```
In previous example Username was got from bash variable and Password was requested. To purposes of automation is more useful to use separate Account instance which you can pass to constructor of the Executor. Of course you can use one Account to many instances of Executor.
```
>>> from telneter import Account
>>> a = Account()
... Password: 
>>> ex = Executor('exos-switch', account=a)
>>> print(ex.cmd('show version | include Extreme'))
... show version | include Extreme
... Image   : ExtremeXOS version 15.5.3.4 v1553b4-patch1-5 by release-manager
... exos-switch.4 # 
```
To use different username and/or password you can pass it to the constructor of Account object
```
>>> a = Account('user','pass')
>>> a
... Account (username='user')
```

# Installation
Just install it with pip
   
```$ pip install telneter```
