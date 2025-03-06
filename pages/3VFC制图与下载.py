import streamlit as st
import rasterio
from matplotlib import pyplot as plt
import matplotlib.colors as colors
import matplotlib.patches as patches

if st.session_state['VFCs_of_dates']=={}: 
    st.markdown("<font color='red'>请先进行图像计算",unsafe_allow_html=True)
else:
    with st.form('vfc'):
        date=st.selectbox('选择一个时间点', st.session_state['date'])
        #从session_state调用对应时间点的植被覆盖图字典集
        VFCs=st.session_state['VFCs_of_dates'][date]
        selected_province=st.selectbox("请选择一个省级行政区",list(VFCs.keys()))
        save_ds=st.text_input('（可选）自动保存地址,例：D:\Desktop-new\\')
        save=st.radio('是否自动保存图像',['是','否'],index=1)#默认为“否”
        submitted=st.form_submit_button('生成植被覆盖图')
        
        if submitted: 
            #获取对应省份的VFC的tif文件
            selected_VFC = rasterio.open(VFCs[selected_province])
            # 读取tif文件的数据
            data = selected_VFC.read(1)
            # 创建新的figure和axes
            fig, ax = plt.subplots()
            plt.rcParams['font.sans-serif'] = ['SimHei']
            ax.set_title(f'{selected_province}植被覆盖度({date})')
            # 创建自定义的颜色映射,分为五级
            cmap = colors.LinearSegmentedColormap.from_list("vfc", ["red", "orange", "yellow", "lightgreen", "green"])
            # 在axes上显示图像
            img = ax.imshow(data, cmap=cmap)
            # 创建图例
            legend_labels = ['0 - 0.2', '0.2 - 0.4', '0.4 - 0.6', '0.6 - 0.8', '0.8 - 1']
            legend_handles = [patches.Patch(color=cmap(i/5.0)) for i in range(5)]
            ax.legend(legend_handles, legend_labels, title='图例', bbox_to_anchor=(1.05, 0), loc='lower left')
            # 设置坐标轴
            x_ticks = range(0, data.shape[1], int(data.shape[1]/3))
            y_ticks = range(0, data.shape[0], int(data.shape[0]/3))
            ax.set_xticks(x_ticks)
            ax.set_yticks(y_ticks)
            ax.set_xticklabels([round(selected_VFC.xy(0, x)[0], 2) for x in x_ticks])#获取地理坐标值作为坐标轴的值
            ax.set_yticklabels([round(selected_VFC.xy(y, 0)[1], 2) for y in y_ticks])
            ax.set_xticklabels(['{}°E'.format(round(selected_VFC.xy(0, x)[0], 2)) for x in x_ticks])#设置坐标轴值的单位名称
            ax.set_yticklabels(['{}°N'.format(round(selected_VFC.xy(y, 0)[1], 2)) for y in y_ticks])
            # 在图像右上角添加简易指南针
            ax.text(0.95, 0.95, 'N\n|\nS', color='black', verticalalignment='top', horizontalalignment='right', transform=ax.figure.transFigure, fontsize=16)
            # 在Streamlit中显示figure
            st.pyplot(fig)
            if save=='是':
                #按地址保存图像    
                plt.savefig(f'{save_ds}{selected_province}植被覆盖度({date}).png', bbox_inches='tight')
                st.markdown(f"<font color='green'>已经自动保存为{save_ds}{selected_province}植被覆盖度({date}).png",unsafe_allow_html=True)
            