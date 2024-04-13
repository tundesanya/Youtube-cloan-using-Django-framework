# Model Documentations - Initial Version by Ziming Wang

If you wonder how to use a model, you can refer to my test cases in /tests/test_models.py

## Part 0: Notice these before you continue: 
1. It is important to know that Django doesn't encourage (but definitely doable if we want) deleting user. 
Instead, Django encourages us to use is_active=False to deactivate a user.
This warning can be igonored if we want, because sometimes it is easier and less troublesome to directly delete them instead of deactiving them.  
Imagine this scenario, a user A wants to delete his profile, he wishes all his comments are no longer visible to other users. 
When passing the comments to frontend, if A is only deactivated but not deleted, we may need to write some filter statements to filter out inactive user's data. 
However, if A is deleted from DB, then if we set on_delete=CASCADE, all his associated infos are gone forever, at the time he's deleted. 
I believe this will make coding much easier. 
Anyway, we need to carefully design the impact on the DB if a user is truly deleted, no matter we decide to delete them or simply deactivate them.

2. Django's default approach is to use an incremental integer (start from 1) as primary key. This will yield significant security issues if we use these ids to construct URLs. 
E.g. /user/12, video/4. 
Therefore, in my initial design, UUID is used to ensure random, same-length, unique IDs. 
I once had a concern that this will cause extra performance issue, as UUIDs are much longer than integer IDs. 
However, after my research, this doesn't seem like a problem, and even if it is, I don't think it is something we need to opt toptimize now. 
If you google "django UUID performance", some ppl believe this doesn't cause any performance problem, some believe they will, but no stats can be given, only theories. 
Besides, this also highly depend on the DB low-level implementation details. So MySQl and PostgreSQL might be different. 
Anyway, no need to worry about this now. 

3. !!! Extremely important: 
Despite there are some validations applied on model fields in this file, such as blank=True. 
since we are using django-restframework, some model-level validation (e.g. blank=True) DOESN'T WORK WITH SERIALIZERS!!!  
These model-level validations are for, 
+ django templating form, E.g. /admin
OR
+ you manually use "someModel.full_clean()" before .save(), which is not something we should do.
Therfore, all validation must be properly handled in serializer as well as this in this file.
quote from django-restframework's document: 
    Validation in Django REST framework serializers is handled a little differently to how validation works in Django's ModelForm class.
    With ModelForm the validation is performed partially on the form, and partially on the model instance. 
    With REST framework the validation is performed entirely on the serializer class.
    

4. Read 3 before reading this  
null=True/False and blank = True/False:  https://stackoverflow.com/questions/8609192/what-is-the-difference-between-null-true-and-blank-true-in-django
Summary:
+ for most optional fields, set (null=True, blank=True)
+ except for char/text optional field, set (blank=True). And Django will automatically store empty string "" in  DB for missing values instead of NULL. 
+ However, be careful if you are dealing with unique=True optional text field, as empty string "" is not unique.  
    

## Part 1: Current on_delete behaviours: 
+ BaseContentModel:
    - when a user is deleted: don't delete contents he uploaded
+ Comment
    - When the author is deleted: automatically delete all comments he posted (handled by on_delete=CASCADE)
    - when the content is deleted: delete all comments associated with it
+ LikesDislikes: 
    - When the author is deleted: don't delete the likes/dislikes he made
    - when the content is deleted: delete all like-dislike associated with it
+ Friendship:
    - When the requested_by user is deleted, delete the friendship
    - When the sent_to user is deleted, delete the friendship
+ Playlist:
    - when the author is deleted, delete the playlist
+ PlaylistContent:
    - when a content is deleted, remove it from all playlist (by removing it from PlaylistContent Table)
+ ContentTitle
    - When a content is deleted, remove all of its titles
+ ContentPersonnelCast/Produce
    - When a content is deleted, remove all cast/produce table entries
    - When a personnal is deleted, remove all cast/produce table entries

