import arcpy
import os

area='Tulufan'
os.chdir(r'H:\GraduateFile\\'+area+'\Bands\Bands10mMosaic') 
#指定工作目录，即存放影像的目录
arcpy.env.workspace = r"H:\GraduateFile\\"+area+"\Bands\Bands10mMosaic"
filepath=r"H:\GraduateFile\\"+area+"\Bands\Bands10mMosaic"

###获取唯一时间的时间列表
print('获取执行投影影像的列表....')
filenames = glob.glob('*.tif')


#指定输出文件夹
outFolder = r"H:\GraduateFile\\"+area+"\Bands\Bands10mProj"

for day in filenames:
    print('run ',day,' proj...')
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
