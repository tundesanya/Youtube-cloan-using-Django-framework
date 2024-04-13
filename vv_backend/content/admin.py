from django.contrib import admin

from content.models.content import Video, Podcast
from content.models.metadata import Category, Language, Region, Hashtag, Tag, ContentTitle, ChannelDetail, ThumbnailDetail, VideoLocalization
from content.models.people import IndustryPersonnel, ContentPersonnelCast, ContentPersonnelProduce

admin.site.register(
    [
        # Content
        Video,
        Podcast,
        # Metadata
        Category,
        Language,
        Region,
        Hashtag,
        Tag,
        ContentTitle,
        ChannelDetail, 
        ThumbnailDetail,
        # People
        IndustryPersonnel,
        ContentPersonnelCast,
        ContentPersonnelProduce,
        VideoLocalization
    ]
)