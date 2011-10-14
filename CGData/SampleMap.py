
import CGData


class SampleMap(CGData.CGDataSetObject):

    def __init__(self):
        CGData.CGDataSetObject.__init__(self)
        self.mhash = {}

    def read(self, handle):
        for line in handle:
            tmp = line.rstrip().split('\t')
            if not tmp[0] in self.sample_hash:
                self.sample_hash[tmp[0]] = {}
            if len(tmp) > 1:
                self.sample_hash[tmp[0]][tmp[1]] = True

    def get_children(self, sample):
        out = {}
        for a in self.sample_hash.get(sample, {}):
            out[a] = True
            for c in self.get_children(a):
                out[c] = True
        return out.keys()
