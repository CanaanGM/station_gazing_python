from typing import Tuple
import requests, os
import datetime as dt
from dotenv import load_dotenv

load_dotenv()
LOCAL_LNG =float(os.environ.get("LOCAL_LNG", 0))
LOCAL_LAT =float(os.environ.get("LOCAL_LAT", 0))


ISS_URL = "http://api.open-notify.org/iss-now.json"
SUNSET_URL = "https://api.sunrise-sunset.org/json"

def get_iss_current_position(url: str) -> Tuple[float,float]:
    """gets the ISS information and extracts the lat and lng

    Args:
        url (str): the ISS url, should be gotten from http://open-notify.org/Open-Notify-API/ISS-Location-Now/

    Returns:
        Tuple[float,float]: first element is the lat, second is the lng
    """

    iss_res = requests.get(url)

    iss_res.raise_for_status()
    iss_res_json = iss_res.json() 
    iss_position: dict = iss_res_json["iss_position"]
    iss_lat, iss_long = iss_position.values()
    return (iss_lat, iss_long)

iss_lat, iss_long = get_iss_current_position(ISS_URL)

def sunset_sunrise_hour(url: str, lat:float, lng:float) -> Tuple[float, float]:
    """Gets the location sunset/sunrise information using the lat and lng provided

    Args:
        url (str): SunriseSunset api, should be gotten from here https://sunrise-sunset.org/api
        lat (float): latitude of the location desired
        lng (float): longitude of the location desired

    Returns:
        Tuple[float, float]: first element is sunrise time, second is sunset time
    """

    sunset_params = {
        "lat":float(lat),
        "lng":float(lng),
        "formatted":0
    }
    sunset_res = requests.get(url, params=sunset_params)
    sunset_res_json = sunset_res.json()
    sunset_data = sunset_res_json["results"]

    sunrise = sunset_data["sunrise"]
    sunrise_hour = sunrise.split("T")[1].split(":")[0]

    sunset = sunset_data["sunset"]
    sunset_hour = sunset.split("T")[1].split(":")[0]
    return (float(sunrise_hour), float(sunset_hour))

sunrise_hour, sunset_hour = sunset_sunrise_hour(SUNSET_URL, LOCAL_LAT, LOCAL_LNG)



def iss_station_is_overhead(iss_lat:float, iss_long:float, error_margin: float = 5.0) -> bool:
    """checks if the ISS station's lat and lng is the same as locally give or take error_margin.

    Args:
        iss_lat (float): ISS station latitude
        iss_long (float): ISS station 
        error_margin (float): error margin for the location of the ISS

    Returns:
        bool: True if the station is overhead, False if it is not
    """
    if (((LOCAL_LAT - error_margin) <= float(iss_lat) <= (LOCAL_LAT + error_margin))
         and ((LOCAL_LNG - error_margin) <= float(iss_long) <= (LOCAL_LNG + error_margin) )):
        return True
    return False

def its_night(sunset_hour:float) -> bool:
    """checks if it's currntly dark outside by using the sunset hour provided

    Args:
        sunset_hour (float): sunset hour for the current location

    Returns:
        bool: True if current hour is past sunset hour ; 9 - 8 its dark, False if it's not
    """
    local_hour = dt.datetime.now().hour
    if local_hour >= int(sunset_hour):
        return True
    return False


if iss_station_is_overhead(iss_lat, iss_long) and its_night(sunset_hour):
    print("dood the station is over head, look up")
    # send notification to urself, <forever alone meme here please xD>

elif iss_station_is_overhead(iss_lat, iss_long):
    print("station is upove but ya might not see it cause ya know. . SUN!")

else:
    print(f"nothing to look at yet")

