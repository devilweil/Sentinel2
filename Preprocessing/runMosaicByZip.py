# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 10:16:44 2021
相同时间的影像进行拼接镶嵌
@author: LW
"""
from osgeo import gdal,gdal_array,osr, ogr
from skimage import io
import os
import glob
import math
###引入ArcGIS的ArcPy的包
#import sys
#sys.path.append(r'C:\Program Files (x86)\ArcGIS\Desktop10.2\arcpy')
#import arcpy

os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'

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
    return min_x,max_y,max_x,min_y

if __name__ == "__main__": 
    
    ###第1步 获取文件夹下时间唯一的时间列表
    os.chdir(r'H:\GraduateFile\Tulufan\SCL\ProjectSCL20m')
    filename = glob.glob('*.tif')
    dateList=[]
    print('正在执行获取唯一时间的时间列表....')
    for filePath in filename:
        time=filePath.split('_')[2].split('T')[0]
        if time in dateList:
            continue
        else:
            dateList.append(time)
    print('按照时间查询到对应文件进行镶嵌')
    for day in dateList:
        print('正在执行',day,'的镶嵌...')
        originDays=glob.glob('*L2A_'+day+'*.tif')
        print(originDays)
        #获取待镶嵌栅格的最大最小的坐标值
        min_x,max_y,max_x,min_y=GetExtent(originDays[0])
        for in_fn in originDays[1:]:
            minx,maxy,maxx,miny=GetExtent(in_fn)
            min_x=min(min_x,minx)
            min_y=min(min_y,miny)
            max_x=max(max_x,maxx)
            max_y=max(max_y,maxy)
        #计算镶嵌后影像的行列号
        in_ds=gdal.Open(originDays[0])
        geotrans=list(in_ds.GetGeoTransform())
        width=geotrans[1]
        height=geotrans[5]        
        
        columns=math.ceil((max_x-min_x)/width)+1
        rows=math.ceil((max_y-min_y)/(-height))+1
        print(columns,rows)
        in_band=in_ds.GetRasterBand(1)
        
        proj= osr.SpatialReference()
        proj.SetWellKnownGeogCS("WGS84")
        
        driver=gdal.GetDriverByName('GTiff')
        out_ds=driver.Create(r'H:\GraduateFile\Tulufan\SCL\CompositeSCL20m\\'+day+'.tif',columns,rows,1,in_band.DataType)
        out_ds.SetProjection(proj.ExportToWkt())
        geotrans[0]=min_x
        geotrans[3]=max_y
        out_ds.SetGeoTransform(geotrans)
        out_band=out_ds.GetRasterBand(1)
        #定义仿射逆变换
        inv_geotrans=gdal.InvGeoTransform(geotrans)
        out_data=out_band.ReadAsArray()
        #开始逐渐写入
        for in_fn in originDays:
            in_ds=gdal.Open(in_fn)
            in_gt=in_ds.GetGeoTransform()
            #仿射逆变换
            offset=gdal.ApplyGeoTransform(inv_geotrans,in_gt[0],in_gt[3])
            x,y=map(int,offset)
            print(x,y)
            trans=gdal.Transformer(in_ds,out_ds,[])#in_ds是源栅格，out_ds是目标栅格
            success,xyz=trans.TransformPoint(False,0,0)#计算in_ds中左上角像元对应out_ds中的行列号
            x,y,z=map(int,xyz)
            print(x,y,z)
            data=in_ds.GetRasterBand(1).ReadAsArray()
            row,col=data.shape[0],data.shape[1]
#            out_band.WriteArray(data,x,y)#x，y是开始写入时左上角像元行列号
            ###进行对应像元赋值
            rowCount=row+y
            colCount=col+x
            if rowCount>rows:
                rowCount=rows
            if colCount>columns:
                colCount=columns
            for r in range(y,rowCount):
                print('row ',r)
                for c in range(x,colCount):
                    ###取最大值作为该像元的最终值
                    maxVal=max(data[r-y][c-x],out_data[r][c])
                    out_data[r][c]=maxVal
        out_band.WriteArray(out_data)
        del in_ds,out_band,out_ds

        
        
        
        
        #### 对同一天的数据进行投影变换
#        inputImageList=[]
#        for origin in originDays:
#            
#            inputrasfile1 = gdal.Open(origin, gdal.GA_ReadOnly) # 第一幅影像
#            inputImageList.append(inputrasfile1)
#            utm=origin.split('_')[5][1:3]
##            projname=' UTM '+utm+'N '
##            proj = osr.SpatialReference()
##            proj.SetProjCS(projname)
##            proj.SetWellKnownGeogCS("WGS84")
##            proj.SetUTM(int(utm),True)
##            print(proj)
#            
#        detProj= osr.SpatialReference()
#        detProj.SetWellKnownGeogCS("WGS84")
#        ####投影变换 dstSRS='EPSG:4326'
#        option = gdal.WarpOptions(format='GTiff', dstSRS=detProj)
#          
#        gdal.Warp(r'H:\GraduateFile\Tulufan\SCL\CompositeSCL20m\\'+origin,inputImageList,options=option)
#    


    
    
    print('Complete')
