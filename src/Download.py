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
import math
import pycurl
import os
import time
import sys


class EasyCurl:
    """
        EasyCurl is a simple class for downloading files using the cURL library
    """
    

    def __init__(self, proxy=None):        
        self.pco = pycurl.Curl()
        self.pco.setopt(pycurl.FOLLOWLOCATION, 1)
        self.pco.setopt(pycurl.MAXREDIRS,      5)
        #self.pco.setopt(pycurl.TIMEOUT,       5*3600)
        self.pco.setopt(pycurl.CONNECTTIMEOUT, 30)
        self.pco.setopt(pycurl.AUTOREFERER,    1)
        self.pco.setopt(pycurl.NOSIGNAL,       1)
        self.pco.setopt(pycurl.HEADERFUNCTION, self.header)
            
        #TODO: Proxy!
            
        
    def perform(self, url, 
                      filename=None, 
                      display_name=None, 
                      resume=True, 
                      progress=None):
                      
        # Generate filename if not given
        if not filename:
            filename = url.strip("/").split("/")[-1].strip()        
        self.filename = filename
        
        # Display name is filename if not given
        if not display_name:
            display_name = filename
        self.display_name = display_name

        # Get resume information 
        self.existing = 0
        self.start_existing = 0
        if resume and os.path.exists(filename):
            self.existing = self.start_existing = os.path.getsize(filename)
            self.pco.setopt(pycurl.RESUME_FROM, self.existing)
        logging.debug("Existing content %d" % self.existing)

        # Configure progress hook            
        if progress:
            self.pco.setopt(pycurl.NOPROGRESS,       0)
            self.pco.setopt(pycurl.PROGRESSFUNCTION, progress)
            
        # Configure url and destination
        self.pco.setopt(pycurl.URL, url)
        self.pco.setopt(pycurl.WRITEDATA, open(filename, "ab"))
        
        # Start
        self.pco.perform()
        
        sys.stdout.write("\n")


    def header(self, buf):

        #TODO: Use Expires header to determine if we need to redownload all off
        # the file (in case of resume)
        
        logging.debug(buf)
        #200 OK or 206 Partial Content is what we are looking for
        # On 416 we need to crash
        
#        if buf.find("Requested Range Not Satisfiable") == -1:
#            # This error is trapped within pycurl so we might as well just
#            # throw a pycurl error (32, "Failed writing header")
#            #raise AttributeError, "Unable to resume"
#            return 0


    def textprogress(self, download_t, download_d, upload_t, upload_d):
        downloaded = download_d + self.existing
        total      = download_t + self.start_existing
        try:    frac = float(downloaded)/float(total)
        except: frac = 0
        
        #bar = "=" * int(25*frac)
        
        #TODO: RateEstimator
        
        sys.stdout.write("\r%-58.58s %3i%% [%5sB/%5sB]" % \
            (self.display_name,
             frac*100,
             #bar,
             format_number(downloaded),
             format_number(total)))
              

class RateEstimator:
    def __init__(self, timescale=5.0):
        self.timescale = timescale

    def start(self, total=None, now=None):
        if now is None: now = time.time()
        self.total = total
        self.start_time = now
        self.last_update_time = now
        self.last_amount_read = 0
        self.ave_rate = None
        
    def update(self, amount_read, now=None):
        if now is None: now = time.time()
        if amount_read == 0:
            # if we just started this file, all bets are off
            self.last_update_time = now
            self.last_amount_read = 0
            self.ave_rate = None
            return

        #print 'times', now, self.last_update_time
        time_diff = now         - self.last_update_time
        read_diff = amount_read - self.last_amount_read
        self.last_update_time = now
        self.last_amount_read = amount_read
        self.ave_rate = self._temporal_rolling_ave(\
            time_diff, read_diff, self.ave_rate, self.timescale)
        #print 'results', time_diff, read_diff, self.ave_rate
        
    #####################################################################
    # result methods
    def average_rate(self):
        "get the average transfer rate (in bytes/second)"
        return self.ave_rate

    def elapsed_time(self):
        "the time between the start of the transfer and the most recent update"
        return self.last_update_time - self.start_time

    def remaining_time(self):
        "estimated time remaining"
        if not self.ave_rate or not self.total: return None
        return (self.total - self.last_amount_read) / self.ave_rate

    def fraction_read(self):
        """the fraction of the data that has been read
        (can be None for unknown transfer size)"""
        if self.total is None: return None
        elif self.total == 0: return 1.0
        else: return float(self.last_amount_read)/self.total

    #########################################################################
    # support methods
    def _temporal_rolling_ave(self, time_diff, read_diff, last_ave, timescale):
        """a temporal rolling average performs smooth averaging even when
        updates come at irregular intervals.  This is performed by scaling
        the "epsilon" according to the time since the last update.
        Specifically, epsilon = time_diff / timescale

        As a general rule, the average will take on a completely new value
        after 'timescale' seconds."""
        epsilon = time_diff / timescale
        if epsilon > 1: epsilon = 1.0
        return self._rolling_ave(time_diff, read_diff, last_ave, epsilon)
    
    def _rolling_ave(self, time_diff, read_diff, last_ave, epsilon):
        """perform a "rolling average" iteration
        a rolling average "folds" new data into an existing average with
        some weight, epsilon.  epsilon must be between 0.0 and 1.0 (inclusive)
        a value of 0.0 means only the old value (initial value) counts,
        and a value of 1.0 means only the newest value is considered."""
        
        try:
            recent_rate = read_diff / time_diff
        except ZeroDivisionError:
            recent_rate = None
        if last_ave is None: return recent_rate
        elif recent_rate is None: return last_ave

        # at this point, both last_ave and recent_rate are numbers
        return epsilon * recent_rate  +  (1 - epsilon) * last_ave

    def _round_remaining_time(self, rt, start_time=15.0):
        """round the remaining time, depending on its size
        If rt is between n*start_time and (n+1)*start_time round downward
        to the nearest multiple of n (for any counting number n).
        If rt < start_time, round down to the nearest 1.
        For example (for start_time = 15.0):
         2.7  -> 2.0
         25.2 -> 25.0
         26.4 -> 26.0
         35.3 -> 34.0
         63.6 -> 60.0
        """

        if rt < 0: return 0.0
        shift = int(math.log(rt/start_time)/math.log(2))
        rt = int(rt)
        if shift <= 0: return rt
        return float(int(rt) >> shift << shift)
        
        
def format_time(seconds, use_hours=0):
    if seconds is None or seconds < 0:
        if use_hours: return '--:--:--'
        else:         return '--:--'
    else:
        seconds = int(seconds)
        minutes = seconds / 60
        seconds = seconds % 60
        if use_hours:
            hours = minutes / 60
            minutes = minutes % 60
            return '%02i:%02i:%02i' % (hours, minutes, seconds)
        else:
            return '%02i:%02i' % (minutes, seconds)


def format_number(number, SI=0, space=' '):
    """Turn numbers into human-readable metric-like numbers"""
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
    

if __name__ == "__main__":
    url = "http://launchpad.net/keryx/stable/0.92/+download/keryx_0.92.4.zip"
    ec = EasyCurl()
    ec.perform(url, progress=ec.textprogress)


