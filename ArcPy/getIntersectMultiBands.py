import glob

import arcpy
import os


#filepath=r"H:\GraduateFile\Hebei\BestScale\MultiDayNIRTIFFs\\"+str(bandcount)
filepath=r"H:\GraduateFile\Tulufan\ImageSegment\TimeSeriesBandsShapefile"
os.chdir(filepath) 
#ָ������Ŀ¼�������Ӱ���Ŀ¼
arcpy.env.workspace = filepath
    
###��ȡΨһʱ���ʱ���б�
print('����ִ�л�ȡΨһʱ���ʱ���б�....')
filename = glob.glob('*.shp')


#ָ������ļ���
#outFolder = r"H:\GraduateFile\Hebei\BestScale\MultiDayNIRTIFFsComposite\\"
outFolder = r"H:\GraduateFile\Tulufan\ImageSegment\tulufan_allbands_intersect.shp"
#dateList=['20200301']
print('run  compositebands...')
ras_list = ";".join(filename)

#ִ�жನ�κϳɲ���
try:
    
    arcpy.Intersect_analysis(ras_list,outFolder, "ALL", "", "")
    print(ras_list)
    #arcpy.Mosaic_management(ras_list,outFolder+'\\'+day+".tif","LAST","FIRST","0", "0", "", "", "") 0.00021456199
except:
    print arcpy.GetMessages()
    print arcpy.GetMessages()


print('��ɶನ�κϳ�')
