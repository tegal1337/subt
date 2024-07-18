import os
import sys
import time
import argparse
import subprocess
import yaml
from colorama import init, Fore, Style

init(autoreset=True)  # Inisialisasi colorama untuk manajemen warna terminal

def load_vulnerable_domains():
    vulnerable_domains = []
    vulnerable_folder = "vulnerable/"

    for filename in os.listdir(vulnerable_folder):
        if filename.endswith(".yaml"):
            with open(os.path.join(vulnerable_folder, filename), 'r') as file:
                try:
                    data = yaml.safe_load(file)
                    cname = data.get('cname', '')
                    status_code = data.get('status_code', 404)
                    status = data.get('status', 'vulnerable can be takeover!')

                    vulnerable_domains.append({'cname': cname, 'status_code': status_code, 'status': status})
                except yaml.YAMLError as e:
                    print(f"Error reading {filename}: {e}")

    # Menambahkan entri dinamis
    vulnerable_domains.append({'cname': 'github.io', 'status_code': 404, 'status': 'vulnerable can be takeover!'})
    
    return vulnerable_domains

def subfinder_scan(domain):
    try:
        subfinder_process = subprocess.Popen(['subfinder', '-d', domain], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subdomains, subfinder_error = subfinder_process.communicate()
        if subfinder_process.returncode != 0:
            print(f"Subfinder error: {subfinder_error.decode('utf-8')}")
            return []
        subdomains = subdomains.decode('utf-8').strip().split('\n')
        return subdomains
    except Exception as e:
        print(f"Error running subfinder for domain {domain}: {e}")
        return []

def check_subdomain(subdomain):
    try:
        # Gunakan dig untuk mendapatkan CNAME
        dig_process = subprocess.Popen(['dig', subdomain, '+short', 'CNAME'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        dig_output, dig_error = dig_process.communicate()
        if dig_process.returncode != 0:
            print(f"Dig error for {subdomain}: {dig_error.decode('utf-8')}")
            return None, None

        dig_output = dig_output.decode('utf-8').strip()

        # Gunakan curl untuk mendapatkan status code
        curl_process = subprocess.Popen(['curl', '-s', '-o', '/dev/null', '-I', '-w', '%{http_code}', f'http://{subdomain}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        curl_output, curl_error = curl_process.communicate()
        if curl_process.returncode != 0:
            print(f"Curl error for {subdomain}: {curl_error.decode('utf-8')}")
            return None, None

        curl_output = curl_output.decode('utf-8').strip()

        # Dapatkan informasi yang dibutuhkan
        cname = dig_output if dig_output else None
        status_code = int(curl_output) if curl_output.isdigit() else 0

        return cname, status_code
    except Exception as e:
        print(f"Error checking subdomain {subdomain}: {e}")
        return None, None

def main(input, listdomains=False, direct_subdomains=False):
    start_time = time.time()
    vulnerable_domains = load_vulnerable_domains()

    # Logo SubT
    print(Fore.BLUE + r'''
██████████████████████████
█─▄▄▄▄█▄─██─▄█▄─▄─▀█─▄─▄─█
█▄▄▄▄─██─██─███─▄─▀███─███
▀▄▄▄▄▄▀▀▄▄▄▄▀▀▄▄▄▄▀▀▀▄▄▄▀▀

Subdomain Takeover Scanner
Author by Van | Tegalsec
--------------------------
''' + Style.RESET_ALL)

    if listdomains:
        print(Fore.GREEN + "[+] Checking domains from list..." + Style.RESET_ALL)
        with open(input, 'r') as f:
            domains = f.read().splitlines()

        for domain in domains:
            subdomains = subfinder_scan(domain)
            if subdomains:
                print(Fore.CYAN + f"\n[+] Checking subdomains for domain: {domain}" + Style.RESET_ALL)
                found_vulnerable = False
                for subdomain in subdomains:
                    cname, status_code = check_subdomain(subdomain)
                    if cname is not None and status_code != 0:
                        is_vulnerable = False
                        for domain_info in vulnerable_domains:
                            if domain_info['cname'] in cname and domain_info['status_code'] == status_code:
                                print(Fore.RED + f"{subdomain} [{status_code}] | {domain_info['status']} [{domain_info['cname']}]" + Style.RESET_ALL)
                                found_vulnerable = True
                                is_vulnerable = True
                                break
                            # Cek untuk CNAME dinamis
                            elif '*' in domain_info['cname'] and domain_info['cname'].replace('*', '') in cname and domain_info['status_code'] == status_code:
                                print(Fore.RED + f"{subdomain} [{status_code}] | {domain_info['status']} [{domain_info['cname']}]" + Style.RESET_ALL)
                                found_vulnerable = True
                                is_vulnerable = True
                                break
                        if not is_vulnerable:
                            print(Fore.GREEN + f"{subdomain} [{status_code}] | Not vulnerable" + Style.RESET_ALL)

                if not found_vulnerable:
                    print(Fore.GREEN + "No vulnerable subdomains found." + Style.RESET_ALL)

    elif direct_subdomains:
        print(Fore.GREEN + "[+] Checking direct list of subdomains..." + Style.RESET_ALL)
        with open(input, 'r') as f:
            subdomains = f.read().splitlines()

        if subdomains:
            print(Fore.CYAN + f"\n[+] Checking subdomains from file: {input}" + Style.RESET_ALL)
            found_vulnerable = False
            for subdomain in subdomains:
                cname, status_code = check_subdomain(subdomain)
                if cname is not None and status_code != 0:
                    is_vulnerable = False
                    for domain_info in vulnerable_domains:
                        if domain_info['cname'] in cname and domain_info['status_code'] == status_code:
                            print(Fore.RED + f"{subdomain} [{status_code}] | {domain_info['status']} [{domain_info['cname']}]" + Style.RESET_ALL)
                            found_vulnerable = True
                            is_vulnerable = True
                            break
                        # Cek untuk CNAME dinamis
                        elif '*' in domain_info['cname'] and domain_info['cname'].replace('*', '') in cname and domain_info['status_code'] == status_code:
                            print(Fore.RED + f"{subdomain} [{status_code}] | {domain_info['status']} [{domain_info['cname']}]" + Style.RESET_ALL)
                            found_vulnerable = True
                            is_vulnerable = True
                            break
                    if not is_vulnerable:
                        print(Fore.GREEN + f"{subdomain} [{status_code}] | Not vulnerable" + Style.RESET_ALL)

            if not found_vulnerable:
                print(Fore.GREEN + "No vulnerable subdomains found." + Style.RESET_ALL)

    else:
        # Single domain input or direct subdomain list
        if os.path.isfile(input):
            with open(input, 'r') as f:
                subdomains = f.read().splitlines()
        else:
            subdomains = subfinder_scan(input)

        if subdomains:
            print(Fore.CYAN + f"\n[+] Checking subdomains for domain: {input}" + Style.RESET_ALL)
            found_vulnerable = False
            for subdomain in subdomains:
                cname, status_code = check_subdomain(subdomain)
                if cname is not None and status_code != 0:
                    is_vulnerable = False
                    for domain_info in vulnerable_domains:
                        if domain_info['cname'] in cname and domain_info['status_code'] == status_code:
                            print(Fore.RED + f"{subdomain} [{status_code}] | {domain_info['status']} [{domain_info['cname']}]" + Style.RESET_ALL)
                            found_vulnerable = True
                            is_vulnerable = True
                            break
                        # Cek untuk CNAME dinamis
                        elif '*' in domain_info['cname'] and domain_info['cname'].replace('*', '') in cname and domain_info['status_code'] == status_code:
                            print(Fore.RED + f"{subdomain} [{status_code}] | {domain_info['status']} [{domain_info['cname']}]" + Style.RESET_ALL)
                            found_vulnerable = True
                            is_vulnerable = True
                            break
                    if not is_vulnerable:
                        print(Fore.GREEN + f"{subdomain} [{status_code}] | Not vulnerable" + Style.RESET_ALL)

            if not found_vulnerable:
                print(Fore.GREEN + "No vulnerable subdomains found." + Style.RESET_ALL)

    print(Fore.YELLOW + f"\nTotal scan time: {time.time() - start_time:.2f} seconds" + Style.RESET_ALL)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subdomain takeover scanner.")
    parser.add_argument("input", help="Input file containing subdomains, single domain, or list of domains")
    parser.add_argument("--listdomains", action="store_true", help="Specify if input file contains list of domains")
    parser.add_argument("--direct-subdomains", action="store_true", help="Specify if input file contains direct list of subdomains")
    args = parser.parse_args()

    main(args.input, args.listdomains, args.direct_subdomains)
