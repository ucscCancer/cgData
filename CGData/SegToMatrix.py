

import ctypes
import os

base = os.path.dirname(os.path.abspath(__file__))
libFile = base + "/CsegToMatrix.so"
if os.path.exists(libFile):
    segLib = ctypes.cdll.LoadLibrary(libFile)


def seg_to_matrix(seg_handle, out_handle):
    """
    Turn a segment file into a segmented matrix.
    
    seg_handle -- CGData.GenomicSegment object
    out_handle -- File handle to write to
    """
    s = segLib.new_segment()
    t = segLib.new_target_set()
    for line in seg_handle:
        segLib.add_segment_line(s, t, line)

    def printback(s):
        out_handle.write(s)
        return 0

    printbackTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p)
    segLib.print_matrix(s, t, printbackTYPE(printback))
