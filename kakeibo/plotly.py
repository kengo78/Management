import plotly.graph_objects as go

class GraphGenerator:
    def month_pie(self, labels, values):
        fig = go.Figure()#インスタンス作成
        fig.add_trace(go.Pie(labels=labels,
                             values=values))
        return fig.to_html(include_plotlyjs = False)
    
    def month_daily_bar(self, x_list, y_list):
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=x_list,
            y=y_list,
        ))
        return fig.to_html(include_plotlyjs=False)