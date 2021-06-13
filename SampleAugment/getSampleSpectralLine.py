# -*- coding: utf-8 -*-
"""
Created on Fri Jun 11 20:48:21 2021

@author: LW
"""
from osgeo import gdal,gdal_array,osr, ogr
import numpy as np
import glob
import os,sys 
from skimage import io
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

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
    #times=imagePath.split('.')[0]
#    testdate=datetime.date(int(times[0:4]),int(times[4:6]),int(times[6:8]))
#    day=out_day_by_date(testdate)
    #day=int(times)
    #打开栅格数据
    ds =io.imread(imagePath)
    rowC,columnC=ds.shape[0],ds.shape[1]
    for n in range(len(pixellist)):
        if pixellist[n][1][1]>=rowC or pixellist[n][1][0]>=columnC:
            pixellist[n].append([])
        else:
            value=ds[pixellist[n][1][1]][pixellist[n][1][0]]
            value=list(value)
#        ndvi=int(((value[3]-value[2])/(value[3]+value[2]))*10000)
#        value.append(ndvi)
#        value.append(day)
            pixellist[n].append(value)
    del ds
    return pixellist

def plot(xlabel,y,crop):
    fig = plt.figure()  # 创建画布
    ax = plt.subplot()  # 创建作图区域
    # 缺口表示50%分位点的置信区间，缺口太大表示分布太分散了
    #showfliers：是否显示异常值，默认显示；widths：指定箱线图的宽度，默认为0.5；notch：是否是凹口的形式展现箱线图，默认非凹口；patch_artist：是否填充箱体的颜色；
    ax.plot([1,2,3,4,5,6,7], y, linewidth=4)
    # 修改x轴下标
#    ax.set_xticks(x)
#    ax.set_xticklabels(x)
    # 显示y坐标轴的底线
    plt.rcParams['figure.figsize'] = (19.0, 9.0) 
    plt.ylabel('Reflectance', fontsize=25)
    
    tw=1
    x_major_locator=ticker.MultipleLocator(tw)
    y_major_locator=ticker.MultipleLocator(500)
    axc=plt.gca()
    axc.xaxis.set_major_locator(x_major_locator)
    axc.yaxis.set_major_locator(y_major_locator)
    axc.set_xticklabels(xlabel)
    plt.xlabel("Bands", fontsize=20) #
    plt.xticks(rotation=90,fontsize=20)
    plt.yticks(fontsize=20)  #设置y轴刻度的大小
    plt.grid(axis='y')
#    plt.show()
    plt.savefig('H:\GraduateFile\Hebei\ExtendSample\LineExtendSampleResult\\'+str(crop)+'_line_20200919.png', dpi=300)#指定分辨率

def mulitiPlot(xlabel,y):
    fig = plt.figure()  # 创建画布
    ax = plt.subplot()  # 创建作图区域
    # 缺口表示50%分位点的置信区间，缺口太大表示分布太分散了
    #showfliers：是否显示异常值，默认显示；widths：指定箱线图的宽度，默认为0.5；notch：是否是凹口的形式展现箱线图，默认非凹口；patch_artist：是否填充箱体的颜色；
    ax.plot([1,2,3,4,5,6,7], y[0], linewidth=4, mec='r',label='grape')
    ax.plot([1,2,3,4,5,6,7], y[1], linewidth=4, mec='g',label='greenhouse')
    ax.plot([1,2,3,4,5,6,7], y[2], linewidth=4, mec='y',label='forest')
    ax.plot([1,2,3,4,5,6,7], y[3], linewidth=4, mec='o',label='bareland')
    # 修改x轴下标
#    ax.set_xticks(x)
#    ax.set_xticklabels(x)
    # 显示y坐标轴的底线
    plt.rcParams['figure.figsize'] = (19.0, 9.0) 
    plt.ylabel('Reflectance', fontsize=25)
    
    tw=1
    x_major_locator=ticker.MultipleLocator(tw)
    y_major_locator=ticker.MultipleLocator(500)
    axc=plt.gca()
    axc.xaxis.set_major_locator(x_major_locator)
    axc.yaxis.set_major_locator(y_major_locator)
    axc.set_xticklabels(xlabel)
    plt.xlabel("Bands", fontsize=20) #
    plt.xticks(rotation=90,fontsize=20)
    plt.yticks(fontsize=20)  #设置y轴刻度的大小
    plt.grid(axis='y')
    plt.legend()
#    plt.show()
#    plt.savefig('H:\GraduateFile\Hebei\ExtendSample\LineExtendSampleResult\\'+'multibands_line_20200919.png', dpi=300)#指定分辨率
#    plt.savefig(r'H:\GraduateFile\Ningxia\ExtendSample\LineExtendSampleResult\multibands_line_20200918.png', dpi=300)
    plt.savefig(r'H:\GraduateFile\Tulufan\ExtendSample\LineExtendSampleResult\multibands_line_20200917.png', dpi=300)

if __name__ == "__main__": 
    
    # 获取输出图像的行列数

#    os.chdir(r'H:\GraduateFile\Hebei\ExtendSample\LineExtendSample')
#    os.chdir(r'H:\GraduateFile\Ningxia\ExtendSample\LineExtendSample')
    os.chdir(r'H:\GraduateFile\Tulufan\ExtendSample\LineExtendSample')
    dirList = glob.glob('*.xlsx')
    
    samples=[]
    types=[]
    ####导入样本数据
    for xlsx in dirList:
        print('XLSX is ',xlsx)
        points=np.array(pd.read_excel(xlsx))
        for i in range(len(points)):
            samples.append([[points[i][1],points[i][2]]])
            types.append(int(points[i][3]))
        print('sample lenght is ', len(samples))
    
    ####获取行列号
    
    ###获取值
#    tifPaths=r'H:\GraduateFile\Hebei\Bands\Bands10mProjClip\20200919.tif'
#    tifPaths=r'H:\GraduateFile\Ningxia\Bands\Bands10mProj\20200918.tif'
    tifPaths=r'H:\GraduateFile\Tulufan\Bands\Bands10mProjClip\20200917.tif'
    samples=getSampleRowCols(tifPaths,samples)
    samples=getImagePixel(tifPaths,samples)
    
    ###出图
    ys=[]
    ctypes=['grape','greenhouse','forest','bareland']
    for tindex in range(len(ctypes)):
        typeindex=tindex+1
        tvalue=[]
        for sindex in range(len(samples)):
            if len(samples[sindex][2])<1:
                continue
            if types[sindex]==typeindex:
                tvalue.append(samples[sindex][2])
        ###导出图
        tvalue=np.array(tvalue)
        tavg=np.average(tvalue, axis=0)
        ys.append(tavg)
    mulitiPlot(['','B','G','R','NIR','RE1','RE2','RE3'],ys)
#        plot(['','B','G','R','NIR','RE1','RE2','RE3'],tavg,ctypes[tindex])
    print('Complete')
    
        
        
        
        


