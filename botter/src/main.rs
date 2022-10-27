use std::{io::Write, time::{Instant, Duration}};
use phf::phf_map;


const EMPTY_BYTE: u8 = 0;

static KEYS_TO_VALUE: phf::Map<&'static str, u8> = phf_map! {
    "a" => 0x04,
    "b" => 0x05,
    "c" => 0x06,
    "d" => 0x07,
    "e" => 0x08,
    "f" => 0x09,
    "g" => 0x0A,
    "h" => 0x0B,
    "i" => 0x0C,
    "j" => 0x0D,
    "k" => 0x0E,
    "l" => 0x0F,
    "m" => 0x10,
    "n" => 0x11,
    "o" => 0x12,
    "p" => 0x13,
    "q" => 0x14,
    "r" => 0x15,
    "s" => 0x16,
    "t" => 0x17,
    "u" => 0x18,
    "v" => 0x19,
    "w" => 0x1A,
    "x" => 0x1B,
    "y" => 0x1C,
    "z" => 0x1D,
    "1" => 0x1E,
    "2" => 0x1F,
    "3" => 0x20,
    "4" => 0x21,
    "5" => 0x22,
    "6" => 0x23,
    "7" => 0x24,
    "8" => 0x25,
    "9" => 0x26,
    "0" => 0x27,
    "SPACE" => 0x2C,
    "-" => 0x2D,
    "=" => 0x2E,
    "[" => 0x2F,
    "]" => 0x30,
    ";" => 0x33,
    "'" => 0x34,
    "," => 0x36,
    "." => 0x37,
    "/" => 0x38,
    "f1" => 0x3A,
    "f2" => 0x3B,
    "f3" => 0x3C,
    "f4" => 0x3D,
    "f5" => 0x3E,
    "Key.insert" => 0x49,
    "Key.home" => 0x4A,
    "Key.page_up" => 0x4B,
    "Key.delete" => 0x4C,
    "Key.end" => 0x4D,
    "Key.page_down" => 0x4E,
    "Key.left" => 0x50,
    "Key.right" => 0x4F,
    "Key.up" => 0x52,
    "Key.down" => 0x51,
};

static CONTROL_CHARS_TO_VALUE: phf::Map<&'static str, u8> = phf_map! {
    "Key.ctrl_l" => 0b00000001,
    "Key.shift" => 0b00000010,
    "Key.alt_l" => 0b00000100,
    "Key.ctrl_r" => 0b00001000,
    "Key.shift_r" => 0b00100000,
    "Key.alt_gr" => 0b00100000,
};

fn get_byte_code(characters: &Vec<String>) -> [u8; 8] {
    let control_values_in_list: Vec<u8> = characters.iter()
        .map(|character| CONTROL_CHARS_TO_VALUE.get(character))
        .flatten()
        .map(|x| x.clone())
        .collect();
    let modifer_byte: u8 = control_values_in_list.into_iter()
        .reduce(|accum, item| accum ^ item)
        .unwrap_or(0);

    let key_values_in_list: Vec<u8> = characters.iter()
        .map(|character| KEYS_TO_VALUE.get(character))
        .flatten()
        .map(|x| x.clone())
        .take(6)
        .collect();

    [
        modifer_byte,
        EMPTY_BYTE,
        key_values_in_list.get(0).map(|x| x.clone()).unwrap_or(0),
        key_values_in_list.get(1).map(|x| x.clone()).unwrap_or(0),
        key_values_in_list.get(2).map(|x| x.clone()).unwrap_or(0),
        key_values_in_list.get(3).map(|x| x.clone()).unwrap_or(0),
        key_values_in_list.get(4).map(|x| x.clone()).unwrap_or(0),
        key_values_in_list.get(5).map(|x| x.clone()).unwrap_or(0),
    ]
}

fn sleep(millis: u64) {
    let start = Instant::now();
    let duration = Duration::from_millis(millis);
    while start.elapsed() < duration {
        std::hint::spin_loop();
    }
}

struct KeyTracker<'a> {
    active_keys: Vec<String>,
    fd: &'a mut std::fs::File,
}

impl<'a> KeyTracker<'a> {
    fn new(fd: &'a mut std::fs::File) -> KeyTracker<'a> {
        KeyTracker {
            active_keys: vec![],
            fd
        }
    }

    fn handle_event(&mut self, key: String, pressed: bool, wait_millis: u64) {
        sleep(wait_millis);

        if pressed && !self.active_keys.contains(&key) {
            self.active_keys.push(key);
        } else if !pressed && self.active_keys.contains(&key) {
            let index = self.active_keys.iter().position(|x| *x == key).unwrap();
            self.active_keys.remove(index);
        }

        self.write_keys();
    }

    fn stop(&mut self) {
        self.active_keys.clear();
        self.write_keys();
    }

    fn write_keys(&mut self) {
        let packet = get_byte_code(&self.active_keys);
        self.fd.write(&packet).expect("Error writing keypress.");
        self.fd.flush().expect("Error flushing keypress.");
    }
}

impl<'a> Drop for KeyTracker<'a> {
    fn drop(&mut self) {
        self.stop();
    }
}

fn main() {
    let data_file = std::env::args().nth(1).expect("No data file");
    let repeat: bool = std::env::args().nth(2).map(|x| x.parse()).unwrap_or(Result::Ok(false)).unwrap_or(false);
    let output = std::env::args().nth(3).unwrap_or("/dev/hidg0".to_string());

    loop {
        let contents = std::fs::read_to_string(data_file.as_str())
            .expect("Cannot read file");

        let mut fd = std::fs::OpenOptions::new().write(true).open(output.as_str())
            .expect("Cannot open device file.");

        let mut tracker = KeyTracker::new(&mut fd);

        for line in contents.lines() {
            let info: Vec<&str> = line.split(",").collect();
            assert!(info.len() == 3);

            let pressed = info[0] == "Press";
            let key = info[1].to_string();
            let wait_millis = info[2].parse().expect("Cannot parse wait time");

            tracker.handle_event(key, pressed, wait_millis);
        }

        if !repeat {
            break;
        }
    }
}
