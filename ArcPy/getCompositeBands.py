import glob

import arcpy
import os
os.chdir(r'H:\GraduateFile\Hebei\BestScale\MultiDayNIRTIFFs') 
#ָ������Ŀ¼�������Ӱ���Ŀ¼
arcpy.env.workspace = r"H:\GraduateFile\Hebei\BestScale\MultiDayNIRTIFFs"
filepath=r"H:\GraduateFile\Hebei\BestScale\MultiDayNIRTIFFs"

###��ȡΨһʱ���ʱ���б�
print('����ִ�л�ȡΨһʱ���ʱ���б�....')
filename = glob.glob('*.tif')


#ָ������ļ���
outFolder = r"H:\GraduateFile\Hebei\BestScale\MultiDayNIRTIFFsComposite\\"
#dateList=['20200301']
print('run  compositebands...')
ras_list = ";".join(filename) 

#ִ�жನ�κϳɲ���
try:
    
    arcpy.CompositeBands_management(ras_list,outFolder+"hebei_nir_compbands.tif")
    print(ras_list)
    #arcpy.Mosaic_management(ras_list,outFolder+'\\'+day+".tif","LAST","FIRST","0", "0", "", "", "") 0.00021456199
except:
    print arcpy.GetMessages()
    print arcpy.GetMessages()


print('��ɶನ�κϳ�')
