cdef extern from "emscripten.h":
    char *emscripten_run_script_string(const char *)

import json

def ask_command_line():
    return emscripten_run_script_string("askCommandLine()".encode()).decode()

def download_binary(url):
    # Hex-encode the string, because otherwise emscripten
    # will truncate on the first NUL (0x00) character
    code = "hexEncode(downloadBinaryFile({}))".format(json.dumps(url))
    hexstring = emscripten_run_script_string(code.encode()).decode()
    return bytes.fromhex(hexstring)

def offer_download(bytes, filename):
    code = "offerDownloadOfBinaryFile(hexDecode({}), {})".format(
        json.dumps(bytes.hex()), json.dumps(filename))
    emscripten_run_script_string(code.encode())