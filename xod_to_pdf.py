import sys
import os
import zlib
import binascii
import struct
import argparse
from PDFNetPython3.PDFNetPython import PDFDoc, Convert, SDFDoc, PDFNet
from cryptography.hazmat.primitives.ciphers.algorithms import AES


def main(args):
    print("Ola")
    parser = argparse.ArgumentParser(description='Converts password-protected XOD files to PDF files')
    parser.add_argument('xod_file', type=str, help='path to the encrypted XOD file')
    parser.add_argument('password', type=str, help='the password to decrypt the file, in the form of 01-02-03-...')

    args = parser.parse_args()

    # alright.

    fileHandler = open(args.xod_file, "rb")
    password = args.password

    file = bytearray(fileHandler.read())

    new_file = bytearray()
    new_file[:] = file
    centeral_directory_end = file[-22:]
    centeral_directory_location = to_dword(centeral_directory_end[16:16 + 4])
    centeral_directory_size = to_dword(centeral_directory_end[12:12 + 4])
    centeral_directory = file[centeral_directory_location: centeral_directory_location + centeral_directory_size]

    print("[+] file loaded. starting to decrypt the file...")
    while len(centeral_directory) >= 42:
        file_name = centeral_directory[46:46 + to_short(centeral_directory[28:28 + 2])]
        start = to_dword(centeral_directory[42:42 + 4]) + 30 + len(file_name) + to_dword(centeral_directory[30:30 + 4])
        size = to_dword(centeral_directory[20:20 + 4])

        key, iv, encrypted_data = key_and_iv_from_password(str(new_file[start:start + size]), str(file_name), password)
        aes = AES.new(key, AES.MODE_CBC, iv)
        print("[+] decrypting part " + file_name + " with key " + toHex(key))
        decrypted_data = aes.decrypt(encrypted_data)

        new_centeral_directory_index = fix_offsets(new_file, file_name, len(decrypted_data))
        del new_file[start:start + size]
        new_file[start:start] = bytearray(decrypted_data)
        centeral_directory = new_file[new_centeral_directory_index:]
        if centeral_directory[0] != 0x50:
            print("problem")
            break
        file_header_size = 46 + len(file_name) + to_short(centeral_directory[30:30 + 2]) + to_short(
            centeral_directory[32:32 + 2])
        centeral_directory = centeral_directory[file_header_size:]

    print("[+] everything decrypted. converting to pdf...")
    new_file_handler = open("new.xod", "wb")
    new_file_handler.write(new_file)
    new_file_handler.close()
    toPdf("new.xod", "result.pdf")
    os.remove("new.xod")
    print("[+] Done!")


# some helper functions

def toPdf(xodFilename, outputPdfName):
    PDFNet.Initialize()
    pdf_doc = PDFDoc()
    Convert.ToPdf(pdf_doc, xodFilename)
    pdf_doc.Save(outputPdfName, SDFDoc.e_remove_unused)
    pdf_doc.Close()


def toXod(pdfFilename, outputXodName):
    pdf_doc = PDFDoc()
    Convert.ToXod(pdfFilename, outputXodName)


def toHex(byte_array):
    if byte_array is str:
        byte_array = bytearray(byte_array)
    hex = str(binascii.hexlify(byte_array))
    formatted_hex = ':'.join(hex[i:i + 2] for i in range(0, len(hex), 2))
    return formatted_hex


def to_dword(byte_array):
    return struct.unpack('I', byte_array)[0]


def to_short(byte_array):
    return struct.unpack('H', byte_array)[0]


def key_and_iv_from_password(encrypted_data, filename, password):
    key = bytearray([0] * 16)
    for i in range(16):
        key[i] = i
        if i < len(password):
            key[i] |= ord(password[i])
        g = len(filename) + i - 16
        if 0 <= g:
            key[i] |= ord(filename[g])

    iv = []
    for i in range(16):
        iv.append(encrypted_data[i])
    encrypted_data = encrypted_data[16:]

    return (str(key), str(bytearray(iv)), encrypted_data)


def fix_offsets(array, alterted_filename, new_size):
    centeral_directory_end = array[-22:]
    centeral_directory_location = to_dword(centeral_directory_end[16:16 + 4])
    centeral_directory_size = to_dword(centeral_directory_end[12:12 + 4])
    file_offset_from_centeral_directory = 0
    index = 0
    offset_fix_delta = 0

    # fixing the alterted-file's local header
    while index < centeral_directory_location:
        file_name = array[index + 30: index + 30 + to_short(array[index + 26:index + 26 + 2])]
        if file_name == alterted_filename:
            offset_fix_delta = new_size - to_dword(array[index + 18:index + 18 + 4])
            array[index + 18:index + 18 + 4] = struct.pack('I', new_size)
            break
        index += 30 + len(file_name) + to_short(array[index + 28:index + 28 + 2]) + to_dword(
            array[index + 18:index + 18 + 4])

    # fixing the centeral directory
    index = centeral_directory_location
    should_fix_offset = False
    while index < centeral_directory_location + centeral_directory_size:
        file_name = array[index + 46:index + 46 + to_short(array[index + 28:index + 28 + 2])]
        if file_name == alterted_filename:
            should_fix_offset = True
            array[index + 20:index + 20 + 4] = struct.pack('I', new_size)
            file_offset_from_centeral_directory = index - centeral_directory_location
        elif should_fix_offset:
            array[index + 42:index + 42 + 4] = struct.pack('I', to_dword(
                array[index + 42:index + 42 + 4]) + offset_fix_delta)
        file_header_size = 46 + len(file_name) + to_short(array[index + 30:index + 30 + 2]) + to_short(
            array[index + 32:index + 32 + 2])
        index += file_header_size

    array[-6:-6 + 4] = struct.pack('I', to_dword(array[-6:-6 + 4]) + offset_fix_delta)
    return to_dword(array[-6:-6 + 4]) + file_offset_from_centeral_directory


if __name__ == "__main__":
    main(sys.argv)