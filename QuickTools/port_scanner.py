import socket
import concurrent.futures
import sys

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

def format_open_ports(results):
    formatted_results = "Open Ports:\n"
    formatted_results += "{:<8} {:<15} {:<10} {:<10}\n".format("Port", "Service", "TCP", "UDP")
    formatted_results += '-' * 50 + "\n"
    for port, service, banner, tcp_status, udp_status in results:
        if tcp_status or udp_status:
            tcp_str = "Open" if tcp_status else ""
            udp_str = "Open" if udp_status else ""
            formatted_results += f"{port:<8} {service:<15} {RED + tcp_str + RESET:<10} {GREEN + udp_str + RESET:<10}\n"
            if banner and tcp_status:
                banner_lines = banner.split('\n')
                for line in banner_lines:
                    formatted_results += f"{GREEN}{'':<8}{line}{RESET}\n"
    return formatted_results

def get_banner(sock):
    try:
        sock.settimeout(1)
        banner = sock.recv(1024).decode().strip()
        return banner
    except:
        return ""

def scan_tcp_port(target_ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target_ip, port))
        if result == 0:
            try:
                service = socket.getservbyport(port, 'tcp')
            except:
                service = 'Unknown'
            banner = get_banner(sock)
            return port, service, banner, True
        else:
            return port, "", "", False
    except:
        return port, "", "", False
    finally:
        sock.close()

def scan_udp_port(target_ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        sock.sendto(b'', (target_ip, port))
        try:
            data, _ = sock.recvfrom(1024)
            return True  # UDP port répond -> probablement ouvert
        except socket.timeout:
            return None  # UDP port pas de réponse -> ouvert ou filtré
        except socket.error:
            return False  # Erreur -> port fermé
    except:
        return False
    finally:
        sock.close()

def port_scan(target_host, start_port, end_port):
    try:
        target_ip = socket.gethostbyname(target_host)
    except socket.gaierror:
        print(f"Unable to resolve host: {target_host}")
        return

    print(f"Starting scan on host: {target_ip}")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=400) as executor:
        futures_tcp = {executor.submit(scan_tcp_port, target_ip, port): port for port in range(start_port, end_port + 1)}
        futures_udp = {executor.submit(scan_udp_port, target_ip, port): port for port in range(start_port, end_port + 1)}

        tcp_results = {}
        udp_results = {}

        total_ports = end_port - start_port + 1

        for i, future in enumerate(concurrent.futures.as_completed(futures_tcp), start=1):
            port, service, banner, status = future.result()
            tcp_results[port] = (service, banner, status)
            sys.stdout.write(f"\rProgress: {i}/{total_ports} ports scanned (TCP)")
            sys.stdout.flush()

        for i, future in enumerate(concurrent.futures.as_completed(futures_udp), start=1):
            port = futures_udp[future]
            udp_status = future.result()
            udp_results[port] = udp_status
            sys.stdout.write(f"\rProgress: {i}/{total_ports} ports scanned (UDP)")
            sys.stdout.flush()

    sys.stdout.write("\n")

    for port in range(start_port, end_port + 1):
        service, banner, tcp_status = tcp_results.get(port, ("", "", False))
        udp_status = udp_results.get(port, False)
        try:
            if not service or service == 'Unknown':
                service = socket.getservbyport(port, 'udp')
        except:
            pass
        results.append((port, service, banner, tcp_status, udp_status))

    print(format_open_ports(results))

if __name__ == '__main__':
    target_host = input("Enter your target IP: ")
    start_port = int(input("Enter the start port: "))
    end_port = int(input("Enter the end port: "))

    port_scan(target_host, start_port, end_port)
