from flask import Flask, request, jsonify, render_template_string
import subprocess
import os

app = Flask(__name__)

def read_template_file():
    try:
        with open("index.html", "r") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "Error: File 'web/template.html' not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

current_directory = os.getcwd()

python_executable = 'C:\\Users\\lProfesseur\\AppData\\Local\\Programs\\Python\\Python38\\python.exe'

encodings_to_try = ['latin1', 'cp850']

@app.route('/')
def index():
    return render_template_string(read_template_file())

@app.route('/execute', methods=['POST'])
def execute():
    global current_directory
    data = request.json
    command = data.get('command')
    try:
        if command.startswith('python '):
            script_name = command.split(' ')[1]
            output = subprocess.check_output([python_executable, script_name], shell=True, stderr=subprocess.STDOUT, universal_newlines=True, cwd=current_directory)
        elif command.startswith('dir'):
            files = os.listdir(current_directory)
            output = '\n'.join(files)
        elif command.startswith('cd '):
            new_directory = command[3:]
            if not os.path.isabs(new_directory):
                new_directory = os.path.join(current_directory, new_directory)
            new_directory = os.path.abspath(new_directory)
            if os.path.isdir(new_directory):
                output = f'Directory changed to: {new_directory}'
                current_directory = new_directory
            else:
                output = f'Error: {new_directory} is not a directory'
        else:
            for encoding in encodings_to_try:
                try:
                    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True, encoding=encoding, cwd=current_directory)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True, encoding='utf-8', errors='replace', cwd=current_directory)
    except subprocess.CalledProcessError as e:
        output = e.output

    return jsonify({'output': output})

if __name__ == '__main__':
    current_directory = os.path.dirname(os.path.abspath(__file__))
    app.run(host='0.0.0.0', port=5000)