#Commands
from tabnanny import check

STARTBYTE = b'\xaa'
STOPBYTE = b'\x55'

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

#Operating modes
DEVELOPMENT = 0x00
PROGRAMMING = 0xfe
PRODUCTION = 0xff 

#Led configuration
LED_ALWAYS_OFF = 0x00
LED_ALWAYS_ON = 0x01
LED_BLINK_ON_ZENCODE = 0x02
LEB_BLINK_ON_SERIAL = 0x03

#Status codes
OK=0x00
CHECKSUM_ERROR=0x01
DEVICE_LOCKED=0x11
BANK_LOCKED=0x12
BANK_OVERFLOW=0x20

#Zenroom Exit codes
OK=0x00
ERROR=0x01

def calc_checksum(packet):
    checksum = 0
    for el in packet:
        checksum ^= el

    return checksum

class MP1:

    def __init__(self):

        #connect to serial

        pass 


    def _read_serial(self):

        stream = STARTBYTE + b'\x01\x00\x23\x00\x22' + STOPBYTE

        
        startbyte = stream[0].to_bytes(1, 'little')
        data = stream[1:-2]
        checksum = stream[-2]
        stopbyte = stream[-1].to_bytes(1, 'little')

        if startbyte != STARTBYTE or stopbyte != STOPBYTE:
            raise Exception("Incomplete message")

        if checksum == calc_checksum(data):
            return data 
        else:
            raise Exception("Checksum error")


    def _write_serial(self, cmd, msg):
        write_buf = STARTBYTE + cmd.to_bytes(1, 'little') + msg + STOPBYTE
        checksum = calc_checksum(write_buf).to_bytes(1, 'little') 
        print(write_buf + checksum)
        
    def _write_read_mp1(self, cmd, msg = b''):

        self._write_serial(cmd, msg)
        read_buf = self._read_serial()

        content = read_buf[:-1]
        status = read_buf[-1] 

        return content, status 
    
    def read_bank(self, bank_id):

        write_buf = bank_id.to_bytes(1, 'little')
        content, status = self._write_read_mp1(READ_BANK, write_buf)
        length = int.from_bytes(content[0:2], 'little')
        bank_content = content[2: length+2].decode('ascii')

        return bank_content, status 

    def write_bank(self, bank_id, content):
        write_buf = bank_id.to_bytes(1, 'little') + len(content).to_bytes(2, 'little') + bytearray(content.encode('ascii'))

        content, status = self._write_read_mp1(WRITE_BANK, write_buf)

        return status 

    def device_locked(self):
        content, status = self._write_read_mp1(DEVICE_LOCKED)
        return status 

    def device_lock(self):
        content, status = self._write_read_mp1(DEVICE_LOCK)
        return status 

    def device_unlock(self, phrase):
        write_buf = phrase.to_bytes(4, 'little')

        content, status = self._write_read_mp1(DEVICE_UNLOCK, write_buf)
        remaining_attempts = content[0]
        return remaining_attempts, status 

    def set_phrase(self, phrase):
        write_buf = phrase.to_bytes(4, 'little')
        content, status = self._write_read_mp1(SET_PHRASE, write_buf)
        return status 

    def operating_mode(self, mode):
        write_buf = mode.to_bytes(1, 'little')
        content, status = self._write_read_mp1(OPERATING_MODE, write_buf)
        return status 

    def factory_reset(self):
        content, status = self._write_read_mp1(FACTORY_RESET)
        return status 

    def led_conf_set(self, conf):

        write_buf = conf.to_bytes(1, 'little')
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
        write_buf = script_bank_id.to_bytes(1, 'little') + keys_bank_id.to_bytes(1, 'little') + data_bank_id.to_bytes(1, 'little') + stdout_bank_id.to_bytes(1, 'little') + stderr_bank_id.to_bytes(1, 'little')
        content, status = self._write_read_mp1(EXEC_ZENCODE, write_buf)
        zenroom_exit_code = content[0] 

        return zenroom_exit_code, status 



