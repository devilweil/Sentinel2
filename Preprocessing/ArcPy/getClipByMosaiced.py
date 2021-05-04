import glob

import arcpy
import os

area='Tulufan'
os.chdir(r'H:\GraduateFile\\'+area+'\SCL\MosaicSCL') 
#指定工作目录，即存放影像的目录
arcpy.env.workspace = r"H:\GraduateFile\\"+area+"\SCL\MosaicSCL"
filepath=r"H:\GraduateFile\\"+area+"\SCL\MosaicSCL"

###设定三个个研究宁夏贺兰山、新疆吐鲁番和延怀涿的坐标范围
###defined in this order: X-Minimum, Y-Minimum, X-Maximum, Y-Maximum.
rectangle_Hebei="114.988146 40.166336 116.274982 40.626440"
rectangle_Ningxia="105.786945 37.865566 106.246974 38.831627"
rectangle_Tulufan="88.283308 42.586040 90.770113 43.147551"

###获取唯一时间的时间列表
print('正在执行裁剪影像的列表....')
filenames = glob.glob('*.tif')


#指定输出文件夹
outFolder = r"H:\GraduateFile\\"+area+"\SCL\ClipSCL"

for day in filenames:
    print('run ',day,' moasic...')
    outfilename=day
    if 'T' in day:
        outfilename=day.split('_')[2].split('T')[0]+'.tif'

    ###执行裁剪操作
    try:
        arcpy.Clip_management(filepath+'\\'+day,rectangle_Tulufan,outFolder+'\\'+outfilename, "#", "#", "NONE", "NO_MAINTAIN_EXTENT")
        print(outfilename)
        
    except:
        print arcpy.GetMessages()


print('完成裁剪')
