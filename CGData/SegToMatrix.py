

import ctypes
import os

base = os.path.dirname(os.path.abspath(__file__))
segLib = ctypes.cdll.LoadLibrary(base + "/CsegToMatrix.so")


def seg_to_matrix(segHandle, outHandle):
    s = segLib.newSegment()
    t = segLib.newTargetSet()
    for line in segHandle:
        segLib.addSegmentLine(s, t, line)

    def printback(s):
        outHandle.write(s)
        return 0

    printbackTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p)
    segLib.printMatrix(s, t, printbackTYPE(printback))
