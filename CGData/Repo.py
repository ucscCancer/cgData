

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


class RepoElemFile:

    def __init__(self, base, path):
        self.base = base
        self.path = path

    def __str__(self):
        return self.path

    def get_data_path(self):
        return os.path.join(self.base, self.path)

    def get_meta_path(self):
        return os.path.join(self.base, self.path + ".json")

    def check_digest(self):
        calc = self.calc_digest()
        read = self.read_digest()

        out = []
        if calc[0] != read[0]:
            out.append(self.path)
        if calc[1] != read[1]:
            out.append(self.path + ".json")

        return out

    def calc_digest(self):
        dDpath = self.get_data_path()
        dMpath = self.get_meta_path()

        d = hashlib.md5()
        handle = open(dDpath)
        d.update(handle.read())
        handle.close()

        m = hashlib.md5()
        handle = open(dMpath)
        m.update(handle.read())
        handle.close()

        return (d.hexdigest(), m.hexdigest())

    def read_digest(self):
        dDpath = self.get_data_path()
        dMpath = self.get_meta_path()
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

    def write_digest(self):
        v = self.calc_digest()

        dDpath = self.get_data_path()
        dMpath = self.get_meta_path()

        handle = open(dDpath + ".md5", "w")
        handle.write(v[0])
        handle.close()

        handle = open(dMpath + ".md5", "w")
        handle.write(v[1])
        handle.close()


class RepoType:

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

    def check_digest(self):
        out = []
        for name in self.elems:
            out.extend(self.elems[name].check_digest())
        return out

    def write_digest(self):
        for name in self.elems:
            self.elems[name].write_digest()


class Repo:

    def __init__(self):
        self.metaHash = {}
        self.basePath = None
        self.isLocal = False

    def scan_dir(self, path):
        self.isLocal = True
        if self.basePath is None:
            self.basePath = path
        for file in glob(os.path.join(path, "*")):
            if os.path.isdir(file):
                self.scan_dir(file)
            elif file.endswith(".json"):
                handle = open(file)
                data = json.loads(handle.read())
                handle.close()
                if 'type' in data and 'name' in data:
                    if not data['type'] in self.metaHash:
                        self.metaHash[data['type']] = RepoType(data['type'])
                    jPath = os.path.relpath(file, self.basePath)
                    jPath = re.sub(r'.json$', '', jPath)
                    self.metaHash[data['type']][data['name']] =
                    RepoElemFile(self.basePath, jPath)

    def load_url(self, url):
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

    def write_digest(self):
        if not self.isLocal:
            raise RepoError("Can't write digest of non-local repo")

        for type in self.metaHash:
            self.metaHash[type].write_digest()

    def check_digest(self):
        out = []
        for type in self.metaHash:
            out.extend(self.metaHash[type].check_digest())
        return out
