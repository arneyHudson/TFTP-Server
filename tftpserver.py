"""
- NOTE: REPLACE 'N' Below with your section, year, and lab number
- CS2911 - 011
- Fall 2022
- Lab 6 - TFTP Server
- Names:
  - Hudson Arney
  - Josh Sopa

A Trivial File Transfer Protocol Server

Introduction: (Describe the lab in your own words)




Summary: (Summarize your experience with the lab, what you learned, what you liked,what you disliked, and any suggestions you have for improvement)





"""

import socket
import os
import math

# Helpful constants used by TFTP
TFTP_PORT = 69
TFTP_BLOCK_SIZE = 512
MAX_UDP_PACKET_SIZE = 65536


def main():
    """
    Processes a single TFTP request
    """

    client_socket = socket_setup()

    print("Server is ready to receive a request")

    ####################################################
    # Your code starts here                            #
    #   Be sure to design and implement additional     #
    #   functions as needed                            #
    ####################################################

    socket = socket_setup()
    file = open('file_name', 'r')
    blocks = dict
    for x in range(1, get_file_block_count(file) + 1):
        blocks[x] = get_file_block(file, x)

    block_number = 1
    send_response(socket, -1, blocks, block_number)

    ####################################################
    # Your code ends here                              #
    ####################################################

    client_socket.close()


def send_response(udp_socket, error_code, blocks, block_number):
    """
    Prepare and sends a response message to the client
    :param udp_socket: the socket to be sent to
    :param error_code: the error code if there is one
    :file the file to being requested
    :return: if the message was sent
    """
    message = b''
    if error_code != -1:
        message += create_op_code(b'\x03')
        message += create_block_number(block_number)
        message += blocks.get(block_number)
    else:
        message += generate_error()
    return udp_socket.sendTo(message)


def create_op_code(code):
    return b'\x00' + code


def create_block_number(number):
    return number.to_bytes('2', 'big')


# def create_data(data):

def generate_error(error_code):
    message = b'\x00\x05'
    message += error_code.to_bytes('2', 'big')
    errors = {'0': b'Not defined, see error message (if any).',
              '1': b'File not found.',
              '2': b'Access violation.',
              '3': b'Disk full or allocation exceeded.',
              '4': b'Illegal TFTP operation.',
              '5': b'Unknown transfer ID.',
              '6': b'File already exists.',
              '7': b'No such user.'}
    message += errors.get(error_code)
    message += b'\x00'
    return message


# def parse_ack(bytes):

def get_file_block_count(filename):
    """
    Determines the number of TFTP blocks for the given file
    :param filename: THe name b,of the file
    :return: The number of TFTP blocks for the file or -1 if the file does not exist
    """
    try:
        # Use the OS call to get the file size
        #   This function throws an exception if the file doesn't exist
        file_size = os.stat(filename).st_size
        return math.ceil(file_size / TFTP_BLOCK_SIZE)
    except:
        return -1


def get_file_block(filename, block_number):
    """
    Get the file block data for the given file and block number
    :param filename: The name of the file to read
    :param block_number: The block number (1 based)
    :return: The data contents (as a bytes object) of the file block
    """
    # Open the file for reading
    file = open(filename, 'rb')
    block_byte_offset = (block_number - 1) * TFTP_BLOCK_SIZE
    file.seek(block_byte_offset)

    # Read and return the block
    block_data = file.read(TFTP_BLOCK_SIZE)
    file.close()
    return block_data


def put_file_block(filename, block_data, block_number):
    """
    Writes a block of data to the given file
    :param filename: The name of the file to save the block to
    :param block_data: The bytes object containing the block data
    :param block_number: The block number (1 based)
    :return: Nothing
    """
    # Try to create the file if it doesn't exist
    try:
        with open(filename, 'x') as f:
            pass
    except FileExistsError:
        pass

    # Open the file for updating
    file = open(filename, 'r+b')
    block_byte_offset = (block_number - 1) * TFTP_BLOCK_SIZE
    file.seek(block_byte_offset)

    # Write and close the file
    file.write(block_data)
    file.close()


def socket_setup():
    """
    Sets up a UDP socket to listen on the TFTP port
    :return: The created socket
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', TFTP_PORT))
    return s


####################################################
# Write additional helper functions starting here  #
####################################################

def parse_request(udp_socket, file_path):
    """

    :param file_path:
    :param udp_socket:
    :return:
    """
    if validate_file(file_path):
        request = get_op_code(udp_socket)
        request += get_type(udp_socket)
        request += get_source_file(udp_socket)
        return request
    else:
        print("Can't Parse Request")


def get_op_code(message):
    op_code = b''
    for x in range(4):
        op_code += message.recvfrom(MAX_UDP_PACKET_SIZE)
    print(int(op_code.decode()))
    return op_code


def get_type(message):
    """
    :param message:
    :return:
    """
    transfer_type = b''
    data = message.recvfrom(MAX_UDP_PACKET_SIZE)
    while data != '0':
        transfer_type += data
        data = message.recvfrom(MAX_UDP_PACKET_SIZE)

    print(transfer_type.decode())
    return transfer_type


def get_source_file(message):
    """

    :param message:
    :return:
    """
    source_file = b''
    data = message.recvfrom(MAX_UDP_PACKET_SIZE)
    while data != '0':
        source_file += data
        data = message.recvfrom(MAX_UDP_PACKET_SIZE)
    print(source_file.decode())
    return source_file


def validate_file(file_path):
    """

    :param file_path:
    :return:
    """
    valid_file = False
    try:
        if get_file_block_count(file_path) > 0:
            valid_file = True
            print("File is valid")
    except valid_file:
        print("File is not valid")
    finally:
        return valid_file


main()
