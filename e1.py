from flask import Flask, render_template_string, request, send_file
import pandas as pd

app = Flask(__name__)

# Load Excel
EXCEL_FILE = 'fleet_50_entries.xlsx'
df = pd.read_excel(EXCEL_FILE)
df.columns = df.columns.str.strip()
df['Trip Date'] = pd.to_datetime(df['Trip Date'], errors='coerce')
df['Day'] = df['Trip Date'].dt.day

vehicles = sorted(df['Vehicle ID'].dropna().unique())
routes = sorted(df['Route'].dropna().unique()) if 'Route' in df.columns else []

def generate_ai_report(filtered_df):
    if filtered_df.empty:
        return "No data available for AI report."
    
    most_profitable_vehicle = filtered_df.groupby('Vehicle ID')['Net Profit'].sum().idxmax()
    top_routes = ", ".join(filtered_df['Route'].value_counts().head(2).index) if 'Route' in filtered_df.columns else "N/A"
    avg_profit_per_trip = round(filtered_df['Net Profit'].sum() / len(filtered_df), 2)

    rev = filtered_df['Freight Amount'].sum()
    exp = filtered_df['Total Trip Expense'].sum()
    profit = filtered_df['Net Profit'].sum()
    kms = filtered_df['Actual Distance (KM)'].sum()
    profit_pct = round((profit / rev * 100), 1) if rev else 0
    per_km = round(profit / kms, 2) if kms else 0

    return f"""
📊 AI Report Highlights:

Total Trips: {len(filtered_df)}
On-going Trips: {filtered_df[filtered_df['Trip Status'] == 'Pending Closure'].shape[0]}
Completed Trips: {filtered_df[filtered_df['Trip Status'] == 'Completed'].shape[0]}
Profit Percentage: {profit_pct}%

Financials:
- Revenue: ₹{round(rev / 1e6, 2)}M
- Expense: ₹{round(exp / 1e6, 2)}M
- Profit: ₹{round(profit / 1e6, 2)}M
- KMs Travelled: {round(kms / 1e3, 1)}K
- Cost per KM: ₹{per_km}

AI Insights:
- Top Vehicle: {most_profitable_vehicle}
- Average Profit per Trip: ₹{avg_profit_per_trip}
- Top Routes: {top_routes}
"""

@app.route('/')
def dashboard():
    vehicle = request.args.get('vehicle')
    route = request.args.get('route')

    filtered = df.copy()
    if vehicle:
        filtered = filtered[filtered['Vehicle ID'] == vehicle]
    if route:
        filtered = filtered[filtered['Route'] == route]

    total_trips = len(filtered)
    ongoing = filtered[filtered['Trip Status'] == 'Pending Closure'].shape[0]
    closed = filtered[filtered['Trip Status'] == 'Completed'].shape[0]
    flags = filtered[filtered['Trip Status'] == 'Under Audit'].shape[0]
    resolved = filtered[(filtered['Trip Status'] == 'Under Audit') & (filtered['POD Status'] == 'Yes')].shape[0]

    rev = filtered['Freight Amount'].sum()
    exp = filtered['Total Trip Expense'].sum()
    profit = filtered['Net Profit'].sum()
    kms = filtered['Actual Distance (KM)'].sum()

    rev_m = round(rev / 1e6, 2)
    exp_m = round(exp / 1e6, 2)
    profit_m = round(profit / 1e6, 2)
    kms_k = round(kms / 1e3, 1)
    per_km = round(profit / kms, 2) if kms else 0
    profit_pct = round((profit / rev) * 100, 1) if rev else 0

    daily = filtered.groupby('Day')['Trip ID'].count().reindex(range(1, 32), fill_value=0).tolist()
    audited = filtered[filtered['Trip Status'] == 'Under Audit'].groupby('Day')['Trip ID'].count().reindex(range(1, 32), fill_value=0).tolist()
    audit_pct = [round(a / b * 100, 1) if b else 0 for a, b in zip(audited, daily)]

    bar_labels = ['Revenue', 'Expense', 'Profit']
    bar_values = [
        float(rev_m) if pd.notna(rev_m) else 0,
        float(exp_m) if pd.notna(exp_m) else 0,
        float(profit_m) if pd.notna(profit_m) else 0
    ]

    ai_report = generate_ai_report(filtered)

    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Fleet Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-[#0B132B] text-white p-6 font-sans">
  <h1 class="text-3xl font-bold mb-6">Fleet Owner Dashboard</h1>

  <form method="get" class="flex gap-4 mb-6">
    <select name="vehicle" class="text-black p-2 rounded">
      <option value="">All Vehicles</option>
      {% for v in vehicles %}
      <option value="{{v}}" {% if v == selected_vehicle %}selected{% endif %}>{{v}}</option>
      {% endfor %}
    </select>
    <select name="route" class="text-black p-2 rounded">
      <option value="">All Routes</option>
      {% for r in routes %}
      <option value="{{r}}" {% if r == selected_route %}selected{% endif %}>{{r}}</option>
      {% endfor %}
    </select>
    <button class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded">Apply</button>
  </form>

  <div class="grid grid-cols-3 gap-4 mb-6">
    <div class="bg-[#1C2541] p-4 rounded">
      <p>Total Trips: <b>{{ total_trips }}</b></p>
      <p>Ongoing: <b>{{ ongoing }}</b></p>
      <p>Closed: <b>{{ closed }}</b></p>
      <p>Flags: <b>{{ flags }}</b></p>
      <p>Resolved: <b>{{ resolved }}</b></p>
    </div>
    <div class="bg-[#1C2541] p-4 rounded">
      <p class="font-bold mb-2 text-lg">Financial Summary</p>
      <p>Revenue: ₹{{ rev_m }}M</p>
      <p>Expense: ₹{{ exp_m }}M</p>
      <p>Profit: ₹{{ profit_m }}M</p>
      <p>KMs: {{ kms_k }}K</p>
      <p>Per KM: ₹{{ per_km }}</p>
      <p>Profit %: {{ profit_pct }}%</p>
    </div>
    <div class="bg-[#1C2541] p-4 rounded">
      <p class="font-bold mb-2">AI Report</p>
      <pre class="text-sm text-gray-300">{{ ai_report }}</pre>
      <a href="/download-summary" class="mt-2 inline-block bg-green-600 px-3 py-1 rounded hover:bg-green-700">Download Summary</a>
    </div>
  </div>

  <div class="grid grid-cols-2 gap-4">
    <div class="bg-[#1C2541] p-4 rounded">
      <h2 class="mb-2 font-semibold text-lg">Daily Trips vs Audits</h2>
      <canvas id="auditChart" height="120"></canvas>
    </div>
    <div class="bg-[#1C2541] p-4 rounded">
      <h2 class="mb-2 font-semibold text-lg">Finance Chart</h2>
      <canvas id="financeChart" height="120"></canvas>
    </div>
  </div>

  <script>
    new Chart(document.getElementById('auditChart').getContext('2d'), {
      data: {
        labels: Array.from({length: 31}, (_, i) => i + 1),
        datasets: [
          {type: 'bar', label: 'Closed', data: {{ daily | safe }}, backgroundColor: '#4CAF50'},
          {type: 'bar', label: 'Audited', data: {{ audited | safe }}, backgroundColor: '#2196F3'},
          {type: 'line', label: 'Audit %', data: {{ audit_pct | safe }}, yAxisID: 'y1', borderColor: 'yellow', fill: false}
        ]
      },
      options: {
        responsive: true,
        scales: {
          y: {beginAtZero: true, ticks: {color: 'white'}, grid: {color: '#444'}},
          y1: {beginAtZero: true, position: 'right', ticks: {color: 'white'}, grid: {drawOnChartArea: false}},
          x: {ticks: {color: 'white'}, grid: {color: '#444'}}
        },
        plugins: {legend: {labels: {color: 'white'}}}
      }
    });

    new Chart(document.getElementById('financeChart').getContext('2d'), {
      type: 'bar',
      data: {
        labels: {{ bar_labels | safe }},
        datasets: [{
          label: '₹ in Millions',
          data: {{ bar_values | safe }},
          backgroundColor: ['#FFA500', '#FF4444', '#44FF44']
        }]
      },
      options: {
        plugins: {legend: {labels: {color: 'white'}}},
        scales: {
          y: {beginAtZero: true, ticks: {color: 'white'}},
          x: {ticks: {color: 'white'}}
        }
      }
    });
  </script>
</body>
</html>
''',
        total_trips=total_trips, ongoing=ongoing, closed=closed,
        flags=flags, resolved=resolved, rev_m=rev_m, exp_m=exp_m,
        profit_m=profit_m, kms_k=kms_k, per_km=per_km, profit_pct=profit_pct,
        ai_report=ai_report, vehicles=vehicles, routes=routes,
        selected_vehicle=vehicle, selected_route=route,
        daily=daily, audited=audited, audit_pct=audit_pct,
        bar_labels=bar_labels, bar_values=bar_values
    )

@app.route('/download-summary')
def download_summary():
    filtered = df
    report = generate_ai_report(filtered)
    with open("AI_Report_Summary.txt", 'w', encoding='utf-8') as f:
        f.write(report)
    return send_file("AI_Report_Summary.txt", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

