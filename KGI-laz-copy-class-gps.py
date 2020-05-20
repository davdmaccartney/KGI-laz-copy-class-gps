import os
import numpy as np
from laspy.file import File
import time
import easygui
from imutils import paths
import fnmatch
import sys
import pandas as pd
from timeit import default_timer as timer
from decimal import Decimal


pd.options.display.float_format = '{:.6f}'.format

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def update_progress(progress):
    barLength = 30 # Modify this to change the length of the progress bar
    
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% ".format( "#"*block + "-"*(barLength-block), int(progress*100))
    sys.stdout.write(text)
    sys.stdout.flush()



dirname1 = easygui.diropenbox(msg=None, title="Please select the target directory", default=None )
total_con=len(fnmatch.filter(os.listdir(dirname1), '*.las'))
D1 = str(total_con)
msg = str(total_con) +" files do you want to continue?"
title = "Please Confirm"
if easygui.ynbox(msg, title, ('Yes', 'No')): # show a Continue/Cancel dialog
    pass # user chose Continue else: # user chose Cancel
else:
    exit(0)

dirname2 = easygui.diropenbox(msg=None, title="Please select the source to copy from", default=None )
total_con=len(fnmatch.filter(os.listdir(dirname2), '*.las'))
D2 = str(total_con)
msg = str(total_con) +" files do you want to continue?"
title = "Please Confirm"
if easygui.ynbox(msg, title, ('Yes', 'No')): # show a Continue/Cancel dialog
    pass # user chose Continue else: # user chose Cancel
else:
    exit(0)

   
file_Dir1 = os.path.basename(dirname1)
file_Dir2 = os.path.basename(dirname2)

if dirname1 == dirname2:
   easygui.msgbox('The process will end same folder to compare')
   exit(0)

if D1 != D2:
   easygui.msgbox('The process will end not same number of files')
   exit(0)


dirout = os.path.join(dirname1,"new_lidar")
if not os.path.exists(dirout):
    os.mkdir(dirout)
ci=0
cls()
eR=0



for filename in os.listdir(dirname1):
     if filename.endswith(".las"):
        ci  += 1
        #print('Reading LiDAR')
        start = timer()
        inFile1 = File(dirname1+'\\'+filename, mode='r')
        
        try:
           inFile2 = File(dirname2+'\\'+filename, mode='r')


        except OSError:
           easygui.msgbox('No file:'+filename+' in :'+dirname2+' the process will end')
           sys.exit(0) 

  
        # make a copy of the target
        point_copy_ori = inFile1.points.copy()

        # compute any ofsset difference to the target
        hXdif=0
        hYdif=0
        hZdif=0

        if (hXori != hXsrc):
          hXdif = int((hXsrc-hXori)/hSori)

        if (hYori != hYsrc):
          hYdif = int((hYsrc-hYori)/hSori)

        if (hZori != hZsrc):
          hZdif = int((hZsrc-hZori)/hSori)


        # select the layers needed from the target / original to be modified fron the source file
        #class1_points = inFile1.points[(inFile1.raw_classification == 1) | (inFile1.raw_classification == 2) | (inFile1.raw_classification == 5) | (inFile1.raw_classification == 6) | (inFile1.raw_classification == 7)]
        class1_points = inFile1.points[(inFile1.raw_classification == 1)]
        class2_points = inFile2.points

        # creating the Panda array with the joint attributes
        ori = pd.DataFrame(np.empty(0, dtype=[('intensity',np.int), ('flag_byte',np.int), ('raw_classification',np.int), ('angle',np.ubyte),('gps_time',np.float64), ('gps_time_int',np.uint32)]))
        src = pd.DataFrame(np.empty(0, dtype=[('intensity',np.int), ('flag_byte',np.int), ('raw_classificationT',np.int), ('angle',np.ubyte),('gps_time',np.float64), ('gps_time_int',np.uint32)]))


        # feeding the Panda array
        ori['intensity'] = (class1_points['point']['intensity'])
        ori['flag_byte'] = (class1_points['point']['flag_byte'])
        ori['raw_classification'] = (class1_points['point']['raw_classification'])
        ori['angle'] = (class1_points['point']['scan_angle_rank'])
        ori['gps_time'] = (class1_points['point']['gps_time'])
        ori['gps_time_int'] = round(ori.gps_time*1000000)

        src['intensity'] = (inFile2.intensity)
        src['flag_byte'] = (inFile2.flag_byte)
        src['raw_classificationT'] = (inFile2.raw_classification)
        src['angle'] = (inFile2.scan_angle_rank)
        src['gps_time'] = (inFile2.gps_time)
        src['gps_time_int'] =round(src.gps_time*1000000)
        
        # merging
        
        #start = timer()
        src.drop_duplicates(subset =['gps_time_int','intensity','flag_byte','angle'], keep=False,inplace=True)
        #end = timer()
        #print(end - start)

 
        #start = timer()
        res = pd.merge(ori, src, on=['gps_time_int','intensity','flag_byte','angle'], how='left')  
        #end = timer()
        #print(end - start)
     
        # feeding the classification
        res['D'] = res['raw_classificationT']
        res['D'] = res['D'].fillna(res['raw_classification'].fillna(res['raw_classificationT']))

        del res['intensity']
        del res['flag_byte']    
        del res['angle']
        del res['gps_time']       
        del res['gps_time_int']
        del res['gps_timeT']
         
        del res['raw_classification']
        del res['raw_classificationT']

        res.columns = ['raw_classification']

  
        
        # copying the classification
        for row in res.itertuples():
               class1_points[row.Index]['point']['raw_classification']=row.raw_classification
 

   
        point_copy_ori[(inFile1.raw_classification == 1)]= class1_points
        #point_copy_ori[(inFile1.raw_classification == 1) | (inFile1.raw_classification == 2) | (inFile1.raw_classification == 5) | (inFile1.raw_classification == 6) | (inFile1.raw_classification == 7)]= class1_points
        outFile1 = File(dirout+'\\'+filename, mode = "w", header = inFile1.header)
        outFile1.points = point_copy_ori
        outFile1.close()
        



        inFile1.close()
        inFile2.close()
        update_progress(ci/int(D1))

 
if eR>0:
   print('Process finnihed :'+str(eR)+' errors read Comp-result.txt in the source folder')
else:
   print('Process finnihed with no errors')
   

exit(0)