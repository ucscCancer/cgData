
import h5py
import numpy


def writeProbeMap(h5, probeMap):
    if not "probeMap" in h5:
        h5.create_group("probeMap")

    probeType = numpy.dtype(
        [
            ('hugo', 'S'),
            ('chrome', 'S'),
            ('start', 'i'),
            ('stop', 'i'),
            ('strand', 'S'),
        ])
    hProbeType = h5py.new_vlen(probeType)
    print probeType
    probes = probeMap.geneMap.keys()
    probes.sort()
    pmCount = len(probes)

    ds = h5.create_dataset(
    "/probeMap/%s" % (probeMap.attrs['name']), [pmCount], dtype=hProbeType)

    i = 0
    val = numpy.zeros(1, dtype=probeType)
    for probe in probes:
        ds[i] = i
        i += 1


def writeGeneMatrix(h5, gm):
    ds = h5.create_dataset(
    "%s" % (gm.attrs['name']),
    [len(gm.probeHash), len(gm.sampleList)],
    dtype=float)
    i = 0
    for probe in gm.probeHash:
        rowHash = gm.probeHash[probe]
        row = numpy.zeros(len(gm.sampleList))
        for j in range(len(gm.sampleList)):
            if gm.sampleList[j] in rowHash:
                row[j] = rowHash[gm.sampleList[j]]
        ds[i] = row
        i += 1
