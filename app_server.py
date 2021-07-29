import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
import pandas as pd
import plotly.express as px

data1 = {'% recuperación': [num for num in range(1, 100)],
         'Material recuperado': [num for num in range(1, 100)],
         'Material requerido': [100 for num in range(1, 100)]}

df = pd.DataFrame(data1)


external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'dbc.themes.BOOTSTRAP',
    'https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap'
    # {
    #     "href": "https://fonts.googleapis.com/css2?"
    #             "family=Lato:wght@400;700&display=swap",
    #     "rel": "stylesheet",
    #     }
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                title="Federica Cork Analytics!")
server = app.server

markdown_text = '''
Esta es una herramienta interactiva que permite analizar la relación entre cantidad de materia prima requerida y la
cantidad disponible en función de la tasa de recuperación esperada para el material. Para ello:
* Calcula la `Disponibilidad` anual en kilogramos de materia prima en función del estimado de  Botellas comercializadas 
al año (`Botellas año`) y el contenido en kilogramos del corcho de cada botella (`Peso corcho`)
* Calcula el `Requerimiento` anual en kilogramos en función de las `unidades anuales` estimadas a producir, la 
cantidad de corcho` promedio por producto y la `tasa de aprovechamiento` de la materia prima (es decir, que porcentaje del 
corcho recogido es realmente reutilizable)

El punto de cruce de las lineas permite determinar la `tasa de recuperación` mínima requerida. 

**¡Experimenta cambiando algunos de los valores!**
'''

app.layout = html.Div([
    html.Div(
        children=[
            #html.P(children="🥑", className="header-emoji"),
            #html.Img(src='/assets/favicon.ico', className="header-emoji"),
            html.H1(
                children="Federica Cork", className="header-title"
            ),
            html.P(
                children="Herramientas de análisis de la viabilidad técnica"
                         " Disponibilidad de materia prima - Costo de adquisición",
                className="header-description",
            ),
        ],
        className="header",
    ),
    html.Div([
        html.Div([
            html.Div([
                html.H6("Disponibilidad de corcho"),
                html.Label('Botellas año'),
                dcc.Input(id='botellas', value= 10000, type='number'),
                html.Br(),
                html.Label('Peso corcho (kg)'),
                dcc.Input(id='peso_corcho', value=0.05, type='number'),
                html.Br(),
                html.Br(),
                #html.Div(id='mp_total'),
                html.Div([
                    html.Label('Disponibilidad (kg)'),
                    html.Label(id='mp_total')]),
                html.Br(),
                ],
                className="card",
            ),
            html.Div([
                html.H6('Requerimientos corcho'),
                html.Label('Tasa aprovechamiento (%)'),
                dcc.Slider(
                    id="aprovechamiento",
                    min=0,
                    max=100,
                    marks={0: str(0),
                           100:  str(100)},
                    #marks = {i: str(i) for i in [num for num in range(1, 100) if num % 5 == 0]},
                    step=1,
                    value=70,
                    tooltip = { 'always_visible': True }
                ),
                html.Br(),
                html.Label('Unidades anuales'),
                dcc.Input(id='unidades', value=100, type='number'),
                html.Br(),
                html.Label('Corcho por producto (kg)'),
                dcc.Input(id='corcho_prod', value=1.3, type='number'),
                html.Br(),
                html.Br(),
                #html.Div(),
                html.Div([
                    html.Label('Requerimiento (kg)'),
                    html.Label(id='requerimiento')]),
                html.Br(),
                ],
                className="card",
            )

        ],  style = {"padding" : 10},
            className="three columns"
        ),

        html.Div([
            html.Div(
                children=dcc.Graph(
                    id="chart",
                    #config={"displayModeBar": False},
                ),
                className="card",
            ),
            dcc.Markdown(children=markdown_text)
        ], className="nine columns",
           style = {"padding" : 10}),
    ], className="row")
])




@app.callback(
    Output(component_id='mp_total', component_property='children'),
    Input(component_id='botellas', component_property='value'),
    Input(component_id='peso_corcho', component_property='value')
)
def update_totalMP(n_botellas,
                   pesoCorcho):
    total_mp = n_botellas * pesoCorcho
    return "{:.1f}".format(total_mp)


@app.callback(
    Output(component_id='requerimiento', component_property='children'),
    Input(component_id='unidades', component_property='value'),
    Input(component_id='corcho_prod', component_property='value'),
    Input(component_id='aprovechamiento', component_property='value')
)
def update_requerimiento(n_unidades,
                         corchProd,
                         per_aprovech):
    requer = n_unidades * corchProd/(per_aprovech/100)
    return "{:.1f}".format(requer)


@app.callback(
    Output('chart', 'figure'),
    Input(component_id='mp_total', component_property='children'),
    Input(component_id='requerimiento', component_property='children'),
    )
def update_figure(mp_total_text,
                  requerimiento_text):
    copied_data = df
    copied_data["Material recuperado"] = copied_data["% recuperación"]*float(mp_total_text)/100
    copied_data["Material requerido"] = float(requerimiento_text)
    fig1 = px.line(copied_data,
                   x="% recuperación",
                   y=["Material requerido", "Material recuperado"],
                   title="Relación entre la tasa de recuperación y el requerimiento de materia prima",
                   labels={'value':'Toneladas'},
                   )
    fig1.update_layout(xaxis={'ticksuffix': '%'}, hovermode="x unified", transition_duration=500)

    return fig1


if __name__ == "__main__":
    app.run_server(debug=True)