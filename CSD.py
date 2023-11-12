import http.client
import argparse
import urllib.parse
from colorama import Fore, Style
import socket
import ssl

# Function to read hosts from file
def read_hosts_from_file(filename):
    with open(filename, 'r') as file:
        return file.read().splitlines()


# Define the target server
parser = argparse.ArgumentParser()
parser.add_argument('-l', '--filename', help='Input filename')
parser.add_argument('-u', '--url', help='Single URL')
args = parser.parse_args()

# Check if either a filename or a URL is provided
if not (args.filename or args.url):
    parser.error("Please provide either a filename (-l) or a URL (-u).")

if args.filename:
    # Read all hosts from the specified file
    hosts = read_hosts_from_file(args.filename)
    # Remove 'http://' and 'https://' prefixes if present in each host URL
    hosts = [host.replace('http://', '').replace('https://', '') for host in hosts]

    print(hosts)
else:
    # Parse the URL to extract the host
    url = args.url
    parsed_url = urllib.parse.urlparse(url)
    #print(parsed_url)
    hosts = [parsed_url.netloc]

for host in hosts:
    try:
        print(host)
        # Create an HTTPS connection to the server
        conn = http.client.HTTPSConnection(host,timeout=3)
        
        # Define the POST data for the first request
        post_data = "GET /404 HTTP/1.1\r\nFoo: X"
        
        # Define the custom headers for both requests
        headers = {
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded"  # Adjust content type if needed
        }
        
        # Send the first POST request with custom headers
        conn.request("POST", "/", body=post_data, headers=headers)
        response1 = conn.getresponse()
        print(response1.read())
        
        # Send the second POST request with the same custom headers using the same connection
        conn.request("GET", "/")
        response2 = conn.getresponse()

        if response2.status == 404:
            print(f"{Fore.YELLOW}Header: HTTP 404 Not Found response detected.")
            print(f"URL/Hostname: {host}{Style.RESET_ALL}")

        
        # Check for "404 Not Found" in the response header or body
        response_text = response2.read().decode('utf-8')
        if "Not Found" in response_text:
            print(f"{Fore.YELLOW}Body: 404 Not Found detected in the response.")
            print(f"URL/Hostname: {host}{Style.RESET_ALL}")
        
        # Close the connection
        conn.close()
    except socket.timeout:
        print(f"{Fore.RED}Connection to {host} timed out. Skipping...{Style.RESET_ALL}")
    except ConnectionRefusedError:
        print(f"{Fore.RED}Connection to {host} refused. Skipping...{Style.RESET_ALL}")
    except socket.gaierror:
        print(f"{Fore.RED}Failed to resolve {host}. Skipping...{Style.RESET_ALL}")
    except ssl.SSLCertVerificationError:
        print(f"{Fore.RED}SSL verification failed for {host}. Skipping...{Style.RESET_ALL}")
        continue  # Skip to the next domain
    except ConnectionResetError as e:
        if e.errno == 104:
            print(f"{Fore.RED}Connection reset by peer for {host}. Skipping...{Style.RESET_ALL}")
            continue  # Skip to the next domain
