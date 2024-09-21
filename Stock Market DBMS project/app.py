from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, login_user, logout_user, LoginManager, login_required, current_user
from datetime import datetime
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.config['SECRET_KEY'] = 'stockproject'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'stock_market_db'

mysql = MySQL(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, firstname, email, password):
        self.id = id
        self.firstname = firstname
        self.email = email
        self.password = password

    def get_id(self):
        return str(self.id)

class BUser(UserMixin):
    def __init__(self, b_id, b_firstname, b_email, b_password):
        self.b_id = b_id
        self.b_firstname = b_firstname
        self.b_email = b_email
        self.b_password = b_password
    
    def get_id(self):
        return str(self.b_id)


@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM loginpage WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    if user:
        return User(user['id'], user['firstname'], user['email'], user['password'])
    
    cursor.execute('SELECT * FROM brokerlogin WHERE b_id = %s', (user_id,))
    b_user = cursor.fetchone()
    if b_user:
        return BUser(b_user['b_id'], b_user['b_firstname'], b_user['b_email'], b_user['b_password'])
        
    return None

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/back')
def back():
    return redirect(url_for('index'))

@app.route('/back1')
def back1():
    return redirect(url_for('stocks_index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        secondname = request.form.get('secondname')
        gender = request.form.get('gender')
        age = request.form.get('age')
        occupation = request.form.get('occupation')
        city = request.form.get('city')
        mobilenumber = request.form.get('mobilenumber')
        email = request.form.get('email')
        password = request.form.get('password')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account_details WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user:
            flash("Email already exists", "warning")
            return redirect(url_for('signup'))

        cursor.execute('INSERT INTO account_details (firstname, secondname, gender, mobilenumber, email, password, total_balance_amount, age, occupation, city) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                       (firstname, secondname, gender, mobilenumber, email, password, 0, age, occupation, city))
        mysql.connection.commit()
        flash("Signup successful, please login", "success")
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM loginpage WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user and user['email'] == email and user['password'] == password:
            login_user(User(user['id'], user['firstname'], user['email'], user['password']))
            update_stock_prices_and_profits1()
            return redirect(url_for('stocks_index'))
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for('login'))    
    return render_template('login.html')


@app.route('/stocks_index1')
def stocks_index1():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT stock_id, stock_name, stock_price, today_gain FROM stock_details')
    stocks = cursor.fetchall()
    return render_template('base1.html', stocks=stocks)


@app.route('/stocks_index')
@login_required
def stocks_index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT firstname FROM account_details WHERE id=%s',(current_user.id,))
    user=cursor.fetchone()
    cursor.execute('SELECT stock_id, stock_name, stock_price, today_gain FROM stock_details')
    stocks = cursor.fetchall()
    return render_template('base.html',user=user ,stocks=stocks)

@app.route('/stock_details/<int:stock_id>')
@login_required
def stock_details(stock_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM stock_details WHERE stock_id = %s', (stock_id,))
    stock = cursor.fetchone()
    return render_template('stock_details.html', stock=stock)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        firstname = request.form['firstname']
        secondname = request.form['secondname']
        gender = request.form['gender']
        mobilenumber = request.form['mobilenumber']
        email = request.form['email']
        age = request.form['age']
        occupation = request.form['occupation']
        city = request.form['city']
        
        cursor.execute('''UPDATE account_details 
                          SET firstname=%s, secondname=%s, gender=%s, mobilenumber=%s, email=%s, age=%s, occupation=%s, city=%s 
                          WHERE id=%s''', 
                          (firstname, secondname, gender, mobilenumber, email, age, occupation, city, current_user.id))
        mysql.connection.commit()
        flash('Account Edited Successfully', 'success')

    cursor.execute('SELECT * FROM account_details WHERE id = %s', (current_user.id,))
    account = cursor.fetchone()
    return render_template('account.html', account=account)


@app.route('/buy/<int:stock_id>', methods=['POST', 'GET'])
@login_required
def buy(stock_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT stock_id, stock_name, stock_price, today_gain FROM stock_details WHERE stock_id = %s', (stock_id,))
    stock = cursor.fetchone()
    
    if request.method == 'POST':
        quantity = request.form.get('quantity')
        if not quantity or not quantity.isdigit():
            flash("Invalid quantity", "danger")
            return redirect(url_for('buy', stock_id=stock_id))

        quantity = int(quantity)
        amount = stock['stock_price'] * quantity

        cursor.execute('SELECT total_balance_amount FROM account_details WHERE id = %s', (current_user.id,))
        account = cursor.fetchone()

        if account and account['total_balance_amount'] >= amount:
            new_balance = account['total_balance_amount'] - amount
            cursor.execute('UPDATE account_details SET total_balance_amount = %s WHERE id = %s', (new_balance, current_user.id))

            cursor.execute('SELECT quantities FROM holdings WHERE id = %s AND stock_id = %s', (current_user.id, stock_id))
            holding = cursor.fetchone()

            if not holding:
                cursor.execute('INSERT INTO holdings (id, stock_id, stock_name, quantities, buy_date, buy_price, total_profit) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (current_user.id, stock_id, stock['stock_name'], quantity, datetime.now(), stock['stock_price'], 0))
            else:
                new_quantity = holding['quantities'] + quantity
                cursor.execute('UPDATE holdings SET quantities = %s WHERE stock_id = %s AND id = %s', (new_quantity, stock_id, current_user.id))
            mysql.connection.commit()
            flash("Purchase successful", "success")
            update_stock_prices_and_profits()
        else:
            flash("Insufficient balance", "error")
    cursor.execute('SELECT total_balance_amount FROM account_details WHERE id = %s', (current_user.id,))
    user=cursor.fetchone()
    return render_template('buy.html', stock=stock,user=user)

@app.route('/sell/<int:stock_id>', methods=['POST', 'GET'])
@login_required
def sell(stock_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT stock_id, stock_name, stock_price, today_gain FROM stock_details WHERE stock_id = %s', (stock_id,))
    stock = cursor.fetchone()

    if request.method == 'POST':
        quantity = request.form.get('quantity')
        if not quantity or not quantity.isdigit():
            flash("Invalid quantity", "danger")
            return redirect(url_for('sell', stock_id=stock_id))

        quantity = int(quantity)
        amount = stock['stock_price'] * quantity

        cursor.execute('SELECT quantities FROM holdings WHERE id = %s AND stock_id = %s', (current_user.id, stock_id))
        holding = cursor.fetchone()

        if holding and holding['quantities'] >= quantity:
            new_quantity = holding['quantities'] - quantity
            if new_quantity == 0:
                cursor.execute('DELETE FROM holdings WHERE id = %s AND stock_id = %s', (current_user.id, stock_id))
            else:
                cursor.execute('UPDATE holdings SET quantities = %s WHERE id = %s AND stock_id = %s', (new_quantity, current_user.id, stock_id))

            cursor.execute('SELECT total_balance_amount FROM account_details WHERE id = %s', (current_user.id,))
            account = cursor.fetchone()
            new_balance = account['total_balance_amount'] + amount
            cursor.execute('UPDATE account_details SET total_balance_amount = %s WHERE id = %s', (new_balance, current_user.id))
            cursor.execute(
                'INSERT INTO trading_history (t_type, id, stock_id, stock_name, quantities, sell_date, sell_price) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                ('SELL', current_user.id, stock_id, stock['stock_name'], quantity, datetime.now(), stock['stock_price'])
            )
            mysql.connection.commit()
            flash("Sale successful", "success")
            update_stock_prices_and_profits()
        else:
            flash("Insufficient stock quantity", "error")

    cursor.execute('SELECT quantities FROM holdings WHERE id = %s and stock_id=%s', (current_user.id,stock_id))
    user = cursor.fetchone()
    return render_template('sell.html', stock=stock, user=user)


def update_stock_prices_and_profits():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    
    cursor.execute('SELECT * FROM stock_details')
    prices = cursor.fetchall()
    for price in prices:
        old_price = price['stock_price']
        if price['stock_id'] % 4 == 0:
            new_price = old_price - 1.25
        elif price['stock_id'] % 3 == 0:
            new_price = old_price + 2.25
        elif price['stock_id'] % 2 == 0:
            new_price = old_price + 1.75
        else:
            new_price = old_price + 1  

        today_gain = new_price - old_price
        cursor.execute(
            'UPDATE stock_details SET stock_price = %s, today_gain = %s WHERE stock_id = %s',
            (new_price, today_gain, price['stock_id'])
        )
    cursor.execute('SELECT * FROM holdings')
    holdings = cursor.fetchall()
    for hold in holdings:
        cursor.execute('SELECT stock_price FROM stock_details WHERE stock_id = %s', (hold['stock_id'],))
        current_price = cursor.fetchone()['stock_price']
        total_gain = (current_price - hold['buy_price']) * hold['quantities']
        cursor.execute(
            'UPDATE holdings SET total_profit = %s WHERE stock_id = %s AND id = %s',
            (total_gain, hold['stock_id'], hold['id'])
        )
    mysql.connection.commit()


def update_stock_prices_and_profits1():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    
    cursor.execute('SELECT * FROM stock_details')
    prices = cursor.fetchall()
    for price in prices:
        old_price = price['stock_price']
        if price['stock_id'] % 4 == 0:
            new_price = old_price + 2.25
        elif price['stock_id'] % 3 == 0:
            new_price = old_price - 0.75
        elif price['stock_id'] % 2 == 0:
            new_price = old_price + 1.25
        else:
            new_price = old_price - 1.5  

        today_gain = new_price - old_price
        cursor.execute('UPDATE stock_details SET stock_price = %s, today_gain = %s WHERE stock_id = %s',(new_price, today_gain, price['stock_id']))
    cursor.execute('SELECT * FROM holdings')
    holdings = cursor.fetchall()
    for hold in holdings:
        cursor.execute('SELECT stock_price FROM stock_details WHERE stock_id = %s', (hold['stock_id'],))
        current_price = cursor.fetchone()['stock_price']
        total_gain = (current_price - hold['buy_price']) * hold['quantities']
        cursor.execute('UPDATE holdings SET total_profit = %s WHERE stock_id = %s AND id = %s',(total_gain, hold['stock_id'], hold['id']))
    mysql.connection.commit()

def update_stock_prices_and_profits2():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    
    cursor.execute('SELECT * FROM stock_details')
    prices = cursor.fetchall()
    for price in prices:
        old_price = price['stock_price']
        if price['stock_id'] % 4 == 0:
            new_price = old_price - 1.5
        elif price['stock_id'] % 3 == 0:
            new_price = old_price + 1.75
        elif price['stock_id'] % 2 == 0:
            new_price = old_price - 0.5
        else:
            new_price = old_price + 2.25  

        today_gain = new_price - old_price
        cursor.execute(
            'UPDATE stock_details SET stock_price = %s, today_gain = %s WHERE stock_id = %s',
            (new_price, today_gain, price['stock_id'])
        )
    cursor.execute('SELECT * FROM holdings')
    holdings = cursor.fetchall()
    for hold in holdings:
        cursor.execute('SELECT stock_price FROM stock_details WHERE stock_id = %s', (hold['stock_id'],))
        current_price = cursor.fetchone()['stock_price']
        total_gain = (current_price - hold['buy_price']) * hold['quantities']
        cursor.execute('UPDATE holdings SET total_profit = %s WHERE stock_id = %s AND id = %s',(total_gain, hold['stock_id'], hold['id']))
    mysql.connection.commit()


@app.route('/holdings')
@login_required
def holdings():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT h.*, s.stock_price FROM holdings h JOIN stock_details s ON h.stock_id = s.stock_id WHERE h.id = %s', (current_user.id,))
    holdings = cursor.fetchall()
    return render_template('holdings.html', holdings=holdings)


@app.route('/trading')
@login_required
def trading():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM trading_history WHERE id = %s', (current_user.id,))
    tradings = cursor.fetchall()
    return render_template('trading.html', tradings=tradings)


@app.route('/transactions')
@login_required
def transactions():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM fund_transaction WHERE id = %s', (current_user.id,))
    transactions = cursor.fetchall()
    cursor_balance = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor_balance.execute('SELECT total_balance_amount FROM account_details WHERE id=%s', (current_user.id,))
    user = cursor_balance.fetchone()
    return render_template('transactions.html', transactions=transactions, user=user)


from datetime import datetime

@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount'))
            card_number = request.form.get('card_number')
            expiry_month = request.form.get('expiry_month')
            expiry_year = request.form.get('expiry_year')
            cvv = request.form.get('cvv')
            
            expiry_date = datetime.strptime(f'{expiry_year}-{expiry_month}-01', '%Y-%m-%d').date()

            cursor.execute(
                'INSERT INTO bank_details (id, amount, card_number, expiry_date, cvv, date) VALUES (%s, %s, %s, %s, %s, %s)',
                (current_user.id, amount, card_number, expiry_date, cvv, datetime.now())
            )
            cursor.execute('SELECT total_balance_amount FROM account_details WHERE id = %s', (current_user.id,))
            account = cursor.fetchone()
            new_balance = account['total_balance_amount'] + amount

            cursor.execute('UPDATE account_details SET total_balance_amount = %s WHERE id = %s', (new_balance, current_user.id))

            mysql.connection.commit()
            flash("Funds Added Successfully", "success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error: {str(e)}", "error")
        finally:
            cursor.close()

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT total_balance_amount FROM account_details WHERE id = %s', (current_user.id,))
    user = cursor.fetchone()
    cursor.close()
    return render_template('deposit.html', user=user)


@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount'))

            cursor.execute('SELECT * FROM account_details WHERE id = %s', (current_user.id,))
            account = cursor.fetchone()

            if account and account['total_balance_amount'] >= amount:
                new_balance = account['total_balance_amount'] - amount
                cursor.execute('UPDATE account_details SET total_balance_amount = %s WHERE id = %s', (new_balance, current_user.id))
                cursor.execute('INSERT INTO fund_transaction (id, type, date, amount) VALUES (%s, %s, %s, %s)',
                               (current_user.id, 'WITHDRAW', datetime.now(), amount))

                mysql.connection.commit()
                flash("Withdraw Successful", "success")
            else:
                flash("Insufficient balance", "error")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error: {str(e)}", "error")
        finally:
            cursor.close()

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT total_balance_amount FROM account_details WHERE id = %s', (current_user.id,))
    user = cursor.fetchone()
    cursor.close()
    return render_template('withdraw.html', user=user)


@app.route('/brokerlogin', methods=['POST', 'GET'])
def brokerlogin():
    if request.method == 'POST':
        email = request.form.get('b_email')
        password = request.form.get('b_password')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM brokerlogin WHERE b_email = %s', (email,))
        user = cursor.fetchone()

        if user and user['b_email'] == email and user['b_password'] == password:
            login_user(BUser(user['b_id'], user['b_firstname'], user['b_email'], user['b_password']))
            return redirect(url_for('edit_page'))
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for('brokerlogin'))
    return render_template('blogin.html')



@app.route('/add_stock', methods=['GET', 'POST'])
@login_required
def add_stock():
    if request.method == 'POST':
        stock_id=int(request.form['stock_id'])
        stock_name = request.form['stock_name']
        stock_price = float(request.form['stock_price'])
        today_gain = float(request.form['today_gain'])
        one_year_lowprice = float(request.form['one_year_lowprice']) if request.form['one_year_lowprice'] else None
        one_year_highprice = float(request.form['one_year_highprice']) if request.form['one_year_highprice'] else None
        ceo_name = request.form['ceo_name']
        founded = int(request.form['founded']) if request.form['founded'] else None
        industry = request.form['industry']
        headquarters=request.form['headquarters']
        market_cap = int(request.form['market_cap'])
        current_year_profit = int(request.form['current_year_profit'])

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO stock_details (stock_id,stock_name, stock_price, today_gain, one_year_lowprice, one_year_highprice, ceo_name, founded, industry, market_cap, current_year_profit,headquarters) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)',
                       (stock_id,stock_name, stock_price, today_gain, one_year_lowprice, one_year_highprice, ceo_name, founded, industry, market_cap, current_year_profit,headquarters))
        mysql.connection.commit()

        flash('Stock added successfully', 'success')
        return redirect(url_for('add_stock'))  
    return render_template('addstock.html')

@app.route('/edit_page')
@login_required
def edit_page():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT stock_id, stock_name, stock_price, today_gain FROM stock_details')
    stocks = cursor.fetchall()
    return render_template('edit.html', stocks=stocks)


@app.route('/edit_stock/<int:stock_id>', methods=['GET', 'POST'])
@login_required
def edit_stock(stock_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'POST':
        stock_id = request.form['stock_id']
        stock_name = request.form['stock_name']
        stock_price = request.form['stock_price']
        today_gain = request.form['today_gain']
        one_year_lowprice = request.form['one_year_lowprice']
        one_year_highprice = request.form['one_year_highprice']
        ceo_name = request.form['ceo_name']
        founded = request.form['founded']
        industry = request.form['industry']
        headquarters = request.form['headquarters']
        market_cap = request.form['market_cap']
        current_year_profit = request.form['current_year_profit']

        cursor.execute('''UPDATE stock_details 
                          SET stock_name=%s, stock_price=%s, today_gain=%s, one_year_lowprice=%s, one_year_highprice=%s, ceo_name=%s, founded=%s, industry=%s, headquarters=%s, market_cap=%s, current_year_profit=%s 
                          WHERE stock_id=%s''',
                          (stock_name, stock_price, today_gain, one_year_lowprice, one_year_highprice, ceo_name, founded, industry, headquarters, market_cap, current_year_profit, stock_id))
        
        mysql.connection.commit()
        flash('Stock details updated successfully!', 'success')
        return redirect(url_for('edit_stock', stock_id=stock_id))
    
    cursor.execute('SELECT * FROM stock_details WHERE stock_id = %s', (stock_id,))
    stock = cursor.fetchone()
    
    return render_template('editpage.html', stock=stock)

@app.route('/Trades')
@login_required
def Trades():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM trading_history')
    tradings = cursor.fetchall()
    return render_template('trades.html',tradings=tradings)

@app.route('/overview')
@login_required
def overview():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM account_details')
    cus = cursor.fetchall()
    return render_template('cus_overview.html',cus=cus)

@app.route('/logout')
@login_required
def logout():
    update_stock_prices_and_profits2()
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

