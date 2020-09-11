import requests
import json
import datetime

__author__ = 'Dylan Cancelliere'


def main():
    API_KEY = 'secret'
    API_URL = 'https://candidate.hubteam.com/candidateTest/v3/problem/dataset?userKey=secret'
    data = getJSONData(API_URL)
    # data = gettestdata()  # For running against provided test results

    users = {}  # Dict to store every event by a particular user

    # Strings to avoid hardcoding and typos
    visitorId = 'visitorId'
    url = 'url'
    timestamp = 'timestamp'

    # Adds 'event' object which is a list of tuples of the timestamp and the url that was visited. Events are associated
    # with visitorIds
    for event in data['events']:
        if event[visitorId] not in users:
            users[event[visitorId]] = [(event[timestamp], event[url])]
        else:
            users[event[visitorId]] += [(event[timestamp], event[url])]

    # Sorts so that the timestamps are arranged in chronological order, which makes doing math for things like checking
    # to see if it's been less than 10 minutes since the last event and duration much easier
    for user in users:
        users[user].sort()

    # Gathers all the data for the end 'sessionsByUserRaw' dict without adhering to JSON formatting to make life easier.
    # In short, it associates a dict of 'sessions' with users. The key of each 'session' is it's startTime, and the
    # value is an array of size 4.
    #
    # Index 0 is a list of all the timestamps sorted in chronological order.

    # Index 1 is an unordered list of the URLs visited.

    # Index 2 is the most recent chronological timestamp, which is redundant since the timestamps are already
    # chronological, but I implemented because performance was not a concern and it made the code much easier to
    # read/debug
    #
    # Index 3 is the total duration of the session, which is again redundant but helped readability
    sessionsByUserRaw = {}

    for user in users:
        sessions = {}
        tempSesh = None
        for event in users[user]:
            if tempSesh is None:
                # sessions[event[0]]
                tempSesh = [[event[0]], [event[1]], event[0], 0]
                sessions[tempSesh[0][0]] = tempSesh
            else:
                a = datetime.datetime.fromtimestamp(event[0]/1000)
                b = datetime.datetime.fromtimestamp(tempSesh[2]/1000)
                if abs(a - b) < a - (a - datetime.timedelta(minutes=10)):
                    tempSesh[0].append(event[0])
                    tempSesh[0].sort()
                    tempSesh[1].append(event[1])
                    tempSesh[2] = tempSesh[0][len(tempSesh[0]) - 1]
                    tempSesh[3] = tempSesh[2] - tempSesh[0][0]
                    sessions[tempSesh[0][0]] = tempSesh
                else:
                    tempSesh = [[event[0]], [event[1]], event[0], 0]
                    sessions[tempSesh[0][0]] = tempSesh
        sessionsByUserRaw[user] = sessions

    # Format to JSON spec
    sessionsByUser = {}
    for user in sessionsByUserRaw:
        sessionsByUser[user] = []
        for session in sessionsByUserRaw[user]:
            sessionsByUser[user].append({
                'duration': sessionsByUserRaw[user][session][3],
                'pages': sessionsByUserRaw[user][session][1],
                'startTime': sessionsByUserRaw[user][session][0][0]
            })

    sessionsByUser = {'sessionsByUser': sessionsByUser}
    ENDPOINT = 'https://candidate.hubteam.com/candidateTest/v3/problem/result?userKey=8cd1e206cb79eacaa0732da4fa7b'

    r = requests.post(url=ENDPOINT, json=sessionsByUser)
    # print(r.headers)
    print(r.status_code, '\n', r.text)


# Helper function to request the JSON data from the API
def getJSONData(url):
    r = requests.get(url=url)
    data = r.json()
    return data


# Gets the input data from a local file containing the provided test data, rather than the actual API
def gettestdata():
    f = open("/home/dylan/cs/company-challenges/hubspot2020/test.txt", "r")
    temp = f.read()
    temp = temp.replace('\n', '')
    temp = temp.replace('  ', '')
    temp = json.loads(temp)
    return temp


if __name__ == "__main__":
    main()
