import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from ..controller import *

def report1():
    data = mysql_query('''SELECT Pallete_Name,Date,Method,PD_No_of_Cavity,PD_No_of_Seeds,PD_No_of_Cavity * PD_No_of_Seeds as Total,'' as Remaining FROM
    Pallete_Data
        INNER JOIN
    Manufacturer_Seeds ON Pallete_Data.MSID = Manufacturer_Seeds.MSID 
	INNER JOIN
    Manufacturer_Master ON Manufacturer_Seeds.MID=Manufacturer_Master.MID
      INNER JOIN
    seeds_master ON seeds_master.SEEDSID = Manufacturer_Seeds.SEEDSID;''')    
    
    datf=pd.DataFrame(data)
    a=datf.iat[0,5]-datf.iat[1,5]
    b=datf.iat[2,5]-datf.iat[3,5]
    c=datf.iat[4,5]-datf.iat[5,5]
    d=datf.iat[6,5]-datf.iat[7,5]
    e=datf.iat[8,5]-datf.iat[9,5]
    f=datf.iat[10,5]-datf.iat[11,5]
    g=datf.iat[12,5]-datf.iat[13,5]
    h=datf.iat[14,5]-datf.iat[15,5]
    i=datf.iat[16,5]-datf.iat[17,5]
    j=datf.iat[18,5]-datf.iat[19,5]
    k=datf.iat[20,5]-datf.iat[21,5]
    datf.iat[0,6]=a
    datf.iat[2,6]=b
    datf.iat[4,6]=c
    datf.iat[6,6]=d
    datf.iat[8,6]=e
    datf.iat[10,6]=f
    datf.iat[12,6]=g
    datf.iat[14,6]=h
    datf.iat[16,6]=i
    datf.iat[18,6]=j
    datf.iat[20,6]=k
    
    datf = datf.to_html(classes='table table-striped')
    return datf

################ Sowing Data ######################################
def report2():

    data = mysql_query(
    '''
    select Distinct Pallete_Data.Pallete_Name as Boards,System_Name,Date as Sowing_date,PD_No_of_Cavity as Total_Cavity,PD_No_of_Seeds as Sown_Per_Cavity,PD_No_of_Cavity*PD_No_of_Seeds as Total_Sown,"" as Germinated,Quantity ,"" as Dead_After_Germination,"" as Total,"" as Remaining from seeds_master Inner join Manufacturer_Seeds on seeds_master.SEEDSID=Manufacturer_Seeds.SEEDSID Inner join Pallete_Master on Pallete_Master.MSID=Manufacturer_Seeds.MSID Inner Join Pallete_Data on Pallete_Data.PMID=Pallete_Master.PMID Inner join Grow_Channel on Grow_Channel.PMID=Pallete_Data.PMID Inner join Grow_Channel_Name on Grow_Channel_Name.GCNID=Grow_Channel.GCNID Inner Join Grow_System on Grow_Channel_Name.GSID=Grow_System.GSID;
    ''')
    data = pd.DataFrame(data)
    #Germinated
    # data.iat[0,5]=10
    # data.iat[3,5]=30
    # data.iat[9,5]=65
    # data.iat[15,5]=65
    # data.iat[18,5]=65
    # data.iat[18,5]=30
    # data.iat[21,5]=10
    # data.iat[45,5]=25
    # data.iat[63,5]=30

    # #Dead_after_Germn
    # data.iat[0,7]=0
    # data.iat[3,7]=0
    # data.iat[9,7]=5
    # data.iat[15,7]=1
    # data.iat[18,7]=14
    # data.iat[21,7]=1
    # data.iat[45,7]=10
    # data.iat[63,7]=1

    pvt=pd.pivot_table(data,index=['Boards','Sowing_date','Total_Cavity','Sown_Per_Cavity','Total_Sown'],columns=["System_Name"],values='Quantity',aggfunc="first")
    pvt.fillna('-')

    # data.dropna(axis=0,how='any')
    data = data.to_html(classes="table table-striped")
    return data

    ########################### Report Dashboard ########################
def RepoDashboard():
    
    dct = {}
    disData = mysql_query("SELECT distinct(Pallete_Name) as 'PN' from Pallete_Master;")
    
    
    for x in disData:
        
        data = mysql_query(" SELECT Pallete_Master.Pallete_Name,Pallete_Data.Method,Pallete_Data.PD_No_of_Cavity*Pallete_Data.PD_No_of_Seeds AS 'Total Seeds' from Pallete_Data inner join Pallete_Master ON Pallete_Data.PMID=Pallete_Master.PMID where Pallete_Master.Pallete_Name='{}';".format(str(x['PN'])))
        
        data = pd.DataFrame(data)
        df = data
        
        fig = px.pie(df,values='Total Seeds',names='Method',title=str(x['PN'])+"Report")
        fig.to_html(full_html=False,include_plotlyjs=False)
        dct.__setitem__(str(x['PN']),fig.to_html(full_html=False))
    print("END")
    
    data = mysql_query(
    '''
    SELECT Pallete_Master.Pallete_Name,Pallete_Data.Method,Pallete_Data.PD_No_of_Cavity*Pallete_Data.PD_No_of_Seeds AS 'Total Seeds' from Pallete_Data inner join Pallete_Master ON Pallete_Data.PMID=Pallete_Master.PMID;
    ''')
    df = data
    # data.groupby(['Pallete_Name','Method']).sum().plot(kind='pie', subplots=True, shadow = True,startangle=90,figsize=(7,7))
    fig = px.bar(df, x="Pallete_Name", y="Total Seeds",color="Method", title="Pallete Wise Distribution")
    plot_histo = fig.to_html(full_html=False,include_plotlyjs=False)
    return dct,plot_histo