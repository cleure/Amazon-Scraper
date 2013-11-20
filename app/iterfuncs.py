
try:
    rangefn = xrange
except NameError:
    rangefn = range

def chunks(source, n):
    for i in rangefn(0, len(source), n):
        yield source[i:i+n]
