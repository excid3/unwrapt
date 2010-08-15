# -*- coding: utf-8 -*-
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


"""
    Our packages are stored in the following format in self.packages
    
    {"package name": [{version1}, {version2}, {version3}],
     "package two": [{version1}]}
     
     This allows us to easily find a package, as well as all the versions
"""


import gzip
import logging
import os
import shutil
import subprocess
import sys

from DefinitionBase import DefinitionBase
from Download import download_url
from utils import format_number, to_filename, to_url, url_join

from DpkgVersion import DpkgVersion


info = {"name"   : "apt",
        "author" : "Chris Oliver <excid3@gmail.com>",
        "version": "1.0",
        "class"  : "Apt"}


###############################################################################
# Custom Exceptions
###############################################################################
            
class PermissionsError(Exception):
    """
        Unable to run command under current user permissions
    """
    pass
        
            
class UnsupportedArchitecture(Exception):
    """
        Project attempted to use an unsupported architecture type
    """
    pass


class PackageAlreadySet(Exception):
    """
        Package is being marked when it already has a status set
    """
    pass


###############################################################################
# The AptDef
###############################################################################

class Apt(DefinitionBase):
    
    proxy = {"proxy": {},
             "user": None,
             "pass": None}
             
    packages = {}
    status = {}
    supported = ["amd64", "armel", "i386", "ia64", "powerpc", "sparc"]
    status_properties = ["Package", "Version", "Status", "Provides"]
    binary_dependencies = ["Pre-Depends", "Depends", "Recommends"]
    supported_statuses = ["install ok installed", 
                          "to be downloaded",  
                          "dependency to be downloaded",
                          "to be installed", 
                          "dependency to be installed"]
                      

    def on_set_architecture(self, architecture):
        """
            set architecture
        """
        
        if not architecture in self.supported:
            raise UnsupportedArchitecture

        self.architecture = "binary-%s" % architecture
        
    
    def on_set_repositories(self, repositories):
        """
            set repositories list
        """
        
        self.repositories = []
        for repo in repositories:
            rtype, url, dist, sections = repo.split(None, 3)

            for section in sections.split():
                r = {}
                r["rtype"] = rtype
                r["url"] = url
                r["dist"] = dist
                r["section"] = section
                r["url"] = url_join(url, "dists", dist, section)

                self.repositories.append(r)


    def __iter_repositories(self):
        """
            Used for iterating through the repository entries
            This function yields Repository objects and creates them as needed
        """
        for repo in self.repositories:
            yield repo


    def on_update(self, reporthook=None, download=True):
        """
            This is a missing docstring ZOMG!
        """

        if download:
            self._download_lists(reporthook)

        self._read_lists()


    def _download_lists(self, reporthook=None):
        """
            on_update helper function
        """
        
        directory = os.path.join(self.download_directory, "lists")

        # If the download directory does not exist, create it
        if not os.path.exists(directory):
            os.makedirs(directory)

        for repo in self.__iter_repositories():

            # Build the strings
            url = to_url(repo, self.architecture, "Packages")
            filename = to_filename(directory, url)
            display_name = "Repository => %s / %s" % (repo["dist"], repo["section"])

            # Download
            #TODO: catch exceptions
            #TODO: Support bz2 and unarchived Packages files
            filename = "%s.gz" % filename
            download_url("%s.gz" % url, 
                         filename, 
                         display_name, 
                         proxy=self.proxy["proxy"], 
                         username=self.proxy["user"], 
                         password=self.proxy["pass"])


    def _build_lists(self, directory, lists=[]):

        # Build the strings
        for repo in self.__iter_repositories():
            url = to_url(repo, self.architecture, "Packages")
            filename = to_filename(directory, url)
            filename = "%s.gz" % filename  # Works only if the index files are gz
            lists.append((repo, filename))
            
        return lists


    def _read_lists(self):
        """
            on_update helper function
        """
        
        self.packages = {}        
        lists = self._build_lists(os.path.join(self.download_directory, "lists"))
        total = len(lists)            
 
        # Now parse each file, extracting as necessary
        for i, value in enumerate(lists):
            repo, filename = value

            # Display percent read            
            frac = (float(i)/float(total))*100
            sys.stdout.write("\rReading package lists... %3i%%" % frac)
            sys.stdout.flush()

            # Attempt to open the package list.
            try:
                if filename.endswith(".gz"):
                    f = gzip.open(filename, "rb")
                else:
                    f = open(filename, "rb")   
            except:  #FIXME: specify exception.
                logging.error("\nPackage list does not exist: %s" % filename) 
                continue

            # Parse packages into dictionary
            self.__parse(repo, f)
            f.close()

        sys.stdout.write("\rReading package lists... %3i%%" % 100)
        sys.stdout.write("\n")
        logging.info("%i packages available" % len(self.packages))
        

    def __parse(self, repo, f):
        """
            Takes a repository and an open file
            
            returns a dictionary with all packages in file
        """
        
        current = {}
        for line in f:
        
            # Do we have a filled out package?
            if line.startswith("\n"):
                
                # Attach
                current["Repository"] = repo
                if current["Package"] in self.packages:
                    self.packages[current["Package"]].append(current)
                else:
                    self.packages[current["Package"]] = [current]

                current = {}
                    
            # Do we have a long description?
            elif line.startswith(" ") or line.startswith("\t"):
                if "Long" in current:
                    current["Long"] += line
                else:
                    current["Long"] = line

            # Everything else is a standard property that gets handled the same
            else:
                try:
                    key, value = line.split(": ", 1)
                    current[key] = value.strip()
                except Exception, e:
                    logging.debug(repr(line))
                    logging.debug(e)
            

    def on_set_status(self, status="/var/lib/dpkg/status"):
        """
            Parses the dpkg status file for package versions, names, and
            installed statuses.
        """

        f = open(status, "rb")
        
        self.status = {}
        
        current = {}
        for line in f:
        
            # Add package metadata to status
            if line.startswith("\n") and "Package" in current:
                
                # Only add package if it is a supported status
                if current["Status"] in self.supported_statuses:
                    self.status[current["Package"]] = current
                    
                    # Mark the provides as well for dependency calculation
                    if "Provides" in current:
                        for provide in current["Provides"].split(", "):
                            self.status[provide] = current
                    
                current = {}
                
            else:
                # Add property
                try:
                    key, value = line.split(": ", 1)
                    
                    if key in self.status_properties:
                        current[key] = value.strip()
                except:
                    pass
        
        f.close()
        
        logging.info("%i packages installed" % len(self.status))


    def on_get_available_package_names(self):
        if self.packages:
            return self.packages.keys()
        return self.status.keys()
    

    def on_get_latest_binary(self, package):
        """
            Returns the data for latest version of a package
        """
        
        available = self.get_available_binary_versions(package)
        
        if not available:
            return None
            
        # Set the DpkgVersion instance for each package
        for pkg in available:        
            pkg["DpkgVersion"] = DpkgVersion(pkg["Version"])

        # Compare the versions
        newest = available[0]
        for pkg in available[1:]:
            if pkg["DpkgVersion"] > newest["DpkgVersion"]:
                newest = pkg
        
        return newest


    def on_get_binary_version(self, package, version):
        
        available = self.get_available_binary_versions(package)
        
        if available:
            
            # Return the metadata of the package with matching version
            for package in available:
                if DpkgVersion(package["Version"]) == version:
                    return package
        
        return None
        

    def on_get_available_binary_versions(self, package):
        """
            Return a list of metadata for all available packages with a
            matching name
        """
        
        if not package in self.packages:
            return None

        return self.packages[package]


    def on_mark_package(self, metadata, dependency=False):
        """
            Get a list of dependencies based on package metadata
        """

        if not metadata:
            raise AttributeError, "You must supply valid package metadata"

        #TODO: This function obviously needs to be split up and modularized :)

        # First check if the package is installed already?
        status = self.on_get_package_status(metadata["Package"])
        if status != "not installed":
            raise AttributeError, "Package already set to status: %s" % status
        
        # Mark the package itself
        if not dependency: metadata["Status"] = "to be downloaded"
        else: metadata["Status"] = "dependency to be downloaded"
        self.status[metadata["Package"]] = metadata

        logging.info("Finding dependencies for %s..." % metadata["Package"])

        depends = self.on_get_package_dependencies(metadata)
        
        # Do the dependency calculations
        for dep in depends:
            
            # In case we have some ORs
            options = dep.split(" | ")
            
            satisfied = False
            for option in options:
            
                details = option.split(" ")
                name = details[0]
                
                # If any of these packages are already installed
                if name in self.status:
                    #logging.debug("Dependency %s installed!" % name)

                    # Assume installed version will work
                    satisfied = True
                    
                    # Test for compatible version just in case
                    if len(details) > 1:
                        comparison = details[1][1:] # strip the '('
                        version = details[2][:-1] # strip the ')'
                        
                        satisfied = DpkgVersion(self.status[name]["Version"]). \
                                            compare_string(comparison, version)
                        
                    # No need to test the other options if one is found
                    if satisfied:
                        break
                          
            # No package was installed, so take the first one and add it
            # as a dependency
            if not satisfied:

                name = options[0].split(" ", 1)[0]
                pkg = self.get_latest_binary(name)

                #TODO: Verify pkg's version satisfies
                #pkg["Status"] = "to be downloaded"
                #self.status[pkg["Package"]] = pkg
                #print pkg
                
                # Mark sub-dependencies as well
                if pkg:
                    self.on_mark_package(pkg, dependency=True)


    def on_get_package_dependencies(self, metadata):

        # Build a string of the necessary sections we need
        depends = []
        for section in self.binary_dependencies:
            if section in metadata:
                depends += metadata[section].split(", ")

        return depends


    def on_apply_changes(self):
        
        directory = os.path.join(self.download_directory, "packages")
        
        # Build the list of package urls to download
        downloads = [(key, value["Repository"]["url"].split("dists")[0] + value["Filename"]) \
                     for key, value in self.status.items() \
                     if value["Status"] in ["to be downloaded", "dependency to be downloaded"]]
        
        #downloads = []
        #for key, value in self.status.items():
        #    if value["Status"] == "to be downloaded":
        #        downloads.append(value["Repository"]["url"].split("dists")[0] + value["Filename"])
                
        logging.info("%i packages to be installed" % len(downloads))
        
        # Create the download directory if it doesn't exist
        if not os.path.exists(directory):
            os.mkdir(directory)
        
        # Download the files
        for key, url in downloads:
            download_url(url, 
                         "%s/%s" % (directory, url.rsplit("/", 1)[1]), 
                         proxy=self.proxy["proxy"], 
                         username=self.proxy["user"], 
                         password=self.proxy["pass"])
            # Once it's downloaded, mark this package status to "to be installed"
            # or "dependency to be installed", depending on what it is now.
            if self.status[key]["Status"] == "to be downloaded":
                self.status[key]["Status"] = "to be installed"
            elif self.status[key]["Status"] == "dependency to be downloaded":
                self.status[key]["Status"] = "dependency to be installed"
        
        
    def on_save_changes(self, status):
    
        # This will NOT create a status file to override /var/lib/dpkg/status
        # so DO NOT try to replace the system status file.
        # YOU HAVE BEEN WARNED
        
        f = open(status, "wb")
        
        for status, package in self.status.items():

            # Try to write these back in the order they were read
            properties = ["Package", "Status", "Version", "Provides"]
            lines = ["%s: %s\n" % (key, package[key]) for key in properties if key in package]
            
            f.writelines(lines)
            f.write("\n")
            
        f.close()
        
        
    def on_cancel_changes(self, downloads, installs):
        
        for key, value in self.status.items():
            if downloads and value["Status"] in \
                    ["to be downloaded", "dependency to be downloaded"] or \
               installs and value["Status"] in \
                    ["to be installed", "dependency to be installed"]:
                del self.status[key]
        
        
    def on_get_changes_size(self):
    
        # Build list of packages to be downloaded
        packages = [(value["Package"], value["Version"]) \
                    for key, value in self.status.items() \
                    if value["Status"] in ["to be downloaded", "dependency to be downloaded"]]

        count = 0
        total = 0        
        for name, version in packages:
            package = self.get_binary_version(name, version)
            if package:
                total += int(package["Size"])
                count += 1
        
        return (count, format_number(total), total)
        
    
    def on_get_package_status(self, package):

        if package in self.status:
            return self.status[package]["Status"]        
            
        return "not installed"
        
        
    def on_install(self, reporthook=None):
        """
            We will take the approach of installing by copying the lists to
            /var/lib/apt/lists and the packages to /var/cache/apt/archives and
            calling apt-get update and then apt-get install on the packages 
            which have the status of "to be installed". This prevents tampering
            with sources.list and works more or less the exact same if we made
            a local repository.
        """
        
        if not os.geteuid() == 0:    
            raise PermissionsError, "You may only install as root"
        
        # Copy lists over
        for repo in self.__iter_repositories():
            url = to_url(repo, self.architecture, "Packages")
            filename = to_filename(os.path.join(self.download_directory, "lists"), url)

            try:
                # Extract the gz
                g = gzip.open("%s.gz" % filename, "rb")
                f = open(os.path.join("/var/lib/apt/lists", os.path.basename(filename)), "wb")
                f.write(g.read())
                f.close()
                g.close()
            except IOError, e:
                # We will just ignore this, it only trip out if the user did download=False on update()
                pass

        
        # Copy packages over
        for key, value in self.status.items():
            if value["Status"] in ["to be installed", "dependency to be installed"]:
                pkg_filename = self.get_binary_version(value["Package"], value["Version"])["Filename"].rsplit("/", 1)[1]
                filename = os.path.join(self.download_directory, "packages", pkg_filename)
                dest = os.path.join("/var/cache/apt/archives", os.path.basename(filename))
                shutil.copyfile(filename, dest)

                
        # Call apt-get install with the packages
        packages = [value["Package"] for key, value in self.status.items() if value["Status"] == "to be installed"]
        
        subprocess.call("apt-cache gencaches", shell=True)
        subprocess.call("apt-get -y install %s" % " ".join(packages), shell=True)
        
        
    def on_get_upgrades(self):
        
        upgrades = []
        
        # We will only check the installed packages, anything to be downloaded
        # or installed can wait. We might want to change this in the future.
        installed = [value for key, value in self.status.items() if value["Status"] == "install ok installed"]
        
        for current in installed:
            latest = self.get_latest_binary(current["Package"])
            
            # Only if there is a version available should we check to see if
            # there is a newer version. We also don't want to mark it twice if
            # the package is already selected for upgrade
            if latest and latest not in upgrades and DpkgVersion(latest["Version"]) > DpkgVersion(current["Version"]):
                upgrades.append(latest)

        return upgrades
