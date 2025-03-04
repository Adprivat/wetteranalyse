import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from meteostat import Point, Daily, Monthly, Stations

class KasselWeatherData:
    """Klasse zur Verarbeitung und Analyse von Wetterdaten für Kassel"""
    
    def __init__(self):
        # Koordinaten für Kassel
        self.kassel_coords = Point(51.3127, 9.4797)  # Breitengrad, Längengrad für Kassel-Mitte
        
        # Wetterstationen werden später bei Bedarf geladen
        self.stations_df = None
        
        # Standard-Zeitraum für Daten (letzte 10 Jahre)
        self.end_date = datetime.now()
        self.start_date = datetime(self.end_date.year - 10, 1, 1)
        
    def get_station_info(self):
        """Gibt Informationen über verfügbare Wetterstationen in der Nähe von Kassel zurück"""
        # Lade die Stationen nur wenn nötig
        if self.stations_df is None:
            try:
                # Wetterstationen in der Nähe von Kassel finden
                stations = Stations()
                stations = stations.nearby(51.3127, 9.4797)
                self.stations_df = stations.fetch()
                
                # Entfernung zur Station in km berechnen
                if not self.stations_df.empty:
                    # Berechne Entfernung für jede Station (vereinfachte Formel)
                    for idx, row in self.stations_df.iterrows():
                        lat1, lon1 = self.kassel_coords.lat, self.kassel_coords.lon
                        lat2, lon2 = row['latitude'], row['longitude']
                        
                        # Einfache Entfernungsberechnung (Luftlinie in km)
                        dlat = lat2 - lat1
                        dlon = lon2 - lon1
                        # Umrechnung in Bogenmaß
                        a = np.sin(np.radians(dlat)/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(np.radians(dlon)/2)**2
                        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
                        distance = 6371 * c  # Erdradius in km
                        
                        self.stations_df.at[idx, 'distance'] = distance
                    
                    # Nach Entfernung sortieren
                    self.stations_df = self.stations_df.sort_values('distance')
                
                print(f"Gefundene Wetterstationen: {len(self.stations_df)}")
            except Exception as e:
                print(f"Fehler beim Laden der Wetterstationen: {e}")
                # Erstelle eine leere DataFrame mit den richtigen Spalten
                self.stations_df = pd.DataFrame(columns=['id', 'name', 'latitude', 'longitude', 'elevation', 'distance'])
        
        return self.stations_df
    
    def get_daily_data(self, start_date=None, end_date=None, station_id=None):
        """
        Lädt tägliche Wetterdaten für Kassel herunter
        
        Args:
            start_date: Startdatum (default: 10 Jahre zurück)
            end_date: Enddatum (default: heute)
            station_id: ID der Wetterstation (default: nächste Station zu Kassel)
            
        Returns:
            DataFrame mit täglichen Wetterdaten
        """
        if start_date is None:
            start_date = self.start_date
        if end_date is None:
            end_date = self.end_date
            
        # Wenn keine spezifische Station angegeben ist, verwende den Punkt für Kassel
        try:
            if station_id is None:
                data = Daily(self.kassel_coords, start_date, end_date)
            else:
                try:
                    # Versuche, eine Station anhand der ID zu finden
                    station = Stations().id(station_id).fetch(1)
                    if station.empty:
                        # Fallback auf Kassel-Koordinaten, wenn Station nicht gefunden wurde
                        print(f"Station ID {station_id} nicht gefunden. Verwende Kassel-Koordinaten.")
                        data = Daily(self.kassel_coords, start_date, end_date)
                    else:
                        # Station gefunden, verwende deren Koordinaten
                        station_point = Point(station.iloc[0]['latitude'], station.iloc[0]['longitude'])
                        data = Daily(station_point, start_date, end_date)
                except Exception as e:
                    # Bei einem Fehler verwende die Kassel-Koordinaten
                    print(f"Fehler beim Laden der Station {station_id}: {e}. Verwende Kassel-Koordinaten.")
                    data = Daily(self.kassel_coords, start_date, end_date)
                
            # Daten abrufen und in DataFrame umwandeln
            data = data.fetch()
            return data
        except Exception as e:
            print(f"Fehler beim Laden der täglichen Daten: {e}")
            # Rückgabe eines leeren DataFrames mit den erwarteten Spalten
            return pd.DataFrame(columns=['tavg', 'tmin', 'tmax', 'prcp', 'wspd', 'wpgt', 'pres', 'tsun'])
    
    def get_monthly_data(self, start_date=None, end_date=None, station_id=None):
        """
        Lädt monatliche Wetterdaten für Kassel herunter
        
        Args:
            start_date: Startdatum (default: 10 Jahre zurück)
            end_date: Enddatum (default: heute)
            station_id: ID der Wetterstation (default: nächste Station zu Kassel)
            
        Returns:
            DataFrame mit monatlichen Wetterdaten
        """
        if start_date is None:
            start_date = self.start_date
        if end_date is None:
            end_date = self.end_date
            
        try:
            # Wenn keine spezifische Station angegeben ist, verwende den Punkt für Kassel
            if station_id is None:
                data = Monthly(self.kassel_coords, start_date, end_date)
            else:
                try:
                    # Versuche, eine Station anhand der ID zu finden
                    station = Stations().id(station_id).fetch(1)
                    if station.empty:
                        # Fallback auf Kassel-Koordinaten, wenn Station nicht gefunden wurde
                        print(f"Station ID {station_id} nicht gefunden. Verwende Kassel-Koordinaten.")
                        data = Monthly(self.kassel_coords, start_date, end_date)
                    else:
                        # Station gefunden, verwende deren Koordinaten
                        station_point = Point(station.iloc[0]['latitude'], station.iloc[0]['longitude'])
                        data = Monthly(station_point, start_date, end_date)
                except Exception as e:
                    # Bei einem Fehler verwende die Kassel-Koordinaten
                    print(f"Fehler beim Laden der Station {station_id}: {e}. Verwende Kassel-Koordinaten.")
                    data = Monthly(self.kassel_coords, start_date, end_date)
                
            # Daten abrufen und in DataFrame umwandeln
            data = data.fetch()
            return data
        except Exception as e:
            print(f"Fehler beim Laden der monatlichen Daten: {e}")
            # Rückgabe eines leeren DataFrames mit den erwarteten Spalten
            return pd.DataFrame(columns=['tavg', 'tmin', 'tmax', 'prcp', 'wspd', 'wpgt', 'pres', 'tsun'])
    
    def calculate_statistics(self, data):
        """
        Berechnet statistische Auswertungen für die Wetterdaten
        
        Args:
            data: DataFrame mit Wetterdaten
            
        Returns:
            Dictionary mit statistischen Auswertungen
        """
        stats = {}
        
        # Temperaturstatistiken
        if 'tavg' in data.columns:
            stats['temp_mean'] = data['tavg'].mean()
            stats['temp_max'] = data['tmax'].max()
            stats['temp_min'] = data['tmin'].min()
            stats['temp_std'] = data['tavg'].std()
            
            # Extremwerte mit Datum
            max_temp_idx = data['tmax'].idxmax()
            min_temp_idx = data['tmin'].idxmin()
            stats['hottest_day'] = {'date': max_temp_idx, 'temp': data.loc[max_temp_idx, 'tmax']}
            stats['coldest_day'] = {'date': min_temp_idx, 'temp': data.loc[min_temp_idx, 'tmin']}
        
        # Niederschlagsstatistiken
        if 'prcp' in data.columns:
            stats['prcp_total'] = data['prcp'].sum()
            stats['prcp_mean'] = data['prcp'].mean()
            stats['prcp_max'] = data['prcp'].max()
            stats['rainy_days'] = (data['prcp'] > 0).sum()
            
            # Tag mit höchstem Niederschlag
            max_prcp_idx = data['prcp'].idxmax()
            stats['rainiest_day'] = {'date': max_prcp_idx, 'prcp': data.loc[max_prcp_idx, 'prcp']}
        
        # Windstatistiken
        if 'wspd' in data.columns:
            stats['wind_mean'] = data['wspd'].mean()
            stats['wind_max'] = data['wspd'].max()
            
            # Tag mit höchstem Wind
            max_wind_idx = data['wspd'].idxmax()
            stats['windiest_day'] = {'date': max_wind_idx, 'wind': data.loc[max_wind_idx, 'wspd']}
        
        # Sonnenscheindauer
        if 'tsun' in data.columns:
            stats['sunshine_total'] = data['tsun'].sum()
            stats['sunshine_mean'] = data['tsun'].mean()
            
        return stats
    
    def get_seasonal_data(self, data):
        """
        Gruppiert Daten nach Jahreszeiten
        
        Args:
            data: DataFrame mit Wetterdaten und DateTimeIndex
            
        Returns:
            Dictionary mit saisonalen Daten
        """
        # Jahreszeiten definieren (meteorologisch)
        seasons = {
            'Frühling': [3, 4, 5],
            'Sommer': [6, 7, 8],
            'Herbst': [9, 10, 11],
            'Winter': [12, 1, 2]
        }
        
        seasonal_data = {}
        
        for season, months in seasons.items():
            # Filter für die Monate der Jahreszeit
            season_data = data[data.index.month.isin(months)]
            seasonal_data[season] = season_data
            
        return seasonal_data
    
    def get_yearly_averages(self, data, column='tavg'):
        """
        Berechnet jährliche Durchschnittswerte für eine bestimmte Spalte
        
        Args:
            data: DataFrame mit Wetterdaten und DateTimeIndex
            column: Spalte, für die Durchschnittswerte berechnet werden sollen
            
        Returns:
            DataFrame mit jährlichen Durchschnittswerten
        """
        if column not in data.columns:
            return pd.DataFrame()
            
        # Gruppiere nach Jahr und berechne Durchschnitt
        yearly_avg = data[column].groupby(data.index.year).mean()
        return yearly_avg.to_frame(name=column) 