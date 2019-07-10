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
    return output_list


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

def lz_decoder(search_buffer_size, tuple_list):
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
    print(lempel_ziv(9, 9, "001010210210212021021200"))
    lz_decoder(9, lempel_ziv(9, 9, "001010210210212021021200"))
