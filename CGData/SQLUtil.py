

def col_fix( name ):
    out = name.replace( '-', '_' ).strip()
    while (len(out) > 64):
        out = re.sub( r'[aeiou]([^aioeu]*)$', r'\1', out)
    return out

def sql_fix( name ):
    return name.replace("'", "\\'")
