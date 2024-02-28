"""
This script creates a dashboard using Dash and Plotly to visualize Canadian cancer statistics.
It allows users to filter the data based on region, cancer type, and sex.
The dashboard displays two line graphs: one showing the number of new cancer cases and the other showing the average age at diagnosis.
The graphs are interactive and update based on the user's filter selections.
"""

from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import plotly.io as pio
import statsmodels.api as sm
import statsmodels.formula.api as smf

# App initialization
app = Dash(__name__)

# Reading the data
data = pd.read_csv("data.csv")

new_cancer = data[data["Characteristics"] == "Number of new cancer cases"]
age_at_diagnosis = data[data["Characteristics"] == "Average age at diagnosis"]

# Finding unique values for each column
regions = data["GEO"].unique()
types = data["Primary types of cancer (ICD-O-3)"].unique()
sex = data["Sex"].unique()


# HTML LAYOUT
app.layout = html.Div(className="app", children=[
  html.Div(className="left", children=[
    html.H1(children="Filters"),
    html.Div(className="dropdowns", children=[
      html.H2(children="Region"),
      dcc.Dropdown(id="dropdown-region", options=regions, value="Canada"),

      html.H2(children="Cancer Type"),
      dcc.Dropdown(id="dropdown-cancer-type", options=types, value="Total, all primary sites of cancer [C00.0-C80.9]"),

      html.H2(children="Sex"),
      dcc.Dropdown(id="dropdown-sex", options=sex, value=["Both sexes"], multi=True)
    ])
  ]),
  html.Div(className="right", children=[
    html.H1(children="Canadian Cancer Statistics Dashboard", className="header"),
    dcc.Graph(id='graph-1', className="graph"),
    dcc.Graph(id='graph-2', className="graph")
  ])
])


@app.callback(
  Output('graph-1', 'figure'),
  [Input('dropdown-cancer-type', 'value'),
   Input('dropdown-region', 'value'),
   Input('dropdown-sex', 'value')]
)
def update_graph_1(cancer_type, selected_region, sex):
  """
  Callback function to update the first graph based on user's filter selections.
  """
  fig = px.line(labels={"REF_DATE": "Year", "VALUE": "Number of new cancer cases"},
          title=f'Cancer Cases in {selected_region}')
  
  for chosenSex in sex:
    filtered_data = new_cancer[new_cancer["GEO"] == selected_region]
    filtered_data = filtered_data[filtered_data["Primary types of cancer (ICD-O-3)"] == cancer_type]
    filtered_sex_data = filtered_data[filtered_data["Sex"] == chosenSex]
    filtered_sex_data = filtered_sex_data[filtered_sex_data["REF_DATE"] <= 2017]

    fig.add_scatter(x=filtered_sex_data["REF_DATE"], y=filtered_sex_data["VALUE"],
            mode='lines', name=chosenSex) 
    
    # Calculate OLS regression line
    x = sm.add_constant(filtered_sex_data["REF_DATE"])
    y = filtered_sex_data["VALUE"]
    model = smf.ols(formula="VALUE ~ REF_DATE", data=filtered_sex_data).fit()
    predicted_y = model.predict(filtered_sex_data[["REF_DATE"]])

    fig.add_scatter(x=filtered_sex_data["REF_DATE"], y=predicted_y,
            line=dict(color='rgba(0, 0, 255, 0.2)', dash='dash'), name="Regression Line")  

    
  fig.update_layout(template="seaborn")
  fig.update_xaxes(title_text="Year", range=[None, 2017])
  fig.update_yaxes(title_text="Number of new cancer cases")
  return fig

@app.callback(
  Output('graph-2', 'figure'),
  Input('dropdown-cancer-type', 'value'),
  Input('dropdown-region', 'value'),
  Input('dropdown-sex', 'value')
)
def update_graph_2(cancer_type, selected_region, sex):
  """
  Callback function to update the second graph based on user's filter selections.
  """
  fig = px.line(labels={"REF_DATE": "Year", "VALUE": "Number of new cancer cases"},
          title=f'Average age at diagnosis in {selected_region}')
  
  for chosenSex in sex:
    filtered_data = age_at_diagnosis[age_at_diagnosis["GEO"] == selected_region]
    filtered_data = filtered_data[filtered_data["Primary types of cancer (ICD-O-3)"] == cancer_type]
    filtered_sex_data = filtered_data[filtered_data["Sex"] == chosenSex]
    filtered_sex_data = filtered_sex_data[filtered_sex_data["REF_DATE"] <= 2017]

    fig.add_scatter(x=filtered_sex_data["REF_DATE"], y=filtered_sex_data["VALUE"],
            mode='lines', name=chosenSex) 
    
    # Calculate OLS regression line
    x = sm.add_constant(filtered_sex_data["REF_DATE"])
    y = filtered_sex_data["VALUE"]
    model = smf.ols(formula="VALUE ~ REF_DATE", data=filtered_sex_data).fit()
    predicted_y = model.predict(filtered_sex_data[["REF_DATE"]])

    fig.add_scatter(x=filtered_sex_data["REF_DATE"], y=predicted_y,
            line=dict(color='rgba(0, 0, 255, 0.2)', dash='dash'), name="Regression Line")  
  
    
  fig.update_layout(template="seaborn")
  fig.update_xaxes(title_text="Year", range=[None, 2017])
  fig.update_yaxes(title_text="Average age at diagnosis")
  return fig

# Running the app
app.run(debug=True)
