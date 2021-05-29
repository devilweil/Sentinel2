# -*- coding: utf-8 -*-
"""
Created on Wed May 12 22:52:06 2021
基于时间序列判别通道的露天葡萄归属度计算方法
@author: LW
"""
from osgeo import gdal,gdal_array,osr, ogr
import numpy as np
import glob
import os,sys 
from skimage import io
import random


def out_day_by_date(date):
    '''
    根据输入的日期计算该日期是在当年的第几天
    '''
    year=date.year
    month=date.month
    day=date.day
    months=[0,31,59,90,120,151,181,212,243,273,304,334]
    if 0<month<=12:
        sum=months[month-1]
    else:
        print("month error")
    sum+=day
    leap=0
    #接下来判断平年闰年
    if(year%400==0) or ((year%4)==0) and (year%100!=0):
    #and的优先级大于or
    #1、世纪闰年:能被400整除的为世纪闰年
    #2、普通闰年:能被4整除但不能被100整除的年份为普通闰年
        leap=1
    if(leap==1) and (month>2):
        sum+=1#判断输入年的如果是闰年,且输入的月大于2月,则该年总天数加1
    return sum

#获取样本点列表
def getSHPPoint(pointPath):
    #############获取矢量点位的经纬度
    #设置driver
    driver=ogr.GetDriverByName('ESRI Shapefile')
    #打开矢量
    ds=driver.Open(pointPath, 0)
    if ds is None:
        print('Could not open ' +'shapefile')
        sys.exit(1)
        #获取图层
    layer = ds.GetLayer()

    #获取要素及要素地理位置
    xyValues = []
#    yValues = []
    feature = layer.GetNextFeature()
    while feature:
        geometry = feature.GetGeometryRef()
        x = geometry.GetX()
        y = geometry.GetY()
        xyValues.append([x,y])
#        yValues.append(y)  
        feature=layer.GetNextFeature()    
    del ds,driver
    return xyValues
#获取样本点的行列号
def getSampleRowCols(imagePath,pixellist):
    #打开栅格数据
    ds = gdal.Open(imagePath,gdal.GA_ReadOnly)
    if ds is None:
        print('Could not open image')
        sys.exit(1)
    #获取行列、波段
#    rows = ds.RasterYSize
#    cols = ds.RasterXSize
#    bands = ds.RasterCount
    #获取放射变换信息
    transform = ds.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]
    #
    for f in range(len(pixellist)):
        x = pixellist[f][0][0]
        y = pixellist[f][0][1]
        #获取点位所在栅格的位置
        xOffset = int((x-xOrigin)/pixelWidth)
        yOffset = int((y-yOrigin)/pixelHeight)
        pixellist[f].append([xOffset,yOffset])
    del ds
    return pixellist

#根据行列号获取像素值
def getImagePixel(imagePath,pixellist):
    
    #获取当前日期的天数
    times=imagePath.split('.')[0]
#    testdate=datetime.date(int(times[0:4]),int(times[4:6]),int(times[6:8]))
#    day=out_day_by_date(testdate)
    day=int(times)
    #打开栅格数据
    ds =io.imread(imagePath)
    rowT,colT=ds.shape[0],ds.shape[1]
    for n in range(len(pixellist)):
        value=ds[pixellist[n][1][1]][pixellist[n][1][0]]
        value=list(value)
        ndvi=int(((value[3]-value[2])/(value[3]+value[2]))*10000)
        value.append(ndvi)
#        value.append(day)
        pixellist[n].append([day,value])
#    ds = gdal.Open(imagePath,gdal.GA_ReadOnly)
#    if ds is None:
#        print('Could not open image')
#        sys.exit(1)
#    #根据现有的行列号进行值的获取
#    for n in range(len(pixellist)):
#        band = ds.GetRasterBand(1)
#        data = band.ReadAsArray(pixellist[n][1][0], pixellist[n][1][1],1,1)
#        value = data[0,0]
##        if value==1.5 or value==-1.5:
##            continue
#        pixellist[n].append([day,value])
    del ds
    return rowT,colT

def getImagePixels(imagePath,pixellist):
    #获取当前日期的天数
#    times=imagePath.split('_')[0]
#    testdate=datetime.date(int(times[0:4]),int(times[4:6]),int(times[6:8]))
#    day=out_day_by_date(testdate)
    #打开栅格数据
    ds = gdal.Open(imagePath,gdal.GA_ReadOnly)
    if ds is None:
        print('Could not open image')
        sys.exit(1)
    #根据现有的行列号进行值的获取
    for n in range(len(pixellist)):
        band = ds.GetRasterBand(1)
        data = band.ReadAsArray(pixellist[n][1][0], pixellist[n][1][1],1,1)
        value = data[0,0]
        pixellist[n].append([n,value])
    del ds

#根据样本，获取每一天的NDVI的均值和加减1倍标准差的值域范围
def getMeanAndSTD(pixelList):
    returnList=[]
    viname=['B','G','R','NIR','RE1','RE2','RE3','NDVI']
    #按照列的个数循环列数
    for j in range(2,len(pixelList[0])):
        day,relist=getArrayIndexToList(pixelList,j)
        element=[day]
        for vindex in range(len(viname)):
            viValue=[]
            for x in range(len(relist)):
                viValue.append(relist[x][vindex])
        
            mean=np.mean(viValue)
            std=np.std(viValue)
            element.append([mean-std,mean+std])
        returnList.append(element)
    return returnList

#按照列位置index获取天数和值列表   
def getArrayIndexToList(listes,index):
    relist=[]
    day=listes[0][index][0]
    
    for r in range(len(listes)):
#        if math.isnan(listes[r][index][1]):
#            continue
#        else:
#            #去除异常值
#            if listes[r][index][1]==1.5 or listes[r][index][1]==-1.5:
#                continue
#            else:
        relist.append(listes[r][index][1])

    return day,relist

#切分样本点，按照1:4的比例划分为测试和训练样本
def splitSample(listed):
    test=random.sample(listed,int(len(listed)*0.2))
    train=[]
    for i in range(len(listed)):
        #用于判断是否包含在测试样本里，1包含，0不包含
        isTrue=0  
        for j in range(len(test)):
            if listed[i][0] == test[j][0]:
                isTrue=1
                break
            else:
                isTrue=0
        if isTrue==0:
            train.append(listed[i])
    return test,train
#计算不同占比的准确度
def getScaling(images,scale,samples):
    returnScale=[]
    for i in range(len(scale)):
        count=0
        for j in range(len(samples)):
            xy=samples[j][1]
            if images[xy[0]][xy[1]]>=scale[i]:
                count=count+1
            else:
                continue
        returnScale.append(count/(len(samples)))
    return returnScale
def saveImage(tif,filename,filename_out1,clos,rows):
#    filename="H:/MODIS反演生育期/2018nian/2018nian/NDVI_2018001.h26v04.tif"
    dataj=gdal.Open(filename)
    if dataj is None:
        print('Could not open'+filename)
    proj=dataj.GetProjection()
    geotrans=dataj.GetGeoTransform()
    #创建栅格数据
    driver=gdal.GetDriverByName("GTiff")
    datat1_out=driver.Create(filename_out1,clos,rows,1,gdal.GDT_Float64)#GDT_Float32
    datat1_out.SetGeoTransform(geotrans)
    datat1_out.SetProjection(proj)
#    for b in range(8):
#        band1_out=datat1_out.GetRasterBand(b+1)
#        band1_out.WriteArray(tif[:,:,b])
    band1_out=datat1_out.GetRasterBand(1)
    band1_out.WriteArray(tif)
    dataj.FlushCache()
    datat1_out.FlushCache()
    del dataj
    del datat1_out


if __name__ == "__main__": 
    
    # 获取输出图像的行列数
    ###
    os.chdir(r'/mnt/datapool/RemoteSensingData1/LW/GraduateFile/Tulufan/Bands10mProjClip')
#    os.chdir(r'/mnt/datapool/RemoteSensingData1/LW/GraduateFile/Hebei/Bands10mProjClip')
#    os.chdir(r'/mnt/datapool/RemoteSensingData1/LW/GraduateFile/Ningxia/Bands10m')
    
    dirList = glob.glob('*.tif')
    dirLists=[]
    ####获取时间范围内的影像
    i=1
    for paths in dirList:
        print('Progress Images Order:'+ str(i))
        #判断当前遥感影像的样本点是否有异常值
        times=paths.split('.')[0]
        day=int(times)
        if day<20200415 or day>20201115:
            continue
        else:
            dirLists.append(paths)
        i=i+1
    
    dirLists.sort()
    pointPath=r'/home/lw/Sample/Tulufan/originSampleRasterToPoint/tulufangrapeparcel-20210429.shp'
#    pointPath=r'/home/lw/Sample/Hebei/originSampleRasterToPoint/hebeigrapeparcel-20210429.shp'
#    pointPath=r'/home/lw/Sample/Ningxia/originSampleRasterToPoint/ningxiagrapeparcel-projutm48-points-20210429.shp'
#    pointPath=r'E:\SentinelData\OpenStreet\roads-proj.shp'
    #获取矢量的点数
    xyVal=getSHPPoint(pointPath)
    #同时把数据进行划分，一部分验证，一部分训练，按照1:4的比例划分
#    tests,trains=splitSample(xyVal)
    row = len(xyVal)
#    row1 = len(trains)
#    row2 = len(tests)
    #构建存储样本的像素的数组
    pixelList =[] #np.zeros((row,clo,spices))
    for j in range(row):
        pixelList.append([xyVal[j]])
#    pixelList =[] #np.zeros((row,clo,spices))
#    for j in range(row1):
#        pixelList.append([trains[j]])
#    testPixelList =[] #np.zeros((row,clo,spices))
#    for j in range(row2):
#        testPixelList.append([tests[j]])
    #计算出测试和训练样本点所在的行列号
    tests=getSampleRowCols(dirLists[0],pixelList)
#    getSampleRowCols(dirList[0],testPixelList)

    #循环获取栅格像素
    ####记录行列号，用于求最大的
    rowlist=[]
    collist=[]
    i=1
    for paths in dirLists:
        print('Progress Images Order:'+ str(i))
#        if i==2:
#            break
        rowT,colT=getImagePixel(paths,pixelList)
        rowlist.append(rowT)
        collist.append(colT)
        print('rowT,colT are ',rowT,colT)
        i=i+1

    #计算每一天的均值和标准差，获取1倍标准差的值域范围
    ###[[day1,[],[],...,[]],[day2,[],[],...,[]]...,[dayN,[],[],...,[]]]
    meanAndSTD=getMeanAndSTD(pixelList)
#    print(' MeanAndStad is saving... ')
#    np.savetxt('E:\SentinelData\ASampleExpansion\MeanAndStad'+typs+'.csv', meanAndSTD2, delimiter = ',')
    #读取每一景影像，进行NDVI值域范围，在这个范围内的是葡萄地
#    maskimgs=io.imread(dirLists[0])
#    rowss=maskimgs.shape[0]
#    cols=maskimgs.shape[1]
    #存储导出的印象
#    returnImage=np.zeros((rowss,cols))
    #存储求和的影像
    rowss=max(rowlist)
    cols=max(collist)
    sumImage=np.zeros((rowss,cols,8))
#    sumImage.astype(int)
    #循环所有的影像进行求曲线是否在范围内
    i=0
    for dpath in dirLists:
        
        times=dpath.split('.')[0]
        days=int(times)
        originTif= io.imread(dpath)
        originTif.astype(float)
        
        ###计算植被指数
        ndvi=((originTif[:,:,3]-originTif[:,:,2])/(originTif[:,:,3]+originTif[:,:,2]))*10000
        
        ndvi[np.isnan(ndvi)] = 99999
        originTif[np.isnan(originTif)] = 99999
#        ndviPixelTif=ndviPixelTifs.where(ndviPixelTifs.notnull(), 20)
        dayAndY=meanAndSTD[i]
        print('计算阈值范围到第'+str(i)+'景,天数为第'+str(dayAndY[0])+'天')
#        ndviPixelTif[(ndviPixelTif<=dayAndY[1])|(ndviPixelTif>=dayAndY[2])]=3
        for fl in range(7):
            originTif[:,:,fl][(originTif[:,:,fl]>=dayAndY[fl+1][0])&(originTif[:,:,fl]<=dayAndY[fl+1][1])]=float(1)
            originTif[:,:,fl][originTif[:,:,fl]!=1]=0
            sumImage[0:originTif.shape[0],0:originTif.shape[1],fl]=sumImage[0:originTif.shape[0],0:originTif.shape[1],fl]+originTif[:,:,fl]
        
        ndvi[(ndvi>=dayAndY[8][0])&(ndvi<=dayAndY[8][1])]=float(1)
        ndvi[ndvi!=1]=0
        
        sumImage[0:ndvi.shape[0],0:ndvi.shape[1],7]=sumImage[0:ndvi.shape[0],0:ndvi.shape[1],7]+ndvi
        print(sumImage.shape)
        i=i+1
        del ndvi,ndviPixelTif
    
    
    sumImages=sumImage/(len(dirLists))
    print('Image count is ',len(dirLists))

    viname=['B','G','R','NIR','RE1','RE2','RE3','NDVI']
    for vi in range(len(viname)):
        print('Band is ',viname[vi])
        outfilename=r'/home/lw/Sample/Tulufan/Reuslt/tulufan_'+viname[vi]+'_singlebelongdegree.tif'
#        outfilename=r'/home/lw/Sample/Hebei/Reuslt/hebei_'+viname[vi]+'_singlebelongdegree.tif'
#        outfilename=r'/home/lw/Sample/Ningxia/Reuslt/nignxia_'+viname[vi]+'_singlebelongdegree.tif'
        saveImage(sumImages[:,:,vi],dirLists[0],outfilename,cols,rowss)
    #导出影像
#    filenameout=r'/home/lw/Sample/Ningxia/Reuslt/ningxia_belongdegree_Result.tif'
#    saveImage(sumImages,dirLists[0],filenameout,cols,rowss)
    #
    
    #结束
    print('Complete')
    del rowss,cols,xyVal
