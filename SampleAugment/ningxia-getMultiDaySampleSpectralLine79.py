# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 16:47:56 2021
79服务器获取时间序列的多个波段的光谱曲线
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
def getSampleRowCols(imagePath,pixellist,pixeltype):
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
    reTypes=[]
    for f in range(len(pixellist)):
        x = pixellist[f][0][0]
        y = pixellist[f][0][1]
        #获取点位所在栅格的位置
        xOffset = int((x-xOrigin)/pixelWidth)
        yOffset = int((y-yOrigin)/pixelHeight)
        if yOffset>=rows or yOffset<0 or xOffset>=cols or xOffset<0:
            continue
        else:
            rePixellist.append([[xOffset,yOffset]])
            reTypes.append(pixeltype[f])
    del ds
    return rePixellist,reTypes
#根据行列号获取像素值
def getMultiDayImagePixel(imagePath,pixellist):
    #获取当前日期的天数
    times=imagePath.split('.')[0]
#    testdate=datetime.date(int(times[0:4]),int(times[4:6]),int(times[6:8]))
#    day=out_day_by_date(testdate)
    day=int(times)
    
    #打开栅格数据
    ds =io.imread(imagePath)
    rowC,columnC=ds.shape[0],ds.shape[1]
    print('Image shape is ',rowC,columnC)
    for n in range(len(pixellist)):
        value=ds[pixellist[n][0][1]][pixellist[n][0][0]]
        value=list(value)
        if value[3] is None or value[2] is None:
            value.append(np.NaN)
        else:
#            print(value[3],value[2])
            ####判断反射率是否为零
            if value[3]==0 or value[2]==0:
                value.append(np.NaN)
                value[value==0]=np.NaN
            else:
                ndvi=int(((value[3]-value[2])/(value[3]+value[2]))*10000)
                if ndvi>10000 or ndvi<-10000:
                    value.append(np.NaN)
                else:
                    value.append(ndvi)
        value.append(day)
        pixellist[n].append(value)
    del ds
    return pixellist
####按照列进行求均值
def nanAverageClounm(sArray):
    reArrays=[]
    colunms=sArray.shape[1]
    for c in range(colunms):
        ###求取非空元素的均值
        colmean=np.nanmean(sArray[:,c])
        reArrays.append(colmean)
    return np.array(reArrays)
    


def mulitiPlot(xlabel,x,y,bandsname):
    fig = plt.figure()  # 创建画布
    ax = plt.subplot()  # 创建作图区域
    # 缺口表示50%分位点的置信区间，缺口太大表示分布太分散了
    #showfliers：是否显示异常值，默认显示；widths：指定箱线图的宽度，默认为0.5；notch：是否是凹口的形式展现箱线图，默认非凹口；patch_artist：是否填充箱体的颜色；
    ax.plot(x, y[0], linewidth=4, mec='r',label='grape')
    ax.plot(x, y[1], linewidth=4, mec='g',label='greenhouse')
    ax.plot(x, y[2], linewidth=4, mec='y',label='forest')
    ax.plot(x, y[3], linewidth=4, mec='o',label='bareland')
    # 修改x轴下标
#    ax.set_xticks(x)
#    ax.set_xticklabels(x)
    # 显示y坐标轴的底线
    plt.rcParams['figure.figsize'] = (20.0, 11.0) 
    plt.ylabel('Reflectance', fontsize=25)
    
    tw=1
    x_major_locator=ticker.MultipleLocator(tw)
    y_major_locator=ticker.MultipleLocator(500)
    axc=plt.gca()
    axc.xaxis.set_major_locator(x_major_locator)
    axc.yaxis.set_major_locator(y_major_locator)
    axc.set_xticklabels(xlabel)
    plt.xlabel("Bands", fontsize=25) #
    plt.xticks(rotation=90,fontsize=20)
    plt.yticks(fontsize=20)  #设置y轴刻度的大小
    plt.grid(axis='y')
    plt.legend()
#    plt.show()
    plt.savefig('/home/lw/Sample/Hebei/ExtendSample/LineExtendSampleResult/multibands_hebei_'+str(bandsname)+'.png', dpi=300)#指定分辨率
#    plt.savefig(r'/home/lw/Sample/Ningxia/ExtendSampleN48/LineExtendSampleResult/multibands_nningxia_'+str(bandsname)+'.png', dpi=300)
#    plt.savefig(r'/home/lw/Sample/Tulufan/ExtendSample/LineExtendSampleResult/multibands_tulufan_'+str(bandsname)+'.png', dpi=300)

if __name__ == "__main__": 
    
    # 获取样本的坐标和类别

    os.chdir(r'/home/lw/Sample/Hebei/ExtendSample/LineExtendSample')
#    os.chdir(r'/home/lw/Sample/Ningxia/ExtendSampleN48/LineExtendSample')
#    os.chdir(r'/home/lw/Sample/Tulufan/ExtendSample/LineExtendSample')
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
    
    ####获取样本行列号

    tifPaths=r'/mnt/datapool/RemoteSensingData1/LW/GraduateFile/Hebei/Bands10mProjClip/20200919.tif'
#    tifPaths=r'/mnt/datapool/RemoteSensingData1/LW/GraduateFile/Ningxia/Bands10m/20200918.tif'
#    tifPaths=r'/mnt/datapool/RemoteSensingData1/LW/GraduateFile/Tulufan/Bands10mProjClip/20200917.tif'
    samples_new,types_new=getSampleRowCols(tifPaths,samples,types)
    
    ###获取时间序列的多波段光谱值
    os.chdir(r'/mnt/datapool/RemoteSensingData1/LW/GraduateFile/Hebei/Bands10mProjClip')
#    os.chdir(r'/mnt/datapool/RemoteSensingData1/LW/GraduateFile/Ningxia/Bands10m')
#    os.chdir(r'/mnt/datapool/RemoteSensingData1/LW/GraduateFile/Tulufan/Bands10mProjClip')
    dirList = glob.glob('*.tif')
    dirLists=[]
    dirList.sort()
    ####获取时间范围内的影像名称
    i=1
    days=[]
    xdays=['']
    for paths in dirList:
        print('Progress Images Order:'+ str(i))
        #判断当前遥感影像的样本点是否有异常值
        times=paths.split('.')[0]
        day=int(times)
        if day<20200415 or day>20201115:
            continue
        else:
            dirLists.append(paths)
            days.append(i)
            xdays.append(times[4:8])
        i=i+1
    dirLists.sort()
    days.sort()
    ####获取时间范围内的影像
    for paths in dirLists:
        print('Progress Images Order:'+ str(paths))
        samples_new=getMultiDayImagePixel(paths,samples_new)
    
    ###出图
    ys=[[],[],[],[],[],[],[],[]]
    
    ctypes=['grape','greenhouse','forest','bareland']
    for tindex in range(len(ctypes)):
        print('执行重组',ctypes[tindex],'的光谱值')
        typeindex=tindex+1
        tegSample=[]
        for sindex in range(len(samples_new)):
            if len(samples_new[sindex][2])<1:
                continue
            if types[sindex]==typeindex:
                tegSample.append(samples_new[sindex])
        ###进行数组重组
        tvalue=[[],[],[],[],[],[],[],[]]
        for teg in range(len(tegSample)):
            ###重组当前样本数组
            sp=tegSample[teg]
            tempvalue=[[],[],[],[],[],[],[],[]]
            for si in range(1,len(sp)):
                tempvalue[0].append(sp[si][0])   #Blue
                tempvalue[1].append(sp[si][1])   #Green
                tempvalue[2].append(sp[si][2])   #Red
                tempvalue[3].append(sp[si][3])   #NIR
                tempvalue[4].append(sp[si][4])   #RE1
                tempvalue[5].append(sp[si][5])   #RE2
                tempvalue[6].append(sp[si][6])   #RE3
                tempvalue[7].append(sp[si][7])   #NDVI
            ###封装到计算数组中
            tvalue[0].append(tempvalue[0])   #Blue
            tvalue[1].append(tempvalue[1])   #Green
            tvalue[2].append(tempvalue[2])   #Red
            tvalue[3].append(tempvalue[3])   #NIR
            tvalue[4].append(tempvalue[4])   #RE1
            tvalue[5].append(tempvalue[5])   #RE2
            tvalue[6].append(tempvalue[6])   #RE3
            tvalue[7].append(tempvalue[7])   #NDVI
        ###计算每一个子集的均值保存到输出数组
        print('计算重组后',ctypes[tindex],'的光谱值的均值')
        for t in range(len(tvalue)):
            tvalue_t=np.array(tvalue[t])
#            tavg=np.average(tvalue_t, axis=0)
            tavg=nanAverageClounm(tvalue_t)
#            print('打印tavg的shape',tavg)
            ys[t].append(tavg)
    ####根据输出数组进行多波段折线输出
    print('输出多波段折线图')
    print('打印YS的shape',ys)
    mulitiPlot([1],[1],[[1],[1],[1],[1]],'Test')
    bands=['B','G','R','NIR','RE1','RE2','RE3','NDVI']
    for bi in range(len(bands)):
        bandname=bands[bi]
        yarray=ys[bi]
        print('打印',bandname,'的yarray的max',max(yarray[0]),',Days length is ',len(days))
        
        mulitiPlot(xdays,days,yarray,bandname)
#        plot(['','B','G','R','NIR','RE1','RE2','RE3'],tavg,ctypes[tindex])
    print('Complete')
    
        
        
        
        



