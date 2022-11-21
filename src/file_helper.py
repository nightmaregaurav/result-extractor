import os

import weasyprint
from pdf2image import convert_from_path


def create_pdf_from_html(file_path: str) -> None:
    html = weasyprint.HTML(file_path)
    html.write_pdf(file_path.replace(".html", ".pdf"))


def create_images_from_pdf(file_path: str) -> None:
    try:
        os.makedirs(file_path.replace(".pdf", ""))
    except FileExistsError:
        pass

    images: list = convert_from_path(file_path)
    for index, image in enumerate(images):
        image.save(f'{file_path.replace(".pdf", "")}/Page-{index + 1}.jpg', "JPEG")


def make_pdf_files(folder_name: str) -> None:
    for file in os.listdir(folder_name):
        if file.endswith(".html"):
            create_pdf_from_html(folder_name + "/" + file)


def make_image_files(folder_name: str) -> None:
    for file in os.listdir(folder_name):
        if file.endswith(".pdf"):
            create_images_from_pdf(folder_name + "/" + file)


def move_pdfs_in_pdf_folder(folder_name: str) -> None:
    try:
        os.makedirs(folder_name + "/pdfs")
    except FileExistsError:
        pass

    for file in os.listdir(folder_name):
        if file.endswith(".pdf") and not file.endswith("summary.pdf"):
            os.rename(folder_name + "/" + file, folder_name + "/pdfs/" + file)


def move_htmls_in_html_folder(folder_name: str) -> None:
    try:
        os.makedirs(folder_name + "/htmls")
    except FileExistsError:
        pass

    for file in os.listdir(folder_name):
        if file.endswith(".html") and not file.endswith("summary.html"):
            os.rename(folder_name + "/" + file, folder_name + "/htmls/" + file)


def move_folders_to_images_folder(folder_name: str) -> None:
    try:
        os.makedirs(folder_name + "/images")
    except FileExistsError:
        pass

    for file in os.listdir(folder_name):
        if os.path.isdir(folder_name + "/" + file)\
                and not file.endswith("pdfs")\
                and not file.endswith("htmls")\
                and not file.endswith("images")\
                and not file.endswith("summary"):
            os.rename(folder_name + "/" + file, folder_name + "/images/" + file)
