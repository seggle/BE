import urllib

from submission.models import SubmissionCompetition


def csv_download_windows(submission_path: str, base_dir: str | bytes) -> (str, str):
    base_dir = base_dir.replace("\\submission", "")
    csv_path = str(submission_path).split('uploads\\', 1)[1]
    filename = csv_path.split('\\', 2)[2]
    filename = urllib.parse.quote(filename.encode('utf-8'))
    filepath = base_dir + '\\uploads\\' + csv_path

    return filename, filepath


def csv_download_nix(submission_path: str, base_dir: str | bytes) -> (str, str):
    base_dir = base_dir.replace("/submission", "")

    csv_path = str(submission_path).split('uploads/', 1)[1]
    filename = csv_path.split('/', 2)[2]
    filename = urllib.parse.quote(filename.encode('utf-8'))
    filepath = base_dir + '/uploads/' + csv_path

    return filename, filepath


def ipynb_download_windows(submission_path: str, base_dir: str | bytes) -> (str, str):
    base_dir = base_dir.replace("\\submission", "")

    csv_path = str(submission_path).split('uploads\\', 1)[1]
    filename = csv_path.split('\\', 2)[2]
    filename = urllib.parse.quote(filename.encode('utf-8'))
    filepath = base_dir + '\\uploads\\' + csv_path

    return filename, filepath


def ipynb_download_nix(submission_path: str, base_dir: str | bytes) -> (str, str):
    base_dir = base_dir.replace("/submission", "")

    csv_path = str(submission_path).split('uploads/', 1)[1]
    filename = csv_path.split('/', 2)[2]
    filename = urllib.parse.quote(filename.encode('utf-8'))
    filepath = base_dir + '/uploads/' + csv_path

    return filename, filepath
