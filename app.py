import os
import requests
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_login import LoginManager
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import time


#Configure application
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
#Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
#Loads user from data source
@login_manager.user_loader
def load_user(user_id):
    return db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]

#Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final_project.db")
#Fetch crypto price online
def get_crypto_details(crypto_name, retries=3, delay=2):
    """Retrieve the current price and other details of a cryptocurrency using CoinGecko API.

    Args:
        crypto_name (str): Name of the cryptocurrency (e.g., 'bitcoin', 'ethereum').
        retries (int): Number of retries if API call fails.
        delay (int): Delay in seconds between retries.

    Returns:
        dict: Details of the cryptocurrency or None if not found.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_name}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for _ in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Check if the request was successful

            data = response.json()
            return {
                "symbol": data['symbol'].upper(),
                "name": data['name'],
                "price": data['market_data']['current_price']['usd'],
                "volume": data['market_data']['total_volume']['usd'],
                "market_cap": data['market_data']['market_cap']['usd']
            }

        except requests.RequestException as e:
             print(f"Error fetching details for {crypto_name}. Error: {e}. Response: {response.text}")
             time.sleep(delay)
        except KeyError as e:
            print(f"KeyError: {e} when fetching details for {crypto_name}")
            return None

    # If after all retries, the function hasn't returned, return None
    return None

#Harvard CS50 functions:
#Credit goes to Harvard CS50 team for writing this function
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

#Credit goes to Harvard CS50 for writing this function
def apology(message, code=400):

    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                            ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


#Routes, functions and core functionality
#User class for Flask-Login
class User:
    """The is_authenticated, is_active, and is_anonymous methods are commonly used in Flask-Login,
    a Flask extension that manages user authentication and session management in Flask applications.
    Flask-Login uses these methods to determine if a user is authenticated, active, and anonymous."""
    def __init__(self, id):
        self.id = id
    #The is_authenticated method returns a boolean value indicating whether the user is authenticated or not.
    #In this case, it always returns True.
    def is_authenticated(self):
        return True
    #The is_active method returns a boolean value indicating whether the user is active or not.
    #In this case, it always returns True.
    #This method can be used to prevent banned or deactivated users from logging in by returning False for those users.
    def is_active(self):
        return True
    #The is_anonymous method returns a boolean value indicating whether the user is anonymous or not.
    #In this case, it always returns False.
    #When nobody is logged in, Flask-Login’s current_user is set to an AnonymousUser object, which responds to is_authenticated() and is_active() with False and to is_anonymous() with True.
    def is_anonymous(self):
        return False
    #This method returns the unique identifier of the user object as a string.
    #It does this by returning the value of the id instance variable, which was set when the user object was created, converted to a string using the str function.
    #Flask-Login uses this method to get the unique identifier of the user, which is used to load the user from the database and to manage the user session.
    def get_id(self):
        return str(self.id)
#Login
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    #indent
    #Forget user_id
    session.clear()
    #Prepare for login
    if request.method == "POST":
        #Step 1: Get user input
        #reading the data from the request object
        username = request.form.get("username")
        password = request.form.get("password")
        #Step 2: Validate input by ensuring the input is not blank or emppty
        if not username or not password:
            return apology("Username and password are required", 403)
        #Step 3: Varify user existence in database
        user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if not user:
            return apology("Invalid username or it doesn't exist", 403)
        #Step 4: Verify password
        #I will use the check_password_hash function to verify the user's password against the hashed password stored in the database
        if not check_password_hash(user[0]["password_hash"], password):
            return apology("Invalid password", 403)
        #Log user in
        #If the username and password are correct, I will log the user in by storing their user ID in the session
        session["user_id"] = user[0]["id"]
        session["username"] = username
        #Finally, we'll redirect the user to the homepage
        return redirect("/")
    else:
        return render_template("login.html")
#Logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    #Redirect user to login form
    return redirect("/")
#Register
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        #Retrieve user details
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        #Validate input from user and make sure it meets my criteria
        if not username or not password or not confirmation:
            return apology("All fields must be filled in, cannot be empty.", 400)
        #Make sure the password matches with the confirmation password entered by the user
        if password != confirmation:
            return apology("Passwords do not match.", 400)
        #Check if the user already exists in the database
        user = db.execute("SELECT username FROM users WHERE username = ?", username)
        #If a row is returned by the db.execute statement then the if statement will evaluate to true as it contains a username
        if user:
            return apology("User already exists.", 400)
        #Hash the password to make it secure
        hashed_password = generate_password_hash(password)
        #Update the record of this user in the database to reflect a new user's details have been added
        db.execute("INSERT INTO users (username, password_hash) VALUES (:username, :hashed_password)", username=username, hashed_password=hashed_password)
        #Redirect the user to login
        return redirect("/login")
    else:
        return render_template("register.html")

#Change password
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change password"""
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        # Strip the inputs
        current_password = current_password.strip()
        new_password = new_password.strip()
        confirmation = confirmation.strip()

        # Check if fields are None or only contain whitespace
        if not current_password or not new_password or not confirmation:
            return apology("All fields are required")

        if len(new_password) < 8:
            return apology("New password must be at least 8 characters")

        if new_password != confirmation:
            return apology("New password and confirmation do not match")

        # Retrieve user from the database
        user_id = session["user_id"]
        rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)

        if len(rows) != 1:
            return apology("User not found")

        user = rows[0]

        # Check if current password matches
        if not check_password_hash(user["password_hash"], current_password):
            return apology("Incorrect password")

        #Hash the new password and update the database
        new_password_hash = generate_password_hash(new_password)
        db.execute("UPDATE users SET password_hash = ? WHERE id = ?", new_password_hash, user_id)

        messages = flash("Your password has been changed successfully!")
        return render_template("index.html", messages=messages)
    else:
        return render_template("change_password.html")
#Home page
@app.route("/")
@login_required
def index():
    """Load portfolio"""
    #Check if there's an error message stored in the session
    error_message = session.pop("error_message", None)
    #Current user's id in this session
    user_id = session["user_id"]
    rows = db.execute("SELECT cryptocurrency, SUM(amount) as total_amount FROM transactions WHERE user_id = ? GROUP BY cryptocurrency HAVING total_amount > 0", user_id)
    #Extract crypto's from list of dictionaries (rows)
    owned_cryptos = []
    for row in rows:
        owned_cryptos.append(row["cryptocurrency"])

    #Fetching all crypto details at once
    crypto_details_cache = {crypto: get_crypto_details(crypto) for crypto in owned_cryptos}
    #Hold prices of all cryptos
    crypto_prices = {}
    for crypto, details in crypto_details_cache.items():
        if details is None:
            flash(f"Error occurred, details not found for {crypto}.")
            return redirect("/")
        crypto_prices[crypto] = details["price"]

    #Create new dictionary to store the total value of each crypto-currency
    crypto_list = []
    for row in rows:
        #Total number of cryptos per crypto currency type
        total_amount = row["total_amount"]
        #Crypto name
        crypto_name = row["cryptocurrency"]
        if crypto_name not in crypto_prices:
            return apology("Crypto name could not be found.", 400)
        #Price per crypto
        crypto_price = crypto_prices[crypto_name]
        #Crypto details to retrieve symbol
        crypto_details = crypto_details_cache.get(crypto_name)
        if not crypto_details:
            session["error_message"] = f"Error occured, details not found for {crypto_name}."
            return redirect("/")

        crypto_symbol = crypto_details["symbol"]
        total_value = total_amount * crypto_price

        crypto_list.append({"symbol": crypto_symbol,"name": crypto_name, "price": crypto_price, "amount": total_amount, "total": total_value})

    #Retrieve the cash balance of the current user
    cash = db.execute("SELECT cash FROM users WHERE id = ?",user_id)
    cash_balance = round(cash[0]["cash"])

    return render_template("index.html", cryptos=crypto_list, balance=cash_balance, error_message=error_message)

#History transactions of the user
@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    id = session["user_id"]
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ?",id)
    return render_template("history.html", transactions=transactions)

#Retrieve Cryptocurrency Data
def get_market_data():
    #This line defines the URL endpoint that will be accessed to fetch the data and is part of CoinGecko's API
    url = "https://api.coingecko.com/api/v3/coins/markets"
    #These parameters are used to customize the API request
    params = {
        "vs_currency": "usd", #The fiat currency to display prices in (USD in this case)
        "order": "market_cap_desc", #Sorting order of the cryptocurrencies (by market capitalization descending
        "per_page": 15,  # Number of cryptocurrencies you want to display
        "page": 1, #The page number
        "sparkline": False #Whether to include sparkline data (set to False as it's not needed here
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        print("Error fetching market data")
        return None

#Create the Market Route
@app.route("/market")
@login_required
def market():
    market_data = get_market_data()
    if market_data is None:
        return apology("Failed to fetch market data.")

    return render_template("market.html", market_data=market_data)

#Buy crypto
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        if "user_id" not in session:
            return redirect("/login")  # Redirect to login or another appropriate action
        #Retrieve the current user's id
        user_id = session["user_id"]
        #Validate the form data
        try:
            crypto_name = request.form.get("crypto_name").lower()
            amount = float(request.form.get("amount"))
        except ValueError:
            return apology("Invalid input")
        #Retrieve the user's balance from the database
        balance_dic = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_balance = balance_dic[0]["cash"]
        if user_balance is None:
            return apology("Error retrieving funds.", 400)
        #Get the current price of the crypto currency
        crypto_price_dic = get_crypto_details(crypto_name)
        if crypto_price_dic is None:
            return apology(f"Failed to fetch crypto price of {crypto_price_dic}. Data unavailable.", 404)
        crypto_price = crypto_price_dic["price"]
        #Calculate the total
        total_cost = crypto_price * amount
        if total_cost > user_balance:
            return apology("Insufficient funds", 400)
        #Update user balance
        new_balance = user_balance - total_cost
        db.execute("UPDATE users SET cash = ? WHERE id = ?",new_balance, user_id)
        #Log the new transaction
        db.execute("INSERT INTO transactions (user_id, transaction_type, cryptocurrency, amount, price) VALUES (?, ?, ?, ?, ?)", user_id, "purchased", crypto_name, amount, crypto_price)
        #Notify the user that the purchase has happened
        messages = flash("Bought successfully!")
        return redirect("/")
    else:
        return render_template("buy.html")

#Sell crypto
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    #indent
    if request.method == "POST":
        #Retrieve input
        crypto_name = request.form.get("crypto_name")
        amount = float(request.form.get("amount"))
        #Validate this input
        if not crypto_name or not amount or amount <= 0:
            return apology("Invalid input", 400)
        #Check if the user owns enough of the cryptocurrency
        id = session["user_id"]
        owned_cryptos = db.execute("SELECT SUM(amount) as total_amount FROM transactions WHERE user_id = ? AND cryptocurrency = ? GROUP BY cryptocurrency", id, crypto_name )
        if len(owned_cryptos) == 0 or owned_cryptos[0]["total_amount"] <= 0:
            return apology("You don't own any cryptos of this currency.")

        owned_crypto = owned_cryptos[0]["total_amount"]
        #If the user has enough to sell, record the transaction
        if owned_crypto >= amount:
            #Fetch the current price of the crypto
            crypto_details = get_crypto_details(crypto_name)
            if not crypto_details:
                return apology("Error fetching current price. Try again later.", 400)
            price = crypto_details["price"]
            #Calculate total
            total_price = price * amount
            #Fetch current cash balance
            row = db.execute("SELECT cash FROM users WHERE id = ?", id)
            #Extract the cash
            cash_balance = row[0]["cash"]
            #Calculate new balance
            new_balance = cash_balance + total_price
            #Update database wih new cash balance
            username = session.get("username")
            db.execute("UPDATE users SET cash = ? WHERE id = ? AND username = ?",new_balance, id, username)

            #Record the transaction in the database
            db.execute("INSERT INTO transactions (user_id, transaction_type, cryptocurrency, amount, price) VALUES (?, ?, ?, ?, ?)", id, "sold", crypto_name, -int(amount), price)
            #Flash a success message and redirect to a different route (e.g., index or history)
            flash(f"Sold {amount} of {crypto_name} successfully!")
        else:
            return apology("Not enough cryptocurrency to sell", 400)
        return redirect("/")
    else:
        #Retrieve and acquire id
        id = session["user_id"]
        #Retrieve list of crypto currencies owned by this user
        symbols_list = db.execute("SELECT DISTINCT cryptocurrency FROM transactions WHERE user_id = ?", id)
        cryptos = []
        #Extract the cryptocurrencies from the returned rows
        for crypto in symbols_list:
            cryptos.append(crypto["cryptocurrency"])
        #Render the sell template, passing in the list of symbols
        return render_template("sell.html", cryptos=cryptos)

#Get quote
@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        crypto_name = request.form.get("crypto_name")
        if not crypto_name or crypto_name is None:
            return apology("Field can not be empty, enter the name of the crypto.", 400)
        #Look it up to get details
        quote = get_crypto_details(crypto_name)
        if quote is None:
            return apology("Invalid crypto entered/does not exist.", 400)
        return render_template("quote.html", quote=quote)
    else:
        return render_template("quote.html")

@app.route("/profile", methods =["GET","POST"])
@login_required
def profile():
    """ Load User profile """
    if request.method == "POST":
        id = session["user_id"]
        #Retrieve input
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        #Validation for all inputs
        if not name:
            return apology("Name can not be empty.", 400)
        if not email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return apology("Email can not be empty.", 400)
        if not phone and not re.match(r"^\d{10}$", phone):
            return apology("Phone number can not be empty.", 400)
        #Check if all fields are unique
        existing_name = db.execute("SELECT 1 FROM users WHERE name = ? AND id != ?", name, id)
        if existing_name:
            return apology("Name already taken.", 400)

        existing_email = db.execute("SELECT 1 FROM users WHERE email = ? AND id != ?", email, id)
        if existing_email:
            return apology("Email already exists.", 400)

        existing_number = db.execute("SELECT 1 FROM users WHERE phone = ? AND id != ?", phone, id)
        if existing_number:
            return apology("Number already exists.", 400)

        db.execute("UPDATE users SET name = ?, email = ?, phone = ? WHERE id = ?", name, email, phone, id)
        flash("Profile updated successfully.")

        return redirect("/")

    else:
        id = session["user_id"]
        user_details = db.execute("SELECT name, email, phone FROM users WHERE id = ?", id)
        user = user_details[0]

        return render_template("profile.html", user=user)
