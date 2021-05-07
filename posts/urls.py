from django.urls import path

from . import views

app_name = 'posts'
urlpatterns = [
    path('post/<int:id>', views.post, name='post'),
    path('like_post', views.like_post, name='like_post'),
    path('unlike_post', views.unlike_post, name='unlike_post'),
    path('like_comment', views.like_comment, name='like_comment'),
    path('unlike_comment', views.unlike_comment, name='unlike_comment'),
    path('share-post/<int:id>', views.share_post, name='share_post'),
    path('comments-json/<int:post_id>/<int:num_comments>', views.JSONCommentsListView.as_view(), name='comments-json'),
    path('create_post/', views.create_post, name='create_post'),
    path('user_posts/<user>', views.user_posts, name='user_posts'),
    path('addcomment', views.add_comment, name='add_comment'),
    path('<int:id>/update/', views.update_post, name='update'),
    path('<int:id>/delete/', views.delete_post, name='delete'),
    path('delete_shared_post/<int:id>/', views.delete_shared_post, name='delete-shared-post'),
    path('add_to_bookmark', views.add_to_bookmark, name='add_to_bookmark'),
    path('remove_from_bookmark', views.remove_from_bookmark, name='remove_from_bookmark'),
    path('<pk>', views.post_detail, name='posts'),



]
