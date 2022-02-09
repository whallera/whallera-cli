from socket import timeout
import sys
import serial 
import time 


#Serial Start & Stop
STARTBYTE = b'\xaa'
STOPBYTE = b'\x55'

ENDIANESS = 'little'

#Commands
READ_BANK=0x10
WRITE_BANK=0x11
DEVICE_LOCKED=0x20
DEVICE_LOCK=0x21
DEVICE_UNLOCK=0x22
SET_PHRASE=0x23
OPERATING_MODE=0x2e
FACTORY_RESET=0x2f
LED_CONF_SET=0x30
VERSION=0x3f
EXEC_ZENCODE=0x40
EXEC_ZENCODE_STATUS=0x41

#Operating modes
DEVELOPMENT = 0x00
PROGRAMMING = 0xfe
PRODUCTION = 0xff 

#Led configuration
LED_ALWAYS_OFF = 0x00
LED_ALWAYS_ON = 0x01
LED_BLINK_ON_ZENCODE = 0x02
LED_BLINK_ON_SERIAL = 0x03

#Status codes
OK=0x00
CHECKSUM_ERROR=0x01
DEVICE_LOCKED=0x11
BANK_LOCKED=0x12
BANK_OVERFLOW=0x20
WAIT=0x33

#Zenroom Exit codes
OK=0x00
ERROR=0x01

#Just for debugs
DUMMY_TTY = "dummy"

BAUDRATE = 115200 
SERIAL_TIMEOUT = 10 
SERIAL_WAIT = 0.1

def calc_checksum(packet):
    checksum = 0
    for el in packet:
        checksum ^= el

    return checksum

def concatenate(parts):

    buffer = b''
    for part in parts:
        buffer += part 
    
    return buffer

def int8(i):
    return i.to_bytes(1, ENDIANESS)

def int16(i):
    return i.to_bytes(2, ENDIANESS)

def int32(i):
    return i.to_bytes(4, ENDIANESS)

class MP1:

    def __init__(self, interface):

        self.interface = interface   
        
        if self.interface != DUMMY_TTY:
            self.serial = serial.Serial(self.interface, baudrate=BAUDRATE)
            if not self.serial.is_open:
                self.serial.open()

    #This function returns False when no data arrives in the timeout, 
    # True if it exits before the timeout

    def _wait_serial(self, timeout):
        while not self.serial.in_waiting and timeout > time.time():
            time.sleep(SERIAL_WAIT)
        if timeout > time.time():
            return True 
        return False 

    def _read_serial(self):

        if self.interface == DUMMY_TTY:
            stream = concatenate([
                STARTBYTE,
                b'\x01\x00\x23\x00\x22',
                STOPBYTE
            ]) 
            sys.stdout.write('RX: '+str(stream)+'\n')

        else:

            stream = b''
            timeout = time.time() + SERIAL_TIMEOUT

            if not self._wait_serial(timeout):
                raise Exception("Serial Timeout, check connection")

            while self.serial.in_waiting:
                stream += self.serial.read()
                #self._wait_serial(timeout)

        self.rx_stream = stream 

        startbyte = int8(stream[0])
        data = stream[1:-2]
        checksum = stream[-2]
        stopbyte = int8(stream[-1])

        if startbyte != STARTBYTE or stopbyte != STOPBYTE:
            raise Exception("Incomplete message: "+str(stream))

        if checksum == calc_checksum(data):
            return data 
        else:
            raise Exception("Checksum error: "+str(stream))


    def _write_serial(self, cmd, msg):

        write_buf = concatenate([
            STARTBYTE,
            int8(cmd),
            msg,
            STOPBYTE
        ])

        checksum = int8(calc_checksum(write_buf)) 
        self.tx_stream = concatenate([write_buf, checksum])
        
        if self.interface == DUMMY_TTY:
            sys.stdout.write('TX: '+str(self.tx_stream)+'\n')
        else:
            self.serial.write(self.tx_stream)

    def _write_read_mp1(self, cmd, msg = b''):

        self._write_serial(cmd, msg)
        read_buf = self._read_serial()

        content = read_buf[:-1]
        status = read_buf[-1] 

        return content, status 
    
    def read_bank(self, bank_id):

        write_buf = int8(bank_id)
        content, status = self._write_read_mp1(READ_BANK, write_buf)
        length = int.from_bytes(content[0:2], 'little')
        bank_content = content[2: length+2].decode('ascii')

        return bank_content, status 

    def write_bank(self, bank_id, content):
        write_buf = concatenate([
            int8(bank_id),
            int16(len(content)),
            bytearray(content.encode('ascii'))
        ])

        content, status = self._write_read_mp1(WRITE_BANK, write_buf)

        return status 

    def device_locked(self):
        content, status = self._write_read_mp1(DEVICE_LOCKED)
        return status 

    def device_lock(self):
        content, status = self._write_read_mp1(DEVICE_LOCK)
        return status 

    def device_unlock(self, phrase):
        write_buf = int32(phrase)

        content, status = self._write_read_mp1(DEVICE_UNLOCK, write_buf)
        remaining_attempts = content[0]
        return remaining_attempts, status 

    def set_phrase(self, phrase):
        write_buf = int32(phrase)
        content, status = self._write_read_mp1(SET_PHRASE, write_buf)
        return status 

    def operating_mode(self, mode):
        write_buf = int8(mode)
        content, status = self._write_read_mp1(OPERATING_MODE, write_buf)
        return status 

    def factory_reset(self):
        content, status = self._write_read_mp1(FACTORY_RESET)
        return status 

    def led_conf_set(self, conf):

        write_buf = int8(conf)
        content, status = self._write_read_mp1(LED_CONF_SET, write_buf)
        return status  

    def version(self):

        content, status = self._write_read_mp1(VERSION)
        UDID = content[0:12] #TBD
        firmware_version = content[12:15]
        zenroom_version = content[15:18]
        status = OK 

        return UDID, firmware_version, zenroom_version, status 

    def exec_zencode(self, script_bank_id, keys_bank_id, data_bank_id, stdout_bank_id, stderr_bank_id):
        write_buf = concatenate([
            int8(script_bank_id),
            int8(keys_bank_id),
            int8(data_bank_id),
            int8(stdout_bank_id),
            int8(stderr_bank_id)
        ])

        content, status = self._write_read_mp1(EXEC_ZENCODE, write_buf)

        return status 

    def exec_zencode_status(self):

        content, status = self._write_read_mp1(EXEC_ZENCODE_STATUS)

        zenroom_exit_code = content[0] 

        return zenroom_exit_code, status 




