# DorkInjector

### Python script to automate dork search for SQL Injections:
DorkInjector accepts single dork as an argument and performs search using one of the next search engines: Bing (Default), DuckDuckGo or Google.
After performed search all urls will be saved to file for further scan if needed.

By default it will start injecting all found urls, if url is injectable it will be saved to text file. 

### Usage:

```
usage: DorkInjector.py [-h] [-d DORK] [-p [PROXIES]] [-e [{google,duck,bing}]]
                       [-s SITES] [-t [TIMEOUT]] [-m [MAX]] [-o [OUTPUT]]

optional arguments:
  -h, --help            show this help message and exit
  -d DORK, --dork DORK  enter your dork: -d 'inurl:"something.php?id=" ...'
  -p [PROXIES], --proxies [PROXIES]
                        enter your file with proxies in format: -p proxies.txt
  -e [{google,duck,bing}], --engine [{google,duck,bing}]
                        pick one of the engines(google, duck, bing): -e duck
                        or --engine google. Default: Bing
  -s SITES, --sites SITES
                        enter file with list of websites to check: -s
                        websites.txt
  -t [TIMEOUT], --timeout [TIMEOUT]
                        enter timeout length: -t 10; Default 5 seconds
  -m [MAX], --max [MAX]
                        enter how many search pages you need: -m 5; Default is
                        first page
  -o [OUTPUT], --output [OUTPUT]
                        enter output filename: -o results.txt

By default DorkInjector.py will try to find all urls from Bing using your dork,
then it will try to inject them.
P.S You can specify --engine option to pick either Google or DuckDuckGo.
If you picked Google you should have really good private proxies.

```

### Installation:

```
git clone https://github.com/VoltK/DorkInjector.git
cd DorkInjector
pip3 install -r requirements.txt
python3 DorkInjector.py -d inurl:"product.php?id=" -m 5 -o injectable.txt -t 20
```

### Notes:

1) By default search engine is set to Bing.com
2) DuckDuckGo sometimes gives irrelevant results for dork searching -> Check your dork first
3) If you want to use Google- you better have private proxies, otherwise you will stuck in captcha
4) On a stage of injecting DorkInjector uses all your CPUs except one, which is left for system services.
