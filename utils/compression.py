from __future__ import annotations

import datetime
from pathlib import Path
import zipfile
import io
from typing import Any
from enum import Enum
import portalocker
from django.db.models import QuerySet
from django.db import models
from competition.models import Competition
from submission.models import SubmissionCompetition, SubmissionClass
from utils import common


# TODO: Move archive related features to functions
# TODO: Make it fit to Class related views

# Target selection mode defined enum class
class SubmissionArchiveMode(Enum):
    ALL = 0
    LATEST = 1
    HIGHEST = 2


# Create a new archive. Make a stream and write to file
def creat_archive(filepath: Path, base_dir: Path, submission_targets: QuerySet[SubmissionCompetition | SubmissionClass],
                  usernames: list, target_mode: SubmissionArchiveMode = SubmissionArchiveMode.ALL) -> None:
    archive_buffer = io.BytesIO()

    with zipfile.ZipFile(archive_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        extra_str = None

        # Pattern Matching (Python 3.10 or above)
        '''
        match target_mode:
            case SubmissionArchiveMode.LATEST:
                extra_str = 'latest'
            case SubmissionArchiveMode.HIGHEST:
                extra_str = 'highest'
        '''
        if target_mode == SubmissionArchiveMode.LATEST:
            extra_str = 'latest'
        elif target_mode == SubmissionArchiveMode.HIGHEST:
            extra_str = 'highest'

        for user in usernames:
            front_str = user
            pre_dir = '.'
            user_submissions = submission_targets.filter(username=user)

            if target_mode == SubmissionArchiveMode.LATEST:
                latest_submission = user_submissions.latest('created_time')
                put_archive_object(archive, latest_submission, str(latest_submission.ipynb), '.ipynb', pre_dir,
                                   base_dir, front_str, extra_str)
                put_archive_object(archive, latest_submission, str(latest_submission.csv), '.csv', pre_dir, base_dir,
                                   front_str, extra_str)
                continue
            elif target_mode == SubmissionArchiveMode.HIGHEST:
                highest_submission = user_submissions.order_by('-score', '-created_time').first()
                put_archive_object(archive, highest_submission, str(highest_submission.ipynb), '.ipynb', pre_dir,
                                   base_dir, front_str, extra_str)
                put_archive_object(archive, highest_submission, str(highest_submission.csv), '.csv', pre_dir, base_dir,
                                   front_str, extra_str)
                continue

            pre_dir += '/' + user

            for material in user_submissions:
                put_archive_object(archive, material, str(material.ipynb), '.ipynb', pre_dir,
                                   base_dir, front_str, extra_str)
                put_archive_object(archive, material, str(material.csv), '.csv', pre_dir, base_dir,
                                   front_str, extra_str)

    with open(filepath, 'wb') as f:
        portalocker.portalocker.lock(f, portalocker.LockFlags.EXCLUSIVE)
        f.write(archive_buffer.getbuffer())
        portalocker.portalocker.unlock(f)


def put_archive_object(archive: zipfile.ZipFile, material: Any, file_field: str, extension: str, pre_dir: str,
                       base_dir: Path, front_str: str, extra_str: str) -> None:
    arc_filename = Path(get_archive_filename(pre_dir, material.created_time, extension, extra_str, front_str))
    path = base_dir / file_field
    archive.write(filename=str(path), arcname=str(arc_filename))


# Regular Expression을 이용해 datetime을 2010-3-1 이런 식으로 바꿔서 파일 이름을 만듦
def get_archive_filename(path: str, file_date: datetime.datetime, extension: str,
                         extra_str: str = None, front_str: str = None) -> str:
    name = path + '/'
    if front_str is not None:
        name += front_str + '_'
    name += common.convert_date_format(file_date)
    if extra_str is not None:
        name += '_' + extra_str
    name += extension

    return name
