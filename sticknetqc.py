#To do change compass and alter headding
#
import sys
import os
import fileinput
import re
import numpy as np
import scipy as sp
import pylab
import csv
import linecache
from StringIO import StringIO

def updatewind(curfile,deploydir,probefile,stickid,headerwind):
#test if the file has qc flags
    curfile = curfile.replace("/raw/","/reformat/")
    print(curfile)
    header = linecache.getline(curfile,1)
    print(header)
    splitheader = header.split(',')
    newwind=splitheader[6]
    line2 = linecache.getline(curfile,2) 
#    footer = linecache.getline(curfile,-1)
    linecache.clearcache()
 
    if line2[-3:-1] == ",0":        #If true then reformated data 
        data = np.genfromtxt(curfile, delimiter=",", autostrip=True, skip_header=1)
        wdirdata = data[:,5]

    else:
        data = np.genfromtxt(curfile, delimiter=",", autostrip=True, skip_header=1,skip_footer=1)
        time = data[:,0]
        wdirdata = data[:,5]
    
    #Start wind correction
    print(headerwind)
    
    newhead = headerwind[0].rstrip("\n")
    deltadir = np.float(newhead) - np.float(newwind)
    print(newhead)
    print(newwind)
    print(deltadir)
    wdirdata = wdirdata - deltadir
    print(newhead)
    if newhead == "-999":
        print('bad compass')
    else:
        for x in range(len(wdirdata[:])):
            if wdirdata[x] < 0.0:

                wdirdata[x] = 360.0+wdirdata[x]

            elif wdirdata[x] > 360.0:
                wdirdata[x] = wdirdata[x]-360.0

            else:
                continue
    
    data[:,5]=wdirdata[:]
    
    #rewrite new data
    ####Should be a new function
    if len(data[0,:]) == 11:

        np.savetxt(curfile+'.tmp',data,delimiter=",", fmt='%06d,%02.1f,%02.1f,%03.1f,%02.1f,%03.1f,%01.2f,%02.1f,%02.1f,%d,%d')
        pre_append(header,curfile+'.tmp')
        os.rename(curfile+'.tmp',curfile)
    else:
        
        np.savetxt(curfile+'.tmp',data,delimiter=",",fmt='%06.1f,%02.1f,%02.1f,%03.1f,%02.1f,%03.1f,%d,%d')
        pre_append(header,curfile+'.tmp')
        os.rename(curfile+'.tmp',curfile)
    
    return[]

def replaceheader(curfile,deploydir):
    probe1 = open(curfile,'r')
    temp = probe1.readlines()
    probe1.close
    header = temp[0]
    footer = temp[-1]
    print("footer"+footer)
    header = header.replace("\r\n","\n")
    header = header.replace("\r","\n")
    footer = footer.replace("\r\n","\n")
    footer = footer.replace("\r","\n")
    footer = footer+"\n"
    footer = footer.replace("\n\n","\n")
    splithead = header.split(',')
    headerdir = splithead[6]
    reformatdir = curfile.replace("/raw/","/reformat/")
    deploydir = deploydir.replace("/raw/","/reformat/")
    if not os.path.exists(deploydir):
        os.makedirs(deploydir)
    splitfoot = footer.split(',')
    if splitfoot[0] != splithead[0]:
        probe2 = open(reformatdir,'w')
        probe2.write(header)
        probe2.close
        return[headerdir]
    else:
        #if splithead[1] is "00000000" or splithead[2] is "00:00:00" or splithead[3] is "00.0000" or splithead[4] is "000.0000" or splithead[5] is "00000.0" or splithead[6] is "000.0":
        probe2 = open(reformatdir,'w')
        probe2.write(footer)
        probe2.close    
        print("foot equal header")
            
    return[headerdir]
    
def writesticknetreformat(probefile,stickid):
    print("1\n")
    print(probefile)
   # data = np.genfromtxt(probefile, delimiter=",", autostrip=True, skip_header=1, skip_footer=1)
    qc1 = 0
    qc2 = 0
    qccolumns = ',0,0\n'
    print(probefile)
    probe = open(probefile,'r')
    countlines=len(probe.readlines())
    probe.close
    probe = open(probefile)
    reformatdir = probefile.replace("/raw/","/reformat/")
    newprobe = open(reformatdir,'a')
    linecount = -1
    if stickid is '0222B':
        for line in probe:
            splitline = line.split(',')
            print(len(splitline))
            print(splitline)
#    elif not(any(qc1)) or not(any(qc2)):
    elif qc1 ==0:
        print('QCQCQCQCQCQCQCQQC')
        linecount = -1
        for line in probe:
            linecount= linecount+1
            if(linecount == 0 or linecount == countlines-1):
                    #Replace windows line end with unix line ends
                continue
                #Break apart two combined gathered values
            if len(line) >= 50:
                    #Replace windows line end with unix line ends
                line = line.replace("\r\n","\n")
                line = line.replace("\r","\n")
                half=len(line)/2
            #ADD IN QC COLUMNS
                newprobe.write(line[0:half]+qccolumns)
                newprobe.write(line[half:len(line)-1]+qccolumns)
            else:
                line = line.replace("\r\n","\n")
                line = line.replace("\r","\n")
                newprobe.write(line[0:len(line)-1]+qccolumns)
                    #print(line)
    else:
        print('nonqcqcqcq')
        
    probe.close
    newprobe.close
    return[]
    
def smooth(x,window_len,window):

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=np.r_[2*x[0]-x[window_len:1:-1],x,2*x[-1]-x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w= np.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='same')
    return y[window_len-1:-window_len+1]
def pre_append(line, file_name):
    fobj = fileinput.FileInput(file_name, inplace=1)
    first_line = fobj.readline()
    sys.stdout.write("%s%s" % (line, first_line))
    for line in fobj:
        sys.stdout.write("%s" % line)
    fobj.close()
def deployqcreformat(firstdeploydir,k,probes,sticknet,qcfile):

    for y in os.listdir(firstdeploydir):
        probes.append(re.findall(pattern,y))
    sticknet = [elem for elem in probes if len(elem) >= 1]     
    jj=0
    tempdata = []
   
    for x in sticknet:
        print(firstdeploydir+sticknet[jj][0])
        data = np.genfromtxt(firstdeploydir+sticknet[jj][0], delimiter=",", autostrip=True, skip_header=1)
        tempdata = data[:,1]
        rhdata   = data[:,2]
        presdata = data[:,3]
        wspddata = data[:,4]
        wdirdata = data[:,5]
        qcflag1 = data[:,-2]
        qcflag2 = data[:,-1]
        
        #Boxcar filter/average 10 point wide 
        smoothtempdata = smooth(tempdata,10,window='flat')
        smoothrhdata = smooth(rhdata,10,'flat')
        smoothpresdata = smooth(presdata,10,'flat')
        smoothwspddata = smooth(wspddata,10,'flat')
        #compare if data is good
        ii=0
        flagged = []

        for i in tempdata:
            flagged = []
            if abs(tempdata[ii]-smoothtempdata[ii]) >= tempqc or abs(rhdata[ii]-smoothrhdata[ii]) >= rhqc or abs(presdata[ii]-smoothpresdata[ii]) >= presqc:
#    #FLAG ERROR
                qcflag1[ii]=1
    #            flaged = x+'\t'+ii+'\t'+tempdata[ii]+'\t'+smoothtempdata[ii]+'\t'+rhdata[ii]+'\t'+smoothrhdata[ii]+'\t'+presdata[ii]+'\t'+smoothpresdata[ii]
                flagged.append(x)
                flagged.append(ii)
                flagged.append(tempdata[ii])
                flagged.append(smoothtempdata[ii])
                flagged.append(rhdata[ii])
                flagged.append(smoothrhdata[ii])
                flagged.append(presdata[ii])
                flagged.append(smoothpresdata[ii])
                qcfile.writerow(flagged)
                print(flagged)

                flagged = []
            if abs(wspddata[ii]-smoothwspddata[ii] >= wspdqc):
                qcflag2[ii]=1
                flagged.append(x)
                flagged.append(ii)
                flagged.append(wspddata[ii])
                flagged.append(smoothwspddata[ii])
                qcfile.writerow(flagged)
                print(flagged)
                flagged =[]
            ii=1+ii
        
        #####
        #WRITE OUT FLAGED FILE
        #####
        header = linecache.getline(firstdeploydir+sticknet[jj][0],1)
        linecache.clearcache()
        splitheader = header.split(',')
        newwind=splitheader[6]
        if newwind[0].rstrip("\n") == '-999':
            qcflag2[:] = 1
        data[:,-2] = qcflag1
        data[:,-1] = qcflag2
        y= sp.arange(0, len(data[:,0]),1)
        pylab.figure(num=None,figsize=(8,10))
        pylab.plot(y,tempdata, 'g',y,smoothtempdata, 'b',y,smoothtempdata+tempqc,'y--', y,smoothtempdata-tempqc,'y--')
        pylab.savefig(k+'/'+sticknet[jj][0]+'temp.pdf',format='pdf')
        pylab.figure(num=None,figsize=(8,10))
        pylab.plot(y,rhdata, 'g',y,smoothrhdata,'b',y,smoothrhdata+rhqc,'y--',y,smoothrhdata-rhqc,'y--')
        pylab.savefig(k+'/'+sticknet[jj][0]+'rh.pdf',format='pdf')
        pylab.figure(num=None,figsize=(8,10))
        pylab.plot(y,presdata, 'g',y,smoothpresdata, 'b',y,smoothpresdata+presqc,'y--',smoothpresdata-presqc,'y--')
        pylab.savefig(k+'/'+sticknet[jj][0]+'pres.pdf',format='pdf')
        pylab.figure(num=None,figsize=(8,10))
        pylab.plot(y,wspddata, 'g',y,smoothwspddata, 'b',y,smoothwspddata+wspdqc,'y--',smoothwspddata-wspdqc,'y--')
        pylab.savefig(k+'/'+sticknet[jj][0]+'wspd.pdf',format='pdf') 

        pylab.figure(num=None,figsize=(8,10))
        pylab.plot(y,wdirdata,'g')
        pylab.savefig(k+'/'+sticknet[jj][0]+'wdir.pdf',format='pdf')
        pylab.close('all')        

                
        if len(data[0,:]) == 11:

            file1= open(firstdeploydir+sticknet[jj][0],'r')
            header=file1.readline()
            file1.close
            np.savetxt(firstdeploydir+sticknet[jj][0]+'.tmp',data,delimiter=",", fmt='%06d,%02.1f,%02.1f,%03.1f,%02.1f,%03.1f,%01.2f,%02.1f,%02.1f,%d,%d')
            pre_append(header,firstdeploydir+sticknet[jj][0]+'.tmp')
            os.rename(firstdeploydir+sticknet[jj][0]+'.tmp',firstdeploydir+sticknet[jj][0])
        else:
            file1= open(firstdeploydir+sticknet[jj][0],'r')
            header=file1.readline()
            file1.close
            np.savetxt(firstdeploydir+sticknet[jj][0]+'.tmp',data,delimiter=",",fmt='%06.1f,%02.1f,%02.1f,%03.1f,%02.1f,%03.1f,%d,%d')
            pre_append(header,firstdeploydir+sticknet[jj][0]+'.tmp')
            os.rename(firstdeploydir+sticknet[jj][0]+'.tmp',firstdeploydir+sticknet[jj][0])
        jj=jj+1
    return[]





pattern = '0\d\d\d[AB].*.txt'
tempqc = 0.5
rhqc = 5.0
presqc = 1.2
wspdqc = 4.0
k=0
deployments = []
#directory = argv[1]
#directory = '/Volumes/Raid5/aereinha/Vortex2/2009/DATA/STICKNET_V2_DATA/Deployments'
directory = '/Volumes/Raid5/aereinha/Vortex2/2010/DATA/SN/RAW/Deployments'
#directory = '/Users/aereinha/04192010masstest'
directoryfiles = os.listdir(directory)
for x in os.listdir(directory):
    if x.startswith("."):
        continue
    else:
        deployments.append(x)
print(deployments)
for k in deployments:
    for xx in os.listdir(directory+'/'+k):
        print xx
        probes = []
        sticknet = []

        if xx.startswith("first"):
            firstdeploydir = directory+'/'+k+'/first_deployment/raw/'
            for y in os.listdir(firstdeploydir):
                probes.append(re.findall(pattern,y))
            sticknet = [elem for elem in probes if len(elem) >= 1]       
            j=0
            for x in sticknet:
                probefile = directory+'/'+k+'/first_deployment/raw/'+sticknet[j][0]
                stickid = sticknet[j][0].split('_')
                #if argv[2] == "fixwind":
                #    updatewind(firstdeploydir+sticknet[j][0],firstdeploydir,probefile,stickid[0],headerwind)
                
                
                #DO header footer exchange
                headerwind = replaceheader(firstdeploydir+sticknet[j][0],firstdeploydir)
                writesticknetreformat(probefile,stickid[0])
                updatewind(firstdeploydir+sticknet[j][0],firstdeploydir,probefile,stickid[0],headerwind)          
                j=j+1
            
        elif xx.startswith("second"):
            seconddeploydir = directory+'/'+k+'/second_deployment/raw/'
            for y in os.listdir(seconddeploydir):
                probes.append(re.findall(pattern,y))
            sticknet = [elem for elem in probes if len(elem) >= 1]       
            j=0
            for x in sticknet:
                #DO header footer exchange
                stickid = sticknet[j][0].split('_')

                headerwind = replaceheader(seconddeploydir+sticknet[j][0],seconddeploydir)
                probefile = directory+'/'+k+'/second_deployment/raw/'+sticknet[j][0]
                writesticknetreformat(probefile,stickid)
                updatewind(seconddeploydir+sticknet[j][0],seconddeploydir,probefile,stickid[0],headerwind)          
           
                j=j+1
            
        elif xx.startswith("third"):
            thirddeploydir = directory+'/'+k+'/third_deployment/raw/'
            for y in os.listdir(thirddeploydir):
                probes.append(re.findall(pattern,y))
            sticknet = [elem for elem in probes if len(elem) >= 1]       
            j=0
            for x in sticknet:
                #DO header footer exchange
                stickid = sticknet[j][0].split('_')
                headerwind = replaceheader(thirddeploydir+sticknet[j][0],thirddeploydir)
                probefile = directory+'/'+k+'/third_deployment/raw/'+sticknet[j][0]
                writesticknetreformat(probefile,stickid)    
                updatewind(thirddeploydir+sticknet[j][0],thirddeploydir,probefile,stickid[0],headerwind)          
       
                j=j+1
            
        elif xx.startswith("reformat") or xx.startswith("."):
            continue
        
        else:
            deploydir = directory+'/'+k+'/raw/'
            for y in os.listdir(deploydir):
                probes.append(re.findall(pattern,y))
            sticknet = [elem for elem in probes if len(elem) >= 1]     
            print(sticknet)  
            j=0
            for x in sticknet:
                #DO header footer exchange
                stickid = sticknet[j][0].split('_')
                headerwind = replaceheader(deploydir+sticknet[j][0],deploydir)
                probefile = directory+'/'+k+'/raw/'+sticknet[j][0]
                writesticknetreformat(probefile,stickid)  
                updatewind(deploydir+sticknet[j][0],deploydir,probefile,stickid[0],headerwind)          
         
                j=j+1
                
#sys.exit()
#######
######Downsampling of A probes     
k=0
for k in deployments:
    if not os.path.exists(k):
        os.makedirs(k) 
    for xx in os.listdir(directory+'/'+k):
        probes = []
        sticknet = []
        qcfile = csv.writer(open('qcflags'+k+'.txt','w'),delimiter=' ')
        qcfile.writerow(['ID']+['POINT']+['Temp']+['smoothT']+['RH']+['SmoothRH']+['Pres']+['SmoothP'])
        if xx.startswith("first"):
            firstdeploydir = directory+'/'+k+'/first_deployment/reformat/'
            deployqcreformat(firstdeploydir,k,probes,sticknet,qcfile)             
            
        if xx.startswith("second"):             
            firstdeploydir = directory+'/'+k+'/second_deployment/reformat/'
            deployqcreformat(firstdeploydir,k,probes,sticknet,qcfile)
        if xx.startswith("third"):             
            firstdeploydir = directory+'/'+k+'/third_deployment/reformat/'
            deployqcreformat(firstdeploydir,k,probes,sticknet,qcfile)
        if xx.startswith("reformat"):             
            firstdeploydir = directory+'/'+k+'/reformat/'
            deployqcreformat(firstdeploydir,k,probes,sticknet,qcfile)

  
     
     ##############   
        ###########
        ###########
        #NOW BEGIN QC TESTS FOR DATA QUALITY
        
        
#    if xx.startswith("s"):
#        for yy in os.listdir(directory+'/'+deployments[k]+'/second_deployment/raw'):
     #       sticknets2=matchstick.match(yy)
      #      probes.append(sticknets2)
  #            continue
  #  if xx.startswith("."):
  #      continue
  #  else:
   #     probes.append(xx)
#probe = open(directory+deployments)

