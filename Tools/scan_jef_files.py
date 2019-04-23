#!/usr/bin/env python

import sys
import jef
import subprocess


def find_files(path, pattern):
    # TODO Check replacement of commands.mkarg
    # so, si = subprocess.Popen('find ' + commands.mkarg(path) + ' -name "' + pattern + '"')
    so, si = subprocess.Popen(['find', path, '-name "', pattern, '"'])
    si.close()
    return so.readlines()


if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: %s <search path>\n" % sys.argv[0])
        sys.exit(1)

    search_path = sys.argv[1]

    paths = []
    paths += map(lambda line: line.strip(), find_files(search_path, "*.jef"))
    paths += map(lambda line: line.strip(), find_files(search_path, "*.JEF"))

    for path in paths:

        j = jef.Pattern(path)
        for i in range(len(j.colors)):
            if not jef.jef_colors.colors.has_key(j.colors[i]):
                if jef.jef_colors.measured_colors.colors.has_key(j.colors[i]):
                    print
                    path, i + 1, hex(j.colors[i]), "(measured value)"
                else:
                    print
                    path, i + 1, hex(j.colors[i])

    sys.exit()
