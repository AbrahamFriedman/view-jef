"""
convert_html_to_module.py - Converts HTML from threadchart.info into a Python
                            module with colour data.
"""

import sys
from urllib.request import urlopen

if __name__ == "__main__":

    if len(sys.argv) != 3:
        sys.stderr.write("Usage: %s <URL of HTML chart> <Python module>\n" % sys.argv[0])
        sys.stderr.write("The URL should refer to a thread chart on the threadchart.info Web site.\n")
        sys.exit(1)

    html_chart = sys.argv[1]
    python_module = sys.argv[2]

    u = urlopen(html_chart)
    lines = u.readlines()
    u.close()

    lines = filter(lambda line: 'onMouseOut="this.bgColor=' in line or \
                                'Color #' in line, lines)

    groups = {}

    for i in range(0, len(lines), 2):
        colour_line = lines[i]
        colour = colour_line[colour_line.rfind("#"):colour_line.rfind("'")]
        description = lines[i + 1].split("<br>")
        number = int(description[0][description[0].rfind("#") + 1:])
        group = description[1]
        name = description[2][:description[2].find("</font>")]

        name = " ".join(name.split("\xa0"))

        colours = groups.setdefault(group, {})
        colours[number] = (name, colour)

    f = open(python_module, "w")

    f.write("# Generated from the %s file obtained from\n" % html_chart)
    f.write("# http://threadchart.info/%s\n\n" % html_chart)

    f.write("groups = {\n")

    for group, colours in groups.items():

        f.write('  "' + group + '": {\n')
        f.write('    # code: (name, RGB)\n')
        codes = colours.keys()
        codes.sort()

        for code in codes:
            name, colour = colours[code]
            f.write('    ' + str(code) + ': ("' + name + '", "' + colour + '"),\n')

        f.write('  },\n')

    f.write("}\n")
    f.close()

    sys.exit()
