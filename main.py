from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import airportsdata
import calendar
from meteostat import Point, Daily
import argparse

# kept this stuff outside incase I want to call it from anywhere else... doubtful, but who can predict the future
date_format = "%Y-%m-%d"
right_now = datetime.utcnow()
today = datetime.strftime(right_now, date_format)

parser = argparse.ArgumentParser()
parser.add_argument("-t0", type=str, default="2000-1-1")
parser.add_argument("-t1", type=str, default=today)
parser.add_argument('--airport', type=str, default='PAMR')


if __name__ == "__main__":
    args = parser.parse_args()

    # Set time period
    start = datetime.strptime(args.t0, date_format)
    end = datetime.strptime(args.t1, date_format)

    # get latlon data for the airport
    airport = airportsdata.load()[args.airport]

    # get the lat and lon of the airport
    point = Point(airport['lat'], airport['lon'])

    data = Daily(point, start, end)
    data = data.fetch()

    data['year'] = pd.to_datetime(data.index).year
    data['month'] = pd.to_datetime(data.index).month
    data['date'] = pd.to_datetime(data.index)
    data['day'] = pd.to_datetime(data.index).dayofyear
    rain = data.groupby(['year']).cumsum()['prcp']
    data['rain_yearly_cumulative'] = rain
    data.to_csv('output/cumsumdata.csv')
    dfs = []
    for i, year in data.groupby(['year']):
        dfs.append(year)

    fig = go.Figure()

    for df in dfs:
        title = f"{df.iloc[0].year} rainfall (mm)"
        water_plot = go.Scatter(x=df['day'],
                                y=df['rain_yearly_cumulative'].values,
                                text=df['prcp'],
                                name=title)

        fig.add_trace(water_plot)



    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=[1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335],
            ticktext=[month for month in list(calendar.month_name)[1:]]
        ),
        title=f"Cumulative Rainfall for {airport['name']}"
    )
    fig.update_yaxes(title="cumulative rainfall (mm)")

    with open(f"output/{args.airport}.html", "w") as html_file:
        fig.write_html(html_file, full_html=True)
