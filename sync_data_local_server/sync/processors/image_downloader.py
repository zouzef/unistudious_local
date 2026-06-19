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


# ─────────────────────────────────────────────
# Reference student images config (same API as old standalone script)
# ─────────────────────────────────────────────
REFERENCE_API_BASE_URL   = "https://www.unistudious.com"
REFERENCE_GET_REF_PATH   = "/slc/get-reference-student/"
REFERENCE_READ_FILE_PATH = "/slc/google-cloud/read-file"

# Download the reference images of the student (used for face recognition)
def download_student_reference_images(user_id, token):
	"""
	Fetch the list of reference images for a student from the remote server,
	then download any that don't already exist locally.

	Folder structure created:
		uploads/user_img/user_{user_id}/ref_img/{filename}

	args:
		user_id : The user's ID
		token   : Auth token (Bearer)

	returns:
		dict with counts: {"found": int, "downloaded": int, "skipped": int}
	"""
	import base64

	result = {"found": 0, "downloaded": 0, "skipped": 0}

	headers = {"Authorization": f"Bearer {token}"}

	try:
		list_url = f"{REFERENCE_API_BASE_URL}{REFERENCE_GET_REF_PATH}{user_id}"
		response = requests.post(list_url, headers=headers, timeout=15)
		response.raise_for_status()

		data = response.json()
		file_list = data.get("fileList", [])

		if not file_list:
			print(f"      No reference images found for user {user_id}")
			return result

		result["found"] = len(file_list)

	except requests.exceptions.ConnectionError:
		print(f"      ⚠️  Connection error fetching reference list for user {user_id}")
		return result
	except Exception as e:
		print(f"     Could not fetch reference list for user {user_id}: {e}")
		return result

	local_dir = os.path.join(LOCAL_IMAGE_BASE_DIR, f"user_{user_id}", "ref_img")
	os.makedirs(local_dir, exist_ok=True)

	for file_path in file_list:
		file_name = os.path.basename(file_path)
		local_path = os.path.join(local_dir, file_name)

		if os.path.exists(local_path):
			print(f"      Image already exists - skipped ({local_path})")
			result["skipped"] += 1
			continue

		try:
			read_url = f"{REFERENCE_API_BASE_URL}{REFERENCE_READ_FILE_PATH}"
			payload = {"fileName": file_path}
			print(f"     Downloading: {file_path}")

			response = requests.post(read_url, headers=headers, json=payload, timeout=15)
			response.raise_for_status()

			data = response.json()
			content = data.get("content")
			if not content:
				print(f"    No 'content' field in response for: {file_path}")
				continue

			image_data = base64.b64decode(content)
			with open(local_path, "wb") as f:
				f.write(image_data)

			print(f"    Saved to: {local_path}")
			result["downloaded"] += 1

		except requests.exceptions.ConnectionError:
			print(f"      ⚠️  Connection error downloading {file_path} for user {user_id}")
		except Exception as e:
			print(f"     Could not download {file_path} for user {user_id}: {e}")

	return result