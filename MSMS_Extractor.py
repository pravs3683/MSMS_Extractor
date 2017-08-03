# 
# Developed by Praveen Kumar
# Galaxy-P Team (Griffin's Lab)
# University of Minnesota
#
#
#

def main():
    from pyteomics import mzml
    import os
    import sys
    import shutil
    import subprocess
    import re
    import pandas as pd
    from operator import itemgetter
    from itertools import groupby
    import random
    
    if len(sys.argv) >= 7:
        # Start of Reading Scans from PSM file
        # Creating dictionary of PSM file: key = filename key = list of scan numbers
        
        removeORretain = sys.argv[5].strip()
        randomScans = int(sys.argv[6].strip())
        
        ScanFile = sys.argv[2]
        spectrumTitleList = list(pd.read_csv(ScanFile, "\t")['Spectrum Title'])
        scanFileNumber = [[".".join(each.split(".")[:-3]), int(each.split(".")[-2:-1][0])] for each in spectrumTitleList]
        scanDict = {}
        for each in scanFileNumber:
            if scanDict.has_key(each[0]):
                scanDict[each[0]].append(int(each[1]))
            else:
                scanDict[each[0]] = [int(each[1])]
        # End of Reading Scans from PSM file
        
        inputPath = sys.argv[1]
        ##outPath = "/".join(sys.argv[3].split("/")[:-1])
        outPath = sys.argv[3]
        ##outFile = sys.argv[3].split("/")[-1]
        allScanList = []
        # Read all scan numbers using indexedmzML/indexList/index/offset tags
        for k in mzml.read(inputPath).iterfind('indexedmzML/indexList/index/offset'):
            if re.search("scan=(\d+)", k['idRef']):
                a = re.search("scan=(\d+)", k['idRef'])
                allScanList.append(int(a.group(1)))
        # End of Reading mzML file
        
        fraction_name = sys.argv[4]
        if scanDict.has_key(fraction_name):
            scansInList = scanDict[fraction_name]
        else:
            scansInList = []
        scansNotInList = list(set(allScanList) - set(scansInList))
        
        if removeORretain == "remove":
            scan2retain = scansNotInList
            scan2retain.sort()
            scansRemoved = scansInList
            # scan2retain contains scans that is to be retained
            
        elif removeORretain == "retain":
            # Randomly select spectra
            random_scans = list(map(lambda _: random.choice(scansNotInList), range(randomScans)))
            
            scan2retain = random_scans + scansInList
            scan2retain.sort()
            scansRemoved = list(set(allScanList) - set(scan2retain))
            # scan2retain contains scans that is to be retained
            
        # Print Stats
        print >> sys.stdout,"Total number of Scan Numbers: %d" % len(list(set(allScanList)))
        print >> sys.stdout,"Number of Scans retained: %d" % len(scan2retain)
        print >> sys.stdout,"Number of Scans removed: %d" % len(scansRemoved)
        
        
        # Identifying groups of continuous numbers in the scan2retain and creating scanString
        scanString = ""
        for a, b in groupby(enumerate(scan2retain), lambda(i,x):i-x):
            x = map(itemgetter(1), b)
            scanString = scanString + "["+str(x[0])+","+str(x[-1])+"] "
        # end identifying
        
        # start create filter file
        filter_file = open("filter.txt", "w")
        filter_file.write("filter=scanNumber %s\n" % scanString)
        filter_file.close()
        # end create filter file 
        
        # Prepare command for msconvert
        inputFile = fraction_name+".mzML"
        os.symlink(inputPath,inputFile)
        outFile = "filtered_"+fraction_name+".mzML"
        # msconvert_command = "msconvert " + inputFile + " --filter " + "\"scanNumber " + scanString + " \" " + " --outfile " + outFile + " --mzML --zlib"
        msconvert_command = "msconvert " + inputFile + " -c filter.txt " + " --outfile " + outFile + " --mzML --zlib"
        
        
        # Run msconvert
        try:
            subprocess.check_output(msconvert_command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            sys.stderr.write( "msconvert resulted in error: %s: %s" % ( e.returncode, e.output ))
            sys.exit(e.returncode)
        # Copy output to 
        shutil.copyfile(outFile, outPath)
        
    else:
        print "Please contact the admin. Number of inputs are not sufficient to run the program.\n"

if __name__ == "__main__":
    main()
    
    
    
    
