from __future__ import annotations

import datetime
from pathlib import Path
import zipfile
import io
from typing import Any, Dict, List
from enum import Enum
import portalocker
from django.db.models import QuerySet
from django.db import models
from competition.models import Competition
from submission.models import SubmissionCompetition, SubmissionClass
from utils import common


# TODO: Move archive related features to functions
# TODO: Make it fit to Class related views

# Create a new archive. Make a stream and write to file
def creat_archive(filepath: Path, base_dir: Path,
                  submission_targets: Dict[str, List[SubmissionCompetition or SubmissionClass]]) -> None:
    archive_buffer = io.BytesIO()

    with zipfile.ZipFile(archive_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for username in submission_targets.keys():
            front_str = username
            pre_dir = '.'

        for elem in submission_targets[username]:
            jupyter = elem.ipynb.name
            put_archive_object(archive, elem, jupyter, '.ipynb', pre_dir, base_dir, front_str)
            csv = elem.csv.name
            put_archive_object(archive, elem, csv, '.csv', pre_dir, base_dir, front_str)

    with open(filepath, 'wb') as f:
        portalocker.portalocker.lock(f, portalocker.LockFlags.EXCLUSIVE)
        f.write(archive_buffer.getbuffer())
        portalocker.portalocker.unlock(f)


def put_archive_object(archive: zipfile.ZipFile, material: Any, file_field: str, extension: str, pre_dir: str,
                       base_dir: Path, front_str: str) -> None:
    arc_filename = Path(get_archive_filename(pre_dir, material.created_time, extension, front_str=front_str))
    path = base_dir / file_field
    archive.write(filename=str(path), arcname=str(arc_filename))


# Regular Expression을 이용해 datetime을 2010-3-1 이런 식으로 바꿔서 파일 이름을 만듦
def get_archive_filename(path: str, file_date: datetime.datetime, extension: str,
                         front_str: str = None) -> str:
    name = path + '/'
    if front_str is not None:
        name += front_str + '_'
    name += common.convert_date_format(file_date) + extension

    return name
