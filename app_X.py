from flask import *
app = Flask(__name__)

@app.route('/')
def login_form():

    return render_template('login.html')

@app.route('/login', methods = ['POST'])
def login():

    if request.method == 'POST':

        if(request.form['id'] == 'admin' and request.form['pw'] == 'admin123'):

            session['logged'] = True

            session['user'] = request.form['id']

            # return 'Hi, ' + request.form['id']
            return render_template('index.html')

        else:

            return """<script>alert("wrong!");location.href='/';</script>"""

    else:

        return """<script>alert("not allowd!");location.href='/';</script>"""

app.secret_key = 'sample_secret'


if __name__ == '__main__':
       app.run(host='127.0.0.1', debug=True, threaded=True)