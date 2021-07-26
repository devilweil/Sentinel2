import glob

import arcpy
import os


bands=[1,2,3,4]

for bandcount in bands:
    print('Bands ',bandcount)
    #filepath=r"H:\GraduateFile\Hebei\BestScale\MultiDayNIRTIFFs\\"+str(bandcount)
    filepath=r"H:\GraduateFile\Ningxia\BestScale\MultiDayNIRTIFFs\\"+str(bandcount)
    #filepath=r"H:\GraduateFile\Tulufan\BestScale\MultiDayNIRTIFFs\\"+str(bandcount)
    os.chdir(filepath) 
    #ָ������Ŀ¼�������Ӱ���Ŀ¼
    arcpy.env.workspace = filepath
    
    ###��ȡΨһʱ���ʱ���б�
    print('����ִ�л�ȡΨһʱ���ʱ���б�....')
    filename = glob.glob('*.tif')


    #ָ������ļ���
    #outFolder = r"H:\GraduateFile\Hebei\BestScale\MultiDayNIRTIFFsComposite\\"
    outFolder = r"H:\GraduateFile\Ningxia\BestScale\MultiDayNIRTIFFsComposite\\"
    #outFolder = r"H:\GraduateFile\Tulufan\BestScale\MultiDayNIRTIFFsComposite\\"
    #dateList=['20200301']
    print('run  compositebands...')
    ras_list = ";".join(filename) 

    #ִ�жನ�κϳɲ���
    try:
    
        arcpy.CompositeBands_management(ras_list,outFolder+"ningxia_band"+str(bandcount)+"_compbands.tif")
        print(ras_list)
        #arcpy.Mosaic_management(ras_list,outFolder+'\\'+day+".tif","LAST","FIRST","0", "0", "", "", "") 0.00021456199
    except:
        print arcpy.GetMessages()
        print arcpy.GetMessages()


print('��ɶನ�κϳ�')
