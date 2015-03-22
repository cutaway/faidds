# faidds.py - Forensic Acquisition Information and Drive Data Script.
#             This script provides a simple way to gather drive information
#             and acquire a drive from a specified device file to the
#             local directory.
# 
# Copyright (c) 2012, InGuardians, Inc. <consulting@inguardians.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Point Of Contact:    Don C. Weber <don@inguardians.com>

import os
import sys
import subprocess
import time
import re

def usage():
    print sys.argv[0] + ' [-h] [-D] [-dcfldd] [-m hash0,hash1] [-c size in G (1024*1024*1024)] [-s \"serial number\"] -d \"drive location\"'
    print '    -h: help'
    print '    -D: debug information'
    print '    -s: user specified serial number. Default is to find serial number in drive info.'
    print '    -d: device file to acquire'
    print '    -c: size to split file in G (1024*1024*1024)'
    print '    -dcfldd: use dcfldd (default: dc3dd)'
    print '    -m: list of hash algorithms to use. Comma separated with no spaces. (default: md5)'
    sys.exit()

def gettime(tformat = "%Y%m%d%H%M%S"):
    # Times are returned as UTC
    return time.strftime(tformat,time.gmtime())

DEBUG      = False
ftformat   = "%B %d %Y %H:%M:%S"
tzone      = "%Z"

indrive    = ''
serial_num = ''
size       = ''
inhash    = 'md5'
dc3        = True

ops = ['-s','-D','-d','-dcfldd','-m','-c','-h']

while len(sys.argv) > 1:
    op = sys.argv.pop(1)
    if op == '-s':
        serial_num = sys.argv.pop(1)
    if op == '-D':
        DEBUG = True
    if op == '-d':
        indrive = sys.argv.pop(1)
    if op == '-dcfldd':
        dc3 = False
    if op == '-m':
        inhash = sys.argv.pop(1)
    if op == '-c':
        size = sys.argv.pop(1)
    if op == '-h':
        usage()
    if op not in ops:
        usage()


if not indrive:
    usage()

acq = raw_input('Enter YES to acquire' + indrive + ': ')
if acq != 'YES':
    print
    usage()

# Set drive to acquire
serial  = "Serial Number"
sn      = re.compile(serial)

# Command locations
sdparm = "/usr/bin/sdparm"
hdparm = "/sbin/hdparm"
parted = "/sbin/parted"
dcfldd = "/usr/bin/dcfldd"
dc3dd  = "/usr/bin/dc3dd"

###########################
# Capture drive information
###########################
parted_options = "print"
parted_cmd = [parted, indrive, parted_options]

sdparm_options = "--inquiry"
#sdparm_options = "--quiet --page=\'sn\'"
sdparm_cmd = [sdparm,sdparm_options, indrive]

hdparm_options = "-I"
hdparm_cmd = [hdparm,hdparm_options, indrive]

data_cmds = [parted_cmd,hdparm_cmd,sdparm_cmd]

info = []

# Get drive data
for cmd in data_cmds:
    if DEBUG: print ' '.join(cmd)

    info.append(' '.join(cmd))
    p = subprocess.Popen(cmd,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
    info.append(p.communicate()[0])

# Search for serial number and grab
if not serial_num:
    for e in info:
        if serial_num:
            break
        if sn.search(e):
            for l in e.split('\n'):
                if sn.search(l):
                    if DEBUG: print l.split(':')[1].lstrip()
                    serial_num = l.split(':')[1].lstrip()
                    break

if not serial_num:
    serial_num = 'serial_unknown'

###########################

###########################
# Acquire drive
# dcfldd: http://www.forensicswiki.org/wiki/Dcfldd
###########################

ctime    = gettime()
infile   = 'if=' + indrive
outfile  = 'of=./' + serial_num + '_' + ctime + '.dd'
if dc3:
    hashfile = 'log=./' + serial_num + '_' + ctime + '_hash.txt'
    err      = 'rec=on'
    dd       = dc3dd
    # dc3dd hashes are provided one at a time
    if inhash != 'md5':
        thash    = []
        for e in inhash.split(','):
            thash.append('hash=' + e)
    else:
        thash = ['hash=' + inhash]
    cmd = [dd, hashfile, err, infile]
    cmd.extend(thash)
    if size:
        outfile  = 'ofs=./' + serial_num + '_' + ctime + '.dd.0000'
        cmd.append('ofsz=' + size + 'G')
    cmd.append(outfile)
else:
    # dcfldd hashes are provided as a comma separated list
    thash = 'hash=' + inhash
    hashfile = 'hashlog=./' + serial_num + '_' + ctime + '_hash.txt'
    err      = 'conv=noerror,sync'
    dd       = dcfldd
    cmd = [dd, thash, hashfile, err, infile]
    if size:
        cmd.extend(['split=' + size + 'G','splitformat=0000'])
    # Split and split format MUST come before the filename
    cmd.append(outfile)


print 'System Time Zone Is:',time.tzname[time.daylight]
info.append('System Time Zone Is:' + time.tzname[time.daylight] + '\n')

print 'Start Time:',gettime(ftformat),'UTC'
info.append('Start Time: ' +  gettime(ftformat) + 'UTC')

print 'Acquisition command:',' '.join(cmd)
info.append('Acquisition command: ' + ' '.join(cmd))

# Run dcfldd - do not use stderr and stdout to prevent blocking due to large stderr output
subprocess.Popen(cmd).wait()

print 'Stop Time:',gettime(ftformat),'UTC'
info.append('Stop Time: ' +  gettime(ftformat) + 'UTC')

###########################


# Output file
onf     = 'drive_data_' + indrive.replace("/","_") + '_' + serial_num + '_' + gettime() + '.txt'

ONF = open(onf,'w')
for e in info:
    ONF.write(e + '\n')
ONF.close()
