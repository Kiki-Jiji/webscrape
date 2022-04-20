

def get_free_proxies():

    url = "https://free-proxy-list.net/"
    # get the HTTP response and construct soup object
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    proxies = []

    table = soup.find_all('tbody')

    ip_addresses = [i for i in [i for i in table][0]]

    rows = {}
    count = 0

    for table_row in ip_addresses:

        try:
            ip = [i for i in table_row.children]

            row = {
                'ip': get_child(ip, 0),
                'port': get_child(ip, 1),
                'code': get_child(ip, 2),
                'country': get_child(ip, 3),
                'Anonymity': get_child(ip, 4),
                'Google': get_child(ip, 5),
                'Https': get_child(ip, 6),
                'last_checked': get_child(ip, 7),
            }

            rows[count] = row
        except:
            pass
        count += 1

    return pd.DataFrame.from_dict(rows, orient='index')



class Proxy:
    def __init__(self, HEADERS) -> None:
        self.headers = HEADERS
        self.proxies = 5
        self.proxy_num = 0
        self.current_proxy = self.proxies.ip.array[self.proxy_num]

    def get_webpage(self, url):
        success = False
        while success is False:
            print(self.current_proxy)
            try:
                webpage = self.try_proxy(url)
                logging.debug(f'Success with {self.current_proxy}, proxy number {self.proxy_num}')
                success = True
            except:
                self.set_current_proxy()
        return webpage

    def set_current_proxy(self):
        self.proxy_num += 1
        self.current_proxy = self.proxies.ip.array[self.proxy_num]

    def try_proxy(self, url):

        i = 1
        n = 2
        success_status = False
        while success_status is False:
            print(success_status)
            try:
                webpage = requests.get(url, headers=self.headers , proxies={"http": self.current_proxy, "https": self.current_proxy}, timeout=2)
                page = BeautifulSoup(webpage.content, features= "html.parser")
                
                if amazon_blocked(page):
                    logging.info(f'Amazon blocked {self.current_proxy}')
                    if i < n:
                        i += 1
                    else:
                        success_status = True
                success_status = True
            except ProxyError:
                if i < n:
                    i += 1
                else:
                    success_status = True
        
        assert i < n, "Proxy failed"

        return webpage


def amazon_blocked(page):
    print("run amazon blocking")
    comments = page.find_all(string=lambda text: isinstance(text, Comment))

    print(True in ['automated' in i for i in comments])
    return True in ['automated' in i for i in comments]

