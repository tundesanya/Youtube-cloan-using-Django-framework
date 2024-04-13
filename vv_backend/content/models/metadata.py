from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

"""
Category, Language, Region: they seemed coupled, but 
1. Language and region are two mandatory fields that must be specified when the user uploads a content. 
    Not like category where user can select whatever they want. 
    Keeping them in a single category table will be hard to enforce this. 
2. Most importantly, considering that globe design and the TOP-k regional popular videos feature, 
    we need to frequently make queries regarding region/language. 
3. The exact usages of Language and Region are to be decided when we have more requirements/usecases, 
    for now, we all bit confused on how such information gonna be used. And we don't know if they require extra fields/modelling in the future. 
    So better to seperate them in three tables for now. 
"""

class Category(models.Model):
    name = models.CharField(unique=True, null=False)

class Language(models.Model):
    name = models.CharField(unique=True, null=False)

class Region(models.Model):
    name = models.CharField(unique=True, null=False)

class Hashtag(models.Model):
    name = models.CharField(unique=True, null=False)

# Differs from Hashtags
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class ContentTitle(models.Model):
    title_text = models.CharField(null=False)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, related_name = "titles")
    is_native = models.BooleanField(null=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True) # Its not a good idea to delete a content type anyway
    content_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'content_id')


### Additional Youtube fields
class VideoLocalization(models.Model):
    video = models.ForeignKey('content.Video', on_delete=models.CASCADE, related_name='video_localizations')
    language = models.CharField(max_length=10)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('video', 'language')

    def __str__(self):
        return f"{self.language}: {self.title}"
    
class ChannelDetail(models.Model):
    video = models.ForeignKey('content.Video', on_delete=models.CASCADE, related_name='channel_details')
    channel_title = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=255)
    
class ThumbnailDetail(models.Model):
    video = models.ForeignKey('content.Video', on_delete=models.CASCADE, related_name='thumbnail_details')
    # Where the image is stored.
    url = models.URLField(max_length=1024)
    width = models.IntegerField()
    height = models.IntegerField()