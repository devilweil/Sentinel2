# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 12:58:39 2021

@author: LW
"""

import os

#https://scihub.copernicus.eu/apihub   https://scihub.copernicus.eu/dhus
from sentinelsat.sentinel import SentinelAPI, read_geojson, geojson_to_wkt

#GeoJSON数据目录
os.chdir(r'H:\Temp\ResearchArea\Shandong')
api = SentinelAPI('weiliucau', '034517Kexian', 'https://scihub.copernicus.eu/apihub')
#api = SentinelAPI('devilweil', '034517Kexian', 'https://scihub.copernicus.eu/apihub')
# search by polygon, time, and Hub query keywords
#geojson=read_geojson('tulufan.geojson')
footprint = geojson_to_wkt(read_geojson('yantai.geojson')) # 设置范围
#footprint = geojson_to_wkt(read_geojson('ShandongRegion.geojson')) # 设置范围
#products = api.query(footprint,
#                     date = ('20190308', date(2019, 3, 9)),
#                     platformname = 'Sentinel-2',
#                     cloudcoverpercentage = (0, 100))

# download all results from the search
outfolder="H:/基础数据/哨兵二数据/山东2020冬季/L1C/"
#api.download_all(products, outfolder, checksum=False)
#通过设置OpenSearch API查询参数筛选符合条件的所有Sentinel-2 L2A级数据
products =api.query(footprint,                        #Area范围
		date=('20201101','20210401'),  #搜索的日期范围
		platformname='Sentinel-2',        #卫星平台名，Sentinel-2                    
		producttype='S2MSI1c',            #产品数据等级，‘S2MSI2A’表示S2-L2A级产品
		cloudcoverpercentage=(0,50))   # 云量百分比
		
#通过for循环遍历并打印、下载出搜索到的产品文件名
for product in products:
	#通过OData API获取单一产品数据的主要元数据信息
	product_info = api.get_product_odata(product)
	#打印下载的产品数据文件名      
	print(product_info['title'])
	#下载产品id为product的产品数据
	api.download(product,outfolder, checksum=False)

 # 此处checksum默认为True，本人在下载的时候出现问题，所以设置False
