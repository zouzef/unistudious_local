# Presence API

Base URL: `/scl`

Authentication required for all endpoints except image serving.

Manages face detection, unknown student identification, and attendance verification through the **academie_attendance_system** integration.

**External Dependencies:**
- `academie_attendance_system/dataset` - Face detection dataset storage
- `academie_attendance_system/user_students` - Known student face images

---

## Endpoints

### 1. Associate Known Student Attendance
**POST** `/scl/associate-known-student-attendance/<session_id>`

Associate an unknown face folder with a known student and mark them present.

**Parameters:**
- `session_id` (int): Session ID

**Request Body:**
```json
{
  "userId": 123,
  "folder": "person_001",
  "calanderId": 456,
  "attendanceId": 789
}
```

**Process:**
1. Validates user, calendar, and attendance exist
2. Moves all images from unknown folder to user's folder
3. Marks attendance as present
4. Adds audit trail
5. Deletes empty unknown folder

**Response (200):**
```json
{
  "success": true,
  "message": "Successfully moved 15 files from person_001 to user 123",
  "filesMoved": 15
}
```

**Response (400):**
```json
{
  "error": "Missing required parameters"
}
```

**Response (404):**
```json
{
  "error": "Source folder not found: person_001"
}
```

---

### 2. Delete Folder of Unknown User
**DELETE** `/scl/delete_folder_user/<calander_id>`

Delete an entire unknown person folder.

**Parameters:**
- `calander_id` (int): Calendar ID

**Request Body:**
```json
{
  "folderName": "person_001"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Folder deleted successfully"
}
```

**Response (400):**
```json
{
  "error": "Missing userId or folderName"
}
```

**Response (404):**
```json
{
  "error": "Folder does not exist"
}
```

---

### 3. Delete Image from Folder
**POST** `/scl/delete_image_folder/<calander_id>`

Delete a specific image from an unknown person folder.

**Parameters:**
- `calander_id` (int): Calendar ID

**Request Body:**
```json
{
  "folder": "person_001",
  "file_name": "face_001.jpg"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Image deleted successfully"
}
```

**Response (404):**
```json
{
  "error": "Image does not exist"
}
```

---

### 4. Get Unknown Student Attendance
**GET** `/scl/get-unknown-student-attendance/<calenderId>`

Get list of students with attendance records for a calendar.

**Parameters:**
- `calenderId` (int): Calendar ID

**Response (200):**
```json
{
  "success": true,
  "students": [
    {
      "id": 123,
      "name": "John Doe",
      "email": "john@example.com",
      "attendanceId": 789
    }
  ]
}
```

**Response (500):**
```json
{
  "success": false,
  "error": "Internal server error"
}
```

---

### 5. Serve Unknown Image
**GET** `/scl/unknown-image/<session_id>/<person_folder>/<filename>`

Serve an image file from the unknown faces directory.

**Parameters:**
- `session_id` (int): Session ID
- `person_folder` (string): Folder name (e.g., "person_001")
- `filename` (string): Image filename (e.g., "face_001.jpg")

**Authentication:** Not required (public image serving)

**Example:**
```
GET /scl/unknown-image/5/person_001/face_001.jpg
```

**Response (200):**
Returns the image file (binary)

**Response (404):**
```json
{
  "error": "Image not found"
}
```

---

### 6. Show Attendance Unknown Students
**GET** `/scl/show-attendance-unknown/<calender_id>`

Get all unknown face folders with up to 6 sample images each.

**Parameters:**
- `calender_id` (int): Calendar ID

**Configuration:**
- `MAX_IMAGES_PER_FOLDER`: 6 images maximum per folder

**Response (200):**
```json
{
  "unknownFilesGrouped": {
    "person_001": [
      {
        "url": "/scl/unknown-image/5/person_001/face_001.jpg",
        "filename": "face_001.jpg",
        "type": "image"
      },
      {
        "url": "/scl/unknown-image/5/person_001/face_002.jpg",
        "filename": "face_002.jpg",
        "type": "image"
      }
    ],
    "person_002": [
      {
        "url": "/scl/unknown-image/5/person_002/face_001.jpg",
        "filename": "face_001.jpg",
        "type": "image"
      }
    ]
  },
  "calendarId": 5
}
```

**Supported File Types:**
- **Images:** jpg, jpeg, png, gif, webp, bmp
- **Videos:** mp4, avi, mov, mkv, webm

**Response (200) - No Unknown Faces:**
```json
{
  "unknownFilesGrouped": {},
  "calendarId": 5
}
```

---

## File Structure

### Unknown Faces Directory
```
academie_attendance_system/
└── dataset/
    └── session_{session_id}/
        └── face_crops/
            └── classified_unknown/
                ├── person_001/
                │   ├── face_001.jpg
                │   ├── face_002.jpg
                │   └── ...
                └── person_002/
                    ├── face_001.jpg
                    └── ...
```

### Known Students Directory
```
academie_attendance_system/
└── user_students/
    ├── 123/
    │   ├── face_001.jpg
    │   ├── face_002.jpg
    │   └── ...
    └── 456/
        └── ...
```

---

## Audit Tables

This API logs operations in:
- `sync_images` - Tracks image movements
- `association_audit` - Tracks folder-to-user associations

---

## Error Responses

All endpoints may return:

**Response (500):**
```json
{
  "error": "Error description"
}
```
or
```json
{
  "status": "Error ...",
  "message": "Invalid JSON data"
}
```