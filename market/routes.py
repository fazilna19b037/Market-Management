from flask_mysqldb import MySQL
#from market import app
from flask import render_template, redirect, url_for, flash, request, session
#from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from market import mysql,app,bcrypt
#from flask_login import login_user, logout_user, login_required, current_user
import MySQLdb.cursors
#mycursor=mydb.cursor()


@app.route('/')
@app.route('/home')
def home_page():
    session['loggedin']=False
    return render_template('home.html')

@app.route('/market', methods=['GET', 'POST'])
#@login_required
def market_page():
    #return render_template('market.html')
    #print('session',session['_fresh'])
    if session['loggedin']==False:
        flash('Please login to continue',category='danger')
        return render_template('home.html')
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    if request.method == "POST":
        #Purchase Item Logic
        purchased_item = request.form.get('purchased_item')
        print("pitem",purchased_item)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM item WHERE name=%s",(purchased_item,))
        p_item_object=cursor.fetchone()
        #p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if session['budget']>=p_item_object['price']:
                session['budget']-=p_item_object['price']
                cursor.execute("UPDATE item SET owner=%s WHERE name=%s",(session['id'],purchased_item,))
                cursor.execute(f"UPDATE user SET budget={session['budget']} WHERE id={session['id']}")
                mysql.connection.commit()
                flash(f"Congratulations! You purchased {p_item_object['name']} for {p_item_object['price']}$", category='success')
            else:
                flash(f"Unfortunately, you don't have enough money to purchase {p_item_object['name']}!", category='danger')
        #Sell Item Logic
        sold_item = request.form.get('sold_item')
        cursor.execute("SELECT * FROM item WHERE name=%s",(sold_item,))
        s_item_object = cursor.fetchone()
        if s_item_object:
            if s_item_object['owner']==session['id']:
                session['budget']+=s_item_object['price']
                cursor.execute(f"UPDATE item SET owner=0 WHERE name={s_item_object['name']}")
                cursor.execute(f"UPDATE user SET budget={session['budget']} WHERE id={session['id']}")
                mysql.connection.commit()
                flash(f"Congratulations! You sold {s_item_object['name']} back to market!", category='success')
            else:
                flash(f"Something went wrong with selling {s_item_object['name']}", category='danger')


        return redirect(url_for('market_page'))

    if request.method == "GET":
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT * FROM item WHERE owner!={session["id"]}')
        items = cursor.fetchall()
        cursor.execute(f'SELECT * FROM item WHERE owner={session["id"]}')
        owned_items = cursor.fetchall()
        cursor.execute(f'SELECT * FROM user WHERE id={session["id"]}')
        budget=cursor.fetchone()['budget']
        return render_template('market.html',budget=budget, items=items, purchase_form=purchase_form, owned_items=owned_items, selling_form=selling_form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password1']).decode('utf-8')
        email = request.form['email_address']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE user_name = % s', (username, ))
        account = cursor.fetchone()
        if account:
            flash("Account already exists with same username",category='danger')
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s, 1000)', (username, email,password))
            mysql.connection.commit()
            cursor.execute('SELECT * FROM user WHERE user_name = % s', (username,))
            account = cursor.fetchone()
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['user_name']
            session['budget']=account['budget']
            flash(f"Account created successfully! You are now logged in as {account['user_name']}", category='success')
            return redirect(url_for('market_page'))
        '''user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('market_page'))'''
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        username=request.form['username']
        #password=bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        password=request.form['password']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE user_name=%s',(username,))
        #cursor.execute('SELECT * FROM user WHERE user_name=%s AND password_hash=%s',(username,password))
        account=cursor.fetchone()
        if account and bcrypt.check_password_hash(account['password_hash'], password):
        #if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['user_name']
            session['budget']=account['budget']
            flash(f'Success! You are logged in as: {account["user_name"]}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')
    return render_template('login.html',form=form)

    '''form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)'''

@app.route('/logout')
def logout_page():
    session.pop('loggedin',None)
    session.pop('id', None)
    session.pop('username', None)
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))










