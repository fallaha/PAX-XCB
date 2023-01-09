# PAX-XCB
Pax XCB Client With Serial for windows and Linux

https://github.com/google/python-adb/pull/178

### dependency

  * libusb1
  * M2Crypto

for install M2Crypto in Windows you can use [this prebuild](https://github.com/cperezabo/m2crypto-wheels) for easy to install

### linux
to use in Linux OS change below line
```python
port = 'COM{},115200'.format(tty)
```
to this
```python
port = '/dev/tty{},115200'.format(tty)
```
in clinet.py file


## Usage
for push a file to device use this command (3 is COM port)
```cmd
python client.py 3 push /local/path/in/your/pc /device/path/file
```

for get a file from device use this command (3 is COM port)
```cmd
python client.py 3 pull  /device/path/file /local/path/in/your/pc
```
