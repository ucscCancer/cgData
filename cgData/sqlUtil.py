

def colFix( name ):
	out = name.replace( '-', '_' )
	while (len(out) > 64):
		out = re.sub( r'[aeiou]([^aioeu]*)$', r'\1', out)
	return out

def sqlFix( name ):
	return name.replace("'", "\\'")
