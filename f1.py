from flask import Flask, render_template_string, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# ------------------------ Excel Data ------------------------
EXCEL_FILE = 'fleet_50_entries.xlsx'
df = pd.read_excel(EXCEL_FILE)
df.columns = df.columns.str.strip()

# Stats for Dashboard
summary = {
    'total_trips': len(df),
    'ongoing': df[df['Trip Status'] == 'Pending Closure'].shape[0],
    'completed': df[df['Trip Status'] == 'Completed'].shape[0],
    'under_audit': df[df['Trip Status'] == 'Under Audit'].shape[0],
    'resolved': df[(df['Trip Status'] == 'Under Audit') & (df['POD Status'] == 'Yes')].shape[0],
    'revenue_m': round(df['Freight Amount'].sum() / 1e6, 2),
    'expense_m': round(df['Total Trip Expense'].sum() / 1e6, 2),
    'profit_m': round(df['Net Profit'].sum() / 1e6, 2),
    'kms_k': round(df['Actual Distance (KM)'].sum() / 1e3, 1),
    'cost_per_km': round(df['Net Profit'].sum() / df['Actual Distance (KM)'].sum(), 2) if df['Actual Distance (KM)'].sum() else 0,
    'profit_pct': round((df['Net Profit'].sum() / df['Freight Amount'].sum()) * 100, 1) if df['Freight Amount'].sum() else 0
}

# ------------------------ User DB ------------------------
users = [
    {'name': 'Fleet Owner', 'email': 'owner@example.com', 'role': 'Owner', 'password': generate_password_hash("admin123")},
    {'name': 'Trip Closer', 'email': 'closer@example.com', 'role': 'Closer', 'password': generate_password_hash("closer123")},
]

# ------------------------ Templates ------------------------
TEMPLATE_SIGNUP = '''...'''  # Same as before

TEMPLATE_LOGIN = '''...'''  # Same as before

TEMPLATE_DASHBOARD = '''
<!DOCTYPE html><html><head><title>Dashboard</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#0B132B] text-white p-6">
  <h1 class="text-3xl font-bold mb-4">Welcome {{ user.name }}</h1>
  <div class="grid grid-cols-3 gap-4 mb-6">
    <div class="bg-[#1C2541] p-4 rounded"><p class="text-xl">Total Trips</p><p class="text-3xl font-bold">{{ s.total_trips }}</p></div>
    <div class="bg-[#1C2541] p-4 rounded"><p class="text-xl">Ongoing</p><p class="text-3xl font-bold">{{ s.ongoing }}</p></div>
    <div class="bg-[#1C2541] p-4 rounded"><p class="text-xl">Closed</p><p class="text-3xl font-bold">{{ s.completed }}</p></div>
    <div class="bg-[#1C2541] p-4 rounded"><p class="text-xl">Revenue</p><p class="text-3xl font-bold">₹{{ s.revenue_m }}M</p></div>
    <div class="bg-[#1C2541] p-4 rounded"><p class="text-xl">Profit %</p><p class="text-3xl font-bold">{{ s.profit_pct }}%</p></div>
    <div class="bg-[#1C2541] p-4 rounded"><p class="text-xl">Cost/km</p><p class="text-3xl font-bold">₹{{ s.cost_per_km }}</p></div>
  </div>
  <div class="space-x-4">
    <a href="/trip-generator" class="bg-blue-600 px-4 py-2 rounded">Trip Generator</a>
    <a href="/trip-closure" class="bg-green-600 px-4 py-2 rounded">Trip Closure</a>
    <a href="/trip-auditor" class="bg-yellow-500 px-4 py-2 rounded">Trip Auditor</a>
    <a href="/trip-ongoing" class="bg-purple-600 px-4 py-2 rounded">Ongoing Trips</a>
    <a href="/logout" class="bg-red-600 px-4 py-2 rounded">Logout</a>
  </div>
</body></html>
'''

TEMPLATE_TRIP_MODULE = '''
<!DOCTYPE html><html><head><title>{{ title }}</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#0B132B] text-white p-6">
  <h2 class="text-2xl font-bold mb-4">{{ title }}</h2>
  <table class="table-auto w-full text-sm">
    <thead><tr>{% for col in data.columns %}<th class="border px-2 py-1">{{ col }}</th>{% endfor %}</tr></thead>
    <tbody>
      {% for _, row in data.iterrows() %}<tr>{% for cell in row %}<td class="border px-2 py-1">{{ cell }}</td>{% endfor %}</tr>{% endfor %}
    </tbody>
  </table>
  <a href="/dashboard" class="mt-4 inline-block bg-blue-500 px-4 py-2 rounded">Back</a>
</body></html>
'''

# ------------------------ Routes ------------------------
@app.route('/')
def home(): return redirect('/signup')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users.append({
            'name': request.form['name'],
            'email': request.form['email'],
            'password': generate_password_hash(request.form['password']),
            'role': request.form['role']
        })
        return redirect('/login')
    return render_template_string(TEMPLATE_SIGNUP)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email, password = request.form['email'], request.form['password']
        user = next((u for u in users if u['email'] == email), None)
        if user and check_password_hash(user['password'], password):
            session['user'] = user
            return redirect('/dashboard')
        return "Invalid credentials. <a href='/login'>Try again</a>"
    return render_template_string(TEMPLATE_LOGIN)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect('/login')
    return render_template_string(TEMPLATE_DASHBOARD, user=session['user'], s=summary)

@app.route('/trip-generator')
def trip_generator():
    data = df[['Trip ID', 'Vehicle ID', 'Route', 'Trip Status']].copy()
    return render_template_string(TEMPLATE_TRIP_MODULE, title="Trip Generator", data=data)

@app.route('/trip-closure')
def trip_closure():
    data = df[df['Trip Status'] == 'Pending Closure'][['Trip ID', 'Vehicle ID', 'Route', 'Trip Status']]
    return render_template_string(TEMPLATE_TRIP_MODULE, title="Trip Closure", data=data)

@app.route('/trip-auditor')
def trip_auditor():
    data = df[df['Trip Status'] == 'Under Audit'][['Trip ID', 'Vehicle ID', 'Route', 'Trip Status', 'POD Status']]
    return render_template_string(TEMPLATE_TRIP_MODULE, title="Trip Auditor", data=data)

@app.route('/trip-ongoing')
def trip_ongoing():
    data = df[df['Trip Status'] == 'Pending Closure'][['Trip ID', 'Vehicle ID', 'Route', 'Trip Status']]
    return render_template_string(TEMPLATE_TRIP_MODULE, title="Ongoing Trips", data=data)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)