# wget --no-verbose -w 0.2 --random-wait -U "Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/15.0" -r -l inf -H -D storage.googleapis.com,cdnme.se,evawiklund.blogg.se -A bmp,gif,jpeg,jpg,png --no-parent https://evawiklund.blogg.se/
#
#

import requests
import time
import re
import json
import os
from bs4 import BeautifulSoup

def extract_date_timestamp(text):
    pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
    match = re.search(pattern, text)

    if match:
        return match.group()
    else:
        return None

def log(msg):
    f = open("convert_log.txt", "a")
    f.write(msg)
    f.close()

def register_failed_sub_url(sub_url):
    f = open("failed_sub_urls.txt", "a")
    f.write(sub_url)
    f.close()

def convert_page(sub_url):
    if len(sub_url) < 2:
        return 1

    base_url = 'https://evawiklund.blogg.se'

    date_pattern = r"\/(\d{4})\/\w+\/"
    date_year_month_path = re.match(date_pattern, sub_url).group()

    data = None

    num_retries = 5

    wait_duration = 2.5

    while num_retries > 0:
        try:
            response = requests.get(base_url + sub_url)
            if response.status_code == 200:
                data = response.text
                break
            else:
                print(f"Failed to retrieve data. Status code: {response.status_code}")
                if num_retries == 0:
                    print("ERROR: No response after retrying. Aborting...")
                    register_failed_sub_url(sub_url)
                    return 1
                else:
                    print("Retrying...")
                    time.sleep(wait_duration)
                    wait_duration += 2.5
                    num_retries -= 1
                    continue
        except:
            print("Request failed!")
            register_failed_sub_url(sub_url)
            return 1

    soup = BeautifulSoup(data, 'html.parser')


    entrymeta = soup.find('div', attrs={'class': "entrymeta"})
    article = soup.find('article', attrs={'class': "entry"})
    h3 = article.find('h3')
    entrybody = article.find('div', attrs={'class': "entrybody"})
    imgs = article.find_all('img')
    
    #print(article.prettify())

    # TODO: Find all images, download them and place them in the correct folder

    post_image_paths = []
    for i in range(len(imgs)):
        src = imgs[i]['src']
        try:
            resp = requests.get(src)
            if (resp.status_code != 200):
                msg = f"Error ('{sub_url}'): image '{src}' could not be downloaded.\n"
                log(msg)
                continue
            sub_dir = os.path.dirname(src).split('/')[-1]
            file_name = os.path.basename(src)
            image_path = f'./assets/img{date_year_month_path}{sub_dir}/{file_name}'
            post_image_paths.append(image_path[1:])
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            f = open(image_path,'wb')
            f.write(resp.content) 
            f.close() 
        except:
            msg = f"Error ('{sub_url}'): image '{src}' could not be downloaded.\n"
            log(msg)


    post_title = h3.text
    post_date_time = extract_date_timestamp(entrymeta.text)
    post_date = post_date_time.split(' ')[0]
    post_best_thumbnail = ""
    if (len(post_image_paths) > 0):
        post_best_thumbnail = post_image_paths[0]
    post_year_month = date_year_month_path
    post_content = entrybody.get_text("\n\n").rstrip()

    if (post_date_time == None):
        print(f"Failed to read date from {sub_url}")
        register_failed_sub_url(sub_url)
        return 1

    page = f'''---
layout: post
sitemap: false

title:  "{post_title.replace('"', "&quot;")}"
date:   {post_date_time} +0100
thumbnail-img: {post_best_thumbnail}
tags: [blogg.se]
---

{post_content}

'''
    for i in range(len(post_image_paths)):
        page += f'![]({post_image_paths[i]})' + "\n\n"

    post_file_name = os.path.basename(sub_url).split('.')[0]
    post_dir = f'./_posts{post_year_month}'
    post_path = post_dir + f'{post_date}-{post_file_name}.md'

    os.makedirs(post_dir, exist_ok=True)
    f = open(post_path, "w")
    f.write(page)
    f.close()

    return 0

def main():

    #TODO: loop all sub urls
    file = open("../eva_links.txt", "r")
    i = 0
    count = sum(1 for _ in file)
    file.seek(0)
    for sub_url in file:
        print(f'{i}/{count}: ' + sub_url.rstrip() + " ... ", end="", flush=True)
        i += 1
        ret_code = convert_page(sub_url.rstrip())

        if ret_code == 1:
            print("FAILED")
            continue

        print("OK")
    
    file.close()
    
if __name__ == "__main__":
    main()