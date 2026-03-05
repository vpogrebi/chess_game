"""URL configuration for the chess application.

This module defines the URL patterns for all chess-related views,
including game creation, management, move handling, and player interactions.

URL patterns include:
- Home page and game creation
- Game listing and individual game views
- Move validation and execution endpoints
- Game status checking and management
- Player actions (resignation, draw offers)

"""

from django.urls import path
from . import views

app_name = 'chess'

urlpatterns = [
    path('', views.chess_home, name='home'),
    path('create/', views.create_game, name='create_game'),
    path('games/', views.game_list, name='game_list'),
    path('game/<int:game_id>/', views.game_view, name='game'),
    path('game/<int:game_id>/start/', views.StartGameView.as_view(), name='start_game'),
    path('game/<int:game_id>/move/', views.MoveView.as_view(), name='make_move'),
    path('game/<int:game_id>/valid-moves/', views.GetValidMovesView.as_view(), name='get_valid_moves'),
    path('game/<int:game_id>/check-status/', views.CheckStatusView.as_view(), name='check_status'),
    path('game/<int:game_id>/resign/', views.ResignView.as_view(), name='resign'),
    path('game/<int:game_id>/draw/', views.DrawView.as_view(), name='draw'),
    path('game/<int:game_id>/check-draw-offer/', views.CheckDrawOfferView.as_view(), name='check_draw_offer'),
    path('game/<int:game_id>/delete/', views.delete_game, name='delete_game'),
]
