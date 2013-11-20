import os, sys

class WireProtocol(object):
    def __init__(self, r, w, chunksize=1024):
        """ Parameters 'r' and 'w' should be pipe File Descriptors, capable of being
            used by os.read() and os.write(). """
    
        self.r = r
        self.w = w
        self.chunksize = chunksize

    def write_tuple(self, item):
        os.write(self.w, '%s\n' % (','.join([str(i) for i in item])))

    def write_finished(self):
        os.write(self.w, '\n')

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
