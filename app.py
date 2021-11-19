import pandas as pd
import numpy as np
import plotly.express as px
import requests
import pymongo
from dotenv import load_dotenv
from dash import Dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input,Output,State, ALL
import plotly.graph_objects as go
import os
import plotly.figure_factory as ff

load_dotenv()

#user=os.environ.get('USER')
#password=os.environ.get('PASSWORD')
#server=os.environ.get('SERVER')
#bd=os.environ.get('DB')

geojson = requests.get('https://cdn.buenosaires.gob.ar/datosabiertos/datasets/barrios/barrios.geojson').json()
#uri = f'mongodb+srv://{user}:{password}@{server}/{bd}?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE'
#data = list(pymongo.MongoClient(uri)['bohemio']['datos_barrios'].find())
#df_scores = pd.DataFrame.from_records(data)

df_scores = pd.read_csv('datos_final_dash.csv')
df_scores.rename(columns={'area': 'superficie'}, inplace=True)
df_scores['m2verdes'] =[round(i) for i in df_scores.m2verdes]

#defino un diccionario que contiene las etiquetas de cada indicador.
score_labels = {
    'score_poblacion':'Población | Cant. Habitantes / Superficie',
    'score_valuacion':'Valuación | Valor Venta por M2 en USD',
    'score_educacion':'Educación | Cant. Escuelas / Densidad Poblacional',
    'score_salud':'Salud | Cant. Hospitales / Densidad Poblacional',
    'score_transporte':'Accesibilidad | Cant. Estaciones de Transporte Público / Superficie',
    'score_verde':'Espacios Verdes | M2 de Espacios Verdes / Superficie',
    'score_delitos':'Seguridad | Índice de Delincuencia',
    'score_accidentes':'Accidentes | Siniestros viales / (Superficie * Cant. Hab)',
    'score_esparcimiento':'Esparcimiento | Cant. Locales Gastronómicos / Superficie',
    'score_barriospop':'Barrios Populares | Cant. Habitantes de Barrios Populares',
}

score_labels_inv = {
    'score_poblacion':'Población',
    'score_valuacion_inv':'Valuación',
    'score_educacion':'Educación',
    'score_salud':'Salud',
    'score_transporte':'Accesibilidad',
    'score_verde':'E. Verdes',
    'score_delitos_inv':'Delitos',
    'score_accidentes_inv':'Accidentes',
    'score_esparcimiento':'Esparcimiento',
    'score_barriospop_inv':'Barrios Populares',
}

data_labels ={'densidad_poblacion':'Cant. Habitantes / Superficie', 
              'valorxm2':'Valor Venta por M2 en USD', 
              'centros_ed_x_densidad_pobl': 'Cant. Escuelas / Densidad Poblacional', 
              'centrosalud_x_densidad_pobl':'Cant. Hospitales / Densidad Poblacional', 
              'densidad_stc':'Cant. Estaciones de Transporte Público / Superficie', 
              'densidad_verde':'M2 de Espacios Verdes / Superficie', 
              'grado_delincuencia':'Índice de Delincuencia', 
              'habitantes_bp':'Cant. Personas en Barrios Populares'}

#listado de scores
data = ['superficie','comuna', 'poblacion', 'valorxm2', 'cant_escuelas', 'cant_hospitales', 'cant_estaciones_stc', 'm2verdes', 'grado_delincuencia', 'cant_bp']
data_mult = ['BARRIO']+data

color1=['#4541bf','#636bc7','#8195d0','#9fc0d8', '#bdeae1']
escala1 = ['Muy Alto', 'Alto', 'Medio', 'Bajo', 'Muy Bajo']
escala_dict1 = {'1':'Muy Bajo', '2':'Bajo', '3':'Medio', '4':'Alto', '5':'Muy Alto'}


escala2 = ['Muy Alto', 'Alto', 'Bajo', 'Muy Bajo']
escala_dict2 = {'1': 'Muy Bajo', '2':'Bajo', '3':'Alto', '4':'Muy Alto'}
color2=['#4541bf','#636bc7','#9fc0d8', '#bdeae1']
#['#7AC45C', '#AEEB5A','#73D2BF','#FC5845', '#C40186']

app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True,meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    ])
server = app.server
app.title='Bohemio - Conocé tu Ciudad'
app._favicon = 'logo.ico'

navbar=dbc.Navbar([
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src='./assets/logo.svg', height="60em")),
                ],
                align="center",
            ), href='/page-1'
        ),
        html.Div(
            [
             dbc.NavItem(dbc.NavLink("Investigá", href="/page-1", style={'text-decoration':'None', 'color':'#0E4666'})),
             dbc.NavItem(dbc.NavLink("Buscá", href="/page-2", style={'text-decoration':'None', 'color':'#0E4666'})),
             dbc.NavItem(dbc.NavLink("Informate", href="/page-3", style={'text-decoration':'None', 'color':'#0E4666'})),
             dbc.NavItem(dbc.NavLink("Compará", href="/page-4", style={'text-decoration':'None', 'color':'#0E4666'})),
            ], style={'display':'flex'}
        )
        
    ],
    color='#FFFFF',
    className='pt-4',
    )

indicadores = dbc.Card([
                        html.H5('Seleccioná Indicador', style={'color':'#0E4666'}),
                        dbc.Checklist(id='indicador', options=[{'value':i,'label':score_labels_inv.get(i)} for i in score_labels_inv], value=[],className='pt-2', style={'color':'#0E4666', 'font-size':'14px'})
              ],body=True)
titulo=html.H5('Elegí tu preferencia', className='pb-2')
sliders = dbc.Card(
                   children=[titulo], className='pt-4 pb-4', id='card', style={'color':'#0E4666'}
                   )


checklist = dbc.Card([
                html.H5('Seleccionar indicador', style={'color':'#0E4666'}),
                html.P('Agregue todos los indicadores que desee relacionar y visualizar en el Mapa.', style={'color':'#0E4666'}),
                dbc.Checklist(id='seleccion_score', options=[{'value':i,'label':score_labels.get(i)} for i in score_labels],
                              value=list(score_labels)[:1], labelStyle={'display':'inline-block','color':'#0E4666', 'font-size':'12px', 'padding-bottom':'10px'})
            ], body=True)   


dropdown1 = html.Div([
                        dbc.Row(dbc.Col(html.H5('Conocé los datos', className='pt-3 text-center', style={'color':'#0E4666'}))),
                        dbc.Row([
                            dbc.Col(
                                    [html.H6('Elegí un barrio', className='text-center', style={'color':'#0E4666'}),
                                    dcc.Dropdown(id='barrio', clearable=False, options=[{'value':i,'label':i.title()} for i in df_scores.BARRIO], style={'color':'#0E4666'}, value='PALERMO')],sm=6
                                ),
                            dbc.Col(
                                [html.H6('Seleccioná un indicador', className='text-center', style={'color':'#0E4666'}),
                                dcc.Dropdown(id='dropdown-1', options=[{'value':i,'label':data_labels.get(i)} for i in data_labels], 
                                         value='densidad_poblacion',placeholder="Seleccionar indicador", clearable=False,style={'color':'#0E4666','font-size':'18px'})],sm=6
                        )   
                            
                            
                            ], className='pt-3'),
                            
                                 
              ])

barrios = dbc.Card([
                     dbc.Row(dbc.Col(html.H5('Seleccioná los barrios a comparar'), className='pt-3 text-center',style={'color':'#0E4666'}, md=12)),
                     dbc.Row([
                              dbc.Col(
                                dcc.Dropdown(id='barrios-1', clearable=False, options=[{'value':i,'label':i.title()} for i in df_scores.BARRIO], style={'color':'#0E4666'}, value='PALERMO'),sm=6
                              ),
                              dbc.Col(
                                dcc.Dropdown(id='barrios-2', clearable=False, options=[{'value':i,'label':i.title()} for i in df_scores.BARRIO], style={'color':'#0E4666'}, value='CHACARITA'), sm=6
                            )], className='p-3')
                     
])


inf1 = dbc.Col([
    dcc.Graph(id='fig3', responsive=True)], sm=6)
inf2 = dbc.Col([
    dcc.Graph(id='fig4', responsive=True)
],sm=6)

page_1 = dbc.Container([
    dbc.Row([dbc.Col(navbar, sm=12)]),
    html.Hr(),
    dbc.Row([
        dbc.Col([
                checklist    
        ], md=4, sm=12),
        dbc.Col([
            dbc.Card([
                html.H5('Barrios de CABA', style={'color':'#0E4666'}, className='pt-3 text-center'),
                dcc.Graph(id='fig1', responsive=True)
            ])
        ], md=8, sm=12)
    ]),
])


page_2 = dbc.Container([
    dbc.Row([dbc.Col(navbar, sm=12)]),
    html.Hr(),
    dbc.Row([
        dbc.Col(indicadores, md=2, sm=6),
        dbc.Col(sliders, md=4,sm=6,className='text-center'),
        dbc.Col(
                 [
                  dbc.Card([ 
                      dcc.Graph(id='fig2', responsive=True)])
                  ], md=6, sm=12)
    ]),
])


page_3 = dbc.Container([
                        dbc.Row([dbc.Col(navbar, sm=12)]),
                        html.Hr(),
                        dbc.Row(dbc.Col(dbc.Card(dropdown1, className='pb-4 ps-5 pe-5'))),
                        dbc.Row(
                            [
                            dbc.Col(
                                dbc.Card(dbc.Row([
                                    inf1,
                                    inf2
                                ]))
                                , sm=12
                                
                            )
                            ], className='pt-4')
                        
])

page_4= dbc.Container([
        dbc.Row([dbc.Col(navbar, sm=12)]),
        html.Hr(),
        dbc.Row([
            dbc.Col(
                barrios         
            )
        ]),
        dbc.Row([
            dbc.Col(
                dbc.Card([ 
                      dcc.Graph(id='fig5', responsive=True)]), sm=12, className='mx-auto'       
            )
        ], className='pt-3')
        
    
    
])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', children=page_1)
])

@app.callback(
    Output('fig1', 'figure' ),
    Input('seleccion_score','value')
)
def display_grafico(seleccion_score):
    
    
    if len(seleccion_score) == 1:
            if seleccion_score[0] == 'score_accidentes' or seleccion_score[0]=='score_valuacion':
                df_scores['score_cat'] = df_scores[seleccion_score[0]].astype(str).map(escala_inv_dict)
            else:
                df_scores['score_cat'] = df_scores[seleccion_score[0]].astype(str).map(escala_dict1)

            fig = px.choropleth(df_scores, geojson=geojson, color='score_cat',
                                locations="BARRIO", featureidkey="properties.BARRIO",
                                projection="mercator", color_discrete_sequence= color1
                                ,category_orders={'score_cat':escala1}, labels = {'score_cat': 'Ind. Resultado'}, hover_data=data
                               )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    elif len(seleccion_score) > 1:
            df_dinamico = df_scores.loc[:, data_mult+seleccion_score]
            df_dinamico['suma_scores'] = df_dinamico[seleccion_score].sum(axis = 1, numeric_only=True)
            df_dinamico['score_resultado'] = pd.qcut(df_dinamico['suma_scores'], q = 4, labels=['1','2','3','4']).map(escala_dict2)
            fig = px.choropleth(df_dinamico, geojson=geojson, color=df_dinamico.score_resultado,
                                locations="BARRIO", featureidkey="properties.BARRIO",
                                projection="mercator", color_discrete_sequence= color2,
                                category_orders={'score_resultado':escala2}, labels = {'score_resultado':'Ind. Resultado'}, hover_data=data 
                                )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    else:
      fig={}
    return fig

@app.callback(
    Output('card', 'children'),
    Input('indicador', 'value'),
)
def sliders(indicador):
  if len(indicador) > 0:
    labels = [dbc.Label(id=i, children=score_labels_inv.get(i), style={'font-size':'14px'}) for i in indicador]
    sliders = [dcc.RangeSlider(id={'type':'my-slider','index':i}, min=1, max=5, step=1, value=[1,2], marks={1:'Muy Bajo', 2:'Bajo',3:'Normal',4:'Alto',5:'Muy Alto'}, className='ml-3 mr-3 pt-1',persistence=True) for i in indicador]
    combined = [titulo]
    for i in range(len(labels)):
      combined.append(labels[i])
      combined.append(sliders[i])
  else:
    combined = [titulo]

  return combined
  

@app.callback(
    Output('fig2', 'figure'),
    Input({'type': 'my-slider', 'index': ALL}, 'id'),
    Input({'type': 'my-slider', 'index': ALL}, 'value')
)
def display(ids, values):
  try:
    sliders = [[ids[i]['index'], values[i]] for i in range(len(ids))]
    df = df_scores.loc[(df_scores[sliders[0][0]] >= sliders[0][1][0]) & (df_scores[sliders[0][0]] <= sliders[0][1][1])]
    data = []
    for i in (sliders):
      data.append(i[0])
      df = df.loc[(df[i[0]] >= i[1][0]) & (df[i[0]] <= i[1][1]), :]

    df_scores['Resultado'] = np.where(df_scores.BARRIO.isin(df.BARRIO), 'Cumple Requisitos', 'No Cumple Requisitos')

    fig = px.choropleth(df_scores, geojson=geojson, color='Resultado',
                      locations="BARRIO", featureidkey="properties.BARRIO",
                      projection="mercator", hover_data=data, color_discrete_map={'Cumple Requisitos': '#4541bf', 'No Cumple Requisitos': '#bdeae1'}
                    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig  
  except:
    return {}


@app.callback(
    Output('fig3', 'figure'),
    Input('dropdown-1', 'value'),
    Input('barrio', 'value')
)
def lineplot(tema, barrio):
    df_b = df_scores
    df_a = df_scores[['BARRIO', tema]].sort_values(tema, ascending=False).reset_index(drop=True)[['BARRIO']]
    df_a['ranking'] = [f'Posición: {i+1}'for i in df_a.index]
    df_b = df_b.merge(df_a, how='left', on='BARRIO')
    colores = [("#57F9E2" if i == barrio else '#FC5845')  for i in df_b["BARRIO"] ]
    anchos  = [(10 if i == barrio else 5) for i in df_b["BARRIO"] ]
    
    fig = go.Figure(data=[go.Scatter(y=df_b[tema], x=df_b["BARRIO"],                                  
                                 marker_color=colores,
                                 marker_opacity=1,
                                 marker_size=anchos,
                                 marker_line_color=colores,
                                 mode='lines+markers',
                                 text= df_b.ranking,
                                 line=dict(color="#FC5845")
                                 )])
    fig.update_xaxes(showticklabels=False,title_text = "Barrios")
    fig.update_yaxes(showticklabels=False,title_text = data_labels.get(tema))
    fig.update_layout(title={
        'text': f'El barrio resaltado es {barrio.title()}',
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    return fig


@app.callback(
    Output('fig4', 'figure'),
    Input('dropdown-1','value'),
)
def display(tema):
    dfl = df_scores.nlargest(3,tema)[["BARRIO",tema]].sort_values(tema, ascending=False)
    dfs = df_scores.nsmallest(3,tema)[["BARRIO",tema]].sort_values(tema, ascending=False)
    fig = go.Figure(
        data = [
        go.Bar(name="Lo más",   x=dfl["BARRIO"], y=dfl[tema], marker_color='#7AC45C'),
        go.Bar(name="Los menos",x=dfs["BARRIO"], y=dfs[tema], marker_color='#C40186')],
    )
    fig.update_xaxes(title_text = "")
    fig.update_yaxes(showticklabels=False,title_text = data_labels.get(tema))
    fig.update_layout(title={
        'text': "Los más y los menos",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    return fig

@app.callback(
    Output('fig5', 'figure'),
    Input('barrios-1', 'value'),
    Input('barrios-2', 'value'),
    
)
def multiple_polar(val1,val2):
  if val1 is not None and val2 is not None:
    df_drop1 = df_scores.loc[df_scores.BARRIO == (val1)][score_labels_inv.keys()].transpose().reset_index()
    df_drop1['BARRIO'] = val1
    df_drop1.columns = ["label","valor", 'Barrio']
    df_drop2 = df_scores.loc[df_scores.BARRIO == (val2)][score_labels_inv.keys()].transpose().reset_index()
    df_drop2['BARRIO'] = val2
    df_drop2.columns = ["label","valor", 'Barrio']
    
    df_drop = pd.concat([
        df_drop1,
        df_drop2
    ], axis=0).reset_index()
    
    df_drop["label"] = [score_labels_inv.get(i) for i in df_drop["label"]]
    fig = px.line_polar(df_drop,r=df_drop.valor, theta=df_drop.label, color=df_drop.Barrio, width=500,line_close=True, color_discrete_sequence=['#7AC45C', '#C40186'])
  else:
    fig={}
  return fig



@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/page-1':
        return page_1
    elif pathname == '/page-2':
        return page_2
    elif pathname == '/page-3':
        return page_3
    elif pathname == '/page-4':
        return page_4
    else:
        return page_1

if __name__ == '__main__':
    app.run_server(debug=True)
