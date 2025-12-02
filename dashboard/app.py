from flask import Flask, render_template_string, request, jsonify
import json, os
import numpy as np
import plotly.express as px

app = Flask(__name__)

INDEX_HTML = '''<!doctype html>
<html>
<head>
  <title>Reentry Sim Dashboard (Prototype)</title>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
  <h1>Reentry Sim - Footprint Viewer (Prototype)</h1>
  <div id="plot"></div>
  <script>
    fetch('/api/sample_landings').then(r=>r.json()).then(data=>{
        var fig = {
          data: [{
            x: data.lons, y: data.lats, mode: 'markers', type: 'scatter'
          }],
          layout: {title: 'Sample Monte-Carlo Landings', xaxis:{title:'Longitude'}, yaxis:{title:'Latitude'}}
        };
        Plotly.newPlot('plot', fig);
    });
  </script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/api/sample_landings')
def sample_landings():
    # generate synthetic sample scatter
    center_lat = 52.0; center_lon = 21.0
    lats = list( (center_lat + 0.01*np.random.randn(200)).tolist() )
    lons = list( (center_lon + 0.02*np.random.randn(200)).tolist() )
    return jsonify({'lats': lats, 'lons': lons})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
