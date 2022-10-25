"""

- NOTE: REPLACE 'N' Below with your section, year, and lab number
- CS2911 - 011
- Fall 2022
- Lab 6 - TFTP Server
- Names:
  - Hudson Arney
  - Josh Sopa

A Trivial File Transfer Protocol Server

Introduction: (Describe the lab in your own words):
We look to develop a TFTP server which uses a UDP connection (sending only one byte at a time)
from a file block. We first parse the request of the given message which contains the opcode, filename, and
transfer type. Then depending upon if the filename is valid within the project we will look to send that file to the
server. If the file is valid we will send one byte at a time to the server and have the server send back an
acknowledgement message. If the file is not valid we will display an error message.




Summary: (Summarize your experience with the lab, what you learned, what you liked,what you disliked,
and any suggestions you have for improvement)
We again enjoyed this lab as it offered another chance for us to explore a unique protocol which
was challenging but fair. We learned how a TFTP header works and what happens when errors occur and how to
send acknowledgement messages once the data has been received. We liked breaking up the TFTP example
we got from wireshark and how to get the specific parts of the message. We disliked the debugging process for the lab
which took the majority of our time. We suggest that for the lab, in class lectures we go over TFTP slightly more.
Much of our information was obtained from the RFC.




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

    print("Server is ready to receive a request")

    ####################################################
    # Your code starts here                            #
    #   Be sure to design and implement additional     #
    #   functions as needed                            #
    ####################################################

    client_socket = socket_setup()
    (tempVal, sourceAddress) = client_socket.recvfrom(MAX_UDP_PACKET_SIZE)
    print("tempVal: ")
    print(tempVal)
    request = parse_request(tempVal)
    if valid_file(request['file_name']):
        error_code = -1
        block_number = 1
        while block_number <= get_file_block_count(request['file_name']):
            response = send_response(client_socket, error_code, request['file_name'], block_number)
            client_socket.sendto(response, sourceAddress)
            (ack, sourceAddress) = client_socket.recvfrom(MAX_UDP_PACKET_SIZE)
            if get_op_code(ack) == 5:
                print(send_response(client_socket, 5, request['file_name'], block_number))
                block_number = get_file_block_count(request['file_name'])
            else:
                block_number = int.from_bytes(get_block_num(ack), 'big') + 1
    else:
        response = send_response(client_socket, 1, request['file_name'], 1)
        client_socket.sendto(response, sourceAddress)

    ####################################################
    # Your code ends here                              #
    ####################################################

    client_socket.close()


def send_response(udp_socket, error_code, file_name, block_number):
    """
    Prepare and sends a response message to the client
    :param udp_socket: the socket to be sent to
    :param error_code: the error code if there is one
    :file the file to being requested
    :return: if the message was sent
    """
    message = b''
    if error_code == -1:
        message += create_op_code(3)
        message += create_block_number(block_number)
        message += get_file_block(file_name, block_number)
    else:
        message += generate_error(error_code)
    return message


def create_op_code(code):
    """
    creates an opcode two bytes in length
    :param code: the op code assigned in the main
    :return: the op code
    """
    return code.to_bytes(2, 'big')


def create_block_number(number):
    """
    creates a block number two bytes in length
    :param number: the block number assigned in the main
    :return: the block number
    """
    return number.to_bytes(2, 'big')


# def create_data(data):

def generate_error(error_code):
    message = b'\x00\x05'
    message += error_code.to_bytes(2, 'big')

    errors = {'0': b'Not defined, see error message (if any).',
              '1': b'File not found.',
              '2': b'Access violation.',
              '3': b'Disk full or allocation exceeded.',
              '4': b'Illegal TFTP operation.',
              '5': b'Unknown transfer ID.',
              '6': b'File already exists.',
              '7': b'No such user.'}
    message += errors[str(error_code)]
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


def valid_file(filename):
    """
    checks if the file requested exists
    :param filename: the source file within the message
    :return: a bool if the file is within the project or not
    """
    return filename == b'msoe.png' or filename == b'index.html' \
           or filename == b'styles.css'


def get_block_num(message):
    return message[2:4]


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

def parse_request(message):
    """
    parse request takes in the message which contains the opcode, file name,
    and transfer type. It splits these sections up based on their characteristics
    shown from the RFC and returns a dictionary of the three
    :param message: the message which contains the opcode, file name, and transfer type.
    :return: a dictionary of the three received parts of the message
    """
    op_code = get_op_code(message)
    # manipulates the message by getting rid of the op code bytes
    message = message.replace(op_code, b'')

    source_file = get_source_file(message)
    # manipulates the message by getting rid of the source file bytes
    message = message.replace(source_file + b'\x00', b'')

    transfer_type = get_type(message)
    request_dict = {'opcode': op_code,
                    'file_name': source_file,
                    'type': transfer_type}
    return request_dict


def get_op_code(message):
    """
    gets the first two bytes of the message which must be the op code
    :param message: the initial message with all 3 parts
    :return: those first two bytes (The op code)
    """
    op_code = message[0:2]
    print("opcode: ")
    print(op_code)
    print()
    return op_code


def get_type(message):
    """
    reads the message until a b'\x00' is found where it stops and returns the type
    :param message: The initial message minus the opcode and file name
    :return: the transfer type which is the last part of the message
    """
    print("message in get_type: ")
    print(message)
    transfer_type = b''

    index = 0
    while message[index].to_bytes(1, 'big') != b'\x00':
        transfer_type += message[index].to_bytes(1, 'big')
        index += 1
    print("transfer type: ")
    print(transfer_type)
    print()
    return transfer_type


def get_source_file(message):
    """
    reads the message until a b'\x00' is found where it stops and returns the type
    :param message: The initial message minus the opcode
    :return: the file name which is the middle part of the message
    """
    source_file = b''
    print("message in get_source_file: ")
    print(message)
    index = 0
    while message[index].to_bytes(1, 'big') != b'\x00':
        source_file += message[index].to_bytes(1, 'big')
        index += 1

    print("source file: ")
    print(source_file)
    print()
    return source_file


main()
