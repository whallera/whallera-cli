import argparse
import re
import sys

from lib.mp1 import * 
from lib.discovery import discovery, tty_name
        
def parse_bank_id(string):
    if re.match(r'0[xX][0-9aAbBcCdDeEfF]{2}', string):
        return int(string, base=16)
    return int(string)

def read_stdin():
    r = ""
    for line in sys.stdin:
        r += line 

    return r 

def request_for_confirmation(msg):
    answer = input(msg+" [yes/no]: ")
    if answer.lower() in ["y","yes"]:
        return True 
    elif answer.lower() in ["n","no"]:
        return False
    else:
        return request_for_confirmation("Only yes or no allowed")

def exit_status(status, interactive=True):
    if status == OK:
        if interactive:
            sys.stdout.write("OK")

        sys.exit(0)

    elif status == CHECKSUM_ERROR and interactive:
        sys.stderr.write("Checksum Error")
        
    elif status == DEVICE_LOCKED and interactive:
        sys.stderr.write("Device Locked")
        
    elif status == BANK_LOCKED and interactive:
        sys.stderr.write("Bank Locked")
        
    elif status == BANK_OVERFLOW and interactive:
        sys.stderr.write("Bank Overflow")
        
    elif interactive:
        sys.stderr.write("Unknown Error: %i" % (status))
    
    sys.exit(1)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Whallera CLI')
    
    
    parser.add_argument('--no-interactive', help="Disable interactive mode (don't ask for confirmation)", action="store_false")
    parser.add_argument('--interface', type=str, help=tty_name()+" interface", metavar=(tty_name(),))

    commands = parser.add_mutually_exclusive_group()

    commands.add_argument('--discovery', action="store_true")
    commands.add_argument('--read-bank', type=str, help="Read bank", metavar=("BANK"))
    commands.add_argument('--write-bank', nargs = 2, help="Write bank, use - for stdin", metavar=("BANK", "CONTENT"))
    commands.add_argument('--device-locked', help="Check if device is locked", action="store_true")
    commands.add_argument('--device-lock', help="Lock the device", action="store_true")
    commands.add_argument('--device-unlock', type=int, help="Unlock the device", metavar=("PHRASE"))
    commands.add_argument('--set-phrase', type=int, help="Set phrase", metavar=("PHRASE"))
    commands.add_argument('--operating-mode', type=str, help="Change operating mode: DEVELOPMENT | PROGRAMMING | PRODUCTION", metavar=("OPERATING MODE"))
    commands.add_argument('--factory-reset', help="Factory reset", action="store_true")
    commands.add_argument('--led-conf-set', help="Configure the led: ALWAYS_ON | ALWAYS_OFF | BLINK_ON_ZENCODE | BLINK_ON_SERIAL", metavar=("CONFIG"))
    commands.add_argument('--version', help="Get the version", action="store_true")
    commands.add_argument('--exec-zencode', nargs=5, help="Execute zencode", metavar=("SCRIPT_BANK", "KEYS_BANK", "DATA_BANK", "STDOUT_BANK", "STDERR_BANK"))
    
    args = parser.parse_args()

    if args.discovery:
        print(discovery())
        sys.exit(0)

    if not args.interface:
        #Pick the first discoverable interface
        d = discovery()
        if len(d) > 0:
            interface = d[0]
        else:
            print("error: Connect your Whallera or specify it using --interface")
            sys.exit(1)
    else:
        interface = args.interface

    mp1 = MP1(interface)

    if args.read_bank:
        bank_id = parse_bank_id(args.read_bank)
        bank_content, status = mp1.read_bank(bank_id)
        print(bank_content)
        exit_status(status, args.no_interactive)

    elif args.write_bank:
        if args.no_interactive and not request_for_confirmation("Are you sure to write the bank?"):
            sys.exit(0)


        bank_id = parse_bank_id(args.write_bank[0])
        content = args.write_bank[1]
        if content == '-':
            content = read_stdin()

        status = mp1.write_bank(bank_id, content)

        exit_status(status, args.no_interactive)
        
    elif args.device_locked:
        status = mp1.device_locked()

        exit_status(status, args.no_interactive)

    elif args.device_lock:
        status = mp1.device_lock()

        exit_status(status, args.no_interactive)

    elif args.device_unlock:
        remaining_attempts, status  = mp1.device_unlock(args.device_unlock)
        if status == DEVICE_LOCKED and args.no_interactive:
            sys.stdout.write("%i attempts remaining before factory reset" % (remaining_attempts,))

        exit_status(status, args.no_interactive)

    elif args.set_phrase:
        if args.no_interactive and not request_for_confirmation("Are you sure to set the phrase?"):
            sys.exit(0)
        status = mp1.set_phrase(args.set_phrase)

        exit_status(status, args.no_interactive)

    elif args.operating_mode:
        
        if args.operating_mode == "DEVELOPMENT":
            conf = DEVELOPMENT
        elif args.operating_mode == "PROGRAMMING":
            conf = PROGRAMMING
        elif args.operating_mode == "PRODUCTION":
            conf = PRODUCTION
        else:
            if args.no_interactive:
                sys.stderr.write("%s parameter not allowed" % (args.operating_mode))
            sys.exit(1)

        if args.no_interactive and not request_for_confirmation("Are you sure to change the operating mode?"):
            sys.exit(0)

        status = mp1.operating_mode(conf)

        exit_status(status, args.no_interactive)

    elif args.factory_reset:
        if args.no_interactive and not request_for_confirmation("Are you sure to factory reset?"):
            sys.exit(0)
        status = mp1.factory_reset()

        exit_status(status, args.no_interactive)

    elif args.led_conf_set:

        if args.led_conf_set == "ALWAYS_OFF":
            conf = LED_ALWAYS_OFF
        elif args.led_conf_set == "ALWAYS_ON":
            conf = LED_ALWAYS_ON
        elif args.led_conf_set == "BLINK_ON_ZENCODE":
            conf = LED_BLINK_ON_ZENCODE
        elif args.led_conf_set == "BLINK_ON_SERIAL":
            conf = LED_BLINK_ON_SERIAL
        else:
            if args.no_interactive:
                sys.stderr.write("%s parameter not allowed" % (args.led_conf_set))
            sys.exit(1)
            

        status = mp1.led_conf_set(conf)

        exit_status(status, args.no_interactive)

    elif args.version:
        status = mp1.version()

        exit_status(status, args.no_interactive)

    elif args.exec_zencode:
        script_bank_id = parse_bank_id(args.exec_zencode[0])
        keys_bank_id = parse_bank_id(args.exec_zencode[1])
        data_bank_id = parse_bank_id(args.exec_zencode[2]) 
        stdout_bank_id = parse_bank_id(args.exec_zencode[3]) 
        stderr_bank_id = parse_bank_id(args.exec_zencode[4])

        zenroom_exit_code, status  = mp1.exec_zencode(script_bank_id, keys_bank_id, data_bank_id, stdout_bank_id, stderr_bank_id)

        if args.no_interactive and zenroom_exit_code:
            sys.stdout.write("Zenroom failed with exid code %i\n" % (zenroom_exit_code))

        exit_status(status, args.no_interactive)
    
    else:
        sys.stderr.write("type -h for help!")
        sys.exit(0)

