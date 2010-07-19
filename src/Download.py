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


import os
import sys
import urllib

from datetime import datetime


#TODO: Add resume support: http://code.activestate.com/recipes/83208-resuming-download-of-a-file/


class InvalidCredentials(Exception):
    """
        Exception raised if the proxy credentials are invalid
    """
    
    pass

class ProxyOpener(urllib.FancyURLopener):
    """
        Class for handling proxy credentials
    """
    
    def __init__(self, proxy={}, usr=None, pwd=None):
        urllib.FancyURLopener.__init__(self, proxy)
        self.count = 0
        self.proxy = proxy
        self.usr = usr
        self.pwd = pwd
        
    def prompt_user_passwd(self, host, realm):
        """
            Override the FancyURLopener prompt and simply return what was given
            Raise an error if there is a problem
        """
        
        self.count += 1
        
        if self.count > 1:
            raise InvalidCredentials, "Unable to authenticate to proxy"
                    
        return (self.usr, self.pwd)

        
def textprogress(display, current, total):
    """
        Download progress in terminal
    """
    percentage = current/float(total) * 100
    
    sys.stdout.write("\r%-56.56s %3i%% [%5sB / %5sB]" % \
        (display,
         percentage,
         format_number(current),
         format_number(total)))
         
    if percentage == 100:
        sys.stdout.write("\n")
        
    # This makes sure the cursor ends up on the far right
    # Without this the cursor constantly jumps around
    sys.stdout.flush()


def format_number(number, SI=0, space=' '):
    """
        Turn numbers into human-readable metric-like numbers
        Used from the urlgrabber library
    """
    symbols = ['',  # (none)
               'k', # kilo
               'M', # mega
               'G', # giga
               'T', # tera
               'P', # peta
               'E', # exa
               'Z', # zetta
               'Y'] # yotta
    
    if SI: step = 1000.0
    else: step = 1024.0

    thresh = 999
    depth = 0
    max_depth = len(symbols) - 1
    
    # we want numbers between 0 and thresh, but don't exceed the length
    # of our list.  In that event, the formatting will be screwed up,
    # but it'll still show the right number.
    while number > thresh and depth < max_depth:
        depth  = depth + 1
        number = number / step

    if type(number) == type(1) or type(number) == type(1L):
        # it's an int or a long, which means it didn't get divided,
        # which means it's already short enough
        format = '%i%s%s'
    elif number < 9.95:
        # must use 9.95 for proper sizing.  For example, 9.99 will be
        # rounded to 10.0 with the .1f format string (which is too long)
        format = '%.1f%s%s'
    else:
        format = '%.0f%s%s'
        
    return(format % (float(number or 0), space, symbols[depth]))


def download(url, filename, display=None, progress=textprogress, proxy={}, username=None, password=None):
    """
        Downloads a file to ram and returns a string of the contents
    """
    
    if not display:
        display = url.rsplit("/", 1)[1]

    # Do we already have a file to continue off of?
    # modified determines whether the file is outdated or not based on headers
    modified = None
    downloaded = 0
    if os.path.exists(filename):
        modified = datetime.utcfromtimestamp(os.stat(filename).st_mtime)
        downloaded = os.path.getsize(filename)

    # Open up a temporary connection to see if the file we have downloaded
    # is still usable (based on modification date)
    # format meanings are located http://docs.python.org/library/time.html
    opener = ProxyOpener(proxy, username, password)
    page = opener.open(url)
    if modified and "Last-Modified" in page.headers:
        dt = datetime.strptime(page.headers["Last-Modified"],
                                        "%a, %d %b %Y %H:%M:%S %Z")
       
        # File is too old so we delete the old file 
        if modified < dt:
            #logging.debug("OLD FILE")
            #print "OLD FILE"
            downloaded = 0
            os.remove(filename)
    page.close()


    # Open up the real connection for downloading
    opener = ProxyOpener(proxy, username, password)
    if downloaded:
        opener.addheader("Range", "bytes=%s-" % str(downloaded))
    page = opener.open(url)

    # The file range must have matched the download size
    if not "Content-Length" in page.headers:
        progress("Hit: %s" % display, downloaded, downloaded)
        return

    # Finish downloading the file
    length = int(page.headers["Content-Length"]) + downloaded
    f = open(filename, "ab")

    while 1:
        data = page.read(8192)
        if not data:
            break
        downloaded += len(data)
        f.write(data)
        progress(display, downloaded, length)
    f.close()
    page.close()

    return

    
if __name__ == "__main__":
    # Successful proxy usage
    download("http://launchpad.net/keryx/stable/0.92/+download/keryx_0.92.4.zip",
             "keryx.zip",
             proxy={"http": "http://tank:3128"}, 
             username="excid3", password="password")
             
             
