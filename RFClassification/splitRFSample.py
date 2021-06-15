# -*- coding: utf-8 -*-
"""
Created on Tue Jun 15 16:05:29 2021
进行样本划分储存，train：test：verify=6:2:2，根据地块的ID进行划分；train：test=7:3，根据地块的ID进行划分
@author: LW
"""
from osgeo import gdal,gdal_array,osr, ogr
import os,sys 
import glob
import numpy as np
import random
from skimage import io
import xlwt

from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

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
        x0 = geometry.GetX()
        y0 = geometry.GetY()
        gcode=feature.GetField('GRID_CODE')
        xyValues.append([x0,y0,gcode])
#        yValues.append(y)  
        feature=layer.GetNextFeature()    
    del ds,driver
    return xyValues


if __name__ == "__main__":
    #获取样本点
#    os.chdir(r'H:\GraduateFile\Hebei\ExtendSample\ClassificationSamplePoint')
#    os.chdir(r'H:\GraduateFile\Ningxia\ExtendSampleN48\ClassificationSamplePoint')
    os.chdir(r'H:\GraduateFile\Tulufan\ExtendSample\ClassificationSamplePoint')

    
    shpLists=glob.glob('*.shp')
    
    for shp in shpLists:
        print('Loading '+shp+' sample')
        samples = getSHPPoint(shp)
        ###进行样本划分train：test：verify=6:2:2，根据地块的ID进行划分
        ###进行样本划分train：test=7:3，根据地块的ID进行划分
        landids=[]
        for point in samples:
            if point[2] in landids:
                continue
            else:
                landids.append(point[2])
        landids_train, landids_test= train_test_split(landids,test_size=0.2)
        ####保存CSV到本地
        filename=shp.split('.')[0]
#        save_basepath=r'H:\GraduateFile\Hebei\ExtendSample\RFSplitSample\\'
#        save_basepath=r'H:\GraduateFile\Ningxia\ExtendSampleN48\RFSplitSample\\'
        save_basepath=r'H:\GraduateFile\Tulufan\ExtendSample\RFSplitSample\\'
        ###保存训练样本点
        print('保存训练样本点')
        trains=[]
        for point in samples:
            if point[2] in landids_train:
                trains.append([point[0],point[1]])
            else:
                continue
        np.savetxt(save_basepath+filename+'_train.csv', trains, delimiter = ',')
        ###保存测试样本点
        print('保存测试样本点')
        tests=[]
        for point in samples:
            if point[2] in landids_test:
                tests.append([point[0],point[1]])
            else:
                continue
        np.savetxt(save_basepath+filename+'_tests.csv', tests, delimiter = ',')
        
        
        
    print('Finish')
