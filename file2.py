from flask import Flask, render_template, url_for, request, redirect, session
from bs4 import BeautifulSoup
import requests
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

#start authentication
app.secret_key = 'manu456'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pythonlogin'

# Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()

        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return render_template('index.html', sucmsg='sucess')
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    return render_template('login.html', msg='')




# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


#authentication end



#admin
@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        adminacc = cursor.fetchone()


        # If account exists in accounts table in out database
        if adminacc:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = adminacc['admin_id']
            session['username'] = adminacc['username']
            logintime = adminacc['logintime']
            number_of_users = cursor.execute("SELECT * FROM accounts")
            details = {
                'sucmsg': 'sucess',
                'no_of_users': number_of_users,
                'logindtime':logintime
            }


            return render_template('adninpanel.html', det=details)
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    return render_template('login.html', msg='')




    # db = MySQLdb.connect("localhost", "root", "", "pythonlogin")
    # cursor = db.cursor()
    # number_of_users = cursor.execute("SELECT * FROM accounts")
    # return render_template('admin.html', total_users=number_of_users)



@app.route('/', methods=['POST', 'GET'])
def homepage():
   return shops()

def shops():
    if request.method == 'POST':
        searchterm = request.form['searchterm']
        minprice = int(request.form['minprice'])
        maxprice = int(request.form['maxprice'])
        # cutomer_input = 1000
#jumia
        url = "https://www.jumia.co.ke/catalog/?q={0}".format(searchterm)
        html_text = requests.get(url).text.encode()
        soup = BeautifulSoup(html_text, 'lxml')
        items = soup.find_all('article', class_="prd _fb col c-prd")

        listofdetails = []
        suggestions_a = []
        for item in items:
            product_name = item.find('h3', class_='name').text
            price = item.find('div', class_='prc').text
            nlist = item.find('a', class_='core')
            imagediv = nlist.find('div', class_='img-c')
            image_url = imagediv.find('img', class_='img')
            price_in_numbers = ''.join(filter(lambda i: i.isdigit(), price))
            striped_price = int(price_in_numbers)
            if striped_price>= minprice:
                if striped_price<= maxprice:
                    suggested_from_jumia = {
                        'href': nlist['href'],
                        'name': product_name,
                        'price': price,
                        'imageurl': image_url['data-src']
                    }
                    suggestions_a.append(suggested_from_jumia);



            itemdetails = {
                'href': nlist['href'],
                'name': product_name,
                'price': price,
                'imageurl': image_url['data-src']

            }
            listofdetails.append(itemdetails)

#jamboshop
        url2 = "https://www.jamboshop.com/search?k={0}".format(searchterm)
        html_text2 = requests.get(url2).text.encode()
        soup2 = BeautifulSoup(html_text2, 'lxml')
        items2 = soup2.find_all('div', class_="col-xs-6 col-sm-4 col-md-4 col-lg-3")

        listofdetails2 = []
        for item2 in items2:
            product_name2 = item2.find('h6', class_='prd-title').text
            price2 = item2.find('span', class_='offer-price').text
            linklist2 = item2.find('a', class_='thumbnail')
            image_list2 = linklist2.find('img', class_='img-responsive')
            itemdetails2 = {
                'name': product_name2,
                'price': price2,
                'imageurl': image_list2['data-image'],
                'href': linklist2['href']

            }
            listofdetails2.append(itemdetails2)
#shopit
        url4 = "https://shopit.co.ke/?match=all&subcats=Y&pcode_from_q=Y&pshort=Y&pfull=Y&pname=Y&pkeywords=Y&search_performed=Y&q={0}".format(searchterm)+"&dispatch=products.search&security_hash=9724314b5a15c02cc34f9a7cddf915b3"
        html_text4 = requests.get(url4).text.encode()
        soup4 = BeautifulSoup(html_text4, 'lxml')
        items4 = soup4.find_all('div', class_="ut2-gl__body")


        listofdetails4 = []
        for item4 in items4:
            product_name4 = item4.find('div', class_="ut2-gl__name").text
            pricedivs1 = item4.find('div', class_="ut2-gl__price")
            pricedivs2 = pricedivs1.find('div')
            price4 = pricedivs2.find('bdi').text
            imageholdingdiv = item4.find('div', class_='ut2-gl__image')
            linklist4 = imageholdingdiv.find('a')
            image_list4 = linklist4.find('img')
            itemdetails4 = {
                'name': product_name4,
                'price': price4,
                'imageurl': image_list4['src'],
                'href': linklist4['href']

            }
            listofdetails4.append(itemdetails4)


        return render_template('searchresults.html', links=[listofdetails, listofdetails2, listofdetails4, suggestions_a])

    else:
        return render_template('index.html')





@app.route('/searchresults')
def searchresults():
    return render_template('searchresults.html', search_term='empty')


if __name__ == "__main__":
    app.run(debug=True)
