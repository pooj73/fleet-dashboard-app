from flask import Flask, render_template_string, send_file
import pandas as pd
import io

app = Flask(__name__)

# 🔹 Load Excel
EXCEL_FILE = 'fleet_50_entries.xlsx'
df = pd.read_excel(EXCEL_FILE)
df.columns = df.columns.str.strip()

# 🔹 Stats
total_trips     = len(df)
ongoing_trips   = df[df['Trip Status'] == 'Pending Closure'].shape[0]
closed_trips    = df[df['Trip Status'] == 'Completed'].shape[0]
flags           = df[df['Trip Status'] == 'Under Audit'].shape[0]
resolved        = df[(df['Trip Status']=='Under Audit') & (df['POD Status']=='Yes')].shape[0]
trip_id_example = df.at[0, 'Trip ID']

total_revenue = df['Freight Amount'].sum()
total_expense = df['Total Trip Expense'].sum()
net_profit    = df['Net Profit'].sum()
kms           = df['Actual Distance (KM)'].sum()

rev_m    = round(total_revenue / 1e6, 2)
exp_m    = round(total_expense / 1e6, 2)
profit_m = round(net_profit / 1e6, 2)
kms_k    = round(kms / 1e3, 1)
per_km   = round(net_profit / kms, 2) if kms else 0
profit_pct = round((net_profit / total_revenue * 100), 1) if total_revenue else 0

# 🔹 AI Report Generator
def generate_ai_insights(df):
    most_profitable_vehicle = df.groupby('Vehicle ID')['Net Profit'].sum().idxmax()

    avg_profit_per_trip = df['Net Profit'].mean()
    return {
        "most_profitable_vehicle": most_profitable_vehicle,
        "avg_profit_per_trip": round(avg_profit_per_trip / 1e6, 2),  # in millions
        "top_routes": "A & C"
    }

    return {
        'most_profitable_vehicle': most_profitable_vehicle,
        'avg_profit_per_trip': avg_profit_per_trip,
        'top_routes': ', '.join(top_routes)
    }

ai_report = generate_ai_insights(df)

# 🔹 HTML Template
HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Fleet Owner Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0B132B] text-white font-sans p-6">
  <h1 class="text-2xl font-bold mb-2">Fleet Owner Dashboard</h1>
  <div class="flex space-x-6 border-b border-gray-600 pb-2 mb-6 text-sm">
    <button class="text-white border-b-2 border-white pb-1">Dashboard</button>
    <button class="text-gray-300 hover:text-white">Trip Generator</button>
    <button class="text-gray-300 hover:text-white">Trip Closer</button>
    <button class="text-gray-300 hover:text-white">Trip Auditor</button>
  </div>

  <!-- Summary Cards -->
  <div class="grid grid-cols-4 gap-4 mb-6">
    <div class="bg-[#1C2541] p-4 rounded">
      <p class="text-xl font-semibold mb-1">{{ total_trips }}</p>
      <p class="text-gray-400 text-sm">Total Trips</p>
      <p class="text-xl font-semibold mt-4">{{ ongoing_trips }}</p>
      <p class="text-gray-400 text-sm">On going</p>
      <p class="text-xl font-semibold mt-4">{{ closed_trips }}</p>
      <p class="text-gray-400 text-sm">Trip Closed</p>
      <div class="h-20 bg-[#0E1A36] mt-4 rounded flex items-center justify-center text-gray-400 text-sm italic">
        Trip Bar Chart
      </div>
    </div>

    <div class="bg-[#1C2541] p-4 rounded">
      <p class="text-2xl font-semibold mb-2">{{ profit_pct }}%</p>
      <p class="text-gray-400 text-sm mb-4">Profit %</p>
      <ul class="text-sm text-gray-300 space-y-1">
        <li><span class="inline-block w-3 h-3 bg-orange-400 mr-2 rounded-full"></span>Revenue: ₹{{ rev_m }}M</li>
        <li><span class="inline-block w-3 h-3 bg-yellow-300 mr-2 rounded-full"></span>Expense: ₹{{ exp_m }}M</li>
        <li><span class="inline-block w-3 h-3 bg-blue-300 mr-2 rounded-full"></span>Profit: ₹{{ profit_m }}M</li>
        <li><span class="inline-block w-3 h-3 bg-teal-400 mr-2 rounded-full"></span>KMs: {{ kms_k }}K</li>
      </ul>
    </div>

    <div class="bg-[#1C2541] p-4 rounded col-span-2">
      <h2 class="text-lg font-semibold mb-2">Detailed Financials</h2>
      <div class="grid grid-cols-3 gap-4 text-sm mb-4">
        <div><p class="text-xl font-bold">₹{{ rev_m }} M</p><p class="text-gray-400">Revenue</p></div>
        <div><p class="text-xl font-bold">₹{{ profit_m }} M</p><p class="text-gray-400">Profit</p></div>
        <div><p class="text-xl font-bold">{{ kms_k }} K</p><p class="text-gray-400">KM Travelled</p></div>
      </div>
      <div class="h-24 bg-[#0E1A36] rounded mb-4 flex items-center justify-center text-gray-400 text-sm italic">
        Financial Bar Chart
      </div>
      <div class="flex items-center justify-between text-sm">
        <div>
          <p class="text-gray-400">Cost per KM</p>
          <p class="text-lg font-bold">₹{{ per_km }}</p>
        </div>
        <button class="bg-green-600 px-4 py-1 rounded font-semibold hover:bg-green-700">₹{{ per_km }}</button>
      </div>
    </div>
  </div>

  <!-- Auditing & AI Reports -->
  <div class="grid grid-cols-3 gap-4">
    <div class="bg-[#1C2541] p-4 rounded">
      <h2 class="text-lg font-semibold mb-2">Auditing</h2>
      <p class="text-sm">Flags: <span class="font-bold">{{ flags }}</span></p>
      <p class="text-sm">Sample Trip ID: <span class="font-bold">{{ trip_id_example }}</span></p>
      <p class="text-sm">Resolved: <span class="font-bold">{{ resolved }}</span></p>
    </div>

    <!-- AI Reports -->
    <div class="bg-[#1C2541] p-4 rounded col-span-2">
      <h2 class="text-lg font-semibold mb-2">AI Reports</h2>
      <div class="grid grid-cols-2 gap-4">
        <ul class="list-disc list-inside text-sm space-y-2 text-gray-300">
          <li>Top Vehicle: {{ ai.most_profitable_vehicle }}</li>
          <li>Avg profit per trip: ₹{{ ai.avg_profit_per_trip }}K</li>
          <li>Top routes: {{ ai.top_routes }}</li>
        </ul>
        <div class="flex flex-col items-center justify-center text-sm text-gray-300">
          <p class="italic mb-2">Automated Insights</p>
          <a href="/download-summary" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded font-semibold">
            ⬇️ Download Summary
          </a>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(HTML,
        total_trips=total_trips,
        ongoing_trips=ongoing_trips,
        closed_trips=closed_trips,
        profit_pct=profit_pct,
        rev_m=rev_m,
        exp_m=exp_m,
        profit_m=profit_m,
        kms_k=kms_k,
        per_km=per_km,
        flags=flags,
        resolved=resolved,
        trip_id_example=trip_id_example,
        ai=ai_report
    )

@app.route('/download-summary')
def download_summary():
    output = io.BytesIO()
    summary_df = pd.DataFrame([{
        'Total Trips': total_trips,
        'Ongoing Trips': ongoing_trips,
        'Closed Trips': closed_trips,
        'Profit %': profit_pct,
        'Revenue (M)': rev_m,
        'Expense (M)': exp_m,
        'Profit (M)': profit_m,
        'KMs (K)': kms_k,
        'Cost per KM': per_km,
        'Flags': flags,
        'Resolved Audits': resolved
    }])
    summary_df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, download_name="fleet_summary_report.xlsx", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
