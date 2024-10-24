import requests
import argparse
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import re
import random
from colorama import Fore, Style, init
import time
import sys

# Initialize colorama
init(autoreset=True)

def show_header():
    header_text = """
{light_blue} ____  ____   _____  ____   __  _____ ___   ___  _     
|  _ \|  _ \ / _ \ \/ /\ \ / / |_   _/ _ \ / _ \| |    
| |_) | |_) | | | \  /  \ V /    | || | | | | | | |    
|  __/|  _ <| |_| /  \   | |     | || |_| | |_| | |___ 
|_|   |_| \_\\___/_/\_\  |_|     |_| \___/ \___/|_____|
{reset}
    """
    
    made_by_text = f"{Fore.RED}Made by TheXMog{Style.RESET_ALL}"
    
    # Display the header text and the "Made by TheXMog" text with reduced spacing
    print(header_text.format(light_blue=Fore.LIGHTCYAN_EX, reset=Style.RESET_ALL))
    print(f"{made_by_text}\n")

def scrape_proxies(url, limit, proxy_type):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        proxies = set()

        for line in soup.get_text().splitlines():
            match = re.match(r'(\d+\.\d+\.\d+\.\d+:\d+)', line)
            if match:
                proxy = match.group(1)
                proxies.add(proxy)

        return list(proxies)[:limit]
    except requests.RequestException as e:
        print(f"{Fore.RED}Failed to scrape {url} with error: {e}")
        return []

def check_http_proxy(proxy):
    try:
        response = requests.get('http://httpbin.org/ip', proxies={"http": proxy, "https": proxy}, timeout=5)
        if response.status_code == 200:
            return proxy
        else:
            return None
    except requests.RequestException:
        return None

def check_socks_proxy(proxy, proxy_type):
    try:
        proxies = {
            "http": f"{proxy_type}://{proxy}",
            "https": f"{proxy_type}://{proxy}"
        }
        response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=5)
        if response.status_code == 200:
            return proxy
        else:
            return None
    except requests.RequestException:
        return None

def save_proxies(proxies, filename):
    with open(filename, 'w') as f:
        for proxy in proxies:
            f.write(f"{proxy}\n")

def generate_random_proxy(proxy_type):
    ip = '.'.join(str(random.randint(0, 255)) for _ in range(4))
    port = random.randint(1024, 65535)
    return f"{ip}:{port}"

def main():
    show_header()

    print(f"{Fore.CYAN}Please choose an option:")
    print(f"{Fore.YELLOW}1) Scrape working proxies")
    print(f"{Fore.YELLOW}2) Generate random proxies")

    choice = input(f"{Fore.GREEN}Answer: ").strip()

    filename = input(f"{Fore.CYAN}Enter the filename to save the proxies (with .txt extension): ").strip()

    if choice == '1':
        urls = [
            "https://www.freeproxylists.net/",
            "https://www.sslproxies.org/",
            "https://www.us-proxy.org/"
        ]

        limit = int(input(f"{Fore.CYAN}How many proxies do you want to scrape? "))
        
        print(f"{Fore.CYAN}Choose proxy type:")
        print(f"{Fore.YELLOW}1) HTTP")
        print(f"{Fore.YELLOW}2) SOCKS4")
        print(f"{Fore.YELLOW}3) SOCKS5")
        
        proxy_type_choice = input(f"{Fore.GREEN}Answer: ").strip()
        proxy_type = "http" if proxy_type_choice == "1" else "socks4" if proxy_type_choice == "2" else "socks5"

        print(f"{Fore.CYAN}Scraping proxies from multiple sources...")

        all_proxies = []
        for url in urls:
            scraped_proxies = scrape_proxies(url, limit, proxy_type)
            print(f"{Fore.YELLOW}Scraped {len(scraped_proxies)} proxies from {url}.")
            all_proxies.extend(scraped_proxies)

        if not all_proxies:
            print(f"{Fore.RED}No proxies found during scraping. Please try again later.")
            return

        print(f"{Fore.CYAN}Total proxies scraped: {len(all_proxies)}")
        print(f"{Fore.CYAN}Checking scraped proxies...")

        with ThreadPoolExecutor(max_workers=10) as executor:
            if proxy_type == 'http':
                working_proxies = list(filter(None, executor.map(check_http_proxy, all_proxies)))
            else:
                working_proxies = list(filter(None, executor.map(check_socks_proxy, all_proxies, [proxy_type]*len(all_proxies))))

        if working_proxies:
            print(f"{Fore.GREEN}\nWorking proxies ({len(working_proxies)}):")
            save_proxies(working_proxies, filename)
            print(f"{Fore.GREEN}Working proxies saved to '{filename}'.")
        else:
            print(f"{Fore.RED}No working proxies found.")

    elif choice == '2':
        print(f"{Fore.CYAN}Choose proxy type:")
        print(f"{Fore.YELLOW}1) HTTP")
        print(f"{Fore.YELLOW}2) SOCKS4")
        print(f"{Fore.YELLOW}3) SOCKS5")
        
        proxy_type_choice = input(f"{Fore.GREEN}Answer: ").strip()
        proxy_type = "http" if proxy_type_choice == "1" else "socks4" if proxy_type_choice == "2" else "socks5"

        count = int(input(f"{Fore.CYAN}How many proxies do you want to generate? "))

        generated_proxies = [generate_random_proxy(proxy_type) for _ in range(count)]
        
        # Check generated proxies
        print(f"{Fore.CYAN}Checking generated proxies...")
        with ThreadPoolExecutor(max_workers=10) as executor:
            if proxy_type == 'http':
                working_generated_proxies = list(filter(None, executor.map(check_http_proxy, generated_proxies)))
            else:
                working_generated_proxies = list(filter(None, executor.map(check_socks_proxy, generated_proxies, [proxy_type]*len(generated_proxies))))

        if working_generated_proxies:
            save_proxies(working_generated_proxies, filename)
            print(f"{Fore.GREEN}Working generated proxies saved to '{filename}'.")
        else:
            print(f"{Fore.RED}No working generated proxies found.")

    else:
        print(f"{Fore.RED}Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
