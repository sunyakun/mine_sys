import csv
import sys

from PIL import Image

if len(sys.argv) != 6:
    print("Usage:\n\t from_csv.py csv_file dst color x y")
    exit(0)

filename, csv_file, dst, color, *size = sys.argv

if len(size) != 2:
    raise Exception("size error")

size = [int(size[0]), int(size[1])]


im = Image.new('L', size)

with open(csv_file, 'r') as fp:
    reader = csv.reader(fp)
    for x in range(size[0]):
        for y in range(size[1]):
            pixel = [int(i)*int(color) for i in next(reader)]
            im.putpixel((x, y), tuple(pixel))

im.save(dst)
