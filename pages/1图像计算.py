import streamlit as st
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask
from rasterio.io import MemoryFile
import os
import re
#建立各页面公用数据的session state
#建立以日期为键、全国各省份NDVI平均值的矢量数据为值的字典
if 'mean_NDVI_vectors_of_dates' not in st.session_state:
    st.session_state['mean_NDVI_vectors_of_dates'] = {}
#建立以日期为键、各省份植被覆盖图字典集为值的字典
if 'VFCs_of_dates' not in st.session_state:
    st.session_state['VFCs_of_dates'] = {}
#建立以日期为键、各省份NDVI平均值和省名两个列的简单df表格为值的字典
if 'mean_NDVIs_of_dates' not in st.session_state:
    st.session_state['mean_NDVIs_of_dates'] = {}
#建立用于记录日期时间点的列表
if 'date' not in st.session_state:
    st.session_state['date'] = []

tif_files=os.listdir("data\egFiles_China_NDVI_tif_by_months")
st.title("MODND1M 中国 500M NDVI 月合成产品图像切割、NDVI区域均值计算、VFC估值") 

with st.form('my fform'):
    st.markdown("<font color='grey'>（程序工作路径已自动设置为当前py文件所在文件夹）",unsafe_allow_html=True)
    file_names=st.multiselect("请选择需要计算的若干图像文件名", tif_files)
    geojson_ds="data\中国_省.geojson"
    
    submitted=st.form_submit_button('开始计算')
    if submitted: 
        for file_name in file_names:
            # 使用正则表达式查找日期字符串
            match = re.search(r'\d{8}', file_name)
            if match:
                #将文件名中的日期字符赋值给date
                date = match.group()
            st.markdown("<font color='green'>正在计算，请稍等...",unsafe_allow_html=True)
            #建立各省份植被覆盖图字典集
            VFCs={}
            #建立各省份NDVI平均值和省名两个列的简单df表格
            mean_ndvi_simple_record=pd.DataFrame()
            # 读取中国省级行政区边界的geojson文件
            vector = gpd.read_file(geojson_ds)
            #去除境界线
            vector = vector.loc[vector['name'] != '境界线']
            # 将矢量文件转换为WGS1984坐标系
            vector = vector.to_crs('EPSG:4326')
            #读取MODND1M 中国 500M NDVI 月合成产品文件tif图像
            raster = rasterio.open("data\egFiles_China_NDVI_tif_by_months\{}".format(file_name)) 
            # 创建一个新的列来存储NDVI平均值
            vector['mean_NDVI'] = np.nan
            # 对每个省份进行循环
            for i, row in vector.iterrows():
                # 使用rasterio包中的mask函数来裁剪tif图像
                out_image, out_transform = mask(raster, [row['geometry']], crop=True)
                #空值赋值为np.nan
                out_image[out_image == 1.0000000e+10] = np.nan
                # 计算区域平均NDVI值(忽略空值)
                mean_ndvi = np.nanmean(out_image)
                # 将NDVI平均值存储到新的列中
                vector.at[i, 'mean_NDVI'] = mean_ndvi
                #估计植被覆盖度并制图，分别取累积概率为5%和90%的NDVI值作为NDVImin和NDVImax，VFC = (NDVI - NDVImin)/ ( NDVImax - NDVImin) 
                NDVImin, NDVImax = np.nanpercentile(out_image, [5, 90])
                VFC = (out_image - NDVImin) / (NDVImax - NDVImin)
                #建立虚拟文件存储VFC图像
                memfile = MemoryFile()
                #将VFC图像写入虚拟tif文件，各项参数和raster保持一致
                with memfile.open(driver='GTiff', height=out_image.shape[1], 
                                   width=out_image.shape[2], count=1, 
                                   dtype=out_image.dtype, crs=raster.crs,
                                   transform=out_transform) as dataset:
                    dataset.write(VFC)
                #将VFC图像虚拟tif文件放入植被覆盖图字典集
                VFCs[row['name']]=memfile
            #更新session state
            if date not in st.session_state['date']:#防止多次计算同一文件导致日期重复
                st.session_state['date'].append(date)
            st.session_state['mean_NDVI_vectors_of_dates'][date]=vector
            st.session_state['VFCs_of_dates'][date]=VFCs
            #从vector的gdf中提取名称和NDVI平均值两列，建立新的df，并更新session_state
            mean_ndvi_simple_record['name']=vector['name']
            mean_ndvi_simple_record['mean_NDVI']=vector['mean_NDVI']
            st.session_state['mean_NDVIs_of_dates'][date]=mean_ndvi_simple_record
            
            #每次计算后都显示已完成计算的图像及其日期信息
            st.markdown(f"<font color='black'>已完成计算的图像有{len(st.session_state['date'])}个。时间：{st.session_state['date']}",unsafe_allow_html=True)
        #计算完成
        st.markdown("<font color='green'>计算完成",unsafe_allow_html=True)            
