import uuid

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# TODO: Nishil - I think we should have just one people model for any and all people, cast, crew, etc.

class IndustryPersonnel(models.Model):
    """
    actor/producer/host/staff...
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField()
    middle_name = models.CharField()
    last_name = models.CharField()
    # other fields can be added if needed

class ContentPersonnelCast(models.Model):
    personnel = models.ForeignKey(IndustryPersonnel, on_delete=models.CASCADE, related_name="cast_contents_table_entries")

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True) # Its not a good idea to delete a content type anyway
    content_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'content_id')

    class CastType(models.IntegerChoices):
        UNSPECIFIED = 0, 'UNSPECIFIED'
        MAIN_ACTOR = 1, 'MAIN_ACTOR'
        SUPPORT_ACTOR = 2, "SUPPORT_ACTOR"
    cast_type = models.IntegerField(
        choices = CastType.choices, 
        default = CastType.UNSPECIFIED, 
    )

class ContentPersonnelProduce(models.Model):
    personnel = models.ForeignKey(IndustryPersonnel, on_delete=models.CASCADE, related_name='produce_contents_table_entries')

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True) # Its not a good idea to delete a content type anyway
    content_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'content_id')

    class ProduceType(models.IntegerChoices):
        UNSPECIFIED = 0, 'UNSPECIFIED'
        DIRECTOR = 1, 'DIRECTOR'
        PRODUCER = 2, 'PRODUCER'
    produce_type = models.IntegerField(
        choices = ProduceType.choices, 
        default = ProduceType.UNSPECIFIED, 
    )