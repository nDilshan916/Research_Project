import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import requests

BACKEND_URL = "http://localhost:5001/job_dashboard_data"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # for deployment

def fetch_dashboard_data(job_title):
    """Fetch dashboard data from Flask backend."""
    try:
        url = f"{BACKEND_URL}/{job_title}"
        r = requests.get(url)
        if r.ok:
            return r.json()
        return None
    except Exception as e:
        return None

app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),  # Add this
    html.H1("Job Dashboard", className="mt-4 mb-4"),
    html.Div(id="dashboard-content", children=[], className="mt-4"),
])

@app.callback(
    Output("dashboard-content", "children"),
    [Input("url", "search")]
)
def update_dashboard(search):
    import urllib.parse
    params = urllib.parse.parse_qs(search[1:] if search else "")
    job_title = params.get("jobTitle", [""])[0]
    if not job_title:
        return dbc.Alert("No job title specified.", color="warning")
    data = fetch_dashboard_data(job_title)
    # Prepare charts
    sector_data = data.get("sector_counts", {})
    dept_data = data.get("dept_counts", {})
    degree_data = data.get("degree_counts", {})
    honor_grade = data.get("honor_grade", {})
    year_data = data.get("year_counts", {})
    print(data)
    print(honor_grade)

    total_sector = sum(sector_data.values()) if sector_data else 0
    total_degree = sum(degree_data.values()) if degree_data else 0

    # Sector Distribution Bar
    sector_bar = dcc.Graph(
        figure=go.Figure(
            data=[
                go.Bar(
                    x=list(sector_data.keys()),
                    y=list(sector_data.values()),
                    marker_color="indigo"
                )
            ],
            layout=go.Layout(
                title="Sector Distribution",
                yaxis=dict(range=[0, max(total_sector, 1)]),
                xaxis_title="Sector",
                yaxis_title="Count"
            )
        )
    ) if sector_data else html.Div("No sector data.")

    # Department Pie
    dept_pie = dcc.Graph(
        figure=go.Figure(
            data=[
                go.Pie(
                    labels=list(dept_data.keys()),
                    values=list(dept_data.values()),
                    hole=0.3
                )
            ],
            layout=go.Layout(
                title="Department Distribution"
            )
        )
    ) if dept_data else html.Div("No department data.")
    
    # Honor Grade Pie
    honor_pie = dcc.Graph(
        figure=go.Figure(
            data=[
                go.Pie(
                    labels=list(honor_grade.keys()),
                    values=list(honor_grade.values()),
                    hole=0.4
                )
            ],
            layout=go.Layout(
                title="Honor of the Degree"
            )
        )
    ) if honor_grade else html.Div("No data.")

    # Degree Distribution Bar
    degree_bar = dcc.Graph(
        figure=go.Figure(
            data=[
                go.Bar(
                    x=list(degree_data.keys()),
                    y=list(degree_data.values()),
                    marker_color="purple"
                )
            ],
            layout=go.Layout(
                title="Degree Distribution",
                yaxis=dict(range=[0, max(total_degree, 1)]),
                xaxis_title="Degree",
                yaxis_title="Count"
            )
        )
    ) if degree_data else html.Div("No degree data.")

    # Growth Over Time Line
    year_chart = dcc.Graph(
        figure=go.Figure(
            data=[
                go.Scatter(
                    x=list(year_data.keys()),
                    y=list(year_data.values()),
                    mode="lines+markers",
                    line=dict(color="#2B6CB0")
                )
            ],
            layout=go.Layout(
                title="Growth Over Time",
                xaxis_title="Year",
                yaxis_title="Count"
            )
        )
    ) if year_data else html.Div("No year data.")

    return [
        html.H2(f"Dashboard for: {job_title.title()}", className="mb-4"),
        dbc.Row([dbc.Col(sector_bar, width=12)], className="mb-4"),
        dbc.Row([dbc.Col(dept_pie, width=12)], className="mb-4"),
        dbc.Row([dbc.Col(honor_pie, width=12)], className="mb-4"),
        dbc.Row([dbc.Col(degree_bar, width=12)], className="mb-4"),
        dbc.Row([dbc.Col(year_chart, width=12)], className="mb-4"),
        html.Div(f"Total records: {data.get('total_count', 0)}", className="mb-2 font-weight-bold"),
    ]


if __name__ == "__main__":
    app.run(debug=True, port=8050)