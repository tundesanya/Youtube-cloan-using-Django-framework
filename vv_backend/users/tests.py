import uuid

from django.test import TestCase
from django.contrib.auth import get_user_model

from users.models import Friendship

User = get_user_model() # This should be the standard way to make reference to the User model, since we have overridden the default user model
# NOTE: ``from django.conf import settings ... settings.AUTH_USER_MODEL`` is string name of the user model, not the model itself.
# Ref: https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#referencing-the-user-model

class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", email="a@b.com", bio="a11", password="Cc123456789")

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.bio, "a11")
        self.assertIsInstance(self.user.id, uuid.UUID)


class FriendshipModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username="friendshipuser1", email="a@b.com", password="password123")
        cls.user2 = User.objects.create_user(username="friendshipuser2", email="b@c.com", password="password123")
        cls.user3 = User.objects.create_user(username="friendshipuser3", email="c@d.com", password="password123")
        cls.friendship = Friendship.objects.create(
            requested_by=cls.user1,
            sent_to=cls.user2,
            # default: PENDING, so no need to set status here
        )
        cls.friendship2 = Friendship.objects.create(
            requested_by=cls.user2,
            sent_to=cls.user3,
        )

    def test_friendship_creation(self):
        self.assertEqual(self.friendship.requested_by, self.user1)
        self.assertEqual(self.friendship.sent_to, self.user2)
        self.assertEqual(self.friendship.status, Friendship.Status.PENDING)

    def test_friendship_deletion_with_request_user(self):
        """
        If a user involved in a friendship is deleted, the friendship should also be deleted
        """
        self.user1.delete()
        with self.assertRaises(Friendship.DoesNotExist):
            Friendship.objects.get(id=self.friendship.id)

    def test_friendship_deletion_with_request_receive_user(self):
        self.user2.delete()
        with self.assertRaises(Friendship.DoesNotExist):
            Friendship.objects.get(id=self.friendship.id)
        with self.assertRaises(Friendship.DoesNotExist):
            Friendship.objects.get(id=self.friendship2.id)

    def test_friendship_retrieve(self):
        """
        Test to retrieve friendships for a specific user using related name method
        """
        received_friendships_user2 = self.user2.receieved_friendships.all()
        self.assertIn(self.friendship, received_friendships_user2)
        self.assertEqual(received_friendships_user2.count(), 1)
        requested_friendships_user2 = self.user2.requested_friendships.all()
        self.assertIn(self.friendship2, requested_friendships_user2)
        self.assertEqual(requested_friendships_user2.count(), 1)

    def test_friendship_status_update(self):
        self.friendship2.status = Friendship.Status.ACCEPTED
        self.friendship2.save()
        self.assertEqual(Friendship.objects.get(id=self.friendship2.id).status, Friendship.Status.ACCEPTED,)
