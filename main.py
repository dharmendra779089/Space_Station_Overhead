import requests          # Imports the requests library to make HTTP API calls
from datetime import datetime  # Imports datetime to fetch and manage current time data
import smtplib           # Imports smtplib to establish connection and send emails
import time              # Imports time to create delays/intervals in execution

# Configuration Constants
MY_EMAIL = "___YOUR_EMAIL_HERE____"       # Placeholder for your sending email address
MY_PASSWORD = "___YOUR_PASSWORD_HERE___"   # Placeholder for your app-specific email password
MY_LAT = 28.535517                         # Your specific geographic latitude (Noida, India)
MY_LONG = 77.391029                        # Your specific geographic longitude (Noida, India)


def is_iss_overhead():
    """Fetches current ISS coordinates and checks if it is close to the user's location."""
    # Sends a GET request to the Open Notify API for real-time ISS positioning data
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()            # Triggers an exception if the HTTP request returned an error status
    data = response.json()                 # Parses the raw JSON response payload into a Python dictionary

    # Extract the latitude and longitude strings from nested dict keys and convert them to floats
    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])

    # Checks if the ISS coordinates fall within a +/- 5 degree margin of error from your location
    if MY_LAT-5 <= iss_latitude <= MY_LAT+5 and MY_LONG-5 <= iss_longitude <= MY_LONG+5:
        return True                        # Returns True if the ISS is close enough to be considered overhead


def is_night():
    """Fetches local sunrise/sunset windows to verify if the sky is currently dark."""
    # Define query parameters required by the sunrise-sunset API
    parameters = {
        "lat": MY_LAT,         # Pass the user's base latitude
        "lng": MY_LONG,        # Pass the user's base longitude
        "formatted": 0,        # Requests unformatted, raw UTC ISO 8601 strings back
    }
    # Sends a GET request to the API with our location parameter dictionary attached
    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()            # Triggers an exception if the HTTP network request failed
    data = response.json()                 # Parses the returned JSON string into a structured dictionary
    
    # Splits the ISO timestamp string to isolate the hour portion as an integer for sunrise (UTC)
    sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    # Splits the ISO timestamp string to isolate the hour portion as an integer for sunset (UTC)
    sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

    time_now = datetime.now().hour         # Captures the current hour component of the machine's local clock

    # Determines dark hours: if current hour is past sunset OR before sunrise, it's night
    if time_now >= sunset or time_now <= sunrise:
        return True                        # Returns True confirming conditions are dark enough to view the ISS


# Main Execution Loop
while True:                                # Establishes an infinite loop to run the checking service continuously
    time.sleep(60)                         # Pauses code execution for 60 seconds between API poll requests
    
    # Combined Conditional: Code will only execute inner email block if BOTH helper functions return True
    if is_iss_overhead() and is_night():
        # Initializes an SMTP object mapping to your target mail server address
        connection = smtplib.SMTP("__YOUR_SMTP_ADDRESS_HERE___")
        connection.starttls()              # Secures and encrypts the connection stream via TLS
        connection.login(MY_EMAIL, MY_PASSWORD)  # Authenticates with the mail provider using the configured constants
        
        # Fires the email notification alert containing subject headers and message body
        connection.sendmail(
            from_addr=MY_EMAIL,            # Sender address
            to_addrs=MY_EMAIL,             # Recipient address (sent to self)
            msg="Subject:Look Up👆\n\nThe ISS is above you in the sky." # Encoded email message
        )
