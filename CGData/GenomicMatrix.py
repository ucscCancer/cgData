
import csv
import CGData
import CGData.BaseMatrix

class GenomicMatrix(CGData.BaseMatrix.BaseMatrix):

	__format__ = {
            "name" : "genomicMatrix",
            "type" : "type",
            "form" : "matrix",
            "rowType" : "probeMap",
            "colType" : "idMap",
            "valueType" : "float",
            "nullString" : "NA"
        }    

    def __init__(self):
        CGData.BaseMatrix.BaseMatrix.__init__(self)

    def get_probe_list(self):
        return self.get_rows()

    def get_sample_list(self):
        return self.get_cols()

    def write_gct(self, handle, missing=''):
        write = csv.writer(handle, delimiter="\t", lineterminator='\n')
        sampleList = self.get_sample_list()
        sampleList.sort(lambda x, y: self.sampleList[x] - self.sampleList[y])
        write.writerow(["#1.2"])
        write.writerow([len(self.probe_hash), len(sampleList)])
        write.writerow(["NAME", "Description"] + sampleList)
        for probe in self.probe_hash:
            out = [probe, probe]
            for sample in sampleList:
                val = self.probe_hash[probe][self.sampleList[sample]]
                if val is None:
                    val = missing
                out.append(val)
            write.writerow(out)

