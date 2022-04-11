from scrapy.http import TextResponse
import subprocess
import re
import requests


headers = {
    'authority': 'chromedriver.storage.googleapis.com',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91",'
    '"Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
    'accept': '*/*',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://chromedriver.storage.googleapis.com/index.html',
    'accept-language': 'en-US,en;q=0.9',
}

params = (
    ('delimiter', '/'),
    ('prefix', ''),
)


def chromedriver_exists():
    chromedriver = subprocess.Popen("ls", shell=True, stdout=subprocess.PIPE)
    chromedriver_return = chromedriver.stdout.read().decode('utf-8')
    return True if 'chromedriver' in chromedriver_return else False


def chromedriver_updated():
    google_process = subprocess.Popen(
        "google-chrome --version", shell=True, stdout=subprocess.PIPE
    )
    google_process_return = google_process.stdout.read().decode('utf-8')
    chromedriver = subprocess.Popen(
        "./chromedriver --version", shell=True, stdout=subprocess.PIPE
    )
    chromedriver_return = chromedriver.stdout.read().decode('utf-8')
    return (
        True if google_process_return[14:18] == chromedriver_return[13:17] else False
    )


def get_chrome_version():
    google_process = subprocess.Popen(
        "google-chrome --version", shell=True, stdout=subprocess.PIPE
    )
    google_process_return = google_process.stdout.read()
    return google_process_return.decode('utf-8')


def parse_version(chrome_version: str):
    return chrome_version.split()[2]


def get_chromedriver_version(chrome_version: str):
    url = 'https://chromedriver.storage.googleapis.com/'
    response = requests.get(url, headers=headers, params=params)
    response = TextResponse(body=response.content, url=url)

    for item in response.css('Prefix').extract():
        if chrome_version[0:7] in item:
            return re.compile(r'(\d.*\d)').search(item)


def download_chromedriver(chromedriver_version: str):
    headers = {
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91",'
        '"Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        '(KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
        'Referer': 'https://chromedriver.storage.googleapis.com/'
        f'index.html?path={chromedriver_version}/',
    }

    url = (
        f"https://chromedriver.storage.googleapis.com/" 
        f"{chromedriver_version}/chromedriver_linux64.zip"
    )

    with requests.get(url, headers, stream=True) as r:
        r.raise_for_status()
        with open('chromedriver.zip', 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    g = subprocess.Popen(
        "unzip chromedriver.zip && rm chromedriver.zip", 
        shell=True, stdout=subprocess.PIPE
    )
    return g.stdout.read()


class DriverState():
    Existent = chromedriver_exists()
    Updated = chromedriver_exists() and chromedriver_updated()


def main():
    if DriverState.Existent:
        print('Chromedriver already exists in the local repository.')
    if DriverState.Updated:
        print('Chromedriver is already updated.')
    else:
        chrome_version = get_chrome_version()
        parsed_version = parse_version(chrome_version)
        version = get_chromedriver_version(parsed_version)
        download_chromedriver(version.group())
        print(f'👌 Chromedriver updated: {version.group()}')


if __name__ == '__main__':
    main()