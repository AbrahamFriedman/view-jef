"""
convert_html_to_module.py - Converts HTML from threadchart.info into a Python
                            module with color data.
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
        color_line = lines[i]
        color = color_line[color_line.rfind("#"):color_line.rfind("'")]
        description = lines[i + 1].split("<br>")
        number = int(description[0][description[0].rfind("#") + 1:])
        group = description[1]
        name = description[2][:description[2].find("</font>")]

        name = " ".join(name.split("\xa0"))

        colors = groups.setdefault(group, {})
        colors[number] = (name, color)

    f = open(python_module, "w")

    f.write("# Generated from the %s file obtained from\n" % html_chart)
    f.write("# http://threadchart.info/%s\n\n" % html_chart)

    f.write("groups = {\n")

    for group, colors in groups.items():

        f.write('  "' + group + '": {\n')
        f.write('    # code: (name, RGB)\n')
        codes = colors.keys()
        codes.sort()

        for code in codes:
            name, color = colors[code]
            f.write('    ' + str(code) + ': ("' + name + '", "' + color + '"),\n')

        f.write('  },\n')

    f.write("}\n")
    f.close()

    sys.exit()
