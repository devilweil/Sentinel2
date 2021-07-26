import glob

import arcpy
import os
os.chdir(r'H:\GraduateFile\Hebei\BestScale\MultiDayNIRTIFFs') 
#指定工作目录，即存放影像的目录
arcpy.env.workspace = r"H:\GraduateFile\Hebei\BestScale\MultiDayNIRTIFFs"
filepath=r"H:\GraduateFile\Hebei\BestScale\MultiDayNIRTIFFs"

###获取唯一时间的时间列表
print('正在执行获取唯一时间的时间列表....')
filename = glob.glob('*.tif')


#指定输出文件夹
outFolder = r"H:\GraduateFile\Hebei\BestScale\MultiDayNIRTIFFsComposite\\"
#dateList=['20200301']
print('run  compositebands...')
ras_list = ";".join(filename) 

#执行多波段合成操作
try:
    
    arcpy.CompositeBands_management(ras_list,outFolder+"hebei_nir_compbands.tif")
    print(ras_list)
    #arcpy.Mosaic_management(ras_list,outFolder+'\\'+day+".tif","LAST","FIRST","0", "0", "", "", "") 0.00021456199
except:
    print arcpy.GetMessages()
    print arcpy.GetMessages()


print('完成多波段合成')
