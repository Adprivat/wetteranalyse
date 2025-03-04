import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class WeatherVisualizer:
    """Klasse zur Visualisierung von Wetterdaten für Kassel"""
    
    def __init__(self):
        # Farbpalette für die Visualisierungen
        self.colors = {
            'temp': '#FF9500',
            'prcp': '#1E88E5',
            'wind': '#76FF03',
            'sun': '#FFEB3B',
            'winter': '#00BCD4',
            'spring': '#8BC34A',
            'summer': '#FF5722',
            'autumn': '#795548'
        }
        
        # Spracheinstellungen für Plots
        plt.rcParams['axes.formatter.use_locale'] = True
        self.season_colors = {
            'Winter': self.colors['winter'],
            'Frühling': self.colors['spring'],
            'Sommer': self.colors['summer'],
            'Herbst': self.colors['autumn']
        }
        
    def plot_temperature_trend(self, data, title="Temperaturverlauf Kassel", save_path=None):
        """
        Erzeugt ein Liniendiagramm mit dem Temperaturverlauf
        
        Args:
            data: DataFrame mit Wetterdaten und DateTimeIndex
            title: Titel des Diagramms
            save_path: Wenn angegeben, wird das Diagramm als Datei gespeichert
            
        Returns:
            Plotly Figure-Objekt
        """
        if not all(col in data.columns for col in ['tavg', 'tmin', 'tmax']):
            raise ValueError("Daten müssen die Spalten 'tavg', 'tmin' und 'tmax' enthalten")
            
        # Jährliche gleitende Mittelwerte berechnen
        rolling_avg = data['tavg'].rolling(window=365, center=True).mean()
        
        fig = go.Figure()
        
        # Bereich zwischen min und max Temperatur
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['tmax'],
            fill=None,
            mode='lines',
            line_color='rgba(255, 149, 0, 0.1)',
            name='Max Temperatur'
        ))
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['tmin'],
            fill='tonexty', # Füllen des Bereichs zwischen dieser Linie und der vorherigen
            mode='lines',
            line_color='rgba(255, 149, 0, 0.1)',
            name='Min Temperatur'
        ))
        
        # Durchschnittstemperatur
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['tavg'],
            mode='lines',
            line=dict(color=self.colors['temp'], width=1),
            name='Durchschnittstemperatur'
        ))
        
        # Gleitender Mittelwert
        fig.add_trace(go.Scatter(
            x=data.index,
            y=rolling_avg,
            mode='lines',
            line=dict(color='red', width=2),
            name='Gleitender Durchschnitt (365 Tage)'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Datum',
            yaxis_title='Temperatur (°C)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        if save_path:
            fig.write_image(save_path)
            
        return fig
    
    def plot_precipitation(self, data, title="Niederschlag Kassel", save_path=None):
        """
        Erzeugt ein Balkendiagramm mit Niederschlagsdaten
        
        Args:
            data: DataFrame mit Wetterdaten und DateTimeIndex
            title: Titel des Diagramms
            save_path: Wenn angegeben, wird das Diagramm als Datei gespeichert
            
        Returns:
            Plotly Figure-Objekt
        """
        if 'prcp' not in data.columns:
            raise ValueError("Daten müssen die Spalte 'prcp' enthalten")
            
        # Monatliche Niederschlagssummen berechnen
        monthly_prcp = data['prcp'].resample('M').sum()
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=monthly_prcp.index,
            y=monthly_prcp.values,
            marker_color=self.colors['prcp'],
            name='Monatlicher Niederschlag'
        ))
        
        # Gleitender Durchschnitt (12 Monate)
        rolling_avg = monthly_prcp.rolling(window=12, center=True).mean()
        
        fig.add_trace(go.Scatter(
            x=rolling_avg.index,
            y=rolling_avg.values,
            mode='lines',
            line=dict(color='red', width=2),
            name='Gleitender Durchschnitt (12 Monate)'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Datum',
            yaxis_title='Niederschlag (mm)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        if save_path:
            fig.write_image(save_path)
            
        return fig
    
    def plot_seasonal_comparison(self, seasonal_data, variable='tavg', title=None, save_path=None):
        """
        Erzeugt eine Boxplot zur Visualisierung der saisonalen Verteilung einer Variable
        
        Args:
            seasonal_data: Dictionary mit DataFrames für jede Jahreszeit
            variable: Zu visualisierende Variable ('tavg', 'prcp', 'wspd', etc.)
            title: Titel des Diagramms
            save_path: Wenn angegeben, wird das Diagramm als Datei gespeichert
            
        Returns:
            Plotly Figure-Objekt
        """
        var_titles = {
            'tavg': 'Durchschnittstemperatur',
            'tmax': 'Maximale Temperatur',
            'tmin': 'Minimale Temperatur',
            'prcp': 'Niederschlag',
            'wspd': 'Windgeschwindigkeit'
        }
        
        var_units = {
            'tavg': '°C',
            'tmax': '°C',
            'tmin': '°C',
            'prcp': 'mm',
            'wspd': 'km/h'
        }
        
        if title is None:
            title = f"Saisonale Verteilung: {var_titles.get(variable, variable)} in Kassel"
            
        # Daten für den Plot vorbereiten
        plot_data = []
        for season, data in seasonal_data.items():
            if variable in data.columns:
                values = data[variable].dropna()
                for val in values:
                    plot_data.append({
                        'Jahreszeit': season,
                        'Wert': val
                    })
        
        plot_df = pd.DataFrame(plot_data)
        
        # Sortierung der Jahreszeiten in meteorologischer Reihenfolge
        season_order = ['Frühling', 'Sommer', 'Herbst', 'Winter']
        plot_df['Jahreszeit'] = pd.Categorical(plot_df['Jahreszeit'], categories=season_order, ordered=True)
        
        fig = px.box(
            plot_df, 
            x='Jahreszeit', 
            y='Wert',
            color='Jahreszeit',
            color_discrete_map=self.season_colors,
            title=title,
            labels={'Wert': f"{var_titles.get(variable, variable)} ({var_units.get(variable, '')})"}
        )
        
        # Statistische Tests und Anmerkungen hinzufügen
        seasonal_means = {season: data[variable].mean() for season, data in seasonal_data.items() 
                         if variable in data.columns}
        
        annotations = []
        y_pos = max(plot_df['Wert']) * 1.1
        
        for season, mean in seasonal_means.items():
            annotations.append(
                dict(
                    x=season,
                    y=y_pos,
                    text=f"Ø {mean:.1f}",
                    showarrow=False,
                    font=dict(size=10)
                )
            )
        
        fig.update_layout(annotations=annotations)
        
        if save_path:
            fig.write_image(save_path)
            
        return fig
    
    def plot_yearly_trend(self, data, variable='tavg', title=None, save_path=None):
        """
        Erzeugt ein Liniendiagramm mit einem jährlichen Trend einer Variablen
        
        Args:
            data: DataFrame mit Wetterdaten und DateTimeIndex
            variable: Zu visualisierende Variable ('tavg', 'prcp', 'wspd', etc.)
            title: Titel des Diagramms
            save_path: Wenn angegeben, wird das Diagramm als Datei gespeichert
            
        Returns:
            Plotly Figure-Objekt
        """
        var_titles = {
            'tavg': 'Durchschnittstemperatur',
            'tmax': 'Maximale Temperatur',
            'tmin': 'Minimale Temperatur',
            'prcp': 'Niederschlag',
            'wspd': 'Windgeschwindigkeit'
        }
        
        var_units = {
            'tavg': '°C',
            'tmax': '°C',
            'tmin': '°C',
            'prcp': 'mm',
            'wspd': 'km/h'
        }
        
        if title is None:
            title = f"Jährlicher Trend: {var_titles.get(variable, variable)} in Kassel"
            
        # Jährliche Mittelwerte berechnen
        yearly_data = data[variable].groupby(data.index.year).mean()
        
        fig = go.Figure()
        
        # Jährlicher Mittelwert
        fig.add_trace(go.Scatter(
            x=yearly_data.index,
            y=yearly_data.values,
            mode='lines+markers',
            name='Jährlicher Mittelwert',
            line=dict(color=self.colors['temp'])
        ))
        
        # Lineare Trendlinie
        z = np.polyfit(range(len(yearly_data)), yearly_data.values, 1)
        p = np.poly1d(z)
        
        fig.add_trace(go.Scatter(
            x=yearly_data.index,
            y=p(range(len(yearly_data))),
            mode='lines',
            name='Trend',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Jahr',
            yaxis_title=f"{var_titles.get(variable, variable)} ({var_units.get(variable, '')})",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Angabe der Trendsteigung
        slope = z[0]
        annotations = [dict(
            x=yearly_data.index[-1],
            y=p(len(yearly_data) - 1),
            text=f"Trend: {slope:.3f} pro Jahr",
            showarrow=True,
            arrowhead=1,
            ax=50,
            ay=-30
        )]
        
        fig.update_layout(annotations=annotations)
        
        if save_path:
            fig.write_image(save_path)
            
        return fig
    
    def plot_weather_dashboard(self, daily_data, monthly_data, title="Wetterdashboard Kassel", save_path=None):
        """
        Erzeugt ein Dashboard mit mehreren Wettergrafiken
        
        Args:
            daily_data: DataFrame mit täglichen Wetterdaten
            monthly_data: DataFrame mit monatlichen Wetterdaten
            title: Titel des Dashboards
            save_path: Wenn angegeben, wird das Diagramm als Datei gespeichert
            
        Returns:
            Plotly Figure-Objekt
        """
        # Dashboard mit 2x2 Unterplots erstellen
        fig = make_subplots(
            rows=2, 
            cols=2,
            subplot_titles=(
                "Temperaturverlauf", 
                "Niederschlag", 
                "Temperatur nach Jahreszeit",
                "Jährlicher Temperaturtrend"
            ),
            specs=[
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "box"}, {"type": "scatter"}]
            ]
        )
        
        # 1. Temperaturverlauf (oben links)
        rolling_avg = daily_data['tavg'].rolling(window=365, center=True).mean()
        
        fig.add_trace(
            go.Scatter(
                x=daily_data.index,
                y=daily_data['tavg'],
                mode='lines',
                line=dict(color=self.colors['temp'], width=1),
                name='Durchschnittstemperatur'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=daily_data.index,
                y=rolling_avg,
                mode='lines',
                line=dict(color='red', width=2),
                name='Gleitender Durchschnitt (365 Tage)'
            ),
            row=1, col=1
        )
        
        # 2. Niederschlag (oben rechts)
        monthly_prcp = monthly_data['prcp'].resample('M').sum() if 'prcp' in monthly_data.columns else pd.Series()
        
        if not monthly_prcp.empty:
            fig.add_trace(
                go.Bar(
                    x=monthly_prcp.index,
                    y=monthly_prcp.values,
                    marker_color=self.colors['prcp'],
                    name='Monatlicher Niederschlag'
                ),
                row=1, col=2
            )
            
            # Gleitender Durchschnitt (12 Monate)
            rolling_prcp = monthly_prcp.rolling(window=12, center=True).mean()
            
            fig.add_trace(
                go.Scatter(
                    x=rolling_prcp.index,
                    y=rolling_prcp.values,
                    mode='lines',
                    line=dict(color='red', width=2),
                    name='Gleitender Durchschnitt (12 Monate)'
                ),
                row=1, col=2
            )
        
        # 3. Temperatur nach Jahreszeit (unten links)
        from data_handler import KasselWeatherData
        handler = KasselWeatherData()
        seasonal_data = handler.get_seasonal_data(daily_data)
        
        # Daten für den Plot vorbereiten
        seasons = ['Frühling', 'Sommer', 'Herbst', 'Winter']
        season_data = []
        
        for season in seasons:
            if season in seasonal_data and 'tavg' in seasonal_data[season].columns:
                values = seasonal_data[season]['tavg'].dropna().values
                season_data.append(go.Box(
                    y=values,
                    name=season,
                    marker_color=self.season_colors[season]
                ))
        
        for box in season_data:
            fig.add_trace(box, row=2, col=1)
        
        # 4. Jährlicher Temperaturtrend (unten rechts)
        yearly_data = daily_data['tavg'].groupby(daily_data.index.year).mean()
        
        fig.add_trace(
            go.Scatter(
                x=yearly_data.index,
                y=yearly_data.values,
                mode='lines+markers',
                name='Jährliche Durchschnittstemperatur',
                line=dict(color=self.colors['temp'])
            ),
            row=2, col=2
        )
        
        # Lineare Trendlinie
        z = np.polyfit(range(len(yearly_data)), yearly_data.values, 1)
        p = np.poly1d(z)
        
        fig.add_trace(
            go.Scatter(
                x=yearly_data.index,
                y=p(range(len(yearly_data))),
                mode='lines',
                name='Trend',
                line=dict(color='red', dash='dash')
            ),
            row=2, col=2
        )
        
        # Layout anpassen
        fig.update_layout(
            height=800,
            width=1200,
            title_text=title,
            showlegend=False
        )
        
        # Y-Achsen beschriften
        fig.update_yaxes(title_text="Temperatur (°C)", row=1, col=1)
        fig.update_yaxes(title_text="Niederschlag (mm)", row=1, col=2)
        fig.update_yaxes(title_text="Temperatur (°C)", row=2, col=1)
        fig.update_yaxes(title_text="Temperatur (°C)", row=2, col=2)
        
        # X-Achsen beschriften
        fig.update_xaxes(title_text="Datum", row=1, col=1)
        fig.update_xaxes(title_text="Datum", row=1, col=2)
        fig.update_xaxes(title_text="Jahreszeit", row=2, col=1)
        fig.update_xaxes(title_text="Jahr", row=2, col=2)
        
        if save_path:
            fig.write_image(save_path)
            
        return fig 