import streamlit as st
import os

#获取py文件当前实际地址
file_path = os.path.realpath(__file__)
#获取py文件当前实际地址的上一级地址
parent_path = os.path.dirname(file_path)
#修改py文件的工作路径到实际地址的上级地址
os.chdir(parent_path)

st.title('欢迎使用本程序！')

    