import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import base64 #for images
import plotly.express as px

st.set_page_config(page_title='Cost Model', layout = 'wide', page_icon = 'Images/logo2.png', initial_sidebar_state = 'auto')
def insert_logo(imagePath):
	st.markdown(
    f"""
        <center><img src="data:image/png;base64,{base64.b64encode(open(imagePath, "rb").read()).decode()}" class="img-fluid" width=350em ></center><br>
    """,
    unsafe_allow_html=True
)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")


LOGO_IMAGE = "Images/logo.png"
Flag_IMAGE="Images/flag.png"
insert_logo(LOGO_IMAGE)


st.markdown("<h3 style='text-align: center;font-family:Source Sans Pro;font-weight: 700;'>Technology and Infrastructure</h3>", unsafe_allow_html=True)
st.markdown("<center><b><i>Draft Version</i></b></center><br>",unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;background-color:#0073AB;font-family:Source Sans Pro;font-weight: 700;color:white;padding-left:25px;padding-right:25px;'>IRENA Solar PV Manufacturing Cost Model</h3>", unsafe_allow_html=True)
st.markdown(f"<h3 style='background-color:#0073AB;font-family:Source Sans Pro;color:white'><img class='logo-img' src='data:image/png;base64,{base64.b64encode(open(Flag_IMAGE, 'rb').read()).decode()}' class='img-fluid' width=150em style='display:block;'></h3>", unsafe_allow_html=True)




# Cache loading of Excel sheet names
@st.cache_data
def get_sheet_names(path):
    xls = pd.ExcelFile(path)
    return xls.sheet_names

# Cache reading of a specific sheet
@st.cache_data
def read_sheet(path, sheet_name):
    return pd.read_excel(path, sheet_name=sheet_name, header=None)

# File path
file_path = "Dashboard data.xlsx"

# Load sheet names
sheet_names = get_sheet_names(file_path)

# Select a scenario
st.markdown("")
col1, col2,col3 = st.columns(3)
col1.markdown("**Select a Scenario:**")
scenario = col1.selectbox("Select a Scenario", sheet_names,label_visibility="collapsed")

# Read data from selected scenario
df = read_sheet(file_path, scenario)

# Extract and display title from the first 4 rows (rows 0 to 3)
title_rows = df.iloc[0:4]
title_text = " | ".join([str(cell) for cell in title_rows[0] if pd.notna(cell)])
st.markdown(f"The scenario selected is {title_text}")



# Extract countries from row 6 (index 5)
countries = df.iloc[5, 1:]

# Extract technologies and their values from rows 7–18 (index 6–17)
technologies = df.iloc[6:18, 0]
data = df.iloc[6:18, 1:]

# Create stacked bar chart
fig = go.Figure()

for i, tech in enumerate(technologies):
    fig.add_trace(go.Bar(
        x=countries,
        y=data.iloc[i],
        name=tech
    ))

fig.update_layout(
    barmode='stack',
    xaxis_title='Country',
    yaxis_title='Value',
    title=f'{scenario}',
    legend_title='Component',
    margin=dict(l=20, r=20, t=40, b=20),
)

st.plotly_chart(fig, use_container_width=True)


#################################################################
#REFERENCES
st.markdown("---")
st.markdown("<h3 style='background-color:#58585A;padding-left:25px;padding-right:25px;padding-top:25px;color:white;'font-family:Source Sans Pro;>References</h3>", unsafe_allow_html=True)
st.markdown("""<p style='background-color:#58585A;padding-left:25px;padding-right:25px;padding-bottom:25px;font-family:Source Sans Pro;color:white'>
The information and data contained herein comes from the analysis supporting the report "Sao Tome and Principe: Assessment of cost-effective mitigation options to inform the implementation of the NDC".
<br>Datasets and technical assumptions are derived from: ALER (2020), Bhatia M. and Angelou N. (2015), DGRNE (2022a), DGRNE (2022b), Eartheasy (2021),  Hernández, C. et al. (2020), IPCC (2006), NDC Background information, US Department of Energy (2021), World Bank (2016).
<br> <br>Please refer to the report to dig deeper and further explore the analysis conducted, the methodology used, and the default assumptions considered.</p>""", unsafe_allow_html=True)
########################################
#Disclaimer - text is in style.css
st.markdown("---")
st.markdown("""
<div class='custom-footer'>
This publication and the material herein are provided "as is". All reasonable precautions have been taken by IRENA to verify the reliability of the material in this publication. However, neither IRENA nor any of its officials, agents, data or other third-party content providers provides a warranty of any kind, either expressed or implied, and they accept no responsibility or liability for any consequence of use of the publication or material herein. The information contained herein does not necessarily represent the views of all Members of IRENA. The mention of specific companies or certain projects or products does not imply that they are endorsed or recommended by IRENA in preference to others of a similar nature that are not mentioned. The designations employed and the presentation of material herein do not imply the expression of any opinion on the part of IRENA concerning the legal status of any region, country, territory, city or area or of its authorities, or concerning the delimitation of frontiers or boundaries.
</div>
""", unsafe_allow_html=True)

########################################