import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive, GoogleDriveFile


def __get_drive_auth(auth_credentials_file: str = None) -> GoogleDrive:
    if auth_credentials_file is None:
        auth_credentials_file = "credentials.txt"

    auth: GoogleAuth = GoogleAuth()
    auth.LoadCredentialsFile(auth_credentials_file)

    if auth.credentials is None:
        auth.LocalWebserverAuth()
    elif auth.access_token_expired:
        auth.Refresh()
    else:
        auth.Authorize()

    auth.SaveCredentialsFile(auth_credentials_file)
    drive: GoogleDrive = GoogleDrive(auth)

    return drive


def upload_drive_file_to_google_drive(drive_file: GoogleDriveFile, content_type: str = "") -> (str, str):
    drive_file.Upload()
    drive_file.InsertPermission({
        'type': 'anyone',
        'value': 'anyone',
        'role': 'reader'
    })

    content_link: str = drive_file.get('alternateLink')
    content_id: str = drive_file.get('id')

    print(f"{content_type.title()} is uploaded to google drive. You can access it from here: {content_link}")
    return content_id, content_link


def upload_folder_to_drive(folder: str, folder_id: str = None, auth_credentials_file: str = None) -> (str, str):
    drive: GoogleDrive = __get_drive_auth(auth_credentials_file)

    if folder_id is not None:
        parents: dict = {'parents': [{'id': folder_id}]}
    else:
        parents: dict = {}

    folder: GoogleDriveFile = drive.CreateFile({**parents, 'title': folder.split("/")[-1], 'mimeType': 'application/vnd.google-apps.folder'})
    return upload_drive_file_to_google_drive(folder, "Folder")


def upload_file_to_drive(_file: str, folder_id: str = None, auth_credentials_file: str = None) -> (str, str):
    drive: GoogleDrive = __get_drive_auth(auth_credentials_file)

    if folder_id is not None:
        parents: dict = {'parents': [{'id': folder_id}]}
    else:
        parents: dict = {}

    file: GoogleDriveFile = drive.CreateFile({**parents, 'title': _file.split("/")[-1]})
    file.SetContentFile(_file)
    return upload_drive_file_to_google_drive(file, "File")


# upload folder and contents recursively
def upload_folder_to_drive_recursively(folder: str, folder_id: str = None) -> (str, str):
    folder_info: (str, str) = upload_folder_to_drive(folder, folder_id)
    folder_id: str = folder_info[0]
    folder_link: str = folder_info[1]

    for content in os.listdir(folder):
        content_path: str = os.path.join(folder, content)
        if os.path.isdir(content_path):
            upload_folder_to_drive_recursively(content_path, folder_id)
        else:
            upload_file_to_drive(content_path, folder_id)

    return folder_id, folder_link
