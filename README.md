# Crypto Trading
#### Video Demo:  <URL HERE>
#### Description:
##### Warning:
This program uses a free API called CoinGecko and it is not always reliable, it has frequent issues in retrieving data from the source and this causes buggy, inconsistent and frustrating behaviour from the web server, so just be patient, it's not perfect and it will throw errors more than I like it to.

The purpose of this project is to simulate a platform which will allow people to trade with cryptocurrencies online (not real, of course) and it theoretically solves the problem of purchasing, selling and viewing cryptocurrencies online in a relatively safe environment. This website is hosted by Harvard CS50 as I developed it in their cloud-based VS code to make the final submission smooth.
##### Design:
I selected a unique, matrix-like theme as my design choice and I was really happy with the end result. I contemplated using a video or GIF image as my background, but it didn't look as authentic and alive.
##### How to use:
If you took the CS50 course, you'll know, however for anyone who didn't, all you need to do is (assuming you have a console/terminal window) open up the comand-line promp/terminal, go into the "project" directory by typing "cd project" and then type Flask run. This should generate a link that you can click on and take you to the web application. That's it, unless I missed something. In terms of downloading this, I don't know how that would benefit you or help you in any way, but I would feel better if you didn't download it :).
##### Functions:
I believe most of my functions in flask are self-explanatory, it would not make sense for me to explain every function in detail as this would just be a nuisance and waste unnecessary time, but there are enough comments throughout my code to explain what each function are doing for anyone wanting to read through it, to understand what is happening and how. Only the unusual ones will be explained in detail bewlow.

##### get_market_data:
First part:

The first line defines the URL endpoint that will be accessed to retrieve the data.
This specific endpoint is part of CoinGecko's API and is designed to return market data for various cryptocurrencies.

Second part:

currency_id: A unique identifier for each cryptocurrency.
name: The name of the cryptocurrency, such as “Bitcoin” or “Ethereum”.
symbol: The symbol used to represent the cryptocurrency, such as “BTC” or “ETH”.
current_price: The current price of the cryptocurrency in a specific fiat currency, such as USD or EUR.
market_cap: The total market capitalization of the cryptocurrency, which is the total value of all coins in circulation.
volume_24h: The total trading volume of the cryptocurrency in the past 24 hours.
change_24h: The percentage change in the price of the cryptocurrency over the past 24 hours.

Third part:

The requests.get(url, params=params) call sends a GET request to the specified URL with the given parameters.
response.raise_for_status() checks if the request was successful by examining the HTTP status code. If it's an error code (e.g., 404, 500), an exception will be raised.
response.json() converts the JSON response from the API into a Python data structure (usually a list of dictionaries) and returns it.
If any exception occurs (e.g., network issues, bad response), the function prints an error message and returns None.
The result of this function, when successful, is a Python data structure containing the market data for the specified cryptocurrencies.

##### class_User:
Below I will explain the class_User function:
The __init__ method is the constructor of the class, which is called when an instance of the class is created. It takes two arguments, id and username, and assigns them to the instance variables self.id and self.username, respectively.

The is_authenticated method returns a boolean value indicating whether the user is authenticated or not. In this case, it always returns True.

The is_active method returns a boolean value indicating whether the user is active or not. In this case, it always returns True.

The is_anonymous method returns a boolean value indicating whether the user is anonymous or not. In this case, it always returns False.

The get_id method returns the id of the user as a string.

These methods are commonly used in Flask-Login, a Flask extension that manages user authentication and session management in Flask applications. Flask-Login uses these methods to determine if a user is authenticated, active, anonymous, and to get the unique identifier of the user.
##### get_crypto_details:
Purpose:
The get_crypto_details function retrieves details about a given cryptocurrency, including its current price in USD, symbol, name, volume, and market capitalization, by making a request to the CoinGecko API.

Parameters:

crypto_name (str): This is the name of the cryptocurrency you want details about, for example, 'bitcoin' or 'ethereum'.
Return Value:

Returns a dictionary with the cryptocurrency's details if successful.
Returns None if there's any issue fetching the data or if the data doesn't exist.
Function Walkthrough:

URL Definition:

url = f"https://api.coingecko.com/api/v3/coins/{crypto_name}"
This line constructs the API URL by inserting the given cryptocurrency name into the CoinGecko endpoint.
API Request:

The function attempts to fetch the cryptocurrency details by sending a GET request to the above URL.
Error Handling:

If there's any error with the request or if the requested cryptocurrency isn't found on CoinGecko, exceptions will be raised and handled.
Data Extraction:

If the request is successful, the function extracts the necessary details from the response and constructs a dictionary containing the required details.
Detailed Step-by-Step Explanation:

response = requests.get(url)

The function uses the requests.get method to fetch data from the provided URL (CoinGecko API endpoint). The response is stored in the variable response.
response.raise_for_status()

This line checks if the request was successful. If the request resulted in an error (like a 404 or 500 HTTP status), it will raise an HTTPError exception.
data = response.json()

The function assumes the API returns data in JSON format, so it tries to parse the response into a Python dictionary using the .json() method.
Return dictionary:

symbol: Retrieves the symbol of the cryptocurrency and converts it to uppercase.
name: Retrieves the full name of the cryptocurrency.
price: Retrieves the current price of the cryptocurrency in USD.
volume: Retrieves the total volume of the cryptocurrency in USD.
market_cap: Retrieves the market capitalization of the cryptocurrency in USD.
Exception Handling:

a. requests.RequestException:

Catches exceptions raised by the requests library. If there's an error fetching data from the CoinGecko API, it prints an error message and returns None.
b. KeyError:

If the function tries to access a key in the data dictionary that doesn't exist (maybe because the structure of the API response changed or there was an unexpected response), a KeyError will be raised. This is caught by the function, an error message is printed, and None is returned.
Sample Usage:
Suppose you call the function with 'bitcoin' as an argument: get_crypto_details('bitcoin').

This function will contact the CoinGecko API and retrieve details for Bitcoin. If successful, you'll get a dictionary like:

json
Copy code
{
   "symbol": "BTC",
   "name": "Bitcoin",
   "price": 45000.00,
   "volume": 2000000000.00,
   "market_cap": 800000000000.00
}
If there's an issue, the function will print the error and return None
Note: Updated, Date: 2023/08/15, time: 19:07
Added a retries parameter, so the function will try the API call multiple times before giving up.
Introduced a delay to wait between retries.
The timeout is set to 10 seconds. You can adjust this based on the requirements.
A custom User-Agent header is set in the request.
With these enhancements, the function will be more robust against transient failures.

##### login_required:
Purpose:
This function acts as a decorator for Flask routes to ensure that a user is logged in before accessing certain routes or views.

Parameters:

f: The Flask route (or function) you wish to decorate.
Return Value:
Returns the decorated function, which checks if the user is logged in before proceeding.

Function Walkthrough:

@wraps(f):

This line uses the wraps decorator from the functools module. It ensures that the decorated function retains the metadata of the original function. In other words, the name, docstring, and other attributes of f will remain unchanged when it's decorated.
def decorated_function(*args, **kwargs):

This is the inner function which will replace the original function f when it's decorated.
if session.get("user_id") is None:

Here, the function checks if the "user_id" exists in the session. If it doesn't (i.e., None), this means the user is not logged in.
return redirect("/login"):

If the user isn't logged in, redirect them to the login page.
return f(*args, **kwargs):

If the user is logged in, continue with the execution of the original function f with any passed arguments or keyword arguments.
Sample Usage:
You'd use this decorator above any Flask route that you want to protect. For instance:

python
Copy code
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')
With the @login_required decorator in place, only logged-in users can access the 'dashboard' route. Otherwise, they will be redirected to the login page.

2. apology(message, code=400)
Purpose:
This function returns an apology message rendered in an HTML template, intended for situations where there's an error or an unexpected event in your Flask application.

Parameters:

message: The message you want to display to the user as an apology.
code=400: HTTP status code for the response. By default, it's set to 400, which stands for "Bad Request".
Return Value:
Returns a rendered template with the apology message and the provided HTTP status code.

Function Walkthrough:

def escape(s):

This is an inner function responsible for replacing special characters in a string with alternative representations.
For example, a space (' ') is replaced by a hyphen ('-').
for old, new in [...]: s = s.replace(old, new):

This loop iterates over a list of tuple pairs where the first item is the character to be replaced (old) and the second item is the character to replace with (new). The string s is updated in each iteration.
return render_template("apology.html", top=code, bottom=escape(message)), code:

Renders an HTML template named "apology.html". It passes two variables to the template:
top: The HTTP status code.
bottom: The escaped apology message.
The HTTP status code is also returned as part of the response.
Sample Usage:
You'd use this function to handle errors or unexpected situations in your Flask routes. For example:

python
Copy code
@app.route('/some_route')
def some_route():
    if some_error_condition:
        return apology("Something went wrong!", 500)
    return render_template('some_template.html')
In this hypothetical route, if some_error_condition is True, the user would receive an apology with the message "Something went wrong!" and an HTTP status code of 500.