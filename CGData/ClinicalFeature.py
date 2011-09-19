
import csv
import CGData


class ClinicalFeature(CGData.CGObjectBase):
    def __init__(self):
        self.data = None
        
    def read(self,handle):
        self.data = {}
        for line in handle:
            tmp = line.split("\t")
            if tmp[0] not in self.data:
                self.data[tmp[0]] = {}
            if tmp[1] not in self.data[tmp[0]]:
                self.data[tmp[0]][tmp[1]] = []
            self.data[tmp[0]][tmp[1]].append(tmp[2])
