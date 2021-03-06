#!/usr/bin/env python

from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

# Download school-level data of Free Meals and Reduced Price Meals Program.
# Proxy for school-level poverty rate.
addr = 'https://www.cde.ca.gov/ds/sd/sd/filessp.asp'
resp = requests.get(addr)
html = resp.content
soup = bs(html, "html.parser")
ad = "https://www.cde.ca.gov/ds/sd/sd/"
downloads = [ad+i.get("href") for i in soup.find_all("a") if "xls" in str(i)]

files = []
for i in downloads:
    resp = requests.get(i)
    file_name = "{}".format(i.split("/")[-1])
    files.append(file_name)
    with open("frpm/{}".format(file_name), "wb") as out:
        out.write(resp.content)

# Concat yearly data (2004-2016).
year = [i for i in range(2016,2003,-1)]

for_concat = []
for i in range(len(files)):
    if i < 3:
        xls = pd.read_excel("frpm/{}".format(files[i]), sheetname=1, header=1, converters={'County Code': str, 'District Code':str,'School Code':str})
    elif i < len(files)-2:
        xls = pd.read_excel("frpm/{}".format(files[i]), sheetname=1, converters={'County Code':str, 'District Code':str,'School Code':str})
    else:
        xls = pd.read_excel("frpm/{}".format(files[i]), sheetname=1, converters={'CCODE':str, 'DCODE':str,'SCODE':str})
    if i < 4:
        xls = xls.iloc[:, [0,1,2,3,-2,-3]]
    elif i == 4:
        xls = xls.iloc[:, [0,1,2,3,-1,-2]]
    elif i == 5:
        xls = xls.iloc[:, [0,1,2,-2,-3]]
    else:
        xls = xls.iloc[:, [0,1,2,-1,-2]]
    if i >= 5:
        xls["YEAR"] = files[i][4:8]
        cols = xls.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        xls = xls[cols]
    xls.columns.values[0] = "YEAR"
    xls.columns.values[1] = "CCODE"
    xls.columns.values[2] = "DCODE"
    xls.columns.values[3] = "SCODE"
    xls.columns.values[-1] = "FRPM_COUNT"
    xls.columns.values[-2] = "FRPM_%"
    xls["YEAR"] = year[i]
    xls["CDS_CODE"] = xls["CCODE"] + xls["DCODE"] + xls["SCODE"]
    for_concat.append(xls)

results = pd.concat(for_concat, ignore_index=True)
cols = ["YEAR", "CDS_CODE", "FRPM_COUNT", "FRPM_%"]
la_frpm = results[cols]

la_frpm.to_csv("data/school_frpm.csv")
