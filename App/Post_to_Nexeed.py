import requests
import json
import progressbar
import time


def Nexeedpost(payload, url, updateTime):
    # sending post request and saving response as response object
    headers = {
        "Content-Type": "application/json"
    }
    try:
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        pastebin_url = r.content.decode("utf-8")

        # Response from Bosch URL
        if pastebin_url == "{}":
            print("Successfully Posted to Nexeed")
            print(payload)

            print("Waiting to POST ... ")
            bar = progressbar.ProgressBar(maxval=updateTime,
                                          widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
            bar.start()
            for i in range(updateTime):
                bar.update(i + 1)
                time.sleep(1)
            bar.finish()
        else:
            print("URL Response: %s" % pastebin_url)

    except:
        print("Nexeed unreachable")

