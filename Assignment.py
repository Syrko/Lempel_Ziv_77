import json
import base64
import numpy
import random

###################################
# Sender section                  #
###################################

# Global Variables
lookahead_buffer_size = 0
search_buffer_size = 0


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
    search_buffer_size = int(search_buffer_size)
    lookahead_buffer_size = int(lookahead_buffer_size)
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


def linear_code(compressed):
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
    print(compressed)
    print(words_list)
    code_words = []
    G = PtoG_matrix(P, n)
    for i in words_list:
        code_words.append(DtoC(i, G))
    noise = int(input("Input noise amount: "))
    for i in range(len(code_words)):
        counter = 0
        for j in range(len(code_words[i])):
            rand = random.randint(0, 1)
            if rand == 1:
                if code_words[i][j] == 0:
                    code_words[i][j] = 1
                else:
                    code_words[i][j] = 0
                counter = counter + 1
            if counter == noise:
                break
    output = ""
    for i in code_words:
        for j in range(n):
            output += str(i[j]) + ','
        output = output[:-1]
        output += '|'
    encoder(output, P, n, noise)


def PtoG_matrix(P, num):
    I = numpy.eye(num)
    G = numpy.concatenate((I, numpy.array(P)), axis=1)
    return G


def DtoC(d, G):
    temp_list = list(d)
    temp_array = []
    for i in temp_list:
        temp_array.append(int(i))
    D = numpy.array(temp_array)
    C = numpy.matmul(D, G)
    C = numpy.mod(C, [2])
    temp = []
    for i in numpy.array(C).tolist():
        temp.append(int(i))
    return temp


def encoder(code, P, word_length, noise_amount):
    encoded = base64.b64encode(code.encode('ascii'))
    # return json.dumps({"compression_algorithm": "LZ77", "code": {"name": "linear", "P": "[%s]" % encoded}})
    '''data = json.dumps({"compression_algorithm": {"name": "LZ77", "Window size": str(int(lookahead_buffer_size) + int(search_buffer_size)), "Search Buffer Size": str(search_buffer_size), "Lookahead Buffer Size": str(lookahead_buffer_size)}
                , "code": {"name": "linear", "P":str(P), "Word Length": str(word_length), "Noise Amount": str(noise_amount)}
                , "Encoded String": str(encoded)})'''
    '''data = {}
    data['compression_algorithm'] = []
    data['compression_algorithm'].append({
        'name': 'LZ77',
        'Window Size': str(int(lookahead_buffer_size) + int(search_buffer_size)),
        'Search Buffer Size': str(search_buffer_size),
        'Lookahead Buffer Size': str(lookahead_buffer_size)
    })
    data['code'] = []
    data['code'].append({
        'name': 'linear',
        'P': str(P),
        'Word Length': str(word_length),
        'Noise Amount': str(noise_amount)
    })
    data['Encoded String'] = []
    data['Encoded String'].append({'Encoded String': str(encoded)})'''
    data = {}
    data['Statistics'] = []
    data['Statistics'].append({
        'compression_algorithm': {
            'name': 'LZ77',
            'Window Size': str(int(lookahead_buffer_size) + int(search_buffer_size)),
            'Search Buffer Size': str(search_buffer_size),
            'Lookahead Buffer Size': str(lookahead_buffer_size)
        },
        'code': {
            'name': 'linear',
            'P': str(P),
            'Word Length': str(word_length),
            'Noise Amount': str(noise_amount)
        },
        'Encoded String': {'Encoded String': str(encoded)}
    })

    with open('data.csv', 'w') as outfile:
        json.dump(data, outfile)
    # return json.dumps(data)


def sender():
    print("Input search buffer size: ")
    global search_buffer_size
    search_buffer_size = input()
    print("Input look-ahead buffer size: ")
    global lookahead_buffer_size
    lookahead_buffer_size = input()
    print("Input file: ")
    file_name = input()
    file = open(file_name, "r")
    # Lempel-Ziv Compressed string
    lz = lempel_ziv(search_buffer_size, lookahead_buffer_size, file.read())
    # Casting compressed string as bytearray
    lz_bytes = ' '.join(format(ord(x), 'b') for x in lz)
    print("Compression Successful")
    print(len(lz_bytes[lz_bytes.rfind(' ')+1:]))
    mod = numpy.mod(len(lz_bytes[lz_bytes.rfind(' ')+1:]), 3)
    zeros_to_add = 0
    if mod != 0:
        zeros_to_add = 3 - mod
    print(lz_bytes)
    print("00" + lz_bytes.replace(" ", "-"))
    linear_code("00" + lz_bytes.replace(" ", ""))


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


def recipient(data):
    return


# Program start
if __name__ == "__main__":
    '''#print(lempel_ziv(9, 9, "001010210210212021021200"))
    #lz_decoder(9, lempel_ziv(9, 9, "001010210210212021021200"))
    linear_code('100010010101')
    P = [[0,1,1], [1,0,1], [1,1,0]]
    G = PtoG_matrix(P, 3)
    print(DtoC([0, 0, 1], G))
    print(lempel_ziv(9, 9, "001010210210212021021200"))
    lz_decoder(9, bytearray(lempel_ziv(9, 9, "001010210210212021021200"), encoding='utf-8'))'''
    sender()
