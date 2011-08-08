

import json
from urllib2 import urlopen
from glob import glob
import os
import re

import hashlib

sites = [
    "http://hgwdev.cse.ucsc.edu/~kellrott/cgRepo",
]


class RepoError(Exception):

    def __init__(self, text):
        Exception.__init__(self, text)


class repoElemFile:

    def __init__(self, base, path):
        self.base = base
        self.path = path

    def __str__(self):
        return self.path

    def getDataPath(self):
        return os.path.join(self.base, self.path)

    def getMetaPath(self):
        return os.path.join(self.base, self.path + ".json")

    def checkDigest(self):
        calc = self.calcDigest()
        read = self.readDigest()

        out = []
        if calc[0] != read[0]:
            out.append(self.path)
        if calc[1] != read[1]:
            out.append(self.path + ".json")

        return out

    def calcDigest(self):
        dDpath = self.getDataPath()
        dMpath = self.getMetaPath()

        d = hashlib.md5()
        handle = open(dDpath)
        d.update(handle.read())
        handle.close()

        m = hashlib.md5()
        handle = open(dMpath)
        m.update(handle.read())
        handle.close()

        return (d.hexdigest(), m.hexdigest())

    def readDigest(self):
        dDpath = self.getDataPath()
        dMpath = self.getMetaPath()
        try:
            handle = open(dDpath + ".md5")
            dVal = handle.readline().rstrip()
            handle.close()
        except IOError:
            dVal = "0"

        try:
            handle = open(dMpath + ".md5")
            mVal = handle.readline().rstrip()
            handle.close()
        except IOError:
            mVal = "0"
        return (dVal, mVal)

    def writeDigest(self):
        v = self.calcDigest()

        dDpath = self.getDataPath()
        dMpath = self.getMetaPath()

        handle = open(dDpath + ".md5", "w")
        handle.write(v[0])
        handle.close()

        handle = open(dMpath + ".md5", "w")
        handle.write(v[1])
        handle.close()


class repoType:

    def __init__(self, typeName):
        self.typeName = typeName
        self.elems = {}

    def __setitem__(self, name, data):
        if name in self.elems:
            raise RepoError("Duplicate repo name: " + name)
        self.elems[name] = data

    def __getitem__(self, name):
        return self.elems[name]

    def __iter__(self):
        for name in self.elems:
            yield name

    def checkDigest(self):
        out = []
        for name in self.elems:
            out.extend(self.elems[name].checkDigest())
        return out

    def writeDigest(self):
        for name in self.elems:
            self.elems[name].writeDigest()


class repo:

    def __init__(self):
        self.metaHash = {}
        self.basePath = None
        self.isLocal = False

    def scanDir(self, path):
        self.isLocal = True
        if self.basePath is None:
            self.basePath = path
        for file in glob(os.path.join(path, "*")):
            if os.path.isdir(file):
                self.scanDir(file)
            elif file.endswith(".json"):
                handle = open(file)
                data = json.loads(handle.read())
                handle.close()
                if 'type' in data and 'name' in data:
                    if not data['type'] in self.metaHash:
                        self.metaHash[data['type']] = repoType(data['type'])
                    jPath = os.path.relpath(file, self.basePath)
                    jPath = re.sub(r'.json$', '', jPath)
                    self.metaHash[data['type']][data['name']] =
                    repoElemFile(self.basePath, jPath)

    def loadURL(self, url):
        print url

    def __iter__(self):
        for type in self.metaHash:
            yield type

    def __getitem__(self, name):
        return self.metaHash[name]

    def write(self, handle):
        out = {}
        for type in self.metaHash:
            a = {}
            for name in self.metaHash[type]:
                a[name] = self.metaHash[type][name].path
            out[type] = a
        handle.write(json.dumps(out))

    def store(self):
        if not self.isLocal:
            raise RepoError("Can't store to non-local repo")
        out = open(os.path.join(self.basePath, "cgManifest"), "w")
        self.write(out)
        out.close()

    def writeDigest(self):
        if not self.isLocal:
            raise RepoError("Can't write digest of non-local repo")

        for type in self.metaHash:
            self.metaHash[type].writeDigest()

    def checkDigest(self):
        out = []
        for type in self.metaHash:
            out.extend(self.metaHash[type].checkDigest())
        return out
