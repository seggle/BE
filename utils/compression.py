from pathlib import Path
import zipfile
import io
import portalocker
from django.db.models import QuerySet

from competition.models import Competition
from utils.common import get_archive_filename

# TODO: Move archive related features to functions
# TODO: Make it fit to Class related views


# Create a new archive. Make a stream and write to file
def creat_archive(filepath: Path, filename: str, base_dir: Path, submission_targets: QuerySet,
                 usernames: list, competition_info: Competition, is_latest_only=False) -> None:

    archive_buffer = io.BytesIO()

    with zipfile.ZipFile(archive_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        extra_str = None if is_latest_only is False else 'latest'
        for user in usernames:
            front_str = None
            pre_dir = '.'
            user_submissions = submission_targets.filter(username=user)
            if is_latest_only is True:
                user_submissions = user_submissions.latest('created_time')
                front_str = user
            else:
                archive.mkdir(user)
                pre_dir += '/' + user

            for material in user_submissions:
                arc_filename = Path(get_archive_filename(pre_dir, material.created_time, '.ipynb', extra_str, front_str))
                path = base_dir / str(material.ipynb)
                archive.write(filename=str(path), arcname=str(arc_filename))
                arc_filename = Path(get_archive_filename(pre_dir, material.created_time, '.csv', extra_str, front_str))
                path = base_dir / str(material.csv)
                archive.write(filename=str(path), arcname=str(arc_filename))

    with open(filepath, 'wb') as f:
        f.write(archive_buffer.getbuffer())
