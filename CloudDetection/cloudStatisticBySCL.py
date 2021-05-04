# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 15:54:56 2021
根据场景分类统计研究区的云量
@author: LW
"""
from osgeo import gdal,gdal_array,osr, ogr
from skimage import io
import os,sys
import glob
from datetime import date
import numpy as np
import pandas as pd 
from matplotlib import pyplot as plt 
import matplotlib.ticker as ticker

os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'

def showBoxplot(data):
    #进行箱线图的出图并保存
    dt = pd.DataFrame(data) 
    dt.boxplot(showfliers=False,patch_artist=True,widths=0.65,capprops=dict(color='blue',linewidth=3)) # 这里，pandas自己有处理的过程，很方便哦。
    plt.rcParams['figure.figsize'] = (32.0, 14.0) # 设置figure_size尺寸
    plt.ylabel('Value', fontsize=30)
    plt.xlabel("Bands", fontsize=30) #
#    x_major_locator=ticker.MultipleLocator(5)
    #y_major_locator=ticker.MultipleLocator(2)
    #把x轴的刻度间隔设置为1，并存在变量里NDVI CTVI GNADVI:0.2  DVI: 500  EVI:2 TVI:10000  NDWI:5 RVI:2
#    ax=plt.gca()
#    ax.xaxis.set_major_locator(x_major_locator)
#    ax.set_xticklabels(xlabel)
    plt.xticks(rotation=90,fontsize=25)
    plt.yticks(fontsize=25)
    plt.grid(axis="x")
    plt.show()    

def showPlot(x,data):
    
    data=np.array(data)
    y1=data[:,0]
    y2=data[:,1]
    y3=data[:,2]
    y4=data[:,3]
    y5=data[:,4]
    
    l1=plt.plot(x,y1,'r--',label='C7')
    l2=plt.plot(x,y2,'g--',label='C8')
    l3=plt.plot(x,y3,'b--',label='C9')
    l4=plt.plot(x,y3,'r--',label='C10')
    l5=plt.plot(x,y3,'g--',label='AALL')
    
    plt.plot(x,y1,'ro-',x,y2,'g+-',x,y3,'b^-',x,y4,'ro-',x,y5,'g+-')
    plt.title('The Lasers in Three Satatistic')
    plt.legend()

def showSingleLinePlot(x,data):
    
    data=np.array(data)
    y=data[:,2]
    
    plt.plot(x,y,'ro-')
    plt.title('The Lasers in Three Satatistic')
    plt.rcParams['figure.figsize'] = (32.0, 14.0) # 设置figure_size尺寸
    plt.ylabel('Value', fontsize=30)
    plt.xlabel("Bands", fontsize=30) 
    plt.xticks(rotation=90,fontsize=25)
    plt.yticks(fontsize=25)
    plt.grid(axis="x")
    plt.legend()

def getCSAndNodataTimeSeries(filePaths,lt,rb):
    ###根据矢量格式的研究区计算获得的像元个数
    pixelCount=(rb[0]-lt[0])*(rb[1]-lt[1])
    # 打开栅格数据集
    tif=io.imread(filePaths)
    if lt[0]<0:
        lt[0]=0
    if lt[1]<0:
        lt[1]=0
    ###判断TIFF的维数
    tf_height, tf_width, tf_band= (0,0,0)
    
    if len(tif.shape)==3:
        tf_height, tf_width, tf_band= tif.shape
        tif=tif[lt[0]:rb[0],lt[1]:rb[1],:]
        tif=tif[:,:,0]
    else:
        tf_height, tf_width= tif.shape
        tif=tif[lt[0]:rb[0],lt[1]:rb[1]]
    
    print('tf_height, tf_width is ',tf_height, tf_width)
    ###计算云量和缺失数量
    if tf_height<1 or tf_width<1:
        return [100,0]
    
    sumCount0=0
    if np.sum(tif==0) is None:
        sumCount0=0
    else:
        sumCount0=np.sum(tif==0)

    count9=0
    if np.sum(tif==9) is not None:
        count9=int((np.sum(tif==9)/((tf_height*tf_width)-sumCount0))*100)
    
    count0=int(((pixelCount-np.sum(tif!=0))/pixelCount)*100)
    
    
    return [count0,count9]    
def getCloudStatistic(filePaths,lt,rb):
    # 打开栅格数据集
    tif=io.imread(filePaths)
    
    #####获取研究区的SCL数据
    if lt[0]<0:
        lt[0]=0
    if lt[1]<0:
        lt[1]=0
        
    tif=tif[lt[0]:rb[0],lt[1]:rb[1]]
    tf_height, tf_width= tif.shape
    print(tf_height, tf_width)
    ###统计SCL图层像素值7、8、9和10的占比
    
    count7=int((np.sum(tif==7)/(tf_height*tf_width))*100)
    count8=int((np.sum(tif==8)/(tf_height*tf_width))*100)
    count9=int((np.sum(tif==9)/(tf_height*tf_width))*100)
    count10=int((np.sum(tif==10)/(tf_height*tf_width))*100)
    cloudPercent=int(((np.sum(tif==7)+np.sum(tif==8)+np.sum(tif==9)+np.sum(tif==10))/(tf_height*tf_width))*100)
#    print(cloudPercent)
    return [count7,count8,count9,count10,cloudPercent]
    
def getExtentByShapefile(filepath):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(filepath,0)
    if ds is None:
        print("Could not open", filepath)
        sys.exit(1)
    layer = ds.GetLayer()
    #获取范围
    extent = layer.GetExtent()
    
    del ds,driver
    return extent

####经纬度转行列号
def world2Pixel(geotransform, x, y):
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    line = int((y-originY)/pixelHeight)+1
    column = int((x-originX)/pixelWidth)+1
    return [line,column]
####行列号转经纬度
def pixel2World(geotransform, line, column):
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    x = column*pixelWidth + originX - pixelWidth/2
    y = line*pixelHeight + originY - pixelHeight/2
    return [x,y]


def getResearchColRowByExtent(extent,imgPath):
    ####extent=(MinLon,MaxLon,MinLat,MaxLat)
    
    ###打开遥感影像
    ds = gdal.Open(imgPath)
    geotransform = ds.GetGeoTransform()
    
    lt=world2Pixel(geotransform,extent[0],extent[3])
    rb=world2Pixel(geotransform,extent[1],extent[2])
    
    del ds,geotransform
    return lt,rb
    

if __name__ == "__main__": 
    
    ###获取研究区的最小外接矩形
    filepath=r'F:\工作文件\博士研究\研究区域\吐鲁番\Shapefile\tulufanResearchArea.shp'
#    filepath=r'F:\工作文件\博士研究\研究区域\宁夏\NingxiaHelan.shp'
    extents=getExtentByShapefile(filepath)
    print('MinLon,MaxLon,MinLat,MaxLat:',extents)
    
    #设置工作空间
    os.chdir(r'H:\GraduateFile\Tulufan\SCL\CompositeSCL20m')
#    os.chdir(r'H:\GraduateFile\Ningxia\SCL\ProjectSCL20m')
    filename = glob.glob('*.tif')
    dateList=[]
    print('正在执行获取唯一时间的时间列表....')
    for filePath in filename:
        time=filePath.split('.')[0]
        if time in dateList:
            continue
        else:
            dateList.append(time)
    print('按照时间排序后查询到对应文件进行云量统计')
    dateList.sort(reverse = False)
    
    statistic=[]
    
    for day in dateList:
        print('正在执行',day,'的云量检测...')
        originDays=day+'.tif'
        lt,rb=getResearchColRowByExtent(extents,originDays)
        print(lt,rb)
        cloudperc=getCloudStatistic(originDays,lt,rb)
        print(cloudperc)
        cloudperc.append(day)
        statistic.append(cloudperc)
    
    
    
    
        
    ###出箱线图
#    showBoxplot(statistic)
    ###折线图

        
    ###保存到Excel、CSV等文件中        
#    np.savetxt(r'H:\GraduateFile\Ningxia\CloudStatistic\statisticCloud.csv', statistic, delimiter = ',', fmt='%s')
    np.savetxt(r'H:\GraduateFile\Tulufan\CloudStatistic\statisticCloud20210412.csv', statistic, delimiter = ',', fmt='%s')


    
    showSingleLinePlot(dateList,statistic)
    
    

    print('Complete')
