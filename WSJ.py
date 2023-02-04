
import streamlit as st, sys
from selenium import webdriver
from st_aggrid import GridOptionsBuilder, AgGrid, ColumnsAutoSizeMode
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import regex as re ,pandas as pd,  datetime ,os
import plotly.express as px
import plotly.graph_objects as go
import pytz



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
        
        rows_today = list(x[x['Days_Left'] == 0].index)       
        
        gb.configure_selection('multiple', pre_selected_rows=rows_today)
        
        gridOptions = gb.build()
    
        grid_response = AgGrid( x,      gridOptions=gridOptions,                data_return_mode='AS_INPUT',
                                          theme="material" , columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,    enable_enterprise_modules=False,   update_mode='NO_UPDATE',       
                                height=600,           width='100%')    
        
        
        return grid_response              

def final_result(x):
    
    package = []
    
    for i in range(0,len(x),8):
        try:
            
            package.append({
                "Date": x[i],
                "Title": x[i+1],
                "Period": x[i+3],
                "Forecast": x[i+5],
                "Actual": x[i+7],
                "Update_Time": datetime.datetime.now().ctime()
                })
            
        except:
            next    
    return package

def date_check_format(x):
    
    date_string = str(x)
    
    date_string = date_string + " " + str(datetime.datetime.now().year)
    
    date = pd.to_datetime(date_string, format='%d-%b %I:%M %p %Z %Y')
    
    return date.to_pydatetime()

def pre_process(jj):
    
    x = jj.copy()
    
    if x[-2].replace(" ","").lower() == 'forecast':
         x.insert(len(x)-1, "-")
    
    if x[-1].replace(" ","").lower() == 'actual':
         x.append("-")
    

    for i in range(0, len(x)+1):
        try:
            date_period = date_check_format(x[i])
            x[i] = date_period
        except:
            next


    for i in range(0,len(x)+1):
        try:
            
            if x[i].replace(" ","").lower() == 'forecast' and x[i+1].replace(" ","").lower() == 'actual':
                x.insert(i+1, "-") 
        except :        
            next
    
    for i in range(0,len(x)+1):
        try:       
            if x[i].replace(" ","").lower() == 'actual' and type(x[i+1]) == datetime.datetime:
                x.insert(i+1, "-")
            
        except :
                next
    
    return final_result(x)

def divs_find(x):    
    
    lib_ind = []

    for i in range(100,120):        
        if re.search("Calendars & Economy",x[i]):
            lib_ind.append(i)       
        
    for i in range(140,180):    
        if re.search("Mutual Funds Screener",x[i]) :
            lib_ind.append(i)
    
    dm = []
    for i in range(min(lib_ind)+2,max(lib_ind)):    
        
        dm.append(x[i])
            
    return dm

def flatten_list(lst):
  flatten_lst = []
  for i in lst:
    if type(i) == list:
      for j in i:
        flatten_lst.append(j)
    else:
      flatten_lst.append(i)
  return flatten_lst

def runner():    


    options = webdriver.ChromeOptions()
    
    # options.headless = True
    options.add_argument('--headless')
    
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    print("\nScraper Intialized: ",datetime.datetime.now())
    
    # driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
    
    url = 'https://www.wsj.com/market-data'
    
    driver.get(url)
    
    ele_ments = driver.find_elements(By.TAG_NAME,'div')
    
    data = divs_find(flatten_list([i.text.split("\n") for i in ele_ments]))
    
    driver.close()
    
    return data 

def analytics(x):
    
    
    # week_age = TODAY_DATE -  datetime.timedelta(days=1.5)
    today = pd.to_datetime(TODAY_DATE.date())

    gnt = x.copy()
    gnt['Date'] = pd.to_datetime(gnt['Date']).dt.date
    
    gnt['News_Date'] = pd.to_datetime(x['Date'].copy()).dt.strftime('%Y-%m-%d %H:%M:%S')
    gnt['today'] = today
    gnt['today'] =  pd.to_datetime(gnt['today']).dt.date
    gnt['Delta'] = (gnt['Date']-gnt['today']).astype('timedelta64[D]')
    gnt['Days_Left'] = gnt['Delta'].astype('int')

    all_months_standard = gnt.Title.unique()

    default_color = "#1f77b4"
    colors = {all_months_standard[-1]: "#d62728"}

    color_discrete_map = { c : colors.get(c, default_color)  for c in all_months_standard}


    fig = px.timeline(
        
        gnt[gnt['Days_Left'] > 0].sort_values(by=['Days_Left'],ascending=True)
        
        , x_start='today', x_end="News_Date"
                    , y="Title", text= 'Title', title = 'Upcoming Market Events'                    
                    , color_discrete_map=color_discrete_map ,template='presentation', hover_name = 'Delta')

    

    fig.update_layout(
        yaxis_title = ""
        ,yaxis=dict(showticklabels=False)
        ,width = 1800
        ,height =600 )

    fig.add_vline(x=today, line_width=3, line_dash="dash", line_color="red")

    fig.add_vrect(
        
                x0=today,x1=today,
                annotation_text="Today", annotation_position="top right",
                opacity=0, annotation=dict(font_size=20, font_family="Times New Roman")
                
                )

    return  fig ,gnt

def get_next():
        
        with st.spinner("Processing..."):            
        
            try:
                data = runner()
                df = pre_process(data)
                df2 = pd.DataFrame(df)    
                df2 = DB.append(df2)        
                df2 = df2.drop_duplicates(['Title','Date'])
                df2.to_csv("WSJ_Load.csv",index=False)                
                return "Success"
        
            except:
                return "Not Currently Supported on this version"
            
@st.experimental_memo
def convert_df(x):
   return x.to_csv(index=False).encode('utf-8')


def main_page():
    
    current_file_path = os.path.abspath(__file__)
    current_file_dir = os.path.dirname(current_file_path)
    os.chdir(current_file_dir)
    
    chart , table = analytics(DB)        
    
    tbl = table.copy()\
                    [['Title','Period','Forecast','Actual','News_Date','Days_Left','Update_Time']]\
                    .sort_values(by=['Days_Left'],ascending=False)

    
    
    
    
    
    st.plotly_chart(chart,use_container_width=True)
    
    _ , b , _ = st.columns([.1,5,.1])    
    with b:
        st.markdown("**As of** - " + str(TODAY_DATE.strftime('%Y-%m-%d %H:%M:%S')))      
        box_grid(tbl)
        
    _,  al , bl , _ = st.columns([.1,1,1,5])
    with al:
        prompt = st.button("Get Latest Data!")
    with bl: 
        st.download_button( "Export to CSV",   csv,   "ALL_DATA.csv",   "text/csv",   key='download-csv')       

      
    
    winner = st.container()
    if prompt:            
        meg = get_next()
        with winner:
            st.warning(meg)
  
  
sys.tracebacklimit = 0
st.set_page_config(page_title= 'Market Data Hub',page_icon = ":shark:",layout='wide')
with open("main.css") as f:
    sidebar_collapse_design = st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)
    
hide_st_style = """ <style>  #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} </style> """
st.markdown(hide_st_style, unsafe_allow_html=True)
Warning = False   
DB = pd.read_csv("WSJ_Load.csv")\
                .sort_values(by=['Update_Time'],ascending=False)\
                .drop_duplicates(['Title','Date'])
                
csv  =convert_df(DB)
TODAY_DATE = datetime.datetime.now().astimezone(pytz.timezone('America/Chicago'))


main_page()




