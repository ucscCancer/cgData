

import ctypes
import os

base = os.path.dirname(os.path.abspath(__file__))
segLib = ctypes.cdll.LoadLibrary(base + "/CsegToMatrix.so")


def seg_to_matrix(seg_handle, out_handle):
    s = segLib.new_segment()
    t = segLib.new_target_set()
    for line in seg_handle:
        segLib.add_segment_line(s, t, line)

    def printback(s):
        out_handle.write(s)
        return 0

    printbackTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p)
    segLib.print_matrix(s, t, printbackTYPE(printback))
