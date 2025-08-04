import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import base64 #for images
import plotly.express as px
import re

st.set_page_config(page_title='Cost Model', layout = 'wide', page_icon = 'Images/logo2.png', initial_sidebar_state = 'auto')
st.markdown(
        f"""
        <div style="text-align: center; padding-top: 1rem;">
            <img src="data:image/png;base64,{base64.b64encode(open(imagePath, "rb").read()).decode()}" width="350" class="logo-img">
        </div>
        """,
        unsafe_allow_html=True
    )

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

COMPONENT_COLORS = {
    "Polysilicon": "#00BFFF",
    "Wafer": "#008080",
    "Cell Cost": "#FF8C00",
    "Overheads": "#708090",
    "Electricity": "#DAA520",
    "Building and facilities": "#8B4513",
    "Equipment depreciation": "#6A5ACD",
    "Maintenance": "#228B22",
    "Labour": "#DC143C",
    "Other material": "#BA55D3",
    "ESG Certification": "#2E8B57",
    "Operating profits": "#4169E1"
}

LOGO_IMAGE = "Images/logo.png"
Flag_IMAGE="Images/flag.png"
insert_logo(LOGO_IMAGE)


st.markdown("<h3 style='text-align: center;font-family:Source Sans Pro;font-weight: 700;'>IRENA Solar PV Manufacturing Cost Model</h3>", unsafe_allow_html=True)
st.markdown("<center><b><i>Draft Version</i></b></center><br>",unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;background-color:#0073AB;font-family:Source Sans Pro;font-weight: 700;color:white;padding-left:25px;padding-right:25px;'>About the IRENA Solar PV Manufacturing Cost Model</h3>", unsafe_allow_html=True)
st.markdown(f"<h3 style='background-color:#0073AB;font-family:Source Sans Pro;color:white'><img class='logo-img' src='data:image/png;base64,{base64.b64encode(open(Flag_IMAGE, 'rb').read()).decode()}' class='img-fluid' width=150em style='display:block;'></h3>", unsafe_allow_html=True)
st.markdown(f"""<p style='background-color:#0073AB;padding-left:25px;padding-right:25px;padding-bottom:25px;font-family:Source Sans Pro;color:white'>The IRENA Solar PV Manufacturing Cost Model is a strategic decision-support tool developed under the CEM: Transforming Solar Supply Chains initiative, with the invaluable support of the Government of Australia. and the National Energy Efficiency Action Plan (PANEE), that expand on the commitment and measures included in the NDC.
<br>This Excel-based tool provides a quantitative framework to model the levelized cost of production (LCOP) for solar PV modules (USD/Wp) across the complete crystalline silicon value chain, from polysilicon to final module assembly. It covers key global manufacturing markets—including the United States, Germany, China, India, Vietnam, and Australia—and evaluates leading process technologies (monocrystalline PERC and TOPCon). The model allows users to analyze the cost implications of distinct supply chain configurations, such as scenarios based on domestic production versus imported components.
<br>The model is designed to empower policymakers, investors, and industry strategists by enabling them to quantify the impact of policy levers (e.g., tariffs, local content incentives), identify sources of national competitive advantage, and guide strategic investments required to build resilient and diversified solar PV supply chains through 2030.</p>""", unsafe_allow_html=True)


# Cache loading of Excel sheet names
@st.cache_data
def get_sheet_names(path):
    xls = pd.ExcelFile(path)
    return xls.sheet_names

# Cache reading of a specific sheet

def read_sheet(path, sheet_name):
    return pd.read_excel(path, sheet_name=sheet_name, header=None)

####################################################################################
#First graph
####################################################################################
# File path
file_path = "graph1.xlsx"
# Mapping from high-level scenario to display_name → sheet_name
SCENARIO_MAP = {
    "Domestic": {
        "Domestic - Manufacturing 2025: graph 1": "Domestic manufacturing in 2025",
        "Domestic - Manufacturing 2030: graph 2": "Domestic manufacturing in 2030"
    },
    "Imported from China": {
        "Imported - China - Polysilicon: graph 3":"Imported Polysilicon from China",
        "Imported - China - Wafer: graph 4":"Imported Wafer from China",
        "Imported - China - Cell: graph 5":"Imported Cell from China"
    },
    "Imported from Vietnam": {
        "Imported - Vietnam - Wafer: graph 6":"Imported Wafer from Vietnam",
        "Imported - Vietnam - Cell: graph 7":"Imported Cell from Vietnam"
    }
}
st.write("")
st.write("#### Comparative Scenario Analysis for the Major Markets")
col1, col2,col3= st.columns(3)
# First dropdown: select scenario category
col1.markdown("**Select Scenario Type:**")
selected_category = col1.selectbox("Scenario Type", list(SCENARIO_MAP.keys()), label_visibility="collapsed")

# Second dropdown: select sub-scenario
sub_scenarios = list(SCENARIO_MAP[selected_category].keys())
col2.markdown("**Select Sub-scenario:**")
selected_sub_scenario = col2.selectbox("Sub-scenario", sub_scenarios, label_visibility="collapsed")

# Get actual sheet name
original_sheet_name = SCENARIO_MAP[selected_category][selected_sub_scenario]

# Read data from the corresponding sheet
df = read_sheet(file_path, original_sheet_name)

# Extract and display title from the first 4 rows (rows 0 to 3)
title_rows = df.iloc[0:4]
title_text = " | ".join([str(cell) for cell in title_rows[0] if pd.notna(cell)])
st.markdown(f"{title_text}")


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
        name=tech,
        marker=dict(color=COMPONENT_COLORS.get(str(tech), None))  # fallback to default if missing
    ))

fig.update_layout(
    barmode='stack',
    xaxis_title='Country',
    yaxis_title='Total Module Cost USD/Wp',
    title = SCENARIO_MAP[selected_category][selected_sub_scenario],
    legend_title='Component',
    margin=dict(l=20, r=20, t=40, b=20),
)

st.plotly_chart(fig, use_container_width=True)

#################################################################
#Second Graph section
st.markdown("---")
# =========================
# Second Graph (Graph 2)
# =========================

st.markdown("#### Comparative Analysis between Domestic and Imported at Country Level")
col1, col2,col3= st.columns(3)
# Import country selection
import_country = col1.selectbox("Select the Country of Import:", ["China", "Vietnam"])

# File mapping
FILE_MAP = {
    "China": "graph2_China.xlsx",
    "Vietnam": "graph2_Vietnam.xlsx"
}


@st.cache_data
def get_graph2_sheets(file_path):
    return pd.ExcelFile(file_path).sheet_names

@st.cache_data
def read_graph2_sheet(file_path, sheet_name):
    return pd.read_excel(file_path, sheet_name=sheet_name, header=None)

def plot_graph2_stacked_chart(df, import_country, sheet_name):
    # Extract and show title from cell A1
    title_cell = df.iloc[0, 0]

    if pd.notna(title_cell):
        st.markdown(title_cell)

    # Extract legend (components in col A, rows 4–15 → index 3–14)
    components = df.iloc[3:14, 0]

    # Extract bar values (cols B–E → index 1–4)
    data = df.iloc[3:14, 1:5]

    # Extract column names (countries) from row 2 (index 1)
    countries = df.iloc[1, 1:5]

    # Build figure
    fig = go.Figure()
    for i, component in enumerate(components):
        fig.add_trace(go.Bar(
            x=countries,
            y=data.iloc[i],
            name=component,
            marker=dict(color=COMPONENT_COLORS.get(str(component), None))  # fallback to default if missing
        ))

    fig.update_layout(
        barmode='stack',
        xaxis_title='Country',
        yaxis_title='Total Module Cost USD/Wp',
        title=f"",
        legend_title='Component',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


# Step 2: If country selected, show exporter dropdown
file_path = FILE_MAP[import_country]
sheet_names = get_graph2_sheets(file_path)

exporting_country = col2.selectbox(f"Select ?? from {import_country}:", sheet_names)

# Step 3: Load sheet and plot
df_graph2 = read_graph2_sheet(file_path, exporting_country)
fig_graph2 = plot_graph2_stacked_chart(df_graph2, import_country, exporting_country)
st.plotly_chart(fig_graph2, use_container_width=True)

#################################################################
#REFERENCES
st.markdown("---")
st.markdown("<h3 style='background-color:#58585A;padding-left:25px;padding-right:25px;padding-top:25px;color:white;'font-family:Source Sans Pro;>References</h3>", unsafe_allow_html=True)
st.markdown("""<p style='background-color:#58585A;padding-left:25px;padding-right:25px;padding-bottom:25px;font-family:Source Sans Pro;color:white'>
The information and data contained herein comes from the analysis supporting the report
<span style="color:black;">"PV Supply Chain Cost Model : Methodology, Results and Analysis"</span>.
<br>Please refer to the report to dig deeper and further explore the analysis conducted, the methodology used, and the default assumptions considered.
<br><br>
<b><span style="font-size:1.5rem; font-family: Arial;">Acknowledgements</span></b><br>
<SPAN class=li>The work was conducted under the strategic guidance of <span style="color:black;">Norela Constantinescu</span> (Acting Director, Innovation and Technology Centre, IRENA) and <span style="color:black;">Simon Benmarraze</span> (Team Lead, Technology and Infrastructure, IRENA).</SPAN>
<SPAN class=li>The core model development and analysis were conducted by <span style="color:black;">Aakarshan Vaid</span> (IRENA), <span style="color:black;">Alina Gilmanova</span> (IRENA), and <span style="color:black;">Deborah Ayres</span> (IRENA).</SPAN>     
<SPAN class=li>The visualization dashboard was developed by <span style="color:black;">Rayan Dankar</span> (IRENA).</SPAN>
<br>IRENA extends its sincere appreciation to the following external experts for their invaluable technical peer review and input: <span style="color:black;">Michael Woodhouse</span> (National Renewable Energy Laboratory - NREL), and<span style="color:black;"> Sandra Choy, Anna Mazzoleni,</span> and <span style="color:black;">Amanda Wormald</span> (DCCEEW, Australia).</span>
</p>""", unsafe_allow_html=True)


########################################
#Disclaimer - text is in style.css
st.markdown("---")
st.markdown("""
<div class='custom-footer'>
This dashboard for results visualization and the material herein are provided “as is.” While all reasonable precautions have been taken by IRENA to verify the reliability of the content, IRENA makes no warranty, expressed or implied, and accepts no responsibility for any consequences arising from its use. The findings, interpretations, and conclusions expressed do not necessarily represent the views of all IRENA Members. Mention of specific companies or products does not imply endorsement. All references to countries or territories are for statistical or analytical convenience and do not imply any judgment concerning their legal status or national boundaries.
</div>
""", unsafe_allow_html=True)

########################################