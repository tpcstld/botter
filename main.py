from typing import Collection, List
from io import IOBase
import functools
import time
import sys
import os
import random

DEBUG = False
REPEAT = True

NULL_CHAR = chr(0)
EMPTY_BYTE = 0

keys_to_value = {
    'a': 0x04,
    'b': 0x05,
    'c': 0x06,
    'd': 0x07,
    'e': 0x08,
    'f': 0x09,
    'g': 0x0A,
    'h': 0x0B,
    'i': 0x0C,
    'j': 0x0D,
    'k': 0x0E,
    'l': 0x0F,
    'm': 0x10,
    'n': 0x11,
    'o': 0x12,
    'p': 0x13,
    'q': 0x14,
    'r': 0x15,
    's': 0x16,
    't': 0x17,
    'u': 0x18,
    'v': 0x19,
    'w': 0x1A,
    'x': 0x1B,
    'y': 0x1C,
    'z': 0x1D,
    '1': 0x1E,
    '2': 0x1F,
    '3': 0x20,
    '4': 0x21,
    '5': 0x22,
    '6': 0x23,
    '7': 0x24,
    '8': 0x25,
    '9': 0x26,
    '0': 0x27,
    'SPACE': 0x2C,
    '-': 0x2D,
    '=': 0x2E,
    '[': 0x2F,
    ']': 0x30,
    ';': 0x33,
    "'": 0x34,
    ',': 0x36,
    '.': 0x37,
    '/': 0x38,
    'f1': 0x3A,
    'f2': 0x3B,
    'f3': 0x3C,
    'f4': 0x3D,
    'f5': 0x3E,
    'Key.insert': 0x49,
    'Key.home': 0x4A,
    'Key.page_up': 0x4B,
    'Key.delete': 0x4C,
    'Key.end': 0x4D,
    'Key.page_down': 0x4E,
    'Key.left': 0x50,
    'Key.right': 0x4F,
    'Key.up': 0x52,
    'Key.down': 0x51,
}

control_chars_to_value = {
    'Key.ctrl_l': 0b00000001,
    'Key.shift': 0b00000010,
    'Key.alt_l': 0b00000100,
    'Key.ctrl_r': 0b00001000,
    'Key.shift_r': 0b00010000,
    'Key.alt_gr': 0b00100000,
}

def sleep(millis: int) -> None:
    start = time.perf_counter() * 1000
    target = start + millis
    while time.perf_counter() * 1000 < target:
        pass

# Given a set of Key characters, return the 8 byte code defined here: https://usb.org/sites/default/files/hut1_3_0.pdf
# on page 88
def get_byte_code(key_characters: Collection[str]) -> bytearray:
    control_values_in_list = [control_chars_to_value[key] for key in key_characters if key in control_chars_to_value.keys()]
    modifier_byte = functools.reduce(lambda x, y: x ^ y, control_values_in_list, 0)

    key_values_in_list = [keys_to_value[key] for key in key_characters if key in keys_to_value.keys()]
    # truncate to the first 6 keys
    key_values_in_list = key_values_in_list[:6]
    key_bytes = bytearray([modifier_byte] + [EMPTY_BYTE] + key_values_in_list + [EMPTY_BYTE] * (6 - len(key_values_in_list)))
    return key_bytes


class KeyTracker(object):

    def __init__(self):
        self.active_keys: List[str] = []

    def handle_event(self, fd: IOBase, character: str, pressed: bool, duration_milliseconds: int = 100):
        sleep(duration_milliseconds)

        if pressed and character not in self.active_keys:
            self.active_keys.append(character)
        elif not pressed and character in self.active_keys:
            self.active_keys.remove(character)

        packet = get_byte_code(self.active_keys)
        fd.write(packet)
        fd.flush()

    def stop(self, fd: IOBase):
        self.active_keys = []

        packet = get_byte_code(self.active_keys)
        fd.write(packet)
        fd.flush()


def main():
    os.nice(-19)
    i = 0
    args = sys.argv
    file_name = "data.txt"
    if len(args) > 1:
        files = args[1:]
    
    file_queue = files.copy()

    while True:
        tracker = KeyTracker()

        if not file_queue:
            random.shuffle(files)
            file_queue = files.copy()
        file_name = file_queue.pop()

        with open(file_name, 'r') as sequence_file:
            key_sequence = sequence_file.readlines()

        j = 0

        with open('/dev/hidg0', 'rb+') as fd:
        # with open('test', 'wb') as fd:
            try:
                for line in key_sequence:
                    j = j + 1
                    [action, key, wait_millis] = line.split(',')
                    tracker.handle_event(fd, key, action == 'Press', int(wait_millis))
            finally:
                    tracker.stop(fd)

        if not REPEAT:
            break
        else:
            print("repeated", i)
            i = i + 1


if __name__ == '__main__':
    main()