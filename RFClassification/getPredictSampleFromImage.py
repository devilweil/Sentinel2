# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 20:12:40 2021
生成分类所需的预测样本
@author: LW
"""

from osgeo import gdal,gdal_array,osr, ogr
import os,sys 
import glob
import numpy as np
from skimage import io

def getSHPPointByField(pointPath,fieldname):
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
        x0 = geometry.GetX()
        y0 = geometry.GetY()
        gcode=feature.GetField(fieldname)
        xyValues.append([[x0,y0],[-1,-1],[]])
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
    rows = ds.RasterYSize
    cols = ds.RasterXSize
#    bands = ds.RasterCount
    #获取放射变换信息
    transform = ds.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]
    ####定义返回的数据
    rePixellist=[]
#    reTypes=[]
    for f in range(len(pixellist)):
        x = pixellist[f][0][0]
        y = pixellist[f][0][1]
        #获取点位所在栅格的位置
        xOffset = int((x-xOrigin)/pixelWidth)
        yOffset = int((y-yOrigin)/pixelHeight)
#        pixellist[f][1][0]=xOffset
#        pixellist[f][1][1]=yOffset
        if yOffset>=rows or yOffset<0 or xOffset>=cols or xOffset<0:
            continue
        else:
            rePixellist.append(pixellist[f])
            lens=len(rePixellist)
            rePixellist[lens-1][1][0]=xOffset
            rePixellist[lens-1][1][1]=yOffset
#            reTypes.append(pixeltype[f])
    del ds
    return rePixellist

###根据输入的两个数据组进行波段值提取
def getImageValue(imagePath,pixellist1):
    ###定义返回的值
#    reArray1=[]
#    reArray2=[]
    #打开栅格数据
    ds =io.imread(imagePath)
    viArray,viArray_max=calImageVI(ds)
    rowC,columnC=ds.shape[0],ds.shape[1]
    print('Image shape is ',rowC,columnC)
    ###读取训练样本的波段之数据
    for n in range(len(pixellist1)):
        value=ds[pixellist1[n][1][1]][pixellist1[n][1][0]]
        value=list(value)
        for vi in range(len(viArray)):
            viValue1=viArray[vi][pixellist1[n][1][1]][pixellist1[n][1][0]]
            if np.isnan(viValue1)==False:
                pixellist1[n][2].append(viValue1)
            else:
                pixellist1[n][2].append(viArray_max[vi])
#        reArray1.append(value)
    
    del ds
    
    return pixellist1

####计算多植被指数
def calImageVI(imgs):
    reViArray=[]
    reViArray_Max=[]
    B=imgs[:,:,0]  #获取B2 Blue的图层
    G=imgs[:,:,1]  #获取B3 Green的图层
    R=imgs[:,:,2]  #获取B4 Red的图层
    NIR=imgs[:,:,3]  #获取B8 NIR的图层
    ###ndvi
    ndvi=(NIR-R)/(NIR+R)
    ndvi[np.isnan(ndvi)]=1.5
    ndvi[ndvi>1]=1.5
    ndvi[ndvi<-1]=-1.5
    print('NDVI shape ',ndvi.shape)
    reViArray.append(ndvi)
    reViArray_Max.append(np.nanmax(ndvi))
    del ndvi
    ###ndwi:
    ndwi=(G-NIR)/(G+NIR)
    print('ndwi shape ',ndwi.shape)
    reViArray.append(ndwi)
    reViArray_Max.append(np.nanmax(ndwi))
    del ndwi
    ###rvi=NIR/R
    rvi=NIR/R
    print('rvi shape ',rvi.shape)
    reViArray.append(rvi)
    reViArray_Max.append(np.nanmax(rvi))
    del rvi
    #calculate GNDVI
    gndvi=(NIR-G)/(NIR+G)
    print('gndvi shape ',gndvi.shape)
    reViArray.append(gndvi)
    reViArray_Max.append(np.nanmax(gndvi))
    del gndvi
    #calculate TVI 
    tvi=60*(NIR-G)-100*(R-G)
    print('tvi shape ',tvi.shape)
    reViArray.append(tvi)
    reViArray_Max.append(np.nanmax(tvi))
    del tvi
    #calculate DVI 
    dvi=NIR-R
    print('dvi shape ',dvi.shape)
    reViArray.append(dvi)
    reViArray_Max.append(np.nanmax(dvi))
    del dvi
    #calculate CTVI
    ndvi=(NIR-R)/(NIR+R)
    ndvi[ndvi > 1] = 3  # 过滤异常值，NDVI的范围是[-1,1]
    ndvi[ndvi <-1] = -3  # 过滤异常值
    ndvi=np.array([i+0.5 for i in ndvi])
    ndviabs=np.array([abs(i+0.5) for i in ndvi])
    ndviabssqrt=np.array([i**0.5 for i in ndviabs])
    
    ctvi=(ndvi*ndviabssqrt)/ndviabs
    print('ctvi shape ',ctvi.shape)
    reViArray.append(ctvi)
    reViArray_Max.append(np.nanmax(ctvi))
    del ctvi
    return reViArray,reViArray_Max


if __name__ == "__main__":

    ###获取预测样本
    shp=r'/home/lw/Sample/Hebei/ImageSegmentation/SegmentationPoint/hebei400105point.shp'
    print('Loading '+shp+' sample')
    samples = getSHPPointByField(shp,'ORIG_FID')
    ###读取值
    os.chdir(r'/mnt/datapool/RemoteSensingData1/LW/GraduateFile/Hebei/Bands10mProjClip')
#    os.chdir(r'/mnt/datapool/RemoteSensingData1/LW/GraduateFile/Ningxia/Bands10m')
#    os.chdir(r'/mnt/datapool/RemoteSensingData1/LW/GraduateFile/Tulufan/Bands10mProjClip')
    tifLists=glob.glob('*.tif')
    tifLists.sort()
    for tifs in tifLists:
        print('正在处理：',tifs)
        dates=int(tifs.split('.')[0])
        if dates<20200415 or dates>20201115:
            continue
        else:
            samples=getSampleRowCols(tifs,samples)
    
            ###获取样本的影像波段值
            samples=getImageValue(tifs,samples)
        
    
    ###重组成为一个可以存为CSV的数组
    x_train=[]
    for p in samples:
        x_train.append(p[2])
    
    ###存储为一个csv
    print('保存Predict的样本....')
    save_path=r'/home/lw/Sample/Hebei/OptimizeRFResult/PredictSample/'
#    save_path=r'/home/lw/Sample/Ningxia/OptimizeRFResult/XYSample/'
#    save_path=r'/home/lw/Sample/Tulufan/OptimizeRFResult/XYSample/'
    np.savetxt(save_path+'x_predict.csv', x_train, delimiter = ',')
    
    print('Finish')
    
    
    

