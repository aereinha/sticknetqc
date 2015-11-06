####
####
####
#### This code takes the footer value and works backwards replacing incorrect times
####  with correct times
####
####
####
def pre_append(line, file_name):
    fobj = fileinput.FileInput(file_name, inplace=1)
    first_line = fobj.readline()
    sys.stdout.write("%s%s" % (line, first_line))
    for line in fobj:
        sys.stdout.write("%s" % line)
    fobj.close()

import datetime as dt
import os
import sys
import numpy as np
import linecache
import fileinput

f = sys.argv[1]

dt1 = dt.timedelta(seconds=-1)
header = linecache.getline(f, 1)
line1 = linecache.getline(f,3)
line2 = linecache.getline(f,4)
linecache.clearcache()

data = np.genfromtxt(f, delimiter=",", autostrip=True, skip_header=1)
datatime = data[:,0]
datatimeold = data[:,0]

shead = header.split(',')
sline1 = line1.split(',')
sline2 = line2.split(',')
probetype = shead[0]
htime = shead[2]
ltime = sline1[0]
l2time = sline2[0]

hstime = dt.datetime.strptime(htime,"%H:%M:%S")+dt1
if len(line1) >= 50:
    lstime = dt.datetime.strptime(ltime,"%H%M%S")
    ls2time = dt.datetime.strptime(l2time,"%H%M%S")
else:
    lstime = dt.datetime.strptime(ltime,"%H%M%S.%f")
    l2stime = dt.datetime.strptime(l2time,"%H%M%S.%f")
dttime = datatime[2]-datatime[1]
print(dttime)
if dttime <= 1.0:
    print("dt = 1.0")
    dt1 = dt.timedelta(seconds=-1)
if dttime <= 0.3:
    print("dt = 0.2")
    dt1 = dt.timedelta(microseconds=-200000)
if dttime <= 0.1:
    print("dt = 0.1")
    dt1 = dt.timedelta(microseconds=-100000) 
temptime = hstime
#MANUAL CHANGES
#dt1 = dt.timedelta(microseconds=-200000)

print(len(line1))
if len(line1) >= 50:  #if true b probe
    
    for i in range(len(datatime),-1,-1):
        temptime =temptime + dt1
        datatime[i]=temptime.strftime('%H%M%S')
    data[:,0] = datatime
    np.savetxt(f+'.tmp',data,delimiter=",", fmt='%06d,%02.1f,%02.1f,%03.1f,%02.1f,%03.1f,%01.2f,%02.1f,%02.1f,%d,%d')
    pre_append(header,f+'.tmp')
    os.rename(f+'.tmp',f)
else:
    for i in range(len(datatime)-1,-1,-1):
        temptime = temptime + dt1
        datatime[i]=temptime.strftime("%H%M%S.%f")
    data[:,0] = datatime
    np.savetxt(f+'.tmp',data,delimiter=",",fmt='%08.1f,%02.1f,%02.1f,%03.1f,%02.1f,%03.1f,%d,%d')
    pre_append(header,f+'.tmp')
    os.rename(f+'.tmp',f)

        
