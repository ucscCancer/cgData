from django.http import HttpResponse
from CGData.Compiler import BrowserCompiler
from django.template import Context, loader

repoBase = "../cancerGenomeData/"

def index(request):
    print request.path
    b = BrowserCompiler()
    if request.path == "/":
        b.scan_dirs([repoBase])
        t = loader.get_template('repoview.html')
        c = Context({
            'type_list': b.set_hash.keys(),
        })
        return HttpResponse(t.render(c))
    else:
        tmp = request.path.split("/")
        b.scan_dirs([repoBase])
        if tmp[1] in b.set_hash:
            
            col_map = {"name" : 0}
            for name in b.set_hash[tmp[1]]:
                for attr in b.set_hash[tmp[1]][name].get_attrs():
                    if attr not in col_map:
                        col_map[attr] = len(col_map)
            
            cols = [None] * len(col_map)
            for col in col_map:
                cols[col_map[col]] = col
            
            rows = []
            for name in b.set_hash[tmp[1]]:
                r = []
                for c in cols:
                    r.append( b.set_hash[tmp[1]][name].get_attr(c) )
                rows.append(r)
            
            t = loader.get_template('matrixview.html')
            c = Context({
                'cols': cols,
                'rows' : rows
            })
            return HttpResponse(t.render(c))
            
    
