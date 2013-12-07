import os

class WireProtocol(object):
    def __init__(self, r, w, chunksize=1024):
        """ Simple CSV-like protocol for use with int and None types ONLY. Using
            this with string/bytes or unicode types may result in buggy behavior.
            
            Parameters 'r' and 'w' should be File Descriptors, capable of being
            used by os.read() and os.write(), for instance the ones returned by
            os.pipe() or stdin/stdout. """
    
        self.r = r
        self.w = w
        self.chunksize = chunksize
        self.written = False

    def write_tuple(self, item):
        os.write(self.w, '%s\n' % (','.join([str(i) for i in item])))
        self.written = True

    def write_finished(self):
        if self.written:
            os.write(self.w, '\n')
        else:
            os.write(self.w, '\n\n')

    def read_stream(self):
        items = []
        buf = ''

        while True:
            buf += os.read(self.r, self.chunksize)
            if buf[-2:] == '\n\n':
                break

        for line in buf.split('\n'):
            if line == '':
                continue

            row = []
            for item in line.split(','):
                if item == 'None':
                    row.append(None)
                else:
                    try:
                        row.append(int(item))
                    except ValueError:
                        row.append(item)

            items.append(row)
        return items
