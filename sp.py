import http.server
import socketserver
import os
from urllib.parse import parse_qs

PORT = 8000

HTML_FORM = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Smart Fleet Ai - Sign Up</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0B132B] flex flex-col items-center justify-center h-screen text-white font-sans">
  <div class="text-center mb-4">
    <h1 class="text-4xl font-bold">Smart Fleet Ai</h1>
    <p class="text-gray-400 mt-2">Powered by Ai Data Portal</p>
  </div>
  <form method="POST" class="bg-[#0E1A36] p-8 rounded-xl w-full max-w-sm shadow-md space-y-4">
    <input type="text" name="fullname" placeholder="Full Name" required class="w-full bg-[#1C2541] text-white placeholder-gray-400 p-3 rounded-md outline-none" />
    <input type="email" name="email" placeholder="Email" required class="w-full bg-[#1C2541] text-white placeholder-gray-400 p-3 rounded-md outline-none" />
    <input type="text" name="phone" placeholder="Phone Number" required class="w-full bg-[#1C2541] text-white placeholder-gray-400 p-3 rounded-md outline-none" />
    <input type="password" name="password" placeholder="Password" required class="w-full bg-[#1C2541] text-white placeholder-gray-400 p-3 rounded-md outline-none" />
    <input type="password" name="confirm_password" placeholder="Confirm Password" required class="w-full bg-[#1C2541] text-white placeholder-gray-400 p-3 rounded-md outline-none" />
    <button type="submit" class="w-full bg-white text-[#0B132B] font-semibold py-2 rounded-md hover:bg-gray-200 transition duration-200">
      Sign Up
    </button>
  </form>
</body>
</html>"""

class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/signup':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_FORM.encode())
        else:
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode()
        fields = parse_qs(post_data)

        fullname = fields.get("fullname", [""])[0]
        email = fields.get("email", [""])[0]
        phone = fields.get("phone", [""])[0]
        password = fields.get("password", [""])[0]
        confirm_password = fields.get("confirm_password", [""])[0]

        if password != confirm_password:
            self.respond_message("Passwords do not match!")
            return

        with open("users.txt", "a") as f:
            f.write(f"{fullname},{email},{phone}\n")

        self.respond_message("User registered successfully!")

    def respond_message(self, message):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        response = f"<html><body style='background:#0B132B;color:white;padding:2em;'><h2>{message}</h2><br><a href='/'>Back to Signup</a></body></html>"
        self.wfile.write(response.encode())

with socketserver.TCPServer(("", PORT), SimpleHandler) as httpd:
    print(f"✅ Server running at http://localhost:{PORT}")
    httpd.serve_forever()

