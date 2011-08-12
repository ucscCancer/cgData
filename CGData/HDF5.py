
import h5py
import numpy


def write_probe_map(h5, probe_map):
    if not "probe_map" in h5:
        h5.create_group("probe_map")

    probe_type = numpy.dtype(
        [
            ('hugo', 'S'),
            ('chrome', 'S'),
            ('start', 'i'),
            ('stop', 'i'),
            ('strand', 'S'),
        ])
    h_probe_type = h5py.new_vlen(probe_type)
    print probe_type
    probes = probe_map.geneMap.keys()
    probes.sort()
    pm_count = len(probes)

    ds = h5.create_dataset(
    "/probe_map/%s" % (probe_map.attrs['name']), [pm_count], dtype=h_probe_type)

    i = 0
    val = numpy.zeros(1, dtype=probe_type)
    for probe in probes:
        ds[i] = i
        i += 1


def write_gene_matrix(h5, gm):
    ds = h5.create_dataset(
    "%s" % (gm.attrs['name']),
    [len(gm.probe_hash), len(gm.sample_list)],
    dtype=float)
    i = 0
    for probe in gm.probe_hash:
        row_hash = gm.probe_hash[probe]
        row = numpy.zeros(len(gm.sample_list))
        for j in range(len(gm.sample_list)):
            if gm.sample_list[j] in row_hash:
                row[j] = row_hash[gm.sample_list[j]]
        ds[i] = row
        i += 1
