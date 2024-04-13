from django.test import TestCase

from django.contrib.auth import get_user_model

from content.models.content import Video, Podcast
from user_interactions.models import Comment, LikeDislike, Playlist, PlaylistContent

User = get_user_model()  # This should be the standard way to make reference to the User model, since we have overridden the default user model

class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username="commentuser1", email="a@b.com", password="Cc123456789")
        cls.user2 = User.objects.create_user(username="commentuser2", email="b@c.com", password="Cc123456789")
        cls.user3 = User.objects.create_user(username="commentuser3", email="c@d.com", password="Cc123456789")

        cls.video = Video.objects.create(
            uploaded_by=cls.user1,
            # title='Test Video for Comment, uploaded by user1',
            duration="00:10:00",
            description="Test Video Description",
        )

        cls.comment1 = Comment.objects.create(
            text="Sample comment made by user2",
            posted_by=cls.user2,
            content_object=cls.video,
        )

        cls.comment2 = Comment.objects.create(
            text="Sample comment made by user 3",
            posted_by=cls.user3,
            content_object=cls.video,
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment1.posted_by, self.user2)
        self.assertEqual(self.comment1.content_object, self.video)

    def test_get_all_comment_for_user(self):
        """
        User related name for a user to retrieve all comments he posted
        """
        comments_by_user2 = self.user2.comments.all()
        self.assertEqual(comments_by_user2.count(), 1)
        self.assertIn(self.comment1, comments_by_user2)

    def test_comment_deletion_with_user(self):
        """
        If we delete a user, their comments will also be deleted
        """
        self.user2.delete()
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(id=self.comment1.id)

    def test_comment_deletion_with_content(self):
        """
        If we delete a content, all comments for it will also be deleted
        """
        self.assertEqual(len(Comment.objects.all()), 2)
        self.video.delete()
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(id=self.comment2.id)
        self.assertEqual(len(Comment.objects.all()), 0)


class LikeDislikeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username="likedislikeuser1", email="a@b.com", password="password123")
        cls.user2 = User.objects.create_user(username="likedislikeuser2", email="b@c.com", password="password123")

        cls.video = Video.objects.create(
            uploaded_by=cls.user1,
            # title='Test Video for LikeDislike',
            duration="00:20:00",
            description="Test Video Description",
        )

        cls.like_by_user1 = LikeDislike.objects.create(is_like=True, posted_by=cls.user1, content_object=cls.video)

        cls.dislike_by_user2 = LikeDislike.objects.create(is_like=False, posted_by=cls.user2, content_object=cls.video)

    def test_like_dislike_creation(self):
        self.assertTrue(self.like_by_user1.is_like)
        self.assertFalse(self.dislike_by_user2.is_like)
        self.assertEqual(self.like_by_user1.posted_by, self.user1)
        self.assertEqual(self.dislike_by_user2.content_object, self.video)

    def test_like_dislike_deletion_with_user(self):
        """
        If we delete a user, their likes/dislikes should still exist
        """
        self.user1.delete()
        try:
            like = LikeDislike.objects.get(id=self.like_by_user1.id)
            self.assertIsNotNone(like)
            self.assertEqual(like.posted_by, None)  # when users are deleted, their LikeDislike.posted_by will be set to NULL in DB
            self.assertEqual(len(LikeDislike.objects.all()), 2)
        except LikeDislike.DoesNotExist:
            self.fail("LikeDislike object was deleted after user deletion.")

    def test_like_dislike_deletion_with_content(self):
        """
        If we delete a content, all likes/dislikes for it will be deleted
        """
        self.assertEqual(len(LikeDislike.objects.all()), 2)
        self.video.delete()
        with self.assertRaises(LikeDislike.DoesNotExist):
            like = LikeDislike.objects.get(id=self.like_by_user1.id)
            dislike = LikeDislike.objects.get(id=self.dislike_by_user2.id)
        self.assertEqual(len(LikeDislike.objects.all()), 0)


class LikeDislikeModelAutoIncrementContent(TestCase):
    """
    Test the auto incremental behaviour on BaseContentModel.like_count/dislike_count when a like/dislike is created/updated/deleted
    """

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username="likedislikeuser1", email="a@b.com", password="password123")
        cls.user2 = User.objects.create_user(username="likedislikeuser2", email="b@c.com", password="password123")

        cls.video = Video.objects.create(
            uploaded_by=cls.user1,
            # title='Test Video for LikeDislike',
            duration="00:20:00",
            description="Test Video Description",
        )

        cls.like = LikeDislike.objects.create(is_like=True, posted_by=cls.user1, content_object=cls.video)

    def test_like_creation_updates_like_count(self):
        """
        Test that creating a like increases the like count
        """
        self.assertEqual(self.video.like_count, 1)
        self.assertEqual(self.video.dislike_count, 0)

    def test_updating_like_to_dislike_updates_counts(self):
        """
        Test that updating a like to a dislike updates both counts
        """
        self.like.is_like = False
        self.like.save()
        self.video.refresh_from_db()
        self.assertEqual(self.video.like_count, 0)
        self.assertEqual(self.video.dislike_count, 1)

    def test_deleting_like_updates_counts(self):
        """
        Test that deleting a like/dislike updates the counts
        """
        self.like.delete()
        self.video.refresh_from_db()
        self.assertEqual(self.video.like_count, 0)
        self.assertEqual(self.video.dislike_count, 0)


class PlaylistModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="playlistuser", email="p@b.com", password="password123")
        cls.playlist = Playlist.objects.create(name="aaa", created_by=cls.user)

    def test_playlist_creation(self):
        self.assertEqual(self.playlist.name, "aaa")
        self.assertEqual(self.playlist.created_by, self.user)

    def test_playlist_deletion_with_user(self):
        """
        When a user is deleted, the playlists they created should also be deleted
        """
        self.user.delete()
        with self.assertRaises(Playlist.DoesNotExist):
            Playlist.objects.get(id=self.playlist.id)

    def test_adding_remove_content_to_playlist(self):
        video = Video.objects.create(
            #  title="Test Video",
            duration="00:05:00",
            uploaded_by=self.user,
        )
        podcast = Podcast.objects.create(
            # title="Test Podcast",
            duration="00:05:00",
            uploaded_by=self.user,
        )
        # add to
        video_playlist_content = PlaylistContent.objects.create(playlist=self.playlist, content_object=video)
        podcast_playlist_content = PlaylistContent.objects.create(playlist=self.playlist, content_object=podcast)
        self.assertIn(video, [pc.content_object for pc in self.playlist.playlistContent_table_entries.all()])
        self.assertIn(podcast, [pc.content_object for pc in self.playlist.playlistContent_table_entries.all()])
        self.assertEqual(len(self.playlist.playlistContent_table_entries.all()), 2)
        # remove from
        podcast_playlist_content.delete()
        self.assertIn(video, [pc.content_object for pc in self.playlist.playlistContent_table_entries.all()])
        self.assertNotIn(podcast, [pc.content_object for pc in self.playlist.playlistContent_table_entries.all()])
        self.assertEqual(len(self.playlist.playlistContent_table_entries.all()), 1)

    def test_delete_content_removes_from_playlist(self):
        """
        Test that deleting a Content also removes it from associated playlists.
        """
        video = Video.objects.create(
            # title="Test Video for Delete",
            duration="00:05:00",
            uploaded_by=self.user,
        )
        PlaylistContent.objects.create(playlist=self.playlist, content_object=video)
        self.assertIn(video, [pc.content_object for pc in self.playlist.playlistContent_table_entries.all()])
        video.delete()
        self.assertNotIn(video, [pc.content_object for pc in self.playlist.playlistContent_table_entries.all()])
