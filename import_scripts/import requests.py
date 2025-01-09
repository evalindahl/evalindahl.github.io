# wget --no-verbose -w 0.2 --random-wait -U "Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/15.0" -r -l inf -H -D storage.googleapis.com,cdnme.se,evawiklund.blogg.se -A bmp,gif,jpeg,jpg,png --no-parent https://evawiklund.blogg.se/
#
#

import requests
import time
import json

def get_last_entry_timestamp(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['last_ts']
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return None
    except json.JSONDecodeError:
        print("Invalid JSON response.")
        return None

def main():
    url = 'https://evawiklund.blogg.se/_more/entries_allmant_1502373792'
    more_url = 'https://evawiklund.blogg.se/_more/entries_allmant_'

    links = []

    last_timestamp = get_last_entry_timestamp(url)
    if last_timestamp is not None:
        current_timestamp = int(last_timestamp)
        stop = False
        while not stop:
            new_url = f"{more_url}{current_timestamp}"
            print(new_url)
            numTries = 5
            while numTries > 0:
                try:
                    response = requests.get(new_url)
                    if response.status_code == 200:
                        data = response.json()
                        for i in range(len(data['entries'])):
                            print(f"- {data['entries'][i]['permalink']}")
                            links.append(data['entries'][i]['permalink'])
                            
                        last_timestamp = data['last_ts']
                        if (int(last_timestamp) == current_timestamp):
                            stop = True
                        current_timestamp = last_timestamp
                        numTries = 0
                        if last_timestamp is not None:
                            time.sleep(0.5) # pause for 0.5 seconds to avoid hitting rate limits
                        else:
                            print(f"No more responses received with a timestamp greater than {last_timestamp}.")
                            stop = True
                            break
                    else:
                        print(f"Failed to retrieve data. Status code: {response.status_code}")
                        stop = True
                        break
                except requests.exceptions.RequestException as e:
                    print(f"Request failed: {e}")
                    stop = True
                    break

    if last_timestamp is not None:
        print(f"The last timestamp received was {last_timestamp}")

    print("------------------")
    print("-")
    print(links)
    print("------------------")
    print("-")
    for i in range(len(links)):
        print(links[i])

    with open("eva_links.txt", "w") as f:
        for i in range(len(links)):
            f.write(links[i])
            f.write("\n")
        f.close()

if __name__ == "__main__":
    main()