import streamlit as st # web development
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
import time # to simulate a real time data, time loop 
import plotly.express as px # interactive charts 

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as GridSpec
import matplotlib.widgets as widgets
start = time.time()
datapoints = 10000

#if "counter" not in st.session_state:
#    st.session_state.counter = 0
st.set_page_config(
    page_title = 'Visualizacion',
    page_icon = '',
    layout = 'wide'
)

add_selectbox = st.sidebar.selectbox("musculos y sinergias",['a','b'])

#st.header(f"This page has run {st.session_state.counter} times.")
st.button("Run it again")

df ={
    'x': np.linspace(0,datapoints,datapoints),
    'y': np.sin(np.linspace(0,datapoints,datapoints)/100)
}

mainContainer = st.container()
with mainContainer:
    MusclePlaceHolder = st.empty()
    container2 = st.container()
    container1 = st.container()

column11, column12 = container1.columns(2)
with column11:
    st.button("11")
with column12:
    st.button("12")

column21, column22 = container2.columns(2)
with column21:
    st.button("21")
with column22:
    st.button("22")

#fig = px.line(data_frame=df, y='y', x='x')

fig = plt.figure()
ax = fig.add_subplot(111)
line, = ax.plot(df['x'],df['y'])
line.axes.set_ylim(-1, 1)

x =0

while True:
    start=time.time()

    newx=df['x'][-1] + 1
    newy=np.sin(newx/100)

    df['y'] = np.roll(df['y'], -1, axis=0)
    df['y'][-1] = newy

    df['x'] = np.roll(df['x'], -1, axis=0)
    df['x'][-1] = newx
    
    line.set_ydata(df['y'])
    line.set_xdata(df['x'])
    line.axes.set_xlim(df['x'][0], df['x'][-1])
    line.draw()
    

    with MusclePlaceHolder:
        st.pyplot(fig,False,use_container_width=True)

    print(newx, " ", time.time()-start)



        

        
'''    for i, col in enumerate(fig.data):
            fig.data[i]['y'] = df['y']
            fig.data[i]['x'] = df['x']'''
    