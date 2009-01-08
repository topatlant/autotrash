#!/usr/bin/env python
#    autotrash.py - GNOME GVFS Trash old file auto prune
#    
#    Copyright (C) 2008 A. Bram Neijt <bneijt@gmail.com>
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

import sys
import optparse
import ConfigParser
import shutil
import glob
import os.path
import time
import math

def trash_file_name(trash_name):
  '''Get data file from trashinfo file'''
  return os.path.basename(trash_name)[:-10]

def purge(trash_name, dryrun):
  '''Purge the file behind the trash file fname'''
  file_name = trash_file_name(trash_name)
  target = os.path.expanduser('~/.local/share/Trash/files/')+file_name
  if dryrun:
    print 'Remove',target
    print 'Remove',trash_name
    return False
  if os.path.exists(target):
    if os.path.isdir(target):
        shutil.rmtree(target)
    else:
      os.unlink(target)
  os.unlink(trash_name)
  return True

def trash_info_date(fname):
  parser = ConfigParser.SafeConfigParser()
  readCorrectly = parser.read(fname)
  section = 'Trash Info'
  key = 'DeletionDate'
  if readCorrectly.count(fname) and parser.has_option(section, key):
    #Read the file succesfully
    return time.strptime(parser.get(section, key), '%Y-%m-%dT%H:%M:%S')
  return None

def main(args):
  #Load and set configuration options
  parser = optparse.OptionParser()
  parser.set_defaults(days=30, dryrun=False, verbose=False,trash_path='~/.local/share/Trash', check=False)
  parser.add_option("-d", "--days", dest='days', help='Delete files older then this DAYS number of days', metavar='PATH')
  parser.add_option("-T", "--trash-path", dest='trash_path', help='Set Trash path to PATH', metavar='PATH')
  parser.add_option("--verbose", action='store_true', dest='verbose', help='Verbose')
  parser.add_option("--check", action='store_true', dest='check', help='Report .trashinfo files without a real file')
  parser.add_option("--dry-run", action='store_true', dest='dryrun', help='Just list what would have been done')
  parser.add_option("--version", action='store_true', dest='version', help='Show version and exit')
  (options, args) = parser.parse_args()
  
  if options.version:
    print '''Version 0.0.2 \nCopyright (C) 2008 A. Bram Neijt <bneijt@gmail.com>\n License GPLv3+'''
  
  options.days = int(options.days)
  if options.days <= 0:
    print 'Can not work with negative or zero days'
    return 0
  trash_info_path = os.path.expanduser(options.trash_path + '/info')
  if not os.path.exists(trash_info_path):
    print 'Cannot find trash information directory. Make sure you have at least GNOME 2.24'
    print 'Should be at:', trash_info_path
    return 1
  for file_name in glob.iglob('%s/*.trashinfo' % trash_info_path):
    if options.check:
      if not os.path.exists(trash_file_name(file_name)):
        print file_name,'has no real file associated with it.'
    #print 'Loading file',file_name
    file_time = trash_info_date(file_name)
    if file_time == None:
      continue
    #Calculate seconds from now
    seconds_old = time.time() - time.mktime(file_time)
    days_old = int(math.floor(seconds_old/(3600.0*24.0)))
    if options.verbose:
      print 'File',file_name
      print '  is',days_old,'days old (',seconds_old,' seconds)'
      print '  deletion date was', time.strftime('%c', file_time)
    if days_old > options.days:
      purge(file_name, options.dryrun)
      if options.dryrun:
        print '  because it describes a',days_old,'days old file'
  return 0

if __name__ == '__main__':
  sys.exit(main(sys.argv))
