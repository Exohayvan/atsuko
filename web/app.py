from flask import Flask, render_template
import os

# Set CWD to current file path
script_path = os.path.abspath(__file__)
directory_path = os.path.dirname(script_path)
os.chdir(directory_path)

app = Flask(__name__)

@app.route('/')
def coming_soon():
    return render_template('coming_soon.html')

if __name__ == '__main__':
    app.run(debug=True)
