import datetime
import platform
import uuid
import re
from pathlib import Path
from django.utils import timezone
import tzdata

IP_ADDR = "15.165.30.200:8000"


def upload_to_data(instance, filename):
    instance_slug = getattr(instance, "slug", False)
    if not instance_slug:
        instance_slug = str(uuid.uuid4()).replace("-", "")
    return "uploads/{0}/{1}/{2}".format(instance._meta.app_label, instance_slug, filename)


def upload_to_solution(instance, filename):
    instance_slug = getattr(instance, "slug", False)
    if not instance_slug:
        instance_slug = str(uuid.uuid4()).replace("-", "")
    return "uploads/solution/{0}/{1}".format(instance_slug, filename)


def upload_to_submission(instance, filename):
    return "uploads/submission/{0}/{1}".format(instance.path.path, filename)


# OS에 맞춰 파일 이름을 추출해 반환
def get_filename(filepath: str) -> str:
    if platform.system() == 'Windows':
        filename = filepath.split('\\')[-1]
    else:
        filename = filepath.split('/')[-1]

    return filename


# Convert datetime format with user requested separator and regular expression
def convert_date_format(date: datetime.datetime, separator: str = '-', rexp: str = None) -> str:
    rexp = rexp if rexp is not None else '[ :\-.]'
    elems = re.split(rexp, str(date))

    return separator.join(elems)


# 여러 층에 걸쳐 디렉토리를 만듦
def make_mult_level_dir(current_path: Path, target: str) -> None:
    dirs = target.split('/')
    for d in dirs:
        current_path /= d
        if current_path.is_dir() is False:
            current_path.mkdir()


# 현재 시간보다 이전에 끝난 경우 False를 반환
def is_temp(date: datetime.datetime) -> bool:
    return False if datetime.datetime.now() > date else True
