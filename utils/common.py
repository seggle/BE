# from django.contrib.sites.models import Site
import uuid

IP_ADDR = "15.165.30.200:8000"

def upload_to_data(instance, filename):
    instance_slug = getattr(instance,"slug",False)
    if not instance_slug:
        instance_slug = str(uuid.uuid4()).replace("-","")
    return "uploads/{0}/{1}/{2}" . format (instance._meta.app_label, instance_slug, filename)

def upload_to_solution(instance, filename):
    instance_slug = getattr(instance,"slug",False)
    if not instance_slug:
        instance_slug = str(uuid.uuid4()).replace("-","")
    return "uploads/solution/{0}/{1}" . format (instance_slug, filename)

def upload_to_submission(instance, filename):
    return "uploads/submission/{0}/{1}" . format (instance.path.path, filename)

# def upload_to_submission_competition(instance, filename):
#     instance_slug = getattr(instance,"slug",False)
#     if not instance_slug:
#         instance_slug = str(uuid.uuid4()).replace("-","")
#     return "uploads/competition/submission/{0}/{1}" . format (instance_slug, filename)


# def upload_to(instance, filename):

#     current_site = Site.objects.get_current()
#     extension = filename.split(".")[-1]

#     instance_slug = getattr(instance,"slug",False)
#     if not instance_slug:
#         instance_slug = str(uuid.uuid4()).replace("-","")

#     return "{0}/uploads/{1}/{2}-{3}.{4}" . format (current_site.domain, instance._meta.app_label, instance_slug, instance.pk, extension)
