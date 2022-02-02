from lib.mp1 import * 

if __name__ == "__main__":

    mp1 = MP1()

    print("READ_BANK")
    bank_content, status = mp1.read_bank(0x00)
    print(bank_content, status)

    print("WRITE_BANK")
    status = mp1.write_bank(0x00, "ciao")
    print(status)
    

    print("DEVICE_LOCKED")
    status = mp1.device_locked()
    print(status)
    

    print("DEVICE_LOCK")
    status = mp1.device_lock()
    print(status)
    

    print("DEVICE_UNLOCK")
    remaining_attempts, status  = mp1.device_unlock(1234)
    print(remaining_attempts, status )
    

    print("SET_PHRASE")
    status = mp1.set_phrase(1234)
    print(status)
    

    print("OPERATING_MODE")
    status = mp1.operating_mode(DEVELOPMENT)
    print(status)
    

    print("FACTORY_RESET")
    status = mp1.factory_reset()
    print(status)
    

    print("LED_CONF_SET")
    status = mp1.led_conf_set(LED_ALWAYS_OFF)
    print(status)
    

    print("VERSION")
    UDID, firmware_version, zenroom_version, status = mp1.version()
    print(UDID, firmware_version, zenroom_version, status)
    

    print("EXEC_ZENCODE")
    zenroom_exit_code, status  = mp1.exec_zencode(0x01, 0x02, 0x03, 0x04, 0x05)
    print(zenroom_exit_code, status )
    

    print(calc_checksum(b'\x01\x00\x23\x00'))