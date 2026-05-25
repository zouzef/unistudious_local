import socket
import json
import os


def get_local_ip():
	"""Get the actual local IP address of this machine."""
	try:
		# Connect to external address to find local IP
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		ip = s.getsockname()[0]
		s.close()
		return ip
	except Exception:
		return "127.0.0.1"


def update_tablet_config():
	"""Update tablet_configuration.json with current server IP."""

	# Path to tablet config file
	tablet_config_path = os.path.join(
		os.path.dirname(__file__),
		"../tablette_app/tablet_configuration.json"
	)

	# Get current IP and port
	current_ip = get_local_ip()
	port = 5004  # your static port

	# Load existing config
	with open(tablet_config_path, "r") as f:
		config = json.load(f)

	# Update only the API_BASE_URL
	old_url = config["url"]["API_BASE_URL"]
	new_url = f"https://{current_ip}:{port}/scl"
	config["url"]["API_BASE_URL"] = new_url

	# Save back to file
	with open(tablet_config_path, "w") as f:
		json.dump(config, f, indent=2)

	print(f"✅ Tablet config updated!")
	print(f"   Old URL: {old_url}")
	print(f"   New URL: {new_url}")


def update_attendance_system_config():
    """Update attendance_system/configuration.json with current server IP."""

    attendance_config_path = os.path.join(
        os.path.dirname(__file__),
        "../attendance_system/configurations.json"
    )

    current_ip = get_local_ip()
    port = 5004  # your static port

    with open(attendance_config_path, "r") as f:
        config = json.load(f)

    old_url = config["slc_config"]["BASE_URL"]
    new_url = f"https://{current_ip}:{port}/scl"
    config["slc_config"]["BASE_URL"] = new_url

    with open(attendance_config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Attendance config updated!")
    print(f"   Old URL: {old_url}")
    print(f"   New URL: {new_url}")


def update_local_web_config():
    local_web_unistudious = os.path.join(
        os.path.dirname(__file__),
        "../unistudious_local_web/config.json"
    )
    current_ip = get_local_ip()

    with open(local_web_unistudious, "r") as f:
        config = json.load(f)

    # Read port from the config instead of hardcoding it
    port = 5004

    old_url = config["external_api"]["base_url"]
    new_url = f"https://{current_ip}:{port}/scl/"

    config["external_api"]["base_url"] = new_url  # fixed key path + consistent casing

    with open(local_web_unistudious, "w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Local Web config updated!")
    print(f"   Old URL: {old_url}")
    print(f"   New URL: {new_url}")