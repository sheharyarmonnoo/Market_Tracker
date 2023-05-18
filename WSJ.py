
import streamlit as st, sys
from st_aggrid import GridOptionsBuilder, AgGrid, ColumnsAutoSizeMode
import regex as re ,pandas as pd,  datetime ,os
import plotly.graph_objects as go
from deta import Deta
from dotenv import load_dotenv

def do_table_graph(data_x , title_plot = "", format_data = [""], height_table = None ,width_table = 1800, first_column = 60, value_columns  = 160 ):
    
    headerColor = '#44546A'
    rowEvenColor = '#CDCDCD'
    rowOddColor = 'white'
    
    if height_table != None:
        height_table_val = height_table
    else:
        height_table_val  = min((data_x.shape[0] * 75),600)
        
    fig = go.Figure(data=[go.Table(
    
        
            columnwidth=[first_column] + [value_columns] * (len(data_x.columns)-1) ,
            
            header=dict(
                values=data_x.columns,
                line_color=headerColor,
                fill_color=headerColor,
                align=['left','center'],
                font=dict(color='white', size=15),
            ),
            
            cells=dict(
                values=data_x.transpose().values,
                line_color=[[rowEvenColor,rowOddColor]*(12) + [rowEvenColor,rowOddColor]],
                fill_color = [[rowEvenColor,rowOddColor]*len(data_x)],
                align = ['left', 'center'],
                format= format_data,
                font = dict(color = 'darkslategray', size = 17 ,family =['Arial']),
                height = 28,)),
        ])

    fig.update_layout(
        
        title = title_plot
        ,title_x=0.5
        ,margin=dict(l=10, r=10, t=60, b=10)  
        ,yaxis_title = ""         ,xaxis_title = "" 
        ,width = width_table        ,height = height_table_val
        )
    



    return fig

def box_grid(grid_data):
    
        x = grid_data.reset_index().drop({'index'},axis = 1)
        
        gb = GridOptionsBuilder.from_dataframe(x)
                           
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gb.configure_selection('multiple', use_checkbox=False
                                , groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
        
        gb.configure_default_column(groupable=True, 
                            value=True, 
                            enableRowGroup=True, 
                            editable=True,
                            enableRangeSelection=True,
                            filterable=True
                        )
        
        
        gridOptions = gb.build()
    
        grid_response = AgGrid( x,     
                               gridOptions=gridOptions,          
                               data_return_mode='AS_INPUT',
                               theme="material" ,
                               columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW, 
                               enable_enterprise_modules=False,   update_mode='NO_UPDATE',       
                               height=600, width='100%')    
        
        
        return grid_response              



def main_page():
    
    db= deta.Base("wsj_scraped")    
    feed = db.fetch().items 
    
    
    df = pd.DataFrame(feed)[['Event','Date','Period','Forecast','Actual','Date_Scrape']]
    
    df1 = df.drop_duplicates(['Event','Period']).sort_values(['Date'])     
    
       
    _, a , b  = st.columns([.2, 1,1])
    
    with a:
    
        st.header("Weekly Economic Data")
        
    with b:          
        st.metric('Asof:', df1['Date_Scrape'].max())
        
    
    st.markdown("\n\n\n\n\n")
    
    box_grid(df1)
    
    st.markdown("\n\n\n\n\n")
    
    st.markdown("""
                
                These indicators offer valuable insights into various sectors of the economy, including retail, housing, energy, and employment.
                
                They can be useful for tracking economic trends, assessing market conditions, and making informed decisions related to investments and financial planning.
                
                """)
    st.markdown("\n\n")

    st.markdown(          """
                
                
                - Advance Monthly Sales for Retail & Food Services: This indicator provides an early estimate of retail and food service sales for a specific month.

                - Industrial Production & Capacity Utilization: This indicator measures the output and capacity utilization of industrial sectors.

                - New Residential Construction - Housing Starts and Building Permits: This indicator focuses on new residential construction and provides information on housing starts (the number of new residential construction projects that began) and building permits (the number of permits issued for new construction).

                - EIA Weekly Petroleum Status Report: This indicator provides information about petroleum inventory levels on a weekly basis.

                - Unemployment Insurance Weekly Claims Report - Initial Claims: This indicator presents the number of initial unemployment insurance claims filed on a weekly basis.

                - Existing Home Sales: This indicator focuses on the sales of previously owned homes.

                - EIA Weekly Natural Gas Storage Report: This indicator presents the natural gas storage levels on a weekly basis.


                
                """)
    
    st.markdown("\n\n\n\n\n")
    st.markdown("\n\n\n\n\n")

    
    
    st.markdown( """
    <div style='text-align: right'>
        <em>  Shey Coding |  2023 All rights reserved.</em>
    </div>
    """ , unsafe_allow_html=True)


        
# load_dotenv(r'C:\Users\smonnoo\GitHub\MyCode\FARM\backend\.env')
   
DETA_KEY = os.getenv('DETA_KEY')
deta = Deta(DETA_KEY)



sys.tracebacklimit = 0
st.set_page_config(page_title= 'Market Data Hub',page_icon = "chart_with_upwards_trend",layout='wide')
with open("main.css") as f:
    sidebar_collapse_design = st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)
    
hide_st_style = """ <style>  #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} </style> """
st.markdown(hide_st_style, unsafe_allow_html=True)
Warning = False   


main_page()




