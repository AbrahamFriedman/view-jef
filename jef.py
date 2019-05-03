"""
jef.py - Read and write JEF files.

The Janome Embroidery Format (JEF) is a binary file that consists of several sections. Multi-byte numbers appear to be stored little endian.
There is a JEF+ format which this does not cover. The structure of a JEF file is as follows:
   - File-header
   - Thread-color list
   - Thread-type list
   - Stitch list

The format specification can be found in these places:
   https://community.kde.org/Projects/Liberty/File_Formats/Janome_Embroidery_Format
   https://edutechwiki.unige.ch/en/Embroidery_format_JEF

There may be a problem with the specification of the hoop values in the unique.ch version of the spec.

The values for the decode() and encode() are specified by the format character as described below:
struct.unpack formats:
    Character < -> decode using little-endian byte order
    Format  C Type             Python Type  Size
    b       signed char        integer      1
    i       int                integer      4
    I       unsigned int       integer      4

The JEF file header is a fixed block of 116 (dec) or 0x74 (hex) bytes as follows:
    Start  End  Type  Bytes  Value                          Description
        0    3   u32      4  0x74 + 8 * Color_Changes       Offset into file where stitches begin
                        116 dec + 8 * Color Changes
        4    7   u32      4  0x01, 0x0A, 0x14               Flags/Unknown
                             1 (dec), 10 (dec), 20 (dec)
        8   21  char     14  "20180712082429" (example)     Date
       22   22  char      1  m, n, o, p, q, r, s, or t      Version Letter: (Not always set)
                                                                m = 12000
                                                                n = 11000
                                                                o = 10000 v3
                                                                p = 10000 v2.2
                                                                q =  9000
                                                                r = mc350
                                                                s = mc200
                                                                t = mb4
       23   23   u8      1  0x20                           Unknown
       24   27  u32      4  Color Count                    Color Count
       28   31  u32      4  Points Length / 2              Points Length / 2. So 80 01 00 00 is 2 not 1
       32   35  u32      4  Hoop Used (0-4)                Hoop
       36   51  u32     16  Extends                        Distance from center of hoop
       52   67  u32     16  Edge amount for hoop           Distance from default 110 x 110 Hoop, or -1,-1,-1,-1
       68   83  u32     16  Edge amount for hoop           Distance from default 50 x 50 Hoop, or -1,-1,-1,-1
       84   99  u32     16  Edge amount for hoop           Distance from default 140 x 200 hoop or -1,-1,-1,-1
      100  115  u32     16  Edge amount for hoop           Distance from custom hoop, or -1,-1,-1,-1
                                                               -1,-1,-1,-1 indicates if it does not fit
      116    *  u32    4*n Magic Number Color Lookup       List of color changes where n = Color_Changes
        *    *  u32    4*n 0xOD                            The values 0x0D, 0x0D, 0X0D repeated as many times as
                                                               there are color changes
                                                               
The hoop code starts at the 32nd (dec) position and contains the values 0-4 which describe the various hoops
that can be specified. The width and height of the hoops are specified differently in the kde.org and the unige.ch
versions of the spec but the kde.org numbers appear to match those found in other sources and so they are used here.

    Hoop (from code below)
    Value  Width  Height  Name
        0    126     100     A Standard
        1     50      50     C Free Arm
        2    140     200     B Large
        3    126     110     F Spring Loaded
        4    230     200     D Giga
"""

import struct, sys, time

from colors import jef_colors


class Pattern:

    def __init__(self, path=None):

        if path:
            self.load(path)
        else:
            self.date_time = None
            self.threads = 0
            self.hoop_size = (126, 110)
            self.hoop_name = "A"
            self.rectangles = []
            self.colors = []
            self.thread_types = []
            self.coordinates = []

    def load(self, path):
        self.file_name = path

        self.data = d = open(path, mode='rb').read()
        self.data_size = len(d)

        (offset, flags, date, version, unknown, color_count, points_length, hoop, extends1, extends2, extends3,
            extends4, extends5) = self.parse_file(d)

        # OFFSET
        start_of_stitches = struct.unpack("<I", offset)[0]
        data = d[start_of_stitches:]

        # FLAGS

        # DATE
        # TODO Date/time dosn't seem to be parsed out of the file correctly for the WAMALUG logo
        self.date_time = None
        # if struct.unpack("<I", d[4:8])[0] & 1:
        #     self.date_time = time.strptime(d[8:22], "%Y%m%d%H%M%S")
        date_as_bytes = struct.unpack("<14s", date)  # Parse 14 characters in YYYYMMDDHHMMSS format in bytes
        self.date_time = date_as_bytes[0].decode("utf-8")  # Convert bytes to str

        # VERSION
        if version == b"\x00":
            self.version = "Undefined"
        else:
            self.version = struct.unpack(("<1s", version))

            if self.version == 'm':
                self.version = '12000'
            elif self.version == 'n':
                self.version = '11000'
            elif self.version == 'o':
                self.version = '10000 v3'
            elif self.version == 'p':
                self.version = '10000 v2.2'
            elif self.version == 'q':
                self.version = '9000'
            elif self.version == 'r':
                self.version = 'mc350'
            elif self.version == 's':
                self.version = 'mc200'
            elif self.version == 't':
                self.version = 'mb4'
            else:
                self.version = 'Unknown'

        # UNKNOWN

        # COLOR COUNT
        self.threads = struct.unpack("<I", color_count)[0]

        # NUMBER OF POINTS - STITCH COUNT
        self.number_of_points = struct.unpack("<I", points_length)[0]  # Number of start locations + end locations
        self.stitch_count = self.number_of_points * 2

        # HOOP
        hoop_code = struct.unpack("<I", hoop)[0]
        self.hoop_size, self.hoop_name = self.decode_hoop(hoop_code)

        # EXTENDS 1-5
        # These are coordinates specifying rectangles for the pattern in 0.1 mm.
        self.rectangles = []
        offset = 0x24
        while offset < 0x74:

            x1 = struct.unpack("<i", d[offset:offset + 4])[0]
            y1 = struct.unpack("<i", d[offset + 4:offset + 8])[0]
            x2 = struct.unpack("<i", d[offset + 8:offset + 12])[0]
            y2 = struct.unpack("<i", d[offset + 12:offset + 16])[0]

            if x1 != -1 and y1 != -1 and x2 != -1 and y2 != -1:
                self.rectangles.append((-x1, -y1, x2, y2))
            offset += 16

        if hoop_code & 1 == 0:
            # The 4 byte words from 68 to 74 should all be -1.
            pass

        # The color table starts at offset 0x74 (116 dec).
        self.colors = []
        self.thread_types = []

        color_offset = 0x74
        thread_type_offset = 0x74 + (4 * self.threads)
        for i in range(self.threads):
            self.colors.append(struct.unpack("<i", d[color_offset:color_offset + 4])[0])
            self.thread_types.append(struct.unpack("<i", d[thread_type_offset:thread_type_offset + 4])[0])
            color_offset += 4
            thread_type_offset += 4

        self.read_threads(data)

    def parse_file(self, d):
        offset        = d[:4]
        flags         = d[4:8]
        date          = d[8:22]
        version       = d[22:23]
        unknown       = d[23:24]
        color_count   = d[24:28]
        points_length = d[28:32]
        hoop          = d[32:36]
        extends1      = d[36:52]
        extends2      = d[52:68]
        extends3      = d[68:84]
        extends4      = d[84:100]
        extends5      = d[100:116]

        return (
            offset, flags, date, version, unknown, color_count, points_length, hoop, extends1, extends2, extends3,
            extends4, extends5)

    def save(self, path):

        self.threads = len(self.coordinates)
        thread_data = self.write_threads()
        start = 0x74 + (8 * self.threads)

        self._data = b""
        self._data += struct.pack("<I", start)  # data offset
        self._data += struct.pack("<I", 1)  # date-time flag
        if self.date_time:
            # self._data += time.strftime("%Y%m%d%H%M%S", self.date_time)
            self._data += str.encode(self.date_time)
        else:
            self._data += time.strftime("%Y%m%d%H%M%S", time.localtime())
        self._data += b"\x00\x00"

        self._data += struct.pack("<I", self.threads)
        self._data += struct.pack("<I", int(len(thread_data) / 2))

        self._data += self.decode_hoop(self.hoop_name)
        # if self.hoop_name == "A":
        #     self._data += struct.pack("<I", 0)
        # elif self.hoop_name == "C":
        #     self._data += struct.pack("<I", 1)
        # elif self.hoop_name == "B":
        #     self._data += struct.pack("<I", 2)
        # elif self.hoop_name == "F":
        #     self._data += struct.pack("<I", 3)
        # elif self.hoop_name == "D":
        #     self._data += struct.pack("<I", 4)
        # else:
        #     self._data += struct.pack("<I", 0)

        if not self.rectangles:
            # Add a bounding rectangle to the output if no rectangles are
            # specified.
            self.rectangles.append(self.bounding_rect())

        for x1, y1, x2, y2 in self.rectangles:

            if len(self._data) < 0x74:
                self._data += struct.pack("<i", -x1)
                self._data += struct.pack("<i", -y1)
                self._data += struct.pack("<i", x2)
                self._data += struct.pack("<i", y2)

        # Fill the gap between the end of the rectangle list and the color
        # table.
        while len(self._data) < 0x74:
            self._data += struct.pack("<i", -1)

        for i in range(self.threads):
            self._data += struct.pack("<i", self.colors[i])

        for i in range(self.threads):
            self._data += struct.pack("<i", self.thread_types[i])

        self._data += thread_data

        try:
            open(path, "wb").write(self._data)
            return True
        except IOError:
            return False

    def set_color(self, index, code):

        self.colors[index] = code

    def read_threads(self, data):
        # Escaped-command
        # Offset  Length  Type  Description
        # 0       1       Byte  Escape = 128 (dec) or 0x80 (hex)
        # 1       1       Byte  Command-code
        #                     1 (dec) or 0x01 (hex) - Color change
        #                     2 (dec) or 0x02 (hex) - Jump / Trim
        #                    16 (dec) or 0x10 (hex) - End (last stitch)

        self.coordinates = []
        x, y = 0, 0

        coordinates = []
        first = True
        i = 0

        while i < len(data):
            b0 = data[i:i + 1]
            b1 = data[i + 1:i + 2]
            # if data[i:i + 2] == "\x80\x01":
            if (b0 == b'\x80') and (b1 == b'\x01'):  # COLOR_CHANGE
                # Starting a new thread. Record the coordinates already read
                # and skip the next two bytes.
                if coordinates:
                    self.coordinates.append(coordinates)
                coordinates = []
                first = True
                i += 4
                continue
            # elif data[i:i + 2] == "\x80\x02":
            elif (b0 == b'\x80') and (b1 == b'\x02'):  # JUMP / TRIM
                # Move command.
                i += 2
                command = "move"
                first = True
            # elif data[i:i + 2] == "\x80\x10":
            elif (b0 == b'\x80') and (b1 == b'\x10'):  # END
                # End of data.
                if coordinates:
                    self.coordinates.append(coordinates)
                break
            else:
                command = "stitch"

            # x += struct.unpack("<b", data[i])[0]
            # y += struct.unpack("<b", data[i + 1])[0]
            x += int.from_bytes(data[i:i + 1], byteorder='little', signed=True)
            y += int.from_bytes(data[i + 1:i + 2], byteorder='little', signed=True)

            if command == "move":
                coordinates.append((command, x, y))
            elif first:
                coordinates.append(("move", x, y))
                first = False
            else:
                coordinates.append((command, x, y))

            i += 2

    def color_for_thread(self, index):

        try:
            identifier = self.colors[index]
            color = jef_colors.color(identifier)
        except KeyError:
            color = (0, 0, 0)
            sys.stderr.write("Thread %i: Failed to find color 0x%02x (%i).\n" % (index, identifier, identifier))

        return color

    def write_threads(self):

        thread_data = b""

        cx, cy = 0, 0
        first = True

        for coordinates in self.coordinates:

            if first:
                first = False
            else:
                thread_data += b"\x80\x01"
                thread_data += b"\x00\x00"

            for command, x, y in coordinates:

                if command == "move":
                    thread_data += b"\x80\x02"

                thread_data += struct.pack("<b", x - cx)
                thread_data += struct.pack("<b", y - cy)

                cx = x
                cy = y

        thread_data += b"\x80\x10"
        return thread_data

    def bounding_rect(self):

        xmin, xmax, ymin, ymax = [], [], [], []
        for coordinates in self.coordinates:
            # x = map(lambda (command, x, y): x, coordinates)
            # y = map(lambda (command, x, y): y, coordinates)
            x = map(lambda command_x_y: command_x_y[1], coordinates)
            y = map(lambda command_x_y: command_x_y[2], coordinates)
            xmin.append(min(x))
            xmax.append(max(x))
            ymin.append(min(y))
            ymax.append(max(y))

        return (min(xmin), min(ymin), max(xmax), max(ymax))

    def decode_hoop(self, hoop_code):
        # Determine the hoop size in millimetres.
        if hoop_code == 0:
            hoop_size = (126, 110)
            hoop_name = "A Standard"
        elif hoop_code == 1:
            hoop_size = (50, 50)
            hoop_name = "C Free Arm"
        elif hoop_code == 2:
            hoop_size = (140, 200)
            hoop_name = "B Large"
        elif hoop_code == 3:
            hoop_size = (126, 110)
            hoop_name = "F Spring Loaded"
        elif hoop_code == 4:
            hoop_size = (230, 200)
            hoop_name = "D Giga"
        else:
            hoop_size = None
            hoop_name = None

        return hoop_size, hoop_name

    def encode_hoop(self, hoop_name):
        data = b''

        if hoop_name == "A Standard":
            data += struct.pack("<I", 0)
        elif hoop_name == "C Free Arm":
            data += struct.pack("<I", 1)
        elif hoop_name == "B Large":
            data += struct.pack("<I", 2)
        elif hoop_name == "F Spring Loaded":
            data += struct.pack("<I", 3)
        elif hoop_name == "D Giga":
            data += struct.pack("<I", 4)
        else:
            data += struct.pack("<I", 0)

        return data
