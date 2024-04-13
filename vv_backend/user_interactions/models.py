import uuid

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from users.models import User

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    """
    Ziming: 
    these three lines make sure we don't need seperate Video_Comment, Podcast_Comment, and furthermore, Video_like and Podcast_like
    
    Sample usage: 

    video_instance = Video.objects.get(id=video_id)
    user_instance = User.objects.get(id=user_id)
    comment = Comment.objects.create(
        text="This is a comment",
        posted_by=user_instance,
        content_type=ContentType.objects.get_for_model(video_instance),
        content_id=video_instance.id 
    )

    Or:
    
    video_instance = Video.objects.get(id=video_id)
    user_instance = User.objects.get(id=user_id)
    comment = Comment.objects.create(
        text="This is a comment",
        posted_by=user_instance,
        content_object = video_instance, 
    )

    """
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True) # It is not a good idea to delete a content type anyway
    content_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'content_id')

class LikeDislike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    is_like = models.BooleanField()
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='likes_dislikes')
    """
    Ziming: 
    Check the comments in "Comment" model for the usage of these fields
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True) # It is not a good idea to delete a content type anyway
    content_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'content_id')

    def save(self, *args, **kwargs):
        """
        Ziming: 
        This makes sure that when a like/dislike is saved (either newly created or updated), 
        the like_count/dislike_count in the relevant BaseContentModel will be automatically updated,  
        and we don't need to manually handle such behaviour in routes (or views if you perfer to call it this way)
        """

        # check if the save() is trigger by a create or an update
        # self._state.adding == True: creating; 
        # self._state.adding == False: updating; 
        # notice that since _state is prefixed with an understore, by the design principle of python's object-oriented programming
        # we shouldn't access it directly, but nothing can actually stop me from doing so  
        is_create = self._state.adding 

        # If updating, store the old value before saving
        if not is_create:
            # Important: we can't use self.is_like, since it is been overidden already
            old_instance = LikeDislike.objects.get(pk=self.pk)
            old_is_like = old_instance.is_like

        super(LikeDislike, self).save(*args, **kwargs) # Save the LikeDislike entity

        # start updating count fields in BaseContentModel
        content_object = self.content_object
        if content_object:
            # For new likes/dislikes
            if is_create:
                if self.is_like:
                    content_object.like_count += 1
                else:
                    content_object.dislike_count += 1
            # For updated likes/dislikes
            else:
                # Switch from like to dislike
                if old_is_like and not self.is_like:
                    content_object.like_count -= 1
                    content_object.dislike_count += 1
                # Switch from dislike to like
                elif not old_is_like and self.is_like:
                    content_object.dislike_count -= 1
                    content_object.like_count += 1
            content_object.save()

    def delete(self, *args, **kwargs):
        """
        Ziming: 
        This makes sure that when a like/dislike is deleted
        the like_count/dislike_count in the relevant BaseContentModel will be automatically updated, 
        and we don't need to manually handle such behaviour in routes (or views if you perfer to call it this way)
        """
        # Store content_object before deletion
        content_object = self.content_object    
        # Call the real delete() method
        super(LikeDislike, self).delete(*args, **kwargs)    
        # Update like/dislike counts after deletion
        if content_object:
            if self.is_like:
                content_object.like_count -= 1
            else:
                content_object.dislike_count -= 1
            content_object.save()

"""
Ziming: Since Django doesn't auto-resolve generic many-to-many, we need to manually set-up our intermedia broker table "PlaylistContent" to achieve this
The purose of this table is exactly the same as the intermedia table for common many-to-many relationship
Wonder how to use these? Refer to the "/tests/test_models.py/PlaylistModelTest"
"""
class Playlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_public = models.BooleanField(default=False, blank=True)
    name = models.CharField(blank=False, null=False) 
    description = models.TextField(blank = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_playlists')

class PlaylistContent(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='playlistContent_table_entries')
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True) # Its not a good idea to delete a content type anyway
    content_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'content_id')