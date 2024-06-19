from dash import Dash, dcc, Output, Input, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

filepath = "../Datasets/hasil_output.csv"

raw_df = pd.read_csv(filepath, parse_dates=["acq_date"])
main_df = raw_df.dropna(subset=["regency_city", "province"])

# Build Components

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
mytitle = html.H2("Pemantauan Titik Api di Indonesia")
description = """Dashboard ini menampilkan titik api yang diamati oleh Visible Infrared Imaging Radiometer Suite (VIIRS) pada tahun 2021,
            VIIRS memiliki nilai confidence yang diatur ke rendah, nominal, dan tinggi; nilai tersebut didasarkan pada kumpulan kuantitas algoritma menengah
            yang digunakan dalam proses deteksi dan dimaksudkan untuk membantu pengguna mengukur kualitas piksel titik panas/api.
            VIIRS mendeteksi titik panas dengan resolusi 375 meter per piksel, yang berarti dapat mendeteksi kebakaran yang lebih kecil
            dan berintensitas rendah dibandingkan satelit pengamatan lainnya. Dalam skala global, VIIRS mendeteksi setiap 3 jam."""

dropdown = dcc.Dropdown(options=[{"label": str(year), "value": year} for year in main_df["year"].unique()],
                        value=2021,  # initial value
                        clearable=False)

app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                mytitle,
                html.Label("Pilih Tahun"),
                dropdown,
                html.Hr(),
                html.P(description, style={'text-align': 'justify'}),
            ], width=2),
            dbc.Col([
                dbc.Row([
                    dbc.Col(dcc.Graph(figure={}, id="barfig1"), width=10, style={"height": "40%"})
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(figure={}, id="barfig2"), width=10, style={"height": "40%"})
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(figure={}, id="mapfig"), width=10, style={"height": "50%"})
                ]), 
                dbc.Row([
                    dbc.Col(dcc.Graph(figure={}, id="linefig"), width=10, style={"height": "30%"}),
                    dbc.Col(dcc.Graph(figure={}, id="piefig"), width=4, style={"height": "30%"}) 
                ],  style={'display': 'flex', 'flex-direction': 'row'}),
            ], width=3)
        ])
    ], 
    fluid=True)

# Callback (placeholder)
@app.callback(
    Output("barfig1", "figure"),
    Output("barfig2", "figure"),
    Output("mapfig", "figure"),
    Output("linefig", "figure"),
    Output("piefig", "figure"),
    Input(dropdown, "value")
)
def update_dashboard(selected_year):
    dff = main_df[main_df["year"] == selected_year]

    def create_placeholder_figures():
        barfig1 = create_top10_city(dff)
        barfig2 = create_top10_province(dff)
        mapfig = create_density_map(dff)
        linefig = create_line_chart(dff)
        piefig = create_pie_confidence(dff)
            
        return barfig1, barfig2, mapfig, linefig, piefig

    def create_density_map(dataframe):
        # Define hover data
        hover_data = {
            'acq_date': True, 'frp': True, 'province': True,
            'longitude': False, 'latitude': False
        }

        # create density map figure
        fig = px.density_mapbox(
            dataframe, lat='latitude', lon='longitude',
            z='frp', radius=5, center=dict(lat=-2, lon=118),
            zoom=3.8, hover_name='regency_city',
            hover_data=hover_data, color_continuous_scale='matter_r',
            mapbox_style='carto-darkmatter', template='plotly_dark'
        )

        # update figure layout
        fig.update_layout(
            width=1000, height=475,
            margin=dict(r=1, t=1, l=1, b=1), plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)'
        )

        # update colorbar location and orientation
        fig.update_coloraxes(
            showscale=True,
            colorbar=dict(
                len=0.3, yanchor='bottom', y=0,
                xanchor='center',
                thickness=10, title='Fire Radiative Power',
                orientation='h', title_side="top")
        )

        return fig

    def create_top10_city(dataframe):
            grouped = dataframe.groupby(["regency_city"]).agg(
            total_fires = ("frp", "count")
        )
            
            grouped = grouped.sort_values(by="total_fires", ascending=False). reset_index()
            grouped = grouped.head(10)
            
            fig = px.bar(grouped, x="total_fires", y="regency_city", orientation='h', text="total_fires",
                        labels={"regency_city":"", "total_fires":"Jumlah Titik Api"}, template="plotly_dark")
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            
            fig.update_layout(autosize=True, width=550,height=475)
            fig.update_layout(title="10 Kabupaten/Kota Dengan Titik Api Terbanyak",title_font_size=14)
            
            # Mengatur format angka pada sumbu x
            fig.update_xaxes(tickformat=',d')

            # Mengatur ukuran font untuk sumbu x dan y
            fig.update_xaxes(title_font=dict(size=12), tickfont=dict(size=12))
            fig.update_yaxes(tickfont=dict(size=12))

            # Mengatur tampilan teks pada batang
            fig.update_traces(marker_color='indianred', textposition='inside', textfont_size=11)
        
            fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)',})
            fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
            
            return fig

    def create_top10_province(dataframe):
            grouped = dataframe.groupby(["province"]).agg(
            total_fires=("frp", "count")
        )

            grouped = grouped.sort_values(by="total_fires", ascending=False).reset_index()
            grouped = grouped.head(10)

            fig = px.bar(grouped, x="total_fires", y="province", orientation="h", text="total_fires",
                        labels={"province": "", "total_fires": "Jumlah Titik Api"}, template="plotly_dark")

            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            fig.update_layout(autosize=True, width=550, height=400)
            fig.update_layout(title="10 Provinsi Dengan Titik Api Terbanyak", title_font_size=14)

            # Mengatur format angka pada sumbu x
            fig.update_xaxes(tickformat=',d')

            # Mengatur ukuran font untuk sumbu x dan y
            fig.update_xaxes(title_font=dict(size=12), tickfont=dict(size=12))
            fig.update_yaxes(tickfont=dict(size=12))

            # Mengatur tampilan teks pada batang
            fig.update_traces(marker_color='indianred', textposition='inside', textfont_size=11)

            # Mengatur latar belakang
            fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
            fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)

            return fig

    def create_line_chart(dff):
            line_df = dff
            
            # Upsample to daily frequency and count the number of fires in each day
            line_df = line_df.resample('D', on='acq_date')['frp'].count()
            
            fig = px.line(line_df, x=line_df.index, y=line_df.values,
                        labels={"y":"<b>Jumlah Titik Api</b>", "acq_date":""}, template="plotly_dark")
            
            fig.update_layout(autosize=True,width=700,height=400)
            # fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
            fig.update_layout(title="Jumlah Titik Api Harian yang Terdeteksi", title_font_size=16)
            fig.update_traces(line_color='indianred')
            fig.update_layout({'plot_bgcolor':'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)',})
            fig.update_yaxes(title_font=dict(size=12))
            fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
            
            return fig

    def create_pie_confidence(dff):
            # groupby confidence
            percentage_df = dff.groupby(["confidence"])["frp"].agg("count")
            percentage_df = percentage_df.reset_index()
            percentage_df = percentage_df.rename(columns={"frp": "counts"})
            percentage_df["percent"] = round((percentage_df["counts"] / percentage_df["counts"].sum()) * 100, 2)

            # sort by confidence level
            percentage_df = percentage_df.sort_values(by=['confidence'])

            # build pie chart
            fig = px.pie(percentage_df, values='percent', names='confidence', 
                        color_discrete_sequence=['indianred'], 
                        template="plotly_dark", 
                        title="Proporsi Tingkat Confidence Api", 
                        labels={'confidence': 'Tingkat Confidence', 'percent': 'Persentase'})

            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
            fig.update_layout(autosize=True, width=450, height=400)
            fig.update_layout(title_font_size=14)

            return fig



    barfig1, barfig2, mapfig, linefig, piefig = create_placeholder_figures()
    return barfig1, barfig2, mapfig, linefig, piefig

# ------ Run App -------
if __name__ == '__main__':
    app.run_server(debug=True, port=1651)