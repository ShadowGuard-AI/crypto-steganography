# crypto-steganography

A command line tool that hides text inside an image file and extracts it again, using least significant bit (LSB) steganography. The text is encrypted before it is hidden.

## How it works

- A random 16 byte salt is generated for each hide operation.
- A 256 bit key is derived from the password and the salt with PBKDF2-HMAC-SHA256 (390000 iterations).
- The message is encrypted with Fernet (from the `cryptography` package).
- The salt (128 bits), the encrypted message length (32 bits), and the encrypted message are written one bit per pixel into the least significant bits of the image, in that order.
- Extraction reads the salt and length back, derives the same key from the supplied password, and decrypts the message.

## Requirements

- Python 3
- Pillow and cryptography, listed in `requirements.txt`

## Install

```bash
git clone https://github.com/ShadowGuard-AI/crypto-steganography.git
cd crypto-steganography
pip install -r requirements.txt
```

## Usage

Hide a message:

```bash
python3 main.py hide test.png "hello secret world" mypassword
```

This writes `hidden_test.png` in the current directory and logs `Message hidden successfully. Image saved as hidden_test.png`.

Extract a message:

```bash
python3 main.py extract hidden_test.png mypassword
```

On success this prints, for the example above:

```text
Extracted message: hello secret world
```

Show help:

```bash
python3 main.py --help
python3 main.py hide --help
python3 main.py extract --help
```

## Parameters

- `hide <image> <message> <password>`: hide `message` in `image`, protected by `password`.
- `extract <image> <password>`: extract the hidden message from `image` using `password`.
- `-h`, `--help`: show help and exit.

## Limitations

- Output is always saved as a PNG file named `hidden_<original base name>.png` in the current directory, whatever the input format was. PNG is required because lossy formats such as JPEG recompress pixels and destroy the hidden data. Extract from the PNG output, not from a JPEG copy of it.
- Capacity is one bit per pixel, minus a 160 bit header (salt plus length). A 200 by 200 pixel image therefore holds at most 39840 bits, about 4980 bytes, of encrypted data, and the Fernet token is larger than the plain message. Hiding into an image that is too small logs `Error: Image is not large enough to hide the message.` and writes no output file.
- A wrong password logs a decryption failure and prints no extracted message.
- Extracting from an image that contains no valid hidden message logs an error and prints no extracted message.
- There are no bundled tests. The hide and extract round trip above was verified by hand.

## License

Copyright (c) ShadowStrikeHQ
