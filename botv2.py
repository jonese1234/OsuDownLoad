from requests import session
import os
import sys
import time
import urllib.request
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from settings import *

authentication_url = 'https://osu.ppy.sh/forum/ucp.php'
payload = {
    'action': 'login',
    'username': osu_username,
    'password': osu_password,
    'redirect': 'index.php',
    'sid': '',
    'login': 'Login'
}

beatmap_save = set_beatmap_save

TAG_RE = re.compile(r'<[^>]+>')


# todo if no download link use bloodcat
# todo zip each one up
# todo upload to megan

difficulty_no = 0
phase_num = set_phase_num
week_num = set_week_num
start_time = datetime.now()
mappool = mappool_name

with session() as c:
    c.post(authentication_url, data=payload)
    print("I'm now logged in")


    def download_beatmaps(url):
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0")
        r = urllib.request.urlopen(req)
        data = r.read()
        soup = BeautifulSoup(data, "html5lib")
        partname = soup.find('title')
        filename = url_split(url) + ' ' + remove_tags(partname) + ".osz"
        print(filename)
        out_folder = sys.argv[1] if len(sys.argv) == 2 else (beatmap_save + 'Phase ' + str(phase_num) + '/' + 'Week ' + str(week_num) + '/' + difficulty() + '/')

        if not os.path.exists(out_folder):
            os.makedirs(out_folder)  # creates out_folder, including any required parent ones
        else:
            if not os.path.isdir(out_folder):
                raise RuntimeError('output path must be a directory')

        outpath = os.path.join(out_folder, filename)

        print('Downloading...')
        r = c.get(download_url(url), stream=True)
        with open(outpath, 'wb') as beatmap:
            for chunk in r.iter_content(chunk_size=512 * 1024):
                if chunk: # filter out keep-alive new chunks
                    beatmap.write(chunk)
            beatmap.close()
        print('Download completed')


    def remove_tags(text):
        partname = TAG_RE.sub('', text.text)
        title = re.sub('[\/*?:<>"|]', '', partname)
        return title

    def url_split(url):
        return url.rsplit('/', 1)[-1]

    def download_url(url):
        new_url = url.rsplit('/', 2)[-3] + "/d/" + url.rsplit('/', 1)[-1]
        print(new_url)
        return new_url

    def new_download_url(url):
        r = c.get(url)
        soup = BeautifulSoup(r.content, "html5lib")
        new_url_part = soup.find('a', class_='beatmap_download_link')
        new_url = ('https://osu.ppy.sh'+ new_url_part['href'])
        return new_url

    def difficulty():
        if difficulty_no == 0: return 'Beginner'
        elif difficulty_no == 1: return 'Standard'
        elif difficulty_no == 2: return 'Expert'


    def run():
        with open(mappool) as data_file:
            data = json.load(data_file)

        global difficulty_no

        while difficulty_no < 3:
            for all in data[difficulty_no]:
                if difficulty_no == 3: break
                else:
                    print('Number of maps: ' + str(len(data[difficulty_no])))
                    i = 0
                    for each in data[difficulty_no]:
                        id = data[difficulty_no][i]['setid']
                        url = 'https://osu.ppy.sh/s/' + str(id)
                        download_beatmaps(url)
                        i += 1
                        time.sleep(2)
                    time.sleep(5)
                    difficulty_no += 1


def main():
    print('Starting Bot!')
    time.sleep(3)
    run()
    end_time = datetime.now()
    print('Time to Complete: {}'.format(end_time - start_time))
    print('Bot has Finished!')


if __name__ == "__main__":
    main()
