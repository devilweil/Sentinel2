# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 11:07:43 2021

@author: LW
"""
from osgeo import gdal,gdal_array,osr, ogr
import os,sys 
import glob
import numpy as np
import random
from skimage import io


    
if __name__ == "__main__":
    #获取样本点
#    filename=r'H:\GraduateFile\Hebei\Bands\Bands10mProjClip\20200919.tif'
#    filename=r'H:\GraduateFile\Ningxia\Bands\Bands10m\20200918.tif'
    filename=r'H:\GraduateFile\Tulufan\Bands\Bands10mProjClip\20200917.tif'
    
    data_origin=gdal.Open(filename)
    if data_origin is None:
        print('Could not open'+filename)
    proj=data_origin.GetProjection()
    geotrans=data_origin.GetGeoTransform()
    col_s=data_origin.RasterXSize
    row_s=data_origin.RasterYSize
    
    #导出影像的存储路径
#    export_file='H:\GraduateFile\Hebei\BestScale\RGBTIFF\hebei_RGB_20200919.tif'
#    export_file=r'H:\GraduateFile\Ningxia\BestScale\RGBTIFF\ningxia_RGB_20200918.tif'
    export_file=r'H:\GraduateFile\Tulufan\BestScale\RGBTIFF\tulufan_RGB_20200917.tif'
    
    #创建栅格数据
    driver=gdal.GetDriverByName("GTiff")
    datat1_out=driver.Create(export_file,col_s,row_s,3,gdal.GDT_Float32)#GDT_Float32
    datat1_out.SetGeoTransform(geotrans)
    datat1_out.SetProjection(proj)
    for bd in range(3):
        visual_arr = data_origin.GetRasterBand(bd+1).ReadAsArray()
        band=datat1_out.GetRasterBand(bd+1)
        band.WriteArray(visual_arr)

    data_origin.FlushCache()
    datat1_out.FlushCache()
    del data_origin
    del datat1_out
    print('Finish')
    
    