
import CGData
import zipfile
import json

def list(path):
    out = {}
    z = zipfile.ZipFile(path)
    for name in z.namelist():
        if name.endswith(".json"):
            handle = z.open( name )
            try:
                meta = json.loads(handle.read())
                if 'name' in meta and 'type' in meta:
                    if meta['type'] not in out:
                        out[meta['type']] = {}
                    out[meta['type']][name] = meta['name']
            except ValueError:
                pass
            handle.close()
    z.close()
    return out
            

