import dash
from dash import dcc, html, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# Eigene Module importieren
from data_handler import KasselWeatherData
from visualizations import WeatherVisualizer

# Standardmäßige Zeiträume für die Analyse
DEFAULT_START_YEAR = 2000
DEFAULT_END_YEAR = datetime.now().year

# Initialisiere Datenhandler und Visualisierer
data_handler = KasselWeatherData()
visualizer = WeatherVisualizer()

# Ordner für das Speichern von Grafiken erstellen
EXPORT_FOLDER = 'exports'
os.makedirs(EXPORT_FOLDER, exist_ok=True)

# Dash-App initialisieren
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Wetteranalyse Kassel"
server = app.server

# Layout der App definieren
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Wetteranalyse Kassel und Landkreis", className="text-center my-4"),
            html.P("Historische Datenanalyse und Visualisierung des Wetters in der Region Kassel", 
                   className="text-center lead mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Datenauswahl"),
                dbc.CardBody([
                    html.P("Wählen Sie den Zeitraum für die Analyse:"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Von Jahr:"),
                            dcc.Dropdown(
                                id="start-year-dropdown",
                                options=[{"label": str(year), "value": year} for year in range(1980, datetime.now().year + 1)],
                                value=DEFAULT_START_YEAR,
                                clearable=False
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Bis Jahr:"),
                            dcc.Dropdown(
                                id="end-year-dropdown",
                                options=[{"label": str(year), "value": year} for year in range(1980, datetime.now().year + 1)],
                                value=DEFAULT_END_YEAR,
                                clearable=False
                            )
                        ], width=6)
                    ]),
                    html.Div(className="mt-3"),
                    html.P("Wählen Sie eine Wetterstation in der Nähe von Kassel:"),
                    dcc.Loading(
                        id="loading-stations",
                        type="default",
                        children=[
                            dcc.Dropdown(
                                id="station-dropdown",
                                placeholder="Wetterstation wird geladen...",
                                value=None
                            )
                        ]
                    ),
                    html.Div(className="mt-3"),
                    dbc.Button("Daten laden", id="load-data-button", color="primary", className="w-100 mt-2")
                ])
            ]),
            
            dbc.Card([
                dbc.CardHeader("Statistiken"),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-stats",
                        type="default",
                        children=[
                            html.Div(id="statistics-container")
                        ]
                    )
                ])
            ], className="mt-3"),
            
            dbc.Card([
                dbc.CardHeader("Datenexport"),
                dbc.CardBody([
                    dbc.Button("Grafiken exportieren", id="export-button", color="success", className="w-100"),
                    html.Div(id="export-status", className="mt-2")
                ])
            ], className="mt-3")
        ], width=3),
        
        dbc.Col([
            dbc.Tabs([
                dbc.Tab([
                    dcc.Loading(
                        id="loading-dashboard",
                        type="default",
                        children=[
                            dcc.Graph(id="dashboard-graph", style={"height": "80vh"})
                        ]
                    )
                ], label="Dashboard"),
                
                dbc.Tab([
                    dcc.Loading(
                        id="loading-temp",
                        type="default",
                        children=[
                            dcc.Graph(id="temperature-graph", style={"height": "80vh"})
                        ]
                    )
                ], label="Temperatur"),
                
                dbc.Tab([
                    dcc.Loading(
                        id="loading-precip",
                        type="default",
                        children=[
                            dcc.Graph(id="precipitation-graph", style={"height": "80vh"})
                        ]
                    )
                ], label="Niederschlag"),
                
                dbc.Tab([
                    dcc.Loading(
                        id="loading-seasons",
                        type="default",
                        children=[
                            dcc.Graph(id="seasonal-graph", style={"height": "80vh"})
                        ]
                    )
                ], label="Jahreszeiten"),
                
                dbc.Tab([
                    dcc.Loading(
                        id="loading-trend",
                        type="default",
                        children=[
                            dcc.Graph(id="trend-graph", style={"height": "80vh"})
                        ]
                    )
                ], label="Trends")
            ])
        ], width=9)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P([
                "Datenquelle: ",
                html.A("Meteostat", href="https://meteostat.net/de/", target="_blank"),
                " | Daten aus offiziellen Wetterstationen des Deutschen Wetterdienstes (DWD) und anderen Quellen"
            ], className="text-center text-muted")
        ], width=12)
    ])
], fluid=True)

# Callback zum Laden der Wetterstationen
@app.callback(
    [Output("station-dropdown", "options"),
     Output("station-dropdown", "placeholder"),
     Output("station-dropdown", "value"),
     Output("load-data-button", "disabled")],
    [Input("start-year-dropdown", "value")]
)
def load_stations(start_year):
    try:
        stations_df = data_handler.get_station_info()
        
        if stations_df.empty:
            # Falls keine Stationen gefunden wurden, verwende eine Standardstation (Kassel Flughafen)
            fallback_stations = [
                {"label": "Kassel-Calden (10438) - Fallback", "value": "10438"},
                {"label": "Fritzlar (10439) - Fallback", "value": "10439"},
                {"label": "Kassel (03164) - Fallback", "value": "03164"}
            ]
            return fallback_stations, "Fallback-Station auswählen (API-Verbindungsproblem)", fallback_stations[0]["value"], False
        
        # Stationen nach Entfernung sortieren und in Dropdown-Optionen umwandeln
        options = [{"label": f"{row['name']} ({row['id']}) - {row['distance']:.1f} km", "value": row['id']} 
                for _, row in stations_df.iterrows()]
        
        if not options:
            # Falls keine Stationen gefunden wurden, verwende eine Standardstation (Kassel Flughafen)
            fallback_stations = [
                {"label": "Kassel-Calden (10438) - Fallback", "value": "10438"},
                {"label": "Fritzlar (10439) - Fallback", "value": "10439"},
                {"label": "Kassel (03164) - Fallback", "value": "03164"}
            ]
            return fallback_stations, "Fallback-Station auswählen (keine Station gefunden)", fallback_stations[0]["value"], False
        
        # Automatisch die nächste Station auswählen (erste Station in der sortierten Liste)
        default_station = options[0]["value"] if options else None
        
        return options, "Wetterstation auswählen", default_station, False
    except Exception as e:
        print(f"Fehler beim Laden der Stationen: {str(e)}")
        # Falls ein Fehler auftritt, verwende eine Standardstation (Kassel Flughafen)
        fallback_stations = [
            {"label": "Kassel-Calden (10438) - Fallback", "value": "10438"},
            {"label": "Fritzlar (10439) - Fallback", "value": "10439"},
            {"label": "Kassel (03164) - Fallback", "value": "03164"}
        ]
        return fallback_stations, f"Fallback-Station auswählen (Fehler: {str(e)})", fallback_stations[0]["value"], False

# Globale Variablen für die Daten, um sie zwischen Callbacks zu teilen
daily_data = None
monthly_data = None

# Callback zum Laden der Daten und Aktualisieren der Diagramme
@app.callback(
    [Output("dashboard-graph", "figure"),
     Output("temperature-graph", "figure"),
     Output("precipitation-graph", "figure"),
     Output("seasonal-graph", "figure"),
     Output("trend-graph", "figure"),
     Output("statistics-container", "children")],
    [Input("load-data-button", "n_clicks")],
    [dash.dependencies.State("start-year-dropdown", "value"),
     dash.dependencies.State("end-year-dropdown", "value"),
     dash.dependencies.State("station-dropdown", "value"),
     dash.dependencies.State("station-dropdown", "options")]
)
def update_data_and_visualizations(n_clicks, start_year, end_year, station_id, station_options):
    global daily_data, monthly_data
    
    if n_clicks is None:
        # Standardmäßige leere Figuren zurückgeben, wenn noch nicht geklickt wurde
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="Keine Daten geladen",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            annotations=[dict(
                text="Bitte klicken Sie auf 'Daten laden', um Wetterdaten anzuzeigen",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5
            )]
        )
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "Keine Daten geladen"
    
    # Prüfen, ob Wetterstationen verfügbar sind
    if not station_options:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="Keine Wetterstationen verfügbar",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            annotations=[dict(
                text="Es wurden keine Wetterstationen für die Region Kassel gefunden. Bitte versuchen Sie es später erneut.",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5
            )]
        )
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "Keine Wetterstationen verfügbar"
    
    # Zeitraum basierend auf den ausgewählten Jahren erstellen
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    
    # Daten laden
    try:
        daily_data = data_handler.get_daily_data(start_date, end_date, station_id)
        monthly_data = data_handler.get_monthly_data(start_date, end_date, station_id)
    except Exception as e:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="Fehler beim Laden der Daten",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            annotations=[dict(
                text=f"Beim Laden der Daten ist ein Fehler aufgetreten: {str(e)}",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5
            )]
        )
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, f"Fehler: {str(e)}"
    
    # Überprüfen, ob Daten erfolgreich geladen wurden
    if daily_data.empty or monthly_data.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="Keine Daten verfügbar",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            annotations=[dict(
                text="Für den ausgewählten Zeitraum und/oder die Wetterstation sind keine Daten verfügbar",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5
            )]
        )
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "Keine Daten verfügbar"
    
    # Saisonale Daten erstellen
    seasonal_data = data_handler.get_seasonal_data(daily_data)
    
    # Statistiken berechnen
    stats = data_handler.calculate_statistics(daily_data)
    
    # Visualisierungen erstellen
    dashboard_fig = visualizer.plot_weather_dashboard(
        daily_data, 
        monthly_data, 
        title=f"Wetterdashboard Kassel ({start_year}-{end_year})"
    )
    
    temp_fig = visualizer.plot_temperature_trend(
        daily_data, 
        title=f"Temperaturverlauf Kassel ({start_year}-{end_year})"
    )
    
    precip_fig = visualizer.plot_precipitation(
        daily_data,
        title=f"Niederschlag Kassel ({start_year}-{end_year})"
    )
    
    seasonal_fig = visualizer.plot_seasonal_comparison(
        seasonal_data,
        variable='tavg',
        title=f"Temperaturverteilung nach Jahreszeiten ({start_year}-{end_year})"
    )
    
    trend_fig = visualizer.plot_yearly_trend(
        daily_data,
        variable='tavg',
        title=f"Jährlicher Temperaturtrend ({start_year}-{end_year})"
    )
    
    # Statistik-Layout erstellen
    stats_layout = html.Div([
        html.H5("Temperaturen:"),
        html.Ul([
            html.Li(f"Durchschnitt: {stats.get('temp_mean', 'N/A'):.1f} °C"),
            html.Li(f"Maximum: {stats.get('temp_max', 'N/A'):.1f} °C ({stats.get('hottest_day', {}).get('date', 'N/A').strftime('%d.%m.%Y') if stats.get('hottest_day', {}).get('date') else 'N/A'})"),
            html.Li(f"Minimum: {stats.get('temp_min', 'N/A'):.1f} °C ({stats.get('coldest_day', {}).get('date', 'N/A').strftime('%d.%m.%Y') if stats.get('coldest_day', {}).get('date') else 'N/A'})"),
        ]),
        
        html.H5("Niederschlag:"),
        html.Ul([
            html.Li(f"Gesamtniederschlag: {stats.get('prcp_total', 'N/A'):.1f} mm"),
            html.Li(f"Regentage: {stats.get('rainy_days', 'N/A')} Tage"),
            html.Li(f"Stärkster Niederschlag: {stats.get('prcp_max', 'N/A'):.1f} mm ({stats.get('rainiest_day', {}).get('date', 'N/A').strftime('%d.%m.%Y') if stats.get('rainiest_day', {}).get('date') else 'N/A'})"),
        ]),
        
        html.H5("Wind:") if 'wind_mean' in stats else html.Div(),
        html.Ul([
            html.Li(f"Durchschnittsgeschwindigkeit: {stats.get('wind_mean', 'N/A'):.1f} km/h"),
            html.Li(f"Maximum: {stats.get('wind_max', 'N/A'):.1f} km/h ({stats.get('windiest_day', {}).get('date', 'N/A').strftime('%d.%m.%Y') if stats.get('windiest_day', {}).get('date') else 'N/A'})"),
        ]) if 'wind_mean' in stats else html.Div(),
        
        html.H5("Sonnenschein:") if 'sunshine_total' in stats else html.Div(),
        html.Ul([
            html.Li(f"Gesamte Sonnenscheindauer: {stats.get('sunshine_total', 'N/A'):.1f} Stunden"),
            html.Li(f"Durchschnitt pro Tag: {stats.get('sunshine_mean', 'N/A'):.1f} Stunden"),
        ]) if 'sunshine_total' in stats else html.Div(),
    ])
    
    return dashboard_fig, temp_fig, precip_fig, seasonal_fig, trend_fig, stats_layout

# Callback zum Exportieren der Grafiken
@app.callback(
    Output("export-status", "children"),
    [Input("export-button", "n_clicks")]
)
def export_graphics(n_clicks):
    global daily_data, monthly_data
    
    if n_clicks is None or daily_data is None or monthly_data is None:
        return html.Div("Keine Daten zum Exportieren verfügbar", className="text-warning")
    
    try:
        # Saisonale Daten erstellen
        seasonal_data = data_handler.get_seasonal_data(daily_data)
        
        # Grafiken als Bilddateien speichern
        dashboard_fig = visualizer.plot_weather_dashboard(
            daily_data, 
            monthly_data, 
            title="Wetterdashboard Kassel"
        )
        dashboard_fig.write_image(f"{EXPORT_FOLDER}/wetterdashboard_kassel.png")
        
        temp_fig = visualizer.plot_temperature_trend(daily_data)
        temp_fig.write_image(f"{EXPORT_FOLDER}/temperaturverlauf_kassel.png")
        
        precip_fig = visualizer.plot_precipitation(daily_data)
        precip_fig.write_image(f"{EXPORT_FOLDER}/niederschlag_kassel.png")
        
        seasonal_fig = visualizer.plot_seasonal_comparison(seasonal_data, variable='tavg')
        seasonal_fig.write_image(f"{EXPORT_FOLDER}/temperatur_nach_jahreszeit_kassel.png")
        
        trend_fig = visualizer.plot_yearly_trend(daily_data, variable='tavg')
        trend_fig.write_image(f"{EXPORT_FOLDER}/temperaturtrend_kassel.png")
        
        # Zusätzliche Grafiken mit anderen Variablen
        if 'prcp' in daily_data.columns:
            prcp_trend_fig = visualizer.plot_yearly_trend(daily_data, variable='prcp', 
                                                       title="Jährlicher Niederschlagstrend Kassel")
            prcp_trend_fig.write_image(f"{EXPORT_FOLDER}/niederschlagstrend_kassel.png")
            
            seasonal_prcp_fig = visualizer.plot_seasonal_comparison(seasonal_data, variable='prcp',
                                                                  title="Niederschlagsverteilung nach Jahreszeiten")
            seasonal_prcp_fig.write_image(f"{EXPORT_FOLDER}/niederschlag_nach_jahreszeit_kassel.png")
        
        return html.Div([
            html.P("Grafiken erfolgreich exportiert in den Ordner 'exports'", className="text-success"),
            html.Ul([
                html.Li("wetterdashboard_kassel.png"),
                html.Li("temperaturverlauf_kassel.png"),
                html.Li("niederschlag_kassel.png"),
                html.Li("temperatur_nach_jahreszeit_kassel.png"),
                html.Li("temperaturtrend_kassel.png"),
                html.Li("niederschlagstrend_kassel.png") if 'prcp' in daily_data.columns else None,
                html.Li("niederschlag_nach_jahreszeit_kassel.png") if 'prcp' in daily_data.columns else None,
            ])
        ])
        
    except Exception as e:
        return html.Div(f"Fehler beim Exportieren: {str(e)}", className="text-danger")

# Server starten
if __name__ == '__main__':
    app.run_server(debug=False) 