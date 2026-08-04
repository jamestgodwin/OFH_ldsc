"""
Flask-free rewrite of the LDSC API app.

Flask (and its core dependency Werkzeug) are not available in the fixed
environment, so this uses Python's built-in http.server module instead.
Same single route, same JSON response shape as the original.

NOTE: the original code called run_ldsc_command() with only 3 of its 5
required arguments (ldwindow and windUnit were missing), which would have
raised a TypeError on every request. That's fixed here by reading those two
from the query string as well, using the same defaulting behavior
run_ldsc_command() already implements internally.

Like Flask's own app.run(), Python's http.server is a simple single-threaded
dev server -- fine for local/internal use, but not intended to handle
production-scale concurrent traffic. If this needs to serve real load,
that's a separate consideration worth raising on its own.
"""
import subprocess
import os
import glob
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


def run_ldsc_command(pop, genome_build, filename, ldwindow, windUnit):
    fileDir = f"/data/tmp/uploads"
    print(filename)
    ldwindow_value = 1  # Example value, replace with actual value
    # Check if ldwindow is an integer greater than 0, if not set it to 1
    try:
        ldwindow_value = int(ldwindow)
        if ldwindow_value <= 0:
            ldwindow_value = 1
    except (TypeError, ValueError):
        ldwindow_value = 1

    windFlag = '--ld-wind-cm'
    if windUnit == 'cm':
        windFlag = "--ld-wind-cm"
    elif windUnit == 'kb':
        windFlag = "--ld-wind-kb"

    file_chromo = None
    if filename:
        file_parts = filename.split('.')
        for part in file_parts:
            if part.isdigit() and 1 <= int(part) <= 22:
                file_chromo = part
                break

    if file_chromo:
        # Find the file in the directory
        pattern = os.path.join(fileDir, f"{filename}.*")
        for file_path in glob.glob(pattern):
            extension = file_path.split('.')[-1]
            new_filename = f"{file_chromo}.{extension}"
            new_file_path = os.path.join(fileDir, new_filename)
            os.rename(file_path, new_file_path)

    try:
        # Run the command
        # 'cd 1kg_eur && python ../ldsc.py --bfile 22 --l2 --ld-wind-cm 1 --out 22'
        command = f"cd {fileDir} && python /app/ldsc.py --bfile {file_chromo} --l2 {windFlag} {ldwindow_value} --out {file_chromo}"
        result = subprocess.run(
            ['bash', '-c', command],
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e.stderr}"


class LDSCRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != '/ldscore':
            self._send_json({"error": "not found"}, status=404)
            return

        qs = parse_qs(parsed.query)

        def arg(key, default=None):
            values = qs.get(key)
            return values[0] if values else default

        pop = arg('pop')
        genome_build = arg('genome_build')
        filename = arg('filename')
        ldwindow = arg('ldwindow', '1')
        windUnit = arg('windUnit', 'cm')

        print(f"pop: {pop}, genome_build: {genome_build}, filename: {filename}")
        output = run_ldsc_command(pop, genome_build, filename, ldwindow, windUnit)
        self._send_json({"output": output})


if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 5000), LDSCRequestHandler)
    server.serve_forever()
