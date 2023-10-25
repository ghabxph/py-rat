from flask import Flask, request, Response, stream_with_context
from flask_basicauth import BasicAuth
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Create a Flask application
app = Flask(__name__)

# Basic Auth Config
app.config['BASIC_AUTH_USERNAME'] = os.getenv("BASIC_AUTH_USERNAME")
app.config['BASIC_AUTH_PASSWORD'] = os.getenv("BASIC_AUTH_PASSWORD")
basic_auth = BasicAuth(app)

# Global variables to track the current running command and its output
current_command = None
command_output = None

@stream_with_context
def generate_output(command):
    global current_command, command_output

    try:
        # Start the long-running process (e.g., Docker build)
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Stream output to the client
        for line in process.stdout:
            yield line
            command_output += line  # Store the output as it becomes available

        process.stdout.close()
        process.wait()

    except Exception as e:
        # Handle any exceptions and provide error information to the client
        yield f"Error: {str(e)}"

    # Once the command finishes, reset the current_command
    current_command = None

# Define a route for the root URL
@app.route('/')
@basic_auth.required
def hello_world():
    return 'Welcome to Home RAT!'

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

@app.route('/bashl')
@basic_auth.required
def bash_long_running():
    global current_command, command_output

    # Get the value of the 'cmd' query parameter from the URL
    command = request.args.get('cmd', None)

    # Check if a command is already in progress
    if current_command:
        return Response(f"Command '{current_command}' is already running.\n\n{command_output}", content_type="text/plain")

    # If no command is in progress, set the current_command
    current_command = command
    command_output = ""

    if not command:
        return "You didn't provide any command."

    return Response(generate_output(command), content_type='text/plain')

@app.route('/bashl-logs')
@basic_auth.required
def bashl_logs():
    global current_command, command_output

    # Get the latest command output
    return Response(f"{command_output}", content_type="text/plain")

# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=False)