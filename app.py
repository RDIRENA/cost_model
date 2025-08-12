import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import base64 #for images
import plotly.express as px
import re

st.set_page_config(page_title='Cost Model', layout = 'wide', page_icon = 'Images/logo2.png', initial_sidebar_state = 'auto')
def insert_logo(imagePath):
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

st.markdown("<h3 style='text-align:center;background-color:#0073AB;font-family:Source Sans Pro;font-weight: 700;color:white;padding-left:25px;padding-right:25px;'>About the IRENA Solar PV Manufacturing Cost Model</h3>", unsafe_allow_html=True)
st.markdown(f"""<p style='background-color:#0073AB;padding-left:25px;padding-right:25px;padding-bottom:25px;font-family:Source Sans Pro;color:white'>
The IRENA Solar PV Manufacturing Cost Model is a strategic decision-support tool developed under the Clean Energy Ministerial (CEM): Transforming Solar Supply Chains initiative, with the invaluable support of the Government of Australia and the National Energy Efficiency Action Plan (PANEE), that expand on the commitment and measures included in the Nationally Determined Contributions (NDCs).
<br>This dashboard is a user-friendly interface providing an accessible way to explore insights quickly and visualize the results from the <u><b>Solar PV Manufacturing Cost Model</b></u>. It displays outputs based on default data, allowing users to visualise some scenarios and better understand how different factors shape total costs.
<br>However, for more detailed analysis user is invited to consult the the Excel-based tool, which provides a quantitative framework to model the levelized cost of production (LCOP) for solar PV modules (USD/Wp) across the whole value chain, from polysilicon to final module assembly. It covers key global manufacturing markets—including the United States, Germany, China, India, Vietnam, and Australia—and evaluates leading process technologies (monocrystalline PERC and TOPCon). The model allows users to analyze the cost implications of distinct supply chain configurations, such as scenarios based on domestic production versus imported components. The results presented in the dashboard focus on TOPCon, which is the main technology present in the market.
<br>The model is designed to empower policymakers, investors, and industry strategists by enabling them to quantify the impact of policy levers (e.g., tariffs, local content incentives), identify sources of national competitive advantage, and guide strategic investments required to build resilient and diversified solar PV supply chains through 2030.
<br>For more information on the analysis of the results and policy recommendations, please read the report <u><b>PV Supply Chain Cost Model Methodology, Results and Analysis.</b></u>
</p>""", unsafe_allow_html=True)


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
        "Domestic - Manufacturing 2025": "Domestic manufacturing in 2025",
        "Domestic - Manufacturing 2030": "Domestic manufacturing in 2030"
    },
    "Imported from China": {
        "Imported - China - Polysilicon":"Imported Polysilicon from China",
        "Imported - China - Wafer":"Imported Wafer from China",
        "Imported - China - Cell":"Imported Cell from China"
    },
    "Imported from Vietnam": {
        "Imported - Vietnam - Wafer":"Imported Wafer from Vietnam",
        "Imported - Vietnam - Cell":"Imported Cell from Vietnam"
    }
}
st.write("")
st.write("#### Comparative Scenario Analysis for the Major Markets")
st.write("To better assess the impact of various factors—such as trade policies and regional cost differences—this section compares domestic PV module production across the countries which data is available in the cost model: the **United States, Germany, India, Australia, Vietnam, and China**. These countries were selected due to their active policy support for local PV manufacturing.")
st.write("Results from the following scenarios are presented:")
st.write("•	**Domestic manufacturing in 2025 and 2030:** The component is sourced within the manufacturing country and an increase in the manufacturing capacity between 2025 and 2030 is considered. For this comparison, the model assumes a manufacturing capacity of 50 tons for polysilicon and 4 GW for wafers, cells, and modules across all markets in 2025 and 6 GW for wafers, cells, and modules across all markets in 2030.")
st.write("•	**Imported components from China or Vietnam:** Polysilicon, wafer and cells are supplied from a different market than the manufacturing country of the solar PV module. The cost of final PV modules is presented considering polysilicon, wafer or cells, are imported from China or Vietnam, while all the module assembly is produced domestically. Manufacturing is only considered in 2025.")

st.write("##### Key Steps:")
col1, _,_= st.columns(3)
# First dropdown: select scenario category
col1.markdown("**1. Select Scenario Type:**")
selected_category = col1.selectbox("Scenario Type", list(SCENARIO_MAP.keys()), label_visibility="collapsed")


# Second dropdown: select sub-scenario
col2, _,_= st.columns(3)
sub_scenarios = list(SCENARIO_MAP[selected_category].keys())
col2.markdown("**2. Select Sub-scenario:**")
selected_sub_scenario = col2.selectbox("Sub-scenario", sub_scenarios, label_visibility="collapsed")

# Get actual sheet name
original_sheet_name = SCENARIO_MAP[selected_category][selected_sub_scenario]

# Read data from the corresponding sheet
df = read_sheet(file_path, original_sheet_name)

# Extract and display title from the first 4 rows (rows 0 to 3)
title_rows = df.iloc[0:4]
title_text = " | ".join([str(cell) for cell in title_rows[0] if pd.notna(cell)])
col3, _,_= st.columns(3)
col3.markdown("**3. Results:**")
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
st.markdown(
    "<p style='font-size: 0.85em; font-style: italic; color: gray;'>Note: Usually, solar cell includes the costs of wafers and polysilicon. However, in the import scenarios of wafer and polysilicon costs are shown separately (excluded from the solar cell cost) to highlight contribution of each segment.</p>",
    unsafe_allow_html=True
)
#################################################################
#Second Graph section
st.markdown("---")
# =========================
# Second Graph (Graph 2)
# =========================

st.markdown("#### Comparative Analysis between Domestic and Imported at Country Level")
st.write("This section illustrates the comparative cost structure of PV modules under two scenarios: **domestic manufacturing** and **imported components**. By visualizing these elements side by side, the graph highlights the cost competitiveness of each manufacturing route.")
st.write("The purpose of this comparison is to identify which option—domestic production or import of components—offers a more economically viable solution for PV module manufacturing. A lower total cost indicates the more competitive manufacturing pathway, taking into account both direct production expenses and associated supply chain costs.")

st.write("##### Key Steps:")
col1, _,_= st.columns(3)
# Import country selection
col1.markdown("**1. Select the Country of Import:**")
import_country = col1.selectbox("Country of Import:", ["China", "Vietnam"],label_visibility="collapsed")

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
col2, _,_= st.columns(3)
col2.markdown("**2. Select Country of Manufacturing:**")
exporting_country = col2.selectbox(f"Country of Manufacturing:", sheet_names,label_visibility="collapsed")

col3, _,_= st.columns(3)
col3.markdown("**3. Results:**")

# Step 3: Load sheet and plot
df_graph2 = read_graph2_sheet(file_path, exporting_country)
fig_graph2 = plot_graph2_stacked_chart(df_graph2, import_country, exporting_country)
st.plotly_chart(fig_graph2, use_container_width=True)
# Add a note in small, italic, muted font
st.markdown(
    "<p style='font-size: 0.85em; font-style: italic; color: gray;'>Note: Usually, solar cell includes the costs of wafers and polysilicon. However, in the import scenarios of wafer and polysilicon costs are shown separately (excluded from the solar cell cost) to highlight contribution of each segment.</p>",
    unsafe_allow_html=True
)

##################################################################
st.markdown("---")
st.markdown("#### Environmental, Social, and Governance (ESG) certification ")
st.write("As **Environmental, Social, and Governance (ESG) certification** becomes increasingly important for PV manufacturing, the tool has an optional parameter to incorporate the cost of certification into the modelling.  The certification costs typically involve:")
st.markdown("""<SPAN class=li>Initial assessment</SPAN> 
<SPAN class=li>Implementation of ESG practices</SPAN>
<SPAN class=li>Documentation and reporting</SPAN>
<SPAN class=li>Third-party verification</SPAN>
""", unsafe_allow_html=True)
st.markdown("While the exact figures are difficult to provide without specific company details, a general range is used, which we assume to be similar across different countries:")
st.markdown("""<SPAN class=li>Small to medium-sized manufacturers (under 2-3 GW): USD 10 000 – USD 50 000</SPAN> 
<SPAN class=li>Large manufacturers (from 3 GW): USD50 000 - USD200 000</SPAN>
<SPAN class=li>Ongoing costs: Annual maintenance and re-certification fees can range from USD 5 000 to USD 50 000</SPAN>
""", unsafe_allow_html=True)
st.markdown("Based on consultations with ESG certification stakeholders, cost variations across countries are minimal; therefore, the model assumes uniform costs across all selected countries.")
st.markdown("""Please refer to the publication "Solar PV supply chains: Technical and ESG standards for market integration" available at IRENA website <a href='https://www.irena.org/Publications/2024/Sep/Solar-PV-supply-chains-Technical-and-ESG-standards-for-market-integration'>here</a>.""", unsafe_allow_html=True)

st.markdown("#### Main findings and highlights")
st.markdown("""Domestic manufacturing generally has higher costs, particularly when compared to importing components from lower-cost international markets. The most significant cost reductions are observed when importing cells, underscoring the competitive price advantage of established and mature manufacturing centers abroad.

Manufacturing costs vary significantly across countries due to differences in key input factors:""")
st.markdown("""<SPAN class=li><b>Vietnam</b> benefits from cost levels comparable to China, thanks to its geographic proximity to suppliers, low labor costs, and affordable electricity.</SPAN> 
<SPAN class=li><b>India</b> also enjoys low labor costs but faces higher production expenses in 2024, mainly due to elevated electricity tariffs.</SPAN>
<SPAN class=li>Australia, the United States, and European countries all experience higher manufacturing costs, though for slightly different reasons:</SPAN>
<SPAN class=subli>In <b>Australia</b>, high electricity, labor, and building and facilities costs are the main drivers.</SPAN>
<SPAN class=subli>In the <b>United States</b>, labor, building and facilities costs are particularly expensive, although electricity prices vary by region and can be relatively low.</SPAN>
<SPAN class=subli><b>European</b> manufacturers face a combination of high electricity rates and elevated labor and building and facilities costs, contributing to increased overall costs.</SPAN>
""", unsafe_allow_html=True)
st.markdown("The model demonstrates a clear tension between short-term market dynamics and long-term industry sustainability. While low-cost production in China have supported rapid solar deployment globally, these prices are significantly below sustainable production levels. This underscores the need for a balanced approach: maintaining affordability to support solar adoption while ensuring fair market conditions that enable manufacturers—both domestic and international—to operate sustainably.")
#################################################################
#REFERENCES
st.markdown("---")
st.markdown("<h3 style='background-color:#58585A;padding-left:25px;padding-right:25px;padding-top:25px;color:white;'font-family:Source Sans Pro;>References</h3>", unsafe_allow_html=True)
st.markdown("""<p style='background-color:#58585A;padding-left:25px;padding-right:25px;padding-bottom:25px;font-family:Source Sans Pro;color:white'>
The information and data contained herein comes from the analysis supporting the report
<b>"PV Supply Chain Cost Model : Methodology, Results and Analysis"</b>.
<br>Please refer to the report to dig deeper and further explore the analysis conducted, the methodology used, and the default assumptions considered.
<br><br>
<b><span style="font-size:1.5rem; font-family: Arial;">Acknowledgements</span></b><br>
<SPAN class=li>The work was conducted under the strategic guidance of <b>Norela Constantinescu</b> (Acting Director, Innovation and Technology Centre, IRENA) and <b>Simon Benmarraze</b> (Team Lead, Technology and Infrastructure, IRENA).</SPAN>
<SPAN class=li>The core model development and analysis were conducted by <b>Aakarshan Vaid</b> (IRENA), <b>Alina Gilmanova</b> (IRENA), and <b>Deborah Ayres</b> (IRENA).</SPAN>     
<SPAN class=li>The visualization dashboard was developed by <b>Rayan Dankar</b> (IRENA).</SPAN>
<br>IRENA extends its sincere appreciation to the following external experts for their invaluable technical peer review and input: <b>Michael Woodhouse</b> (National Renewable Energy Laboratory - NREL), and<b> Sandra Choy, Anna Mazzoleni,</b> and <b>Amanda Wormald</b> (DCCEEW, Australia).
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