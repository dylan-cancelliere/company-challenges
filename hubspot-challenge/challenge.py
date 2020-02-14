"""
My solution to the HubSpot coding challenge.  I wasn't able to finish on time, but it was a great learning experience.
After stepping back from the problem for a little while, I realized one of the mistakes I made during the challenge was
attempting to parse the dates as integers, which made date pairs like March 31st and April 1st invalid, while they
should certainly have worked.  Implementing Python's datetime library caught that edge case, and once I tweaked my code
a bit to accept datetime objects, everything worked like a charm and I was able to get the right answer.  It's
definitely unfortunate that I couldn't have thought of that while I was on the clock, but it goes to show how sometimes
taking a break and coming back to a problem can turn something that you've been working at for hours into a relatively
trivial task.

:author: Dylan Cancelliere
:date: 2020-02-13
"""

import requests
import json
import datetime


def main():
    API_KEY = '0d465546ce36dbee8f666bf25879'
    URL = 'https://candidate.hubteam.com/candidateTest/v3/problem/dataset?userKey=0d465546ce36dbee8f666bf25879'
    data = getJSONData(URL)
    # data = gettestdata()  # Used for testing against the sample input data, which is stored in a local file
    countries = {}  # Dictionary of each country paired with a list of each person in that country
    json_data = []  # List which gets build into a JSON object.  When a country is fully populated with people,
    # it is added to this list

    # Builds a list of countries
    for key in data['partners']:
        if key['country'] not in countries:
            countries[key['country']] = [key]
        else:
            countries[key['country']].append(key)

    for country in countries:
        calendar = {}   # Dictionary of every date in which at least one person could attend that date as well as the
        # following, paired with frequency
        attending = []  # Dictionary of every person who can attend after the optimal starting date is selected
        for key in countries[country]:
            # Gets every valid date, where a valid date is a date where at least one person can attend that date and
            # the date afterwards, and populates calendar with those values
            dates = key['availableDates']
            previous = datetime.date(int(dates[0][:4]), int(dates[0][5:7]), int(dates[0][8:]))
            dates = dates[1:]
            for day in dates:
                day = datetime.date(int(day[:4]), int(day[5:7]), int(day[8:]))
                diff = day - previous
                if abs(diff.days) == 1:
                    if previous in calendar:
                        calendar[previous] += 1
                    else:
                        calendar[previous] = 1
                previous = day
        startingdate = maxdict(calendar)

        # Adds each person who can attend for both the starting and ending date to attending
        for key in countries[country]:
            if str(startingdate) in key['availableDates'] and str(startingdate + datetime.timedelta(days=1)) in key['availableDates']:
                attending.append(key['email'])

        json_data.append(jsonbody(attending, country, str(startingdate)))   # Adds the completed country dictionary
        # to the array

    json_data = {"countries": json_data}

    print(json_data)

    ENDPOINT = 'https://candidate.hubteam.com/candidateTest/v3/problem/result?userKey=0d465546ce36dbee8f666bf25879'
    # ENDPOINT = 'https://postman-echo.com/post'    # For testing
    r = requests.post(url=ENDPOINT, json=json_data)
    print(r.headers)
    print(r.status_code, '\n', r.text)


def maxdict(mydict):
    """
    Finds the key with the maximum value in the array

    :param mydict: dictionary of dates paired with frequencies
    :return: the date most people can attend
    """
    if len(mydict) == 0:
        return None
    mx = (0, 0)
    for key in mydict:
        if mydict[key] > mx[0]:
            mx = (mydict[key], key)
    return mx[1]


def gettestdata():
    """
    Gets the input data from a file stored locally, rather than the actual API

    :return: the JSON data stored in the file
    """
    f = open("/home/dylan/cs/hubspot-challenge/test", "r")
    temp = f.read()
    temp = temp.replace('\n', '')
    temp = temp.replace('  ', '')
    temp = json.loads(temp)
    return temp


def getJSONData(url):
    """
    Requests the JSON data from the API

    :param url: The URL to request from
    :return: 
    """
    r = requests.get(url=url)
    data = r.json()
    return data


def jsonbody(attendees, country, date):
    """
    Formats the data to spec

    :param attendees: list of the email addresses of people that can attend
    :param country: the name of the country
    :param date: the starting date of the event
    :return: correctly formatted dict
    """
    return {"attendeeCount": len(attendees), "attendees": attendees, "name": country, "startDate": date}


if __name__ == "__main__":
    main()
