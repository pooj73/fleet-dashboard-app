from flask import Flask, render_template_string, jsonify
import pandas as pd

app = Flask(__name__)
DATA_FILE = "c:\\Users\\Admin\\Downloads\\trip_dashboard\\TRIP3\\project\\fleet_trip_data.xlsx"

def load_data():
    df = pd.read_excel(DATA_FILE)
    df.columns = df.columns.str.strip()
    df['Trip Date'] = pd.to_datetime(df['Trip Date'], errors='coerce')
    df['Day'] = df['Trip Date'].dt.day
    return df

@app.route('/')
def dashboard():
    df = load_data()

    # Daily counts
    days = list(range(1, 31 + 1))
    total = df.groupby('Day')['Trip ID'].count().reindex(days, fill_value=0).tolist()
    ongoing = df[df['Trip Status'] == 'Pending Closure'].groupby('Day')['Trip ID'].count().reindex(days, fill_value=0).tolist()
    closed = df[df['Trip Status'] == 'Completed'].groupby('Day')['Trip ID'].count().reindex(days, fill_value=0).tolist()

    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Trip Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body {
      background-color: #0d1b2a;
      font-family: Arial, sans-serif;
      color: white;
      padding: 20px;
    }
    .stats {
      display: flex;
      justify-content: space-around;
      margin-bottom: 20px;
      text-align: center;
    }
    .stat-block h1 {
      font-size: 48px;
      margin: 0;
      color: #f5c518;
    }
    .legend {
      display: flex;
      justify-content: center;
      gap: 30px;
      margin-bottom: 20px;
    }
    .legend label {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 16px;
    }
    canvas {
      background-color: #0d1b2a;
    }
    input[type="checkbox"] {
      transform: scale(1.2);
    }
  </style>
</head>
<body>
  <div class="stats">
    <div class="stat-block">
      <h1>{{ total_sum }}</h1>
      <div>Total Trips</div>
    </div>
    <div class="stat-block">
      <h1>{{ ongoing_sum }}</h1>
      <div>On-going</div>
    </div>
    <div class="stat-block">
      <h1>{{ closed_sum }}</h1>
      <div>Trip Closed</div>
    </div>
  </div>

  <div class="legend">
    <label><input type="checkbox" id="totalCheckbox" checked> Total Trips</label>
    <label><input type="checkbox" id="ongoingCheckbox" checked> On-going</label>
    <label><input type="checkbox" id="closedCheckbox" checked> Trip Closed</label>
  </div>

  <canvas id="tripChart" height="100"></canvas>

  <script>
    const ctx = document.getElementById('tripChart').getContext('2d');
    const labels = Array.from({ length: 30 }, (_, i) => i + 1);
    const chartData = {
      labels: labels,
      datasets: [
        {
          label: 'Total Trips',
          backgroundColor: '#f5c518',
          data: {{ total | safe }}
        },
        {
          label: 'On-going',
          backgroundColor: '#00c896',
          data: {{ ongoing | safe }}
        },
        {
          label: 'Trip Closed',
          backgroundColor: '#007bff',
          data: {{ closed | safe }}
        }
      ]
    };

    const config = {
      type: 'bar',
      data: chartData,
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: 'white' }, grid: { display: false } },
          y: { ticks: { color: 'white' }, grid: { color: '#33415c' } }
        }
      }
    };

    const tripChart = new Chart(ctx, config);

    document.getElementById('totalCheckbox').addEventListener('change', function() {
      tripChart.data.datasets[0].hidden = !this.checked;
      tripChart.update();
    });
    document.getElementById('ongoingCheckbox').addEventListener('change', function() {
      tripChart.data.datasets[1].hidden = !this.checked;
      tripChart.update();
    });
    document.getElementById('closedCheckbox').addEventListener('change', function() {
      tripChart.data.datasets[2].hidden = !this.checked;
      tripChart.update();
    });
  </script>
</body>
</html>
''',
        total=total,
        ongoing=ongoing,
        closed=closed,
        total_sum=sum(total),
        ongoing_sum=sum(ongoing),
        closed_sum=sum(closed)
    )

if __name__ == '__main__':
    app.run(debug=True)

