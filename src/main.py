from flask import Flask, request, Response
from flask_basicauth import BasicAuth
import subprocess
import os

# Create a Flask application
app = Flask(__name__)

# Basic Auth Config
app.config['BASIC_AUTH_USERNAME'] = 'your_username'
app.config['BASIC_AUTH_PASSWORD'] = 'your_password'
basic_auth = BasicAuth(app)

# Define a route for the root URL
@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/bash')
@basic_auth.required
def run_bash():
    # Get the value of the 'cmd' query parameter from the URL
    command = request.args.get('cmd', 'echo You didn\'t provide any command.')

    # Run the Bash command and capture the output
    result = subprocess.run(['fish', '-c', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Check the return code to see if the command was successful (0 indicates success)
    if result.returncode == 0:
        response = Response(result.stdout)
    else:
        response = Response(result.stderr)
    
    # Set the Content-Type header to "text/plain"
    response.headers['Content-Type'] = 'text/plain'
    
    # Return response
    return response
    
@app.route('/cwd')
@basic_auth.required
def change_working_directory():
    # Get the value of the 'path' query parameter from the URL
    path = request.args.get('path', '')

    # Return error message if path is not provided
    if path == '':
        return 'You didn\'t provide the path.'

    # Chagne working directory
    os.chdir(path)

    # Show current path
    result = subprocess.run("echo Current directory:".split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout
    result = subprocess.run("pwd".split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output += result.stdout
    output += '\n'

    # Show files in the path
    result = subprocess.run("echo Files in directory:".split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output += result.stdout
    result = subprocess.run("ls -la".split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output += result.stdout

    # Set response
    response = Response(output)

    # Set the Content-Type header to "text/plain"
    response.headers['Content-Type'] = 'text/plain'

    # Return response
    return response

# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=False)