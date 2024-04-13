from django.contrib import admin

from user_interactions.models import Comment, LikeDislike, Playlist, PlaylistContent

admin.site.register(
    [
        Comment,
        LikeDislike,
        Playlist,
        PlaylistContent
    ]
)