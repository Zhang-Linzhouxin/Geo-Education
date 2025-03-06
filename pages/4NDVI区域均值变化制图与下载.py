import streamlit as st
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

if len(st.session_state['date'])<2: 
    st.markdown("<font color='red'>请至少完成三个图像计算",unsafe_allow_html=True)
else:   
    with st.form('trans'):
        dates = st.multiselect('请有序选择至少三个时间点',st.session_state['date'])
        names = st.multiselect('请选择若干个省级行政区',st.session_state['mean_NDVIs_of_dates'][st.session_state['date'][0]])
        name_str=''
        for i in range(len(names)):
            if i!=len(names)-1:
                name_str+=f"{names[i]}、"
            else:
                name_str+=f"{names[i]}"
        save_ds=st.text_input('（可选）自动保存地址,例：D:\Desktop-new\\')
        save=st.radio('是否自动保存图像',['是','否'],index=1)#默认为“否”
        submitted=st.form_submit_button('生成NVDI区域均值变化对比图')
        
        if submitted: 
            #建立新的df以便收集选定的数据和制图
            df=pd.DataFrame(index=names,columns=dates)
            #收集选定的数据
            for date in dates:
                for name in names:
                     d=st.session_state['mean_NDVIs_of_dates'][date]
                     df.loc[name,date]=d.loc[d['name']==name,'mean_NDVI'].iloc[0]
            st.write(df)
            #创建新的figure和axes
            
            fig, ax = plt.subplots()
            for province in df.index:
                # 绘制原始数据
                y = df.loc[province]
                
                x = np.arange(len(y))
                line, = ax.plot(x, y, label=province)
                # 拟合趋势线
                degree = 1  # 选择拟合的多项式的阶数，1表示线性拟合
                coeffs, residuals, _, _, _ = np.polyfit(x, list(y), degree, full=True)
                trendline = np.poly1d(coeffs)
                # 计算R²值
                ss_total = np.sum((y - np.mean(y))**2)
                r_squared = 1 - (residuals[0] / ss_total)
                # 绘制趋势线
                ax.plot(x, trendline(x), label=f'{province}变化趋势线：{trendline},R^2={r_squared:.4f}', color=line.get_color(), linestyle='dashed', linewidth=0.5)
                
            plt.xticks(np.arange(len(df.columns)), df.columns)
            ax.set_title(f'{name_str}NDVI区域均值变化对比图')
            ax.set_xlabel('时间')
            ax.set_ylabel('mean_NDVI')
            ax.legend(bbox_to_anchor=(1.05, 0), loc='lower left', borderaxespad=0.)
            st.pyplot(fig)
                        
            if save=='是':
                #按地址保存图像    
                plt.savefig(f'{save_ds}{name_str}NDVI区域均值变化对比图.png', bbox_inches='tight')
                st.markdown(f"<font color='green'>已经自动保存为{save_ds}{name_str}NDVI区域均值变化对比图.png",unsafe_allow_html=True)
