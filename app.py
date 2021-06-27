from flask import Flask, render_template, json, request,redirect,session,jsonify
import object_fake_new
app = Flask(__name__)
# app.secret_key = 'why would I tell you my secret key?'

@app.route('/')
def main():
    return render_template('information.html')

@app.route('/add',methods=['POST'])
def add():
    try:
        _information = request.form['inputInformation']
        if object_fake_new.checkObject(_information):
            return render_template('result.html',error = 'TRUE NEW')
        else:
             return render_template('result.html',error = 'FAKE NEW')
    except Exception as e:
        return render_template('result.html',error = str(e))
if __name__ == '__main__':
    app.run(port=5002)
