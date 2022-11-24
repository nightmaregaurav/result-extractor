import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive, GoogleDriveFile

from src.utils import start_progress_spinner, stop_progress_spinner

auth_credentials_file = "client_secrets_credentials.txt"


def prepare_google_drive_credentials(auth: GoogleAuth) -> None:
    if auth.credentials is None:
        auth.LocalWebserverAuth()
    elif auth.access_token_expired:
        auth.Refresh()
    else:
        auth.Authorize()


def __get_drive_auth() -> GoogleDrive:
    auth: GoogleAuth = GoogleAuth()

    if os.path.exists(auth_credentials_file):
        auth.LoadCredentialsFile(auth_credentials_file)

    while True:
        # noinspection PyBroadException
        try:
            prepare_google_drive_credentials(auth)
            break
        except Exception:
            print("Google Drive Authentication Failed! Will retry...")
            pass

    auth.SaveCredentialsFile(auth_credentials_file)
    drive: GoogleDrive = GoogleDrive(auth)

    return drive


def upload_drive_file_to_google_drive(drive_file: GoogleDriveFile, content_type: str = "") -> (str, str):
    progress_message: str = "Uploading " + content_type.title() + " " + drive_file['title']
    with start_progress_spinner(progress_message) as progress_thread:
        while True:
            # noinspection PyBroadException
            try:
                drive_file.Upload()
                drive_file.InsertPermission({
                    'type': 'anyone',
                    'value': 'anyone',
                    'role': 'reader'
                })
                content_link: str = drive_file.get('alternateLink')
                content_id: str = drive_file.get('id')
                stop_progress_spinner(progress_thread, f"Done: {content_link}")
                break
            except Exception:
                progress_thread.write(f"{progress_message} Failed! Will retry...")

    return content_id, content_link


def upload_folder_to_drive(folder: str, folder_id: str = None) -> (str, str):
    drive: GoogleDrive = __get_drive_auth()

    if folder_id is not None:
        parents: dict = {'parents': [{'id': folder_id}]}
    else:
        parents: dict = {}

    folder: GoogleDriveFile = drive.CreateFile({**parents, 'title': folder.split("/")[-1], 'mimeType': 'application/vnd.google-apps.folder'})
    return upload_drive_file_to_google_drive(folder, "Folder")


def upload_file_to_drive(_file: str, folder_id: str = None) -> (str, str):
    drive: GoogleDrive = __get_drive_auth()

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
