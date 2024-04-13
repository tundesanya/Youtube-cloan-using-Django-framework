from django.test import TestCase

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from content.models.content import Video, Podcast
from content.models.metadata import ContentTitle, Category, Language
from content.models.people import IndustryPersonnel, ContentPersonnelCast, ContentPersonnelProduce

User = get_user_model() # This should be the standard way to make reference to the User model, since we have overridden the default user model

class VideoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser', password='Cc123456789')
        cls.category = Category.objects.create(name="Drama")
        cls.video = Video.objects.create(
            uploaded_by=cls.user, 
            duration='00:05:00',
            description='Test Description'
        )
        cls.video.categories.add(cls.category)

    def test_video_creation(self):
        self.assertEqual(self.video.uploaded_by, self.user)
        self.assertIn(self.category, self.video.categories.all())
    
    def test_user_deletion_effect_on_content(self):
        """
        When a user is deleted, the contents he uploaded won't be deleted, but the BaseContentModel.uploaded_by field will be set to NULL
        """
        self.user.delete()
        self.assertEqual(Video.objects.get(id=self.video.id).uploaded_by, None)

class VideoPodcastFormatTests(TestCase):
    def test_video_creation_with_format(self):
        video = Video.objects.create(format=Video.VideoFileFormat.MP4)
        self.assertEqual(video.format, Video.VideoFileFormat.MP4)

    def test_podcast_creation_with_format(self):
        podcast = Podcast.objects.create(format=Podcast.AudioFileFormat.MP3)
        self.assertEqual(podcast.format, Podcast.AudioFileFormat.MP3)
        
class ContentTitleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser', password='Cc123456789')
        cls.category = Category.objects.create(name="Drama")
        cls.video = Video.objects.create(
            uploaded_by=cls.user, 
            duration='00:05:00', 
            description='Test Description'
        )
        cls.title_eng = ContentTitle.objects.create(
            content_type=ContentType.objects.get_for_model(cls.video), 
            content_id=cls.video.id, 
            language=Language.objects.create(name="English"),
            is_native=True,
            title_text="Test Title_eng"
        )
        cls.title_rus = ContentTitle.objects.create(
            content_type=ContentType.objects.get_for_model(cls.video), 
            content_id=cls.video.id, 
            language=Language.objects.create(name="Russian"),
            is_native=False,
            title_text="Test Title_rus"
        )
    
    def testTitleCreation(self):
        self.assertEqual(len(ContentTitle.objects.filter(content_type=ContentType.objects.get_for_model(self.video), content_id=self.video.id)), 2)
        self.assertEqual(self.title_eng.title_text, "Test Title_eng")
        self.assertEqual(self.title_rus.title_text, "Test Title_rus")
        
    def testContentDeletionEffectOnTitle(self):
        """
        if a content is deleted, all titles associated with it should also be deleted
        """
        self.video.delete()
        self.assertEqual(len(ContentTitle.objects.filter(content_type=ContentType.objects.get_for_model(self.video), content_id=self.video.id)), 0)
    
    def testLanguageDelectionEffectOnTitle(self):
        """
        if a lang is deleted, the title in that lang should have lang field set to null
        """
        Language.objects.get(id=self.title_eng.language.id).delete()
        self.assertEqual(ContentTitle.objects.get(id=self.title_eng.id).language, None)

class IndustryPersonnelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser', password='Cc123456789')
        cls.video = Video.objects.create(
            uploaded_by=cls.user, 
            duration='00:05:00', 
            description='Test Description'
        )
        cls.actor = IndustryPersonnel.objects.create(
            first_name='John',
            last_name='Doe'
        )
        cls.director = IndustryPersonnel.objects.create(
            first_name='Jane',
            last_name='Doe'
        )
        cls.cast_entry = ContentPersonnelCast.objects.create(
            content_type=ContentType.objects.get_for_model(cls.video),
            content_id=cls.video.id,
            personnel=cls.actor,
            cast_type=ContentPersonnelCast.CastType.MAIN_ACTOR
        )
        cls.produce_entry = ContentPersonnelProduce.objects.create(
            content_type=ContentType.objects.get_for_model(cls.video),
            content_id=cls.video.id,
            personnel=cls.director,
            produce_type=ContentPersonnelProduce.ProduceType.DIRECTOR
        )

    def test_cast_entry_creation(self):
        self.assertEqual(self.cast_entry.personnel, self.actor)
        self.assertEqual(self.cast_entry.content_object, self.video)
        self.assertEqual(self.cast_entry.cast_type, ContentPersonnelCast.CastType.MAIN_ACTOR)

    def test_produce_entry_creation(self):
        self.assertEqual(self.produce_entry.personnel, self.director)
        self.assertEqual(self.produce_entry.content_object, self.video)
        self.assertEqual(self.produce_entry.produce_type, ContentPersonnelProduce.ProduceType.DIRECTOR)

    def test_content_deletion_effect_on_cast_produce(self):
        """
        When a content is delete, delete all cast/produce entries associated with it
        """
        self.video.delete()
        self.assertEqual(ContentPersonnelCast.objects.all().count(), 0)
        self.assertEqual(ContentPersonnelProduce.objects.all().count(), 0)
        self.assertEqual(IndustryPersonnel.objects.all().count(), 2)

    def test_personnel_deletion_effect_on_cast_produce(self):
        """
        When a personnel is deleted, remove all cast/produce entries associated with it
        """
        self.actor.delete()
        self.assertEqual(ContentPersonnelCast.objects.filter(personnel=self.actor).count(), 0)
        self.director.delete()
        self.assertEqual(ContentPersonnelProduce.objects.filter(personnel=self.director).count(), 0)