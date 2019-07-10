import json
import base64
import numpy
import array
import random

###################################
# Sender section                  #
###################################


def get_longest_match_ref(search_buffer_value, lookahead_buffer_value):
    # Find longest matching substring in window
    window = str(search_buffer_value) + str(lookahead_buffer_value)
    ref_list = [(0, 0)]
    for i in range(len(search_buffer_value)):
        for j in range(len(lookahead_buffer_value), 0, -1):
            if lookahead_buffer_value.find(window[i: i+j]) > -1:
                ref_list.append((i, j))
    ref_list.sort(key=lambda tup: tup[1], reverse=True)
    # return tuple of (index, length) with the greatest length
    return ref_list[0]


def lempel_ziv(search_buffer_size, lookahead_buffer_size, string):
    # Function implementing the Lempel-Ziv 77 algorithm
    # Initializing search buffer with '0'
    search_buffer_value = search_buffer_size * "0"
    lookahead_buffer_value = string[0:lookahead_buffer_size]
    string = search_buffer_value + string
    # Initializing pointers for Search and Look-ahead buffers
    sb_start = 0
    sb_end = search_buffer_size
    lb_start = search_buffer_size
    lb_end = lb_start + lookahead_buffer_size
    output_list = []
    while len(lookahead_buffer_value) > 0:
        reference = get_longest_match_ref(search_buffer_value, lookahead_buffer_value)
        try:
            output_list.append((reference[0], reference[1], string[sb_end + reference[1]]))
        except:
            print("exception: " + reference)
            break
        sb_start += reference[1] + 1
        sb_end += reference[1] + 1
        lb_start += reference[1] + 1
        lb_end += reference[1] + 1
        search_buffer_value = string[sb_start:sb_end]
        lookahead_buffer_value = string[lb_start:lb_end]
    # Formats lempel-ziv list of tuples to string in order to cast as bytes
    output = ""
    for i in output_list:
        output += str(i[0]) + "," + str(i[1]) + "," + i[2] + "|"
    return output


def inputer(compressed):
    k = int(input("Input table size: "))
    matrix_list = []
    for i in range(k):
        matrix_list.append(input("Input row: "))
    P = []
    for i in range(k):
        temp_list = []
        for j in matrix_list[i]:
            temp_list.append(int(j))
        P.append(temp_list)
    n = int(input("Input word length: "))
    words_list = [compressed[i:i+n] for i in range(0, len(compressed), n)]
    G = PtoG_matrix(P, n)
    for i in range(len(words_list)):
        code_words = DtoC(words_list[i], G)
    noise = int(input("Input noise amount: "))
    counter = 0
    for i in range(len(code_words)):
        for j in range(len(code_words[i])):
            rand = random.randint(0, 1)
            counter = counter + 1
            if rand == 1:
                if code_words[j] == 0:
                    code_words[j] = 1
                else:
                    code_words[j] = 0
                counter = counter + 1
        if counter == noise:
            break


def PtoG_matrix(P, num):
    I = numpy.eye(num)
    G = numpy.concatenate((I, numpy.array(P)), axis=1)
    return G


def DtoC(d, G):
    C = numpy.matmul(d, G)
    C = numpy.mod(C, [2])
    return C



def sender():
    print("Input search buffer size: ")
    search_buffer_size = input()
    print("Input look-ahead buffer size: ")
    lookahead_buffer_size = input()
    print("Input file: ")
    file_name = input()
    file = (file_name, "r")
    lempel_ziv(search_buffer_size, lookahead_buffer_size, file.read())


###################################
# Recipient section               #
###################################

def lz_decoder(search_buffer_size, bytes_for_list):
    string = str(bytes_for_list, 'utf-8')
    tuple_list = []
    temp_list = string.split("|")
    for i in temp_list[:-1]:
        temp = i.split(",")
        tuple_list.append((int(temp[0]), (int(temp[1])), temp[2]))
    output_string = search_buffer_size * "0"
    sb_pointer = 0
    for i in tuple_list:
        for j in range(i[1]):
            output_string += output_string[sb_pointer + i[0] + j]
        output_string += i[2]
        sb_pointer += i[1] + 1
    print(output_string)


def encoder (code):
    encoded = base64.b64encode(code.encode('ascii'))
    return json.dumps({"compression_algorithm": "LZ77", "code": {"name": "linear", "P": "[%s]" % encoded}})


# Program start
if __name__ == "__main__":
    #print(lempel_ziv(9, 9, "001010210210212021021200"))
    #lz_decoder(9, lempel_ziv(9, 9, "001010210210212021021200"))
    inputer('100010010101')
    P = [[0,1,1], [1,0,1], [1,1,0]]
    G = PtoG_matrix(P, 3)
    print(DtoC([0, 0, 1], G))
    print(lempel_ziv(9, 9, "001010210210212021021200"))
    lz_decoder(9, bytearray(lempel_ziv(9, 9, "001010210210212021021200"), encoding='utf-8'))
