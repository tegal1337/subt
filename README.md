# Subdomain Takeover Scanner (SubT)

## Details
SubT is a Python tool designed to scan subdomains for potential takeover vulnerabilities based on CNAME and HTTP status codes. It checks each subdomain against a predefined list of vulnerable configurations stored in YAML files.

## Features
- **Subdomain Scanning**: Supports scanning subdomains from a file, a list of domains, or directly provided subdomains.
- **Vulnerability Detection**: Identifies subdomains vulnerable to takeover based on CNAME and HTTP status codes.
- **Color-Coded Output**: Provides clear and colorful output using `colorama` for better readability.
- **Support for Different Input Formats**: Handles single domains, lists of domains, and direct subdomain lists.
- **Integration with Subfinder**: Optionally integrates with Subfinder for discovering subdomains dynamically.

## Usage
### Installation
Clone the repository :
```
git clone https://github.com/yourusername/subdomain-takeover-scanner.git
cd subdomain-takeover-scanner
```
Install dependencies:
```
pip install -r requirements.txt
```
### Command Line Usage
Scan Direct List of Subdomains
```
python subt.py subdo.txt --direct-subdomains
```
Scan List of Domains
```
python subt.py domain.txt --listdomains
```
Scan Single Domain
```
python subt.py example.com
```
