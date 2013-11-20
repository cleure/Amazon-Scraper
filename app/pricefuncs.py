
def str_align(string, align, separator=' ', mode='prefix'):
    out = str(string)
    buf = ''
    align = align - len(string)
    
    for i in range(align):
        buf += str(separator)
    
    if mode == 'prefix':
        return buf + out

    return out + buf

def price_int_to_str(price_int):
    a = price_int / 100
    b = str(price_int - (a * 100))
    
    return '%d.%s' % (a, str_align(b, 2, '0'))

def price_to_int(price_text):
    if price_text[0] == '$':
        price_text = price_text[1:]
    price_parts = price_text.split('.')
    return int(price_parts[0]) * 100 + int(price_parts[1])
