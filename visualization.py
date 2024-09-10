# visualization.py
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd

# Basit matplotlib görselleştirme fonksiyonu
def plot_trends(data, keyword):
    plt.figure(figsize=(10,6))
    plt.plot(data.index, data[keyword], label=f"Trend for {keyword}", color='b')
    plt.title(f"Google Trends - {keyword}")
    plt.xlabel("Date")
    plt.ylabel("Interest over Time")
    plt.grid(True)
    plt.legend()
    plt.show()

# Plotly ile interaktif grafik
def plot_interactive_trends(data, keyword):
    fig = px.line(data, x=data.index, y=keyword, title=f"Google Trends - {keyword} (Interactive)")
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Interest over Time')
    fig.show()

# Flask ile json olarak dönecek plotly grafiği
def get_plotly_graph_json(data, keyword):
    fig = px.line(data, x=data.index, y=keyword, title=f"Google Trends - {keyword} (Interactive)")
    return fig.to_json()  # JSON formatında döndür
