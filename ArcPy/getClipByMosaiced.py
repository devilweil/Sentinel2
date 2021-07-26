import glob

import arcpy
import os

area='Tulufan'
os.chdir(r'H:\GraduateFile\\'+area+'\SCL\MosaicSCL') 
#ָ������Ŀ¼�������Ӱ���Ŀ¼
arcpy.env.workspace = r"H:\GraduateFile\\"+area+"\SCL\MosaicSCL"
filepath=r"H:\GraduateFile\\"+area+"\SCL\MosaicSCL"

###�趨�������о����ĺ���ɽ���½���³�����ӻ��õ����귶Χ
###defined in this order: X-Minimum, Y-Minimum, X-Maximum, Y-Maximum.
rectangle_Hebei="114.988146 40.166336 116.274982 40.626440"
rectangle_Ningxia="105.786945 37.865566 106.246974 38.831627"
rectangle_Tulufan="88.283308 42.586040 90.770113 43.147551"

###��ȡΨһʱ���ʱ���б�
print('����ִ�вü�Ӱ����б�....')
filenames = glob.glob('*.tif')


#ָ������ļ���
outFolder = r"H:\GraduateFile\\"+area+"\SCL\ClipSCL"

for day in filenames:
    print('run ',day,' moasic...')
    outfilename=day
    if 'T' in day:
        outfilename=day.split('_')[2].split('T')[0]+'.tif'

    ###ִ�вü�����
    try:
        arcpy.Clip_management(filepath+'\\'+day,rectangle_Tulufan,outFolder+'\\'+outfilename, "#", "#", "NONE", "NO_MAINTAIN_EXTENT")
        print(outfilename)
        
    except:
        print arcpy.GetMessages()


print('��ɲü�')
