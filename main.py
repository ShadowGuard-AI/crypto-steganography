import argparse
import logging
from PIL import Image
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_key(password, salt):
    """Generates a strong encryption key from a password and salt using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # Key length (256 bits)
        salt=salt,
        iterations=390000,  # Recommended iteration count
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def _write_bits(pixels, width, pixel_index, binary):
    """Write one bit per pixel starting at pixel_index; returns the next index.

    The channel cycles red, green, blue by the bit position inside this
    segment, and each segment (salt, length, payload) restarts the cycle
    at red. Extraction restarts the same way, so the two sides agree
    only because both treat segments independently; merging the
    segments into one continuous bit stream would break old images.
    """
    for i, bit in enumerate(binary):
        x = pixel_index % width
        y = pixel_index // width
        r, g, b = pixels[x, y]
        if i % 3 == 0:
            r = (r & ~1) | int(bit)
        elif i % 3 == 1:
            g = (g & ~1) | int(bit)
        else:
            b = (b & ~1) | int(bit)
        pixels[x, y] = (r, g, b)
        pixel_index += 1
    return pixel_index


def _read_bits(pixels, width, pixel_index, count):
    """Read count bits written by _write_bits; returns (bits, next index)."""
    bits = ""
    for i in range(count):
        x = pixel_index % width
        y = pixel_index // width
        r, g, b = pixels[x, y]
        if i % 3 == 0:
            bits += str(r & 1)
        elif i % 3 == 1:
            bits += str(g & 1)
        else:
            bits += str(b & 1)
        pixel_index += 1
    return bits, pixel_index


def encrypt_message(message, key):
    """Encrypts a message using Fernet symmetric encryption."""
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    return encrypted_message

def decrypt_message(encrypted_message, key):
    """Decrypts a message using Fernet symmetric encryption."""
    f = Fernet(key)
    try:
        decrypted_message = f.decrypt(encrypted_message).decode()
        return decrypted_message
    except Exception as e:
        logging.error(f"Decryption failed: {e}")
        return None

def hide_message(image_path, message, password):
    """Hides a message within an image using LSB steganography with encryption."""
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")  # Ensure the image is in RGB format

        # Generate a random salt for key derivation
        salt = os.urandom(16)

        # Generate the encryption key
        key = generate_key(password, salt)

        # Encrypt the message
        encrypted_message = encrypt_message(message, key)

        binary_message = ''.join(format(byte, '08b') for byte in encrypted_message)
        message_len = len(binary_message)

        # Check if the image is large enough to hide the message.
        # Encoding stores one bit per pixel, plus a 128 bit salt and a
        # 32 bit length header, so capacity is width * height bits total.
        width, height = img.size
        if 128 + 32 + message_len > width * height:
            raise ValueError("Image is not large enough to hide the message.")

        pixels = img.load()
        pixel_index = 0

        # Three segments in a fixed order: salt, length, payload. The
        # reader below depends on both the order and the sizes.
        salt_binary = ''.join(format(byte, '08b') for byte in salt)
        pixel_index = _write_bits(pixels, width, pixel_index, salt_binary)
        len_binary = bin(message_len)[2:].zfill(32)
        pixel_index = _write_bits(pixels, width, pixel_index, len_binary)
        _write_bits(pixels, width, pixel_index, binary_message)

        # Save the modified image. Always save as PNG: lossy formats such
        # as JPEG recompress the pixels and destroy the hidden LSB data.
        new_image_path = "hidden_" + os.path.splitext(os.path.basename(image_path))[0] + ".png"
        img.save(new_image_path, format="PNG")
        logging.info(f"Message hidden successfully. Image saved as {new_image_path}")
        return new_image_path

    except FileNotFoundError:
        logging.error("Image file not found.")
    except ValueError as e:
        logging.error(f"Error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    return None



def extract_message(image_path, password):
    """Extracts a hidden message from an image using LSB steganography and decrypts it."""
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")  # Ensure the image is in RGB format
        pixels = img.load()
        width, height = img.size

        pixel_index = 0
        extracted_salt_binary, pixel_index = _read_bits(pixels, width, pixel_index, 128)
        salt = bytes([int(extracted_salt_binary[i:i+8], 2) for i in range(0, len(extracted_salt_binary), 8)])

        extracted_len_binary, pixel_index = _read_bits(pixels, width, pixel_index, 32)
        message_len = int(extracted_len_binary, 2)
        if message_len == 0 or message_len > width * height - pixel_index:
            logging.error("No valid hidden message found, or the image data is corrupted.")
            return None

        extracted_binary_message, pixel_index = _read_bits(pixels, width, pixel_index, message_len)

        encrypted_message = bytes([int(extracted_binary_message[i:i+8], 2) for i in range(0, len(extracted_binary_message), 8)])


        # Generate key using the extracted salt
        key = generate_key(password, salt)

        # Decrypt the message
        decrypted_message = decrypt_message(encrypted_message, key)

        if decrypted_message:
            logging.info("Message extracted successfully.")
            return decrypted_message
        else:
            logging.error("Failed to decrypt message.  Incorrect password or corrupted data.")
            return None

    except FileNotFoundError:
        logging.error("Image file not found.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    return None


def setup_argparse():
    """Sets up the argument parser for the command-line interface."""
    parser = argparse.ArgumentParser(description="Hide and extract text within image files using LSB steganography with encryption.")
    subparsers = parser.add_subparsers(dest='mode', help='Mode of operation')

    # Hide mode
    hide_parser = subparsers.add_parser('hide', help='Hide a message within an image')
    hide_parser.add_argument('image', help='Path to the image file')
    hide_parser.add_argument('message', help='Message to hide')
    hide_parser.add_argument('password', help='Password for encryption')

    # Extract mode
    extract_parser = subparsers.add_parser('extract', help='Extract a message from an image')
    extract_parser.add_argument('image', help='Path to the image file')
    extract_parser.add_argument('password', help='Password for decryption')

    return parser


def main():
    """Main function to parse arguments and execute the chosen operation."""
    parser = setup_argparse()
    args = parser.parse_args()

    if args.mode == 'hide':
        image_path = args.image
        message = args.message
        password = args.password

        if not os.path.isfile(image_path):
            logging.error("Image file not found.")
            sys.exit(1)

        # hide_message reports failure by returning None; that used to
        # fall through to a normal exit, so a failed hide looked done.
        if hide_message(image_path, message, password) is None:
            sys.exit(1)


    elif args.mode == 'extract':
        image_path = args.image
        password = args.password

        if not os.path.isfile(image_path):
            logging.error("Image file not found.")
            sys.exit(1)

        extracted_message = extract_message(image_path, password)
        if extracted_message:
            print("Extracted message:", extracted_message)
        else:
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()


