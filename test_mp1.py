from lib.mp1 import * 

def test_int8():
    assert int8(255) == b'\xff'

def test_int16():
    assert int16(1234) == b'\xd2\x04'

def test_int32():
    assert int32(56839333) == b'\xa5Lc\x03'

def test_checksum():
    assert calc_checksum(b'\x01\x00\x23\x00') == b'\x22'[0]

def test_concatenate():
    assert concatenate([b'\x00', b'\x01\x02', b'\x03']) == b'\x00\x01\x02\x03'

def test_read_bank():
    
    mp1 = MP1(DUMMY_TTY)
    bank_content, status = mp1.read_bank(0x00)
    assert mp1.tx_stream == b'\xaa\x10\x00U\xef'

def test_write_bank():
    mp1 = MP1(DUMMY_TTY)
    status = mp1.write_bank(0x00, "ciao")
    assert mp1.tx_stream == b'\xaa\x11\x00\x04\x00ciaoU\xee'
    
def test_device_locked():
    mp1 = MP1(DUMMY_TTY)
    status = mp1.device_locked()
    assert mp1.tx_stream == b'\xaa\x11U\xee'
    
def test_device_lock():
    mp1 = MP1(DUMMY_TTY)
    status = mp1.device_lock()
    assert mp1.tx_stream == b'\xaa!U\xde'
    
def test_device_unlock():
    mp1 = MP1(DUMMY_TTY)
    remaining_attempts, status  = mp1.device_unlock(1234)
    assert mp1.tx_stream == b'\xaa"\xd2\x04\x00\x00U\x0b'
    
def test_set_phrase():
    mp1 = MP1(DUMMY_TTY)
    status = mp1.set_phrase(1234)
    assert mp1.tx_stream == b'\xaa#\xd2\x04\x00\x00U\n'
    
def test_operating_mode():
    mp1 = MP1(DUMMY_TTY)
    status = mp1.operating_mode(DEVELOPMENT)
    assert mp1.tx_stream == b'\xaa.\x00U\xd1'
    
def test_factory_reset():
    mp1 = MP1(DUMMY_TTY)
    status = mp1.factory_reset()
    assert mp1.tx_stream == b'\xaa/U\xd0'
    
def test_led_conf_set():
    mp1 = MP1(DUMMY_TTY)
    status = mp1.led_conf_set(LED_ALWAYS_OFF)
    assert mp1.tx_stream == b'\xaa0\x00U\xcf'
    
def test_version():
    mp1 = MP1(DUMMY_TTY)
    UDID, firmware_version, zenroom_version, status = mp1.version()
    assert mp1.tx_stream == b'\xaa?U\xc0'
    
def test_exec_zencode():
    mp1 = MP1(DUMMY_TTY)
    status  = mp1.exec_zencode(0x01, 0x02, 0x03, 0x04, 0x05)
    assert mp1.tx_stream == b'\xaa@\x01\x02\x03\x04\x05U\xbe'
    
def test_exec_zencode_status():
    mp1 = MP1(DUMMY_TTY)
    zenroom_exit_code, status  = mp1.exec_zencode_status()
    assert mp1.tx_stream == b'\xaaAU\xbe'
