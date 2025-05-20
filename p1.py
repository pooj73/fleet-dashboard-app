from flask import Flask, render_template_string, request, redirect, url_for
from werkzeug.security import generate_password_hash  # ✅ uncommented

app = Flask(__name__)




users = [
    {'name': 'Anna Smith', 'email': 'anna.smith@example.com', 'role': 'Admin', 'password': generate_password_hash("password1"),
     'rights': {'view': True, 'edit': True, 'delete': True, 'add_fields': False}},
    {'name': 'John Doe', 'email': 'john.doe@example.com', 'role': 'Manager', 'password': generate_password_hash("password2"),
     'rights': {'view': True, 'edit': False, 'delete': False, 'add_fields': False}},
    {'name': 'Emily Johnson', 'email': 'emily.johnson@example.com', 'role': 'Viewer', 'password': generate_password_hash("password3"),
     'rights': {'view': True, 'edit': False, 'delete': False, 'add_fields': False}},
    {'name': 'Michael Brown', 'email': 'michael.brown@example.com', 'role': 'Trip Closer', 'password': generate_password_hash("password4"),
     'rights': {'view': True, 'edit': True, 'delete': True, 'add_fields': False}},
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Fleet Owner User Settings</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0B132B] text-white font-sans p-6">
  <h1 class="text-2xl font-bold mb-4">Fleet Owner User Settings</h1>

  <!-- Navigation -->
  <div class="flex space-x-6 border-b border-gray-600 pb-2 mb-6 text-sm">
    <button class="text-gray-300 hover:text-white">Dashboard</button>
    <button class="text-gray-300 hover:text-white">Trip Generator</button>
    <button class="text-gray-300 hover:text-white">Trip Closer</button>
    <button class="text-gray-300 hover:text-white">Trip Auditor</button>
    <button class="text-white border-b-2 border-white pb-1">AI Module</button>
  </div>

  <!-- User Table -->
  <div class="grid grid-cols-3 gap-6 mb-8">
    <div class="col-span-2">
      <h2 class="text-lg font-semibold mb-2">User Credentials Table</h2>
      <div class="bg-[#1C2541] p-4 rounded-lg overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="text-left text-gray-400 border-b border-gray-600">
            <tr>
              <th class="pb-2">Name</th>
              <th class="pb-2">Email</th>
              <th class="pb-2">Role</th>
              <th class="pb-2">Rights</th>
            </tr>
          </thead>
          <tbody class="text-white">
            {% for user in users %}
            <tr class="border-b border-gray-700">
              <td class="py-2">{{ user.name }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.role }}</td>
              <td>
                <form action="/update_rights" method="POST" class="flex flex-wrap items-center gap-2">
                  <input type="hidden" name="email" value="{{ user.email }}">
                  <label><input type="checkbox" name="view" {% if user.rights.view %}checked{% endif %}> View</label>
                  <label><input type="checkbox" name="edit" {% if user.rights.edit %}checked{% endif %}> Edit</label>
                  <label><input type="checkbox" name="delete" {% if user.rights.delete %}checked{% endif %}> Delete</label>
                  <label><input type="checkbox" name="add_fields" {% if user.rights.add_fields %}checked{% endif %}> Add Fields</label>
                  <button type="submit" class="bg-gray-600 px-2 py-1 rounded hover:bg-gray-500 text-sm">Save</button>
                </form>
              </td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add New User -->
    <div>
      <h2 class="text-lg font-semibold mb-2">User Credentials</h2>
      <div class="bg-[#1C2541] p-4 rounded-lg">
        <form action="/add_user" method="POST">
          <input type="text" name="name" placeholder="Name" class="w-full bg-[#0E1A36] p-2 rounded text-white placeholder-gray-400 outline-none mb-2" required>
          <input type="email" name="email" placeholder="Email" class="w-full bg-[#0E1A36] p-2 rounded text-white placeholder-gray-400 outline-none mb-2" required>
          <input type="password" name="password" placeholder="Password" class="w-full bg-[#0E1A36] p-2 rounded text-white placeholder-gray-400 outline-none mb-2" required>
          <input type="text" name="role" placeholder="Role" class="w-full bg-[#0E1A36] p-2 rounded text-white placeholder-gray-400 outline-none mb-2" required>

          <div class="space-y-2 text-sm mb-4">
            <div><input type="checkbox" name="view" class="mr-2">View</div>
            <div><input type="checkbox" name="edit" class="mr-2">Edit</div>
            <div><input type="checkbox" name="delete" class="mr-2">Delete</div>
            <div><input type="checkbox" name="add_fields" class="mr-2">Add Fields</div>
          </div>

          <button type="submit" class="bg-blue-600 px-4 py-2 rounded hover:bg-blue-500">Save Credentials</button>
        </form>
      </div>
    </div>
  </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')
    rights = {
        'view': 'view' in request.form,
        'edit': 'edit' in request.form,
        'delete': 'delete' in request.form,
        'add_fields': 'add_fields' in request.form
    }
    hashed_password = generate_password_hash(password)
    users.append({'name': name, 'email': email, 'role': role, 'password': hashed_password, 'rights': rights})
    return redirect(url_for('index'))

@app.route('/update_rights', methods=['POST'])
def update_rights():
    email = request.form.get('email')
    for user in users:
        if user['email'] == email:
            user['rights'] = {
                'view': 'view' in request.form,
                'edit': 'edit' in request.form,
                'delete': 'delete' in request.form,
                'add_fields': 'add_fields' in request.form
            }
            break
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

