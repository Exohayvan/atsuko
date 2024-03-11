from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def coming_soon():
    return render_template('coming_soon.html')

if __name__ == '__main__':
    app.run(debug=True)
