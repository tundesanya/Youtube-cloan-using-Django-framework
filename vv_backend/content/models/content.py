import uuid

from django.db import models
from django.contrib.contenttypes.models import ContentType

from users.models import User
from user_interactions.models import Comment, LikeDislike, PlaylistContent
from content.models.people import ContentPersonnelCast, ContentPersonnelProduce
from content.models.metadata import Category, Language, Region, Hashtag, ContentTitle, Tag, ThumbnailDetail, ChannelDetail, VideoLocalization

# TODO: Nishil - Would media be a better name than content?

class BaseContentModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_uploaded_contents')

    # Content Own Properties
    duration = models.DurationField(null=True)
    description = models.TextField(null=True)
    released_date = models.DateField(null=True)
    original_language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, related_name='%(class)s_all_contents')
    upload_region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='%(class)s_all_contents')
    categories = models.ManyToManyField(Category, related_name='%(class)s_all_contents')
    hashtags = models.ManyToManyField(Hashtag, related_name='%(class)s_all_contents')
    score_imdb = models.DecimalField(null=True, max_digits=3, decimal_places=1) # 0.0 - 10.0, 3 digits max, 1 decimal_place

    # inferenced viewer stats data 
    like_count = models.IntegerField(default=0)
    dislike_count = models.IntegerField(default=0)
    view_count = models.BigIntegerField(default=0)
    comment_count = models.IntegerField(default=0)

    # time related auto-updated data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    """
    Ziming: This is assuming that we treat "file" as static assets configured with Django's static storage setting
    This field will contains a URL to access the files as static assets. 
    However, for more sophisticated features such as user access control (only login user can watch the video), I don't think this will work. 
    This need more knowledge of AWS's video on-demand streaming services as well s3's pre-signed URL perhaps. 
    """
    file = models.FileField()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        """
        Override delete method, so that we can delete all related comments/like-dislikes/, and removing it from all playlists
        """
        # Delete all related comments
        Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            content_id=self.id
        ).delete()

        # delete all related like-dislikes
        LikeDislike.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            content_id=self.id
        ).delete()

        # remove from all playlists
        PlaylistContent.objects.filter(
            content_type=ContentType.objects.get_for_model(self), 
            content_id=self.id
        ).delete()
        
        # remove all cast table entries 
        ContentPersonnelCast.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            content_id=self.id
        ).delete()

        # remove all produce table entries
        ContentPersonnelProduce.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            content_id=self.id
        ).delete()

        # remove all titles
        ContentTitle.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            content_id=self.id
        ).delete()

        # call parent method to actually delete the content itself
        super().delete(*args, **kwargs)

class Video(BaseContentModel):
    # file format
    class VideoFileFormat(models.IntegerChoices):
        UNSPECIFIED = 0, 'UNSPECIFIED'
        MP4 = 1, 'MP4', 
        AVI = 2, 'AVI', 
        MOV = 3, 'MOV',   
        MKV = 4, 'MKV', 
    format = models.IntegerField(
        choices = VideoFileFormat.choices, 
        default = VideoFileFormat.UNSPECIFIED
    )

    youtube_video_id = models.CharField(max_length=255, unique=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='videos')

    # 2D or 3D
    dimension = models.CharField(max_length=10, null=True)
    # HD or SD
    definition = models.CharField(max_length=10, null=True)
    caption = models.BooleanField(default=False)
    # whether the content was uploaded to a channel linked to a YouTube content partner and then claimed by that partner
    licensed_content = models.BooleanField(default=False)
    # 360 or rectangular
    projection = models.CharField(max_length=255, null=True)
    has_custom_thumbnail = models.BooleanField(default=False)
    default_language = models.CharField(max_length=255, null=True)
    default_audio_language = models.CharField(max_length=255, null=True)
    live_broadcast_content = models.CharField(max_length=255, null=True)

    # Video status, may or may not be needed.
    upload_status = models.CharField(max_length=255, null=True)
    privacy_status = models.CharField(max_length=255, null=True)
    # Time the video is scheduled to publish
    publish_at = models.DateTimeField(auto_now=True)
    #Type of licensing: creative Commons or Youtube
    license = models.CharField(max_length=255, null=True)

    embeddable = models.BooleanField(default=False)
    public_stats_viewable = models.BooleanField(default=True)
    made_for_kids = models.BooleanField(default=False)
    self_declared_made_for_kids = models.BooleanField(default=False)

    thumbnail = models.OneToOneField(ThumbnailDetail, on_delete=models.CASCADE, related_name='%(class)s_details', null=True,blank=True)
    channel_info = models.OneToOneField(ChannelDetail, on_delete=models.CASCADE, related_name='%(class)s_details',null=True,blank=True)
    localization = models.OneToOneField(VideoLocalization, on_delete=models.CASCADE, related_name='%(class)s_details',null=True,blank=True)

  


class Podcast(BaseContentModel):
    # file format
    class AudioFileFormat(models.IntegerChoices):
        UNSPECIFIED = 0, 'UNSPECIFIED'
        MP3 = 1, 'MP3', 
        WAV = 2, 'WAV', 
        AAC = 3, 'AAC',   
        FLAC = 4, 'FLAC', 
    format = models.IntegerField(
        choices = AudioFileFormat.choices, 
        default = AudioFileFormat.UNSPECIFIED, 
    )