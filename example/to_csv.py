import csv
import sys
import os

from PIL import Image


filename, image, dst, *_ = sys.argv

if not os.path.isfile(image):
    raise Exception("%s is not a file" % image)


im = Image.open(image)
with open(dst, 'w', newline='') as fp:
    writer = csv.writer(fp)
    writer.writerow(['r', 'g', 'b'])
    for x in range(im.size[0]):
        for y in range(im.size[1]):
            writer.writerow(im.getpixel((x, y)))
