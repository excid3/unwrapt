import logging
import os
import urllib
import sys


def text_hook(url, filename, existing, total):
    #print "%s: %f" % (filename, existing/float(total)*100)
    frac = float(existing)/float(total)
    bar = '='*int(25*frac)
    sys.stdout.write("\r%-25.25s %3i%% |%-25.25s| 5sB 8s ETA " % \
        (filename, frac*100, bar))
    if frac == 1:
        sys.stdout.write("\n")


def download(url, filename=None, reporthook=text_hook):
    if not filename:
        filename = url.strip("/").split("/")[-1]

    urlopener = urllib.FancyURLopener()
    
    exist = 0
    if os.path.exists(filename):
        dest = open(filename, "ab")
        exist = os.path.getsize(filename)
        urlopener.addheader("Range", "bytes=%s-" % exist)
    else:
        dest = open(filename, "wb")
        
    page = urlopener.open(url)
    total = int(page.headers["Content-Length"])
    finished = exist >= total
    logging.debug(exist, total, finished)
    total = total + exist
        
    bytes = 0
    while not finished:
        data = page.read(8192)
        
        reporthook(url, filename, exist + bytes, total)
        
        if not data:
            break    
    
        dest.write(data)
        bytes += len(data)
        
    page.close()
    dest.close()
    
if __name__ == "__main__":
    download("http://launchpad.net/keryx/stable/0.92/+download/keryx_0.92.4.zip")
    print "voila!"

