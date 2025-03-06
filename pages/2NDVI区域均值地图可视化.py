import streamlit as st
import folium
from folium.plugins import MousePosition
from streamlit_folium import st_folium
from folium.features import GeoJson,GeoJsonPopup
import branca

if  st.session_state['mean_NDVI_vectors_of_dates']=={}: 
    st.markdown("<font color='red'>请先进行图像计算",unsafe_allow_html=True)
else:
    with st.form('my form'):
        date=st.selectbox('选择一个时间点生成省级行政区NDVI区域均值地图', st.session_state['date'])
        submitted=st.form_submit_button('生成')
        if submitted:
            #从session_state调用所需的矢量文件
            vector=st.session_state['mean_NDVI_vectors_of_dates'][date]
            #创建地图并叠置各省份平均NDVI值的分布图（梯级设色）
            m = folium.Map(tiles=None)
            m.fit_bounds([(min(vector.bounds["miny"]),min(vector.bounds["minx"])),(max(vector.bounds["maxy"]),max(vector.bounds["maxx"]))])
            minimum, maximum = vector['mean_NDVI'].quantile([0.05, 0.95])#选取5%和95%作为colormap的最小值和最大值，去除离群值的影响
            colormap = branca.colormap.LinearColormap(
                colors=["yellow", "green"],
                vmin=minimum,
                vmax=maximum,caption = "mean_NDVI in provinces")
            def style_function(feature):
                style = {
                    "fillColor": colormap(feature["properties"]['mean_NDVI']),
                    "color": "black",
                    "weight": 1,
                    "fillOpacity": 0.7,
                }
                return style
            gjson=GeoJson(data=vector,
                    style_function=style_function,name='mean_NDVI').add_to(m)
            GeoJsonPopup(fields=['name','mean_NDVI'],
                         labels=True).add_to(gjson)
            folium.TileLayer(tiles="Esri.WorldImagery",
                attr="Esri全球影像"
            ).add_to(m)
            folium.TileLayer(tiles="CartoDB.Positron",
                attr="Carto地图"
            ).add_to(m)
            folium.TileLayer(tiles="Gaode.Normal",
                attr="高德地图"
            ).add_to(m)
            folium.LayerControl().add_to(m)
            MousePosition().add_to(m)
            st_folium(m,width=650, height=600)
            st.markdown("<font color='green'>点击矢量图形以查看平均NDVI数值",unsafe_allow_html=True)      
                     
