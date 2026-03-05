"""Django admin configuration for the chess application.

This module registers the chess models with the Django admin interface,
allowing administrators to manage games, players, pieces, moves,
and other chess-related data through the web admin panel.

Registered models:
- Game: Chess game management
- Player: Player information management
- ChessPiece: Piece position and state management
- Move: Move history and notation
- DrawOffer: Draw offer tracking
- CapturedPiece: Capture history

"""

from django.contrib import admin
from .models import Game, Player, ChessPiece, Move, DrawOffer, CapturedPiece

# Register models with the admin interface
admin.site.register(Game)
admin.site.register(Player)
admin.site.register(ChessPiece)
admin.site.register(Move)
admin.site.register(DrawOffer)
admin.site.register(CapturedPiece)
