import pandas as pd
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

