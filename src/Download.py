#    Unwrapt - cross-platform package system emulator
#    Copyright (C) 2010 Chris Oliver <chris@excid3.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import logging
import os
import urllib
import sys


#TODO: Integrate urlgrabber RateEstimator


def text_hook(url, filename, existing, total):
    frac = float(existing)/float(total)
    bar = '='*int(25*frac)
    sys.stdout.write("\r%-25.25s %3i%% |%-25.25s|" % \ # 5sB 8s ETA " % \
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

