# USAGE
# python search.py --index index.csv --query queries/103100.png --result-path dataset

# import the necessary packages
from pyimagesearch.colordescriptor import ColorDescriptor
from pyimagesearch.searcher import Searcher
import argparse
import cv2
from urllib.request import urlopen
import numpy as np

class Finder:
    cd = ColorDescriptor((8, 12, 3))
    searcher = Searcher("index.csv")
    def __init__(self):
        # initialize the image descriptor
        # perform the search
        self.searcher = Searcher("index.csv")

    def url_to_image(self,url):
        # download the image, convert it to a NumPy array, and then read
        # it into OpenCV format
        #resp = urllib.urlopen(url)
        #image = np.asarray(bytearray(resp.read()), dtype="uint8")
        #image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        req = urlopen(url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img = cv2.imdecode(arr, -1)

        # return the image
        return img
    def findpostid(self,imagepath):
        post_id=0
        #query = cv2.imread(imagepath)
        query = self.url_to_image(imagepath)
        print(query.shape)
        features = self.cd.describe(query)
        results = self.searcher.search(features)
        postifier=results[0]
        print(postifier)
        return postifier