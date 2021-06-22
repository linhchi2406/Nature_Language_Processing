from flask import Flask, render_template, json, request,redirect,session,jsonify
# from flaskext.mysql import MySQL
# from werkzeug import generate_password_hash, check_password_hash
import object_fake_new
# mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'

# MySQL configurations
# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'linhchi'
# app.config['MYSQL_DATABASE_DB'] = 'Laravel'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# mysql.init_app(app)


@app.route('/')
def main():
    return render_template('addWish.html')

@app.route('/addWish',methods=['POST'])
def addWish():
    try:
        _title = request.form['inputTitle']
        _description = request.form['inputDescription']
        if object_fake_new.checkObject(_description):
            return render_template('error.html',error = 'TRUE NEW')
        else:
             return render_template('error.html',error = 'FAKE NEW')
    except Exception as e:
        return render_template('error.html',error = str(e))
   
        # cursor.close()
        # conn.close()
if __name__ == '__main__':
    app.run(port=5002)
