import os
import requests


# ─────────────────────────────────────────────
# CONFIGURATION - update to match your setup
# ─────────────────────────────────────────────
_PROJECT_ROOT        = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
LOCAL_IMAGE_BASE_DIR = os.path.join(_PROJECT_ROOT, "server_local_api", "uploads", "user_img")
LOCAL_IMAGE_ACADEMIE_DIR = os.path.join(_PROJECT_ROOT, "server_local_api", "uploads", "academie_img")
LOCAL_IMAGE_SESSION_BASE_DIR = os.path.join(_PROJECT_ROOT,"server_local_api","uploads","session_img")
REMOTE_IMAGE_BASE_URL = "https://www.unistudious.com/slc/private-image-server/"
REMOTE_IMAGE_PUBLIC_BASE_URL = "https://www.unistudious.com/slc/public-image-server/"
# ─────────────────────────────────────────────

# Download the image profile of the user
def download_user_image(user_id, image_filename,token):
	"""
	Download a user image from the remote server and save it locally
	Folder structure created:
		server_local_api/uploads/user_img/user_{user_id}/{image_filename}
	args:
		user_id        : The user's ID (used to name the folder)
		image_filename : The filename from the API 'image' field (e.g.photo.jpg')
	
	returns:
		True if downloaded or alreay exists, False if failed 
	:param user_id: 
	:param image_filename: 
	:return: 
	"""
	if not image_filename:
		print(f"      No image filename for user {user_id} - skipping ")
		return False


	try:
		local_dir = os.path.join(LOCAL_IMAGE_BASE_DIR, f"user_{user_id}")
		local_path = os.path.join(local_dir, image_filename)

		os.makedirs(local_dir, exist_ok=True)
		if os.path.exists(local_path):
			print(f"      Image already exists - skipped ({local_path})")
			return True

		remote_url = f"{REMOTE_IMAGE_BASE_URL}{image_filename}"
		print(f"     Downloading: {remote_url}")
		headers = {"Authorization": f"Bearer {token}"}

		response = requests.post(remote_url,headers = headers ,timeout=15)
		if response.status_code == 200:
			with open(local_path,"wb") as f:
				f.write(response.content)
			print(f"    Saved to: {local_path}")
			return True
		else:
			print(f"    Remote returned {response.status_code} for: {remote_url}")
			return False
	except requests.exceptions.ConnectionError:
		print(f"      ⚠️  Connection error for user {user_id}")
		return False
	except Exception as e:
		print(f"     Could not download image for user :{user_id}: {e}")
		return False

# Download the image of the session
def download_session_image(session_id,img_filename,token):
	if not(img_filename):
		print(f"      No image filename for user {session_id} - skipping ")
		return False

	try:
		local_dir = os.path.join(LOCAL_IMAGE_SESSION_BASE_DIR, f"session_{session_id}")
		local_path = os.path.join(local_dir, img_filename)
		os.makedirs(local_dir,exist_ok=True)
		if os.path.exists(local_path):
			print(f"      Image already exists - skipped ({local_path})")
			return True

		remote_url = f"{REMOTE_IMAGE_PUBLIC_BASE_URL}{img_filename}"
		headers= {"Authorization":f"Bearer {token}"}
		response = requests.post(remote_url,headers=headers,verify=False,timeout=15)
		if response.status_code == 200:
			with open(local_path,"wb") as f:
				f.write(response.content)
			print(f"    Saved to: {local_path}")
			return True
		else:
			print(f"    Remote returned {response.status_code} for: {remote_url}")
			return False
	except requests.exceptions.ConnectionError:
		print(f"      ⚠️  Connection error for session {session_id}")
		return False

	except Exception as e:
		print(f"     Could not download image for session :{session_id}: {e}")
		return False

# Download the image of the academie
def download_academie_image(account_id,img_filename,token):

	if not(img_filename):
		print(f"      No image filename for academie {account_id} - skipping ")
		return False
	try:
		local_dir = os.path.join(LOCAL_IMAGE_ACADEMIE_DIR,f"academie_{account_id}")
		local_path = os.path.join(local_dir, img_filename)
		os.makedirs(local_dir,exist_ok=True)
		if os.path.exists(local_path):
			print(f"      Image already exists - skipped ({local_path})")
			return True
		remote_url = f"{REMOTE_IMAGE_PUBLIC_BASE_URL}{img_filename}"
		headers= {"Authorization":f"Bearer {token}"}
		response = requests.post(remote_url,headers=headers,verify=False,timeout=15)
		if response.status_code == 200:
			with open(local_path,"wb") as f:
				f.write(response.content)
			print(f"    Saved to: {local_path}")
			return True
		else:
			print(f"    Remote returned {response.status_code} for: {remote_url}")
			return False
	except requests.exceptions.ConnectionError:
		print(f"      ⚠️  Connection error for academie {account_id}")
		return False

	except Exception as e:
		print(f"     Could not download image for academie :{account_id}: {e}")
		return False
