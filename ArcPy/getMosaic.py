import glob

import arcpy
import os
os.chdir(r'H:\GraduateFile\Tulufan\Bands\Bands10m') 
#ָ������Ŀ¼�������Ӱ���Ŀ¼
arcpy.env.workspace = r"H:\GraduateFile\Tulufan\Bands\Bands10m"
filepath=r"H:\GraduateFile\Tulufan\Bands\Bands10m"

 
#ָ���ù����ռ��µ�һ��Ӱ��Ϊ����Ӱ��Ϊ����Ĳ�����ȡ��׼��
#base = "S2A_MSIL2A_20191204T045151_N9999_R076_T45TXH_20210323T030721.tif"
 
#����һ�δ�����Ϊִ��ƴ��������׼��
#out_coor_system = arcpy.Describe(base).spatialReference #��ȡ����ϵͳ
#dataType = arcpy.Describe(base).DataType  
#cellwidth = arcpy.Describe(base).meanCellWidth #��ȡդ��Ԫ�ĵĿ��
#bandcount = arcpy.Describe(base).bandCount #��ȡbandCount
 
#��ӡͼ����Ϣ
#print out_coor_system.name
#print dataType
#print piexl_type
#print cellwidth
#print bandcount

###��ȡΨһʱ���ʱ���б�
print('����ִ�л�ȡΨһʱ���ʱ���б�....')
filename = glob.glob('*.tif')
dateList=[]
for filePath in filename:
    time=filePath.split('_')[2].split('T')[0]
    print(time)
    if time in dateList:
        continue
    else:
        dateList.append(time)

#ָ������ļ���
outFolder = r"H:\GraduateFile\Tulufan\Bands\Bands10mMosaic"
#dateList=['20200301']
for day in dateList:
    print('run ',day,' moasic...')
    ###�ж��Ƿ��Ѿ��ϳ�
    os.chdir(r'H:\GraduateFile\Tulufan\Bands\Bands10mMosaic')
    tempFileName=glob.glob('*.tif')
    if day+'.tif' in tempFileName:
        continue

    ####��δ������Ӱ�����ƴ��
    os.chdir(r'H:\GraduateFile\Tulufan\Bands\Bands10m')
    print('run the ',day,' of unmoasic...')
    originDays=glob.glob('*L2A_'+day+'*.tif')

    out_coor_system = arcpy.Describe(originDays[0]).spatialReference #��ȡ����ϵͳ
    dataType = arcpy.Describe(originDays[0]).DataType  
    #cellwidth = arcpy.Describe(base).meanCellWidth #��ȡդ��Ԫ�ĵĿ��
    bandcount = arcpy.Describe(originDays[0]).bandCount #��ȡbandCount

    rasters = []
    for oday in originDays:
        rasters.append(oday)
    ras_list = ";".join(rasters) 
    #ִ����Ƕ����
    try:
        arcpy.MosaicToNewRaster_management(ras_list, outFolder, day+".tif", out_coor_system, "16_BIT_UNSIGNED", 10, bandcount, "MAXIMUM", "FIRST")
        print(ras_list)
        #arcpy.Mosaic_management(ras_list,outFolder+'\\'+day+".tif","LAST","FIRST","0", "0", "", "", "") 0.00021456199
    except:
        print arcpy.GetMessages()
        print arcpy.GetMessages()


print('���ƴ��')


