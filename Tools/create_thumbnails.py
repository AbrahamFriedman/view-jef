#!/usr/bin/env python

import os, subprocess, sys


def find_files(path, pattern):
    # TODO check replacement of commands.mkarg
    # so, si = popen2.popen2('find ' + commands.mkarg(path) + ' -name "' + pattern + '"')
    so, si = subprocess.Popen(['find', path, '-name "', pattern, '"'])
    si.close()
    return so.readlines()


if __name__ == "__main__":

    if len(sys.argv) != 4:
        sys.stderr.write("Usage: %s <search path> <dimensions> <output directory>\n" % sys.argv[0])
        sys.exit(1)

    search_path = sys.argv[1]
    dimensions = sys.argv[2]
    output_dir = sys.argv[3]

    paths = []
    paths += map(lambda line: line.strip(), find_files(search_path, "*.jef"))
    paths += map(lambda line: line.strip(), find_files(search_path, "*.JEF"))

    for path in paths:

        directory, file_name = os.path.split(path)
        # TODO Check replacement of commands.mkarg
        # if os.system(
        #         "python jef2png.py --stitches-only " + dimensions + " " + commands.mkarg(path) + " " + commands.mkarg(
        #                 os.path.join(output_dir, file_name + ".png"))) == 0:
        if os.system(
                "python jef2png.py --stitches-only " + dimensions + " " + path + " " +  (
                        os.path.join(output_dir, file_name + ".png"))) == 0:
            print
            os.path.join(output_dir, file_name + ".png")
        else:
            sys.stderr.write("Failed to convert file: " + path + "\n")

    sys.exit()
