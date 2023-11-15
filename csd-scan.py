import socket
import ssl
import argparse

def send_request(host, port, data):
    context = ssl.create_default_context()

    # Create a socket object and wrap it with SSL
    with context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host) as s:
        s.settimeout(10)

        try:
            # Connect to the server
            s.connect((host, port))

            # Send the HTTP request
            s.sendall(data.encode())

            # Receive the response
            response = s.recv(4096).decode()

            return response

        except (socket.timeout, socket.error) as e:
            print(f"Error: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description='Simple HTTPS client for testing.')
    parser.add_argument('-u', '--url', help='Single URL to test')
    parser.add_argument('-f', '--file', help='File containing a list of URLs')
    args = parser.parse_args()

    if not args.url and not args.file:
        print("Please provide either a single URL (-u) or a file of URLs (-f)")
        return

    urls = []

    if args.url:
        urls.append(args.url)

    if args.file:
        with open(args.file, 'r') as file:
            urls.extend(file.read().splitlines())

    for url in urls:
        host, port, path = parse_url(url)
        data = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Length: 8\r\n\r\n"

        response = send_request(host, port, data)

        if response:
            print(f"URL: {url} - Response: {response}")

def parse_url(url):
    parts = url.split('/')
    host_port = parts[2].split(':')
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 443  # Default to port 443 for HTTPS
    path = '/' + '/'.join(parts[3:])
    return host, port, path

if __name__ == "__main__":
    main()

