import csv
import os

from colors import all_colors, janome_colors, sulky_rayon_colors, robison_polyester_colors, robison_rayon_colors, \
    measured_colors


def read_colors():
    csv_file = open(os.path.join(os.path.split(__file__)[0], "colors.csv"), newline='')
    csv_reader = csv.reader(csv_file)
    color_groups = next(csv_reader)

    known_colors = all_colors.groups
    known_colors.update(janome_colors.groups)
    known_colors.update(robison_rayon_colors.groups)
    known_colors.update(robison_polyester_colors.groups)
    known_colors.update(sulky_rayon_colors.groups)

    default_colors = {}
    color_mappings = {}

    # Examine the rows in the CSV file mapping internal color codes to other
    # color codes, looking up each code in the dictionaries mapping color codes
    # to known colors.

    for row in csv_reader:

        internal_code = int(row[0])

        for group, other_code in zip(color_groups[1:], row[1:]):

            # if other_code and known_colors.has_key(group):
            if other_code and group in known_colors:

                colors_dict = known_colors[group]
                other_code = int(other_code)

                # if not colors_dict.has_key(other_code):
                if not other_code in colors_dict:
                    continue

                color_mappings.setdefault(internal_code, {})[group] = other_code

                # if default_colors.has_key(internal_code):
                if internal_code in default_colors:
                    continue

                try:
                    default_colors[internal_code] = colors_dict[other_code]
                except KeyError:
                    pass

    csv_file.close()
    return color_groups[1:], known_colors, default_colors, color_mappings


def color(identifier):
    try:
        name, rgb = default_colors[identifier]
    except KeyError:
        name, rgb = measured_colors.colors[identifier]

    return int(rgb[1:3], 16), int(rgb[3:5], 16), int(rgb[5:7], 16)


color_groups, known_colors, default_colors, color_mappings = read_colors()
