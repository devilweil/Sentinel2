# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 16:16:13 2021
统计空间尺度上的研究区内的云量和数据丰富度
@author: LW
"""
from osgeo import gdal,gdal_array,osr, ogr
from skimage import io
import os,sys
import glob
from datetime import date
import numpy as np
import pandas as pd 
import math

os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'

    
def getSpatialCloudStatisticByTimeSeries(filePaths,lt,rb):
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

###获得某一天栅格在研究区栅格上的起始行列号
def getColRowByResearchAreaExtent(originDayExtent,researchAreaGeotransform):
    ####extent=(MinLon,MaxLon,MinLat,MaxLat)
    
    lt=world2Pixel(researchAreaGeotransform,originDayExtent[0],originDayExtent[3])
    rb=world2Pixel(researchAreaGeotransform,originDayExtent[1],originDayExtent[2])
    
    return lt,rb

#获取影像的左上角和右下角坐标
def GetExtent(in_fn):
    ds=gdal.Open(in_fn)
    geotrans=list(ds.GetGeoTransform())
    xsize=ds.RasterXSize 
    ysize=ds.RasterYSize
    min_x=geotrans[0]
    max_y=geotrans[3]
    max_x=geotrans[0]+xsize*geotrans[1]
    min_y=geotrans[3]+ysize*geotrans[5]
    ds=None
    return [min_x,max_x,min_y,max_y]

if __name__ == "__main__": 
    
    ###获取研究区的最小外接矩形
#    filepath=r'F:\工作文件\博士研究\研究区域\吐鲁番\Shapefile\tulufanResearchArea.shp'
#    filepath=r'F:\工作文件\博士研究\研究区域\宁夏\NingxiaHelan.shp'
    filepath=r'F:\工作文件\博士研究\研究区域\河北\Shapefile\Huailaixian.shp'
    extents=getExtentByShapefile(filepath)
    print('MinLon,MaxLon,MinLat,MaxLat:',extents)
    
    #设置工作空间
#    os.chdir(r'H:\GraduateFile\Tulufan\SCL\CompositeSCL20m')
#    os.chdir(r'H:\GraduateFile\Ningxia\SCL\ProjectSCL20m')
    os.chdir(r'H:\GraduateFile\Hebei\SCL\CompositeSCL20m')
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
    
    ####创建研究区区域的栅格，通过自定义的仿射变换参数、行列数等
    in_ds=gdal.Open(dateList[0]+'.tif')
    geotrans=list(in_ds.GetGeoTransform())
    width=geotrans[1]
    height=geotrans[5]        
        
    columns=math.ceil((extents[1]-extents[0])/width)+1
    rows=math.ceil((extents[3]-extents[2])/(-height))+1
    print(columns,rows)
    in_band_datatype=in_ds.GetRasterBand(1).DataType
    
    proj= osr.SpatialReference()
    proj.SetWellKnownGeogCS("WGS84")
    
    out_band=np.zeros((rows,columns))
    
    del in_ds
    ####-nondata
    outfile=r'F:\工作文件\博士研究\毕业论文\毕业用图\空值检测\空间尺度云量占比和像元缺失\hebei_SpatialCloudStatistic.tif'
    driver=gdal.GetDriverByName('GTiff')
    out_ds=driver.Create(outfile,columns,rows,1,in_band_datatype)
    out_ds.SetProjection(proj.ExportToWkt())
    geotrans[0]=extents[0]
    geotrans[3]=extents[3]
    out_ds.SetGeoTransform(geotrans)
    
    ####进行空间尺度的云量占比统计和像元缺失
    count=0
    for day in dateList:
        print('正在执行',day,'的云量检测...')
#        if count==1:
#            break
        originDays=day+'.tif'
        originExtend=GetExtent(originDays)
        lt,rb=getColRowByResearchAreaExtent(originExtend,geotrans)
        print('LRow,LCol,RRow,RCol:',lt,rb)
        
        tif=io.imread(originDays)
        tif[tif!=9]=0
        tif[tif==9]=1
#        tif[tif==0]=100
#        tif[tif!=100]=0
#        tif[tif==100]=1
        print(tif.shape)
        ###判断某一天的栅格在研究区栅格左上角起始位
        
        ###判断左上行
        if lt[0]<0:
            tif=tif[abs(lt[0]):tif.shape[0],:]
            lt[0]=0
        if lt[1]<0:
            tif=tif[:,abs(lt[1]):tif.shape[1]]
            lt[1]=0
        if rb[0]>rows:
            tif=tif[0:rows-lt[0],:]
            rb[0]=rows
        if rb[1]>columns:
            tif=tif[:,0:columns-lt[1]]
            rb[1]=columns
        
        tif=tif[0:rb[0],0:rb[1]]
        temp_band=np.zeros((rows,columns))
        if tif.shape[0]<1 or tif.shape[1]<1:
            temp_band=temp_band+1
            continue
        print(lt[0],rb[0],lt[1],rb[1])
        temp_band[lt[0]:lt[0]+tif.shape[0],lt[1]:lt[1]+tif.shape[1]]=temp_band[lt[0]:lt[0]+tif.shape[0],lt[1]:lt[1]+tif.shape[1]]+tif
        out_band=out_band+temp_band
        
        
#        out_band[lt[0]:rb[0],lt[1]:rb[1]]=out_band[lt[0]:rb[0],lt[1]:rb[1]]+tif
        
#        if lt[0]<0:
#            tifRStart=abs(lt[0])
#            rCount=tif.shape[0]-abs(lt[0])
#            if rCount>rows:
#                rCount=rows
#                tifREnd=rCount+abs(lt[0])
#        else:
#            rCount=tif.shape[0]-abs(lt[0])
#            if rCount>rows:
#                tifREnd=rows+abs(lt[0])
#        
#        tifCStart=0
#        tifCEnd=tif.shape[1]
#        if lt[1]<0:
#            tifCStart=abs(lt[1])
#            cCount=tif.shape[1]-abs(lt[1])
#            if cCount>columns:
#                cCount=columns
#                tifCEnd=cCount+abs(lt[1])
#        else:
#            cCount=tif.shape[1]-abs(lt[1])
#            if cCount>columns:
#                tifCEnd=columns+abs(lt[1])
        
        
        
        
        
#        for r in range(tif.shape[0]):
#            print('row ',r)
#            if r+lt[0]<0 or r+lt[0]>=rows:
#                continue
#            for c in range(tif.shape[1]):
#                if c+lt[1]<0 or c+lt[1]>=columns:
#                    continue
#                out_band[r+lt[0]][c+lt[1]]=out_band[r+lt[0]][c+lt[1]]+tif[r][c]
#        
#        
        count=count+1
    outband=out_ds.GetRasterBand(1)   
    outband.WriteArray(out_band)
    del outband,out_ds
    ###保存到Excel、CSV等文件中        
#    np.savetxt(r'H:\GraduateFile\Ningxia\CloudStatistic\statisticCloud.csv', statistic, delimiter = ',', fmt='%s')
#    np.savetxt(r'H:\GraduateFile\Tulufan\CloudStatistic\statisticCloud20210412.csv', statistic, delimiter = ',', fmt='%s')

    
    

    print('Complete')
