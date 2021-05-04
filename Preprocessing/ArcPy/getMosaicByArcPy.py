import glob

import arcpy
import os
os.chdir(r'H:\GraduateFile\Tulufan\SCL\ProjectSCL20m') 
#指定工作目录，即存放影像的目录
arcpy.env.workspace = r"H:\GraduateFile\Tulufan\SCL\ProjectSCL20m"
filepath=r"H:\GraduateFile\Tulufan\SCL\ProjectSCL20m"

 
#指定该工作空间下的一副影像为基础影像，为后面的参数提取做准备
#base = "S2A_MSIL2A_20191204T045151_N9999_R076_T45TXH_20210323T030721.tif"
 
#以下一段代码是为执行拼接做参数准备
#out_coor_system = arcpy.Describe(base).spatialReference #获取坐标系统
#dataType = arcpy.Describe(base).DataType  
#cellwidth = arcpy.Describe(base).meanCellWidth #获取栅格单元的的宽度
#bandcount = arcpy.Describe(base).bandCount #获取bandCount
 
#打印图像信息
print out_coor_system.name
print dataType
#print piexl_type
#print cellwidth
print bandcount
###获取唯一时间的时间列表
print('正在执行获取唯一时间的时间列表....')
filename = glob.glob('*.tif')
dateList=[]
for filePath in filename:
    time=filePath.split('_')[2].split('T')[0]
    print(time)
    if time in dateList:
        continue
    else:
        dateList.append(time)

#指定输出文件夹
outFolder = r"H:\GraduateFile\Tulufan\SCL\MosaicSCL"

for day in dateList:
    print('run ',day,' moasic...')
    originDays=glob.glob('*L2A_'+day+'*.tif')

    out_coor_system = arcpy.Describe(originDays[0]).spatialReference #获取坐标系统
    dataType = arcpy.Describe(originDays[0]).DataType  
    #cellwidth = arcpy.Describe(base).meanCellWidth #获取栅格单元的的宽度
    bandcount = arcpy.Describe(originDays[0]).bandCount #获取bandCount

    rasters = []
    for oday in originDays:
        rasters.append(oday)
    ras_list = ";".join(rasters) 
    #执行拼接操作
    try:
        arcpy.MosaicToNewRaster_management(ras_list, outFolder, day+".tif", out_coor_system, "16_BIT_UNSIGNED", 0.00021456199, bandcount, "MAXIMUM", "FIRST")
        print(ras_list)
        #arcpy.Mosaic_management(ras_list,outFolder+'\\'+day+".tif","LAST","FIRST","0", "0", "", "", "")
    except:
        print arcpy.GetMessages()
        print arcpy.GetMessages()


print('完成拼接')





