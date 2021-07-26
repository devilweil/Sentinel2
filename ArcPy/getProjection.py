import arcpy
import os

area='Tulufan'
os.chdir(r'H:\GraduateFile\\'+area+'\Bands\Bands10mMosaic') 
#ָ������Ŀ¼�������Ӱ���Ŀ¼
arcpy.env.workspace = r"H:\GraduateFile\\"+area+"\Bands\Bands10mMosaic"
filepath=r"H:\GraduateFile\\"+area+"\Bands\Bands10mMosaic"

###��ȡΨһʱ���ʱ���б�
print('��ȡִ��ͶӰӰ����б�....')
filenames = glob.glob('*.tif')


#ָ������ļ���
outFolder = r"H:\GraduateFile\\"+area+"\Bands\Bands10mProj"

for day in filenames:
    print('run ',day,' proj...')
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
