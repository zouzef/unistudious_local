# detection/network.py

import socket
from scapy.all import ARP, Ether, srp
from utils.logger import logger


def get_local_subnet() -> str:
    """Detect the local network subnet automatically."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    subnet = local_ip.rsplit('.', 1)[0] + '.0/24'
    logger.info(f"Detected local IP: {local_ip} — subnet: {subnet}")
    return subnet


def scan_all_devices(subnet: str = None) -> list:
    """Scan network and return list of devices with ip and mac."""
    if subnet is None:
        subnet = get_local_subnet()

    logger.info(f"Scanning network: {subnet}")
    try:
        arp    = ARP(pdst=subnet)
        ether  = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp
        result = srp(packet, timeout=3, verbose=0)[0]

        devices = [
            {"ip": received.psrc, "mac": received.hwsrc}
            for sent, received in result
        ]

        if devices:
            logger.info(f"Found {len(devices)} device(s) on network.")
            for d in devices:
                logger.info(f"  IP: {d['ip']} — MAC: {d['mac']}")
        else:
            logger.warning("No devices found on network.")

        return devices

    except Exception as e:
        logger.error(f"Network scan failed: {e}")
        return []