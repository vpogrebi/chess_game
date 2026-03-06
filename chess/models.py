"""Django models for the chess game application.

This module defines the database models that represent the core entities
of the chess game system including players, games, chess pieces, moves,
and game-related data.

The models provide:
- Player management with color assignment
- Game lifecycle management
- Chess piece positioning and state tracking
- Move history and notation
- Special move handling (castling, en passant, promotion)
- Game outcome tracking

"""

from typing import Any
from django.db import models
from django.utils import timezone


class Player(models.Model):
    """Represents a chess player.

    Stores player information and assigns them to either white or black pieces.
    Each player can only be assigned one color to ensure unique assignments
    across games.

    Attributes:
        first_name: Player's first name (max 50 characters).
        last_name: Player's last name (max 50 characters).
        color: Piece color assignment ('white' or 'black', unique).
        created_at: Timestamp when the player record was created.
    """
    COLOR_CHOICES = [
        ('white', 'White'),
        ('black', 'Black'),
    ]
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    color = models.CharField(max_length=5, choices=COLOR_CHOICES, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        """Return string representation of the player.

        Returns:
            str: Player's full name with color in parentheses.
        """
        return f"{self.first_name} {self.last_name} ({self.color})"
    
    @property
    def full_name(self) -> str:
        """Get the player's full name.

        Returns:
            str: Concatenated first and last name.
        """
        return f"{self.first_name} {self.last_name}"


class Game(models.Model):
    """Represents a chess game.

    Manages the complete lifecycle of a chess game including player assignments,
    game state tracking, move history, and outcome determination.

    Attributes:
        name: Descriptive name for the game (max 200 characters).
        white_player: Player controlling white pieces.
        black_player: Player controlling black pieces.
        current_turn: Whose turn it is ('white' or 'black').
        status: Current game status.
        winner: Player who won the game (null if ongoing/draw).
        started_at: Timestamp when game started.
        ended_at: Timestamp when game ended.
        created_at: Timestamp when game was created.
    """
    STATUS_CHOICES = [
        ('waiting', 'Waiting to start'),
        ('active', 'Active'),
        ('check', 'Check'),
        ('checkmate', 'Checkmate'),
        ('stalemate', 'Stalemate'),
        ('resigned', 'Resigned'),
        ('draw', 'Draw'),
    ]
    
    name = models.CharField(max_length=200)
    white_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='white_games')
    black_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='black_games')
    current_turn = models.CharField(max_length=5, choices=Player.COLOR_CHOICES, default='white')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_games')
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        """Return string representation of the game.

        Returns:
            str: Game name with player names.
        """
        return f"{self.name} - {self.white_player.full_name} vs {self.black_player.full_name}"
    
    def start_game(self) -> None:
        """Start the game and initialize pieces.

        Sets the game status to 'active', records the start time,
        and initializes all chess pieces in their starting positions.
        """
        self.status = 'active'
        if not self.started_at:
            self.started_at = timezone.now()
        self.save()
        self.initialize_pieces()
    
    def initialize_pieces(self) -> None:
        """Initialize all chess pieces for a new game.

        Creates and places all chess pieces in their standard starting
        positions. Clears any existing pieces first.

        Piece placement:
        - Pawns: Rank 2 for white, Rank 7 for black
        - Other pieces: Rank 1 for white, Rank 8 for black
          in order: Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook
        """
        # Clear existing pieces
        self.pieces.all().delete()
        
        # Initialize pawns
        for x in range(8):
            # White pawns (row 1, index 1)
            ChessPiece.objects.create(
                game=self, type='pawn', color='white', 
                position_x=x, position_y=1
            )
            # Black pawns (row 6, index 6)
            ChessPiece.objects.create(
                game=self, type='pawn', color='black', 
                position_x=x, position_y=6
            )
        
        # Initialize other pieces
        piece_order = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        
        for x, piece_type in enumerate(piece_order):
            # White pieces (row 0)
            ChessPiece.objects.create(
                game=self, type=piece_type, color='white', 
                position_x=x, position_y=0
            )
            # Black pieces (row 7)
            ChessPiece.objects.create(
                game=self, type=piece_type, color='black', 
                position_x=x, position_y=7
            )


class ChessPiece(models.Model):
    """Represents a chess piece on the board.

    Stores the position, type, and state of individual chess pieces.
    Tracks special move capabilities like castling and en passant.

    Attributes:
        game: The game this piece belongs to.
        type: Type of chess piece.
        color: Piece color ('white' or 'black').
        position_x: X coordinate on board (0-7, representing a-h).
        position_y: Y coordinate on board (0-7, representing 1-8).
        is_captured: Whether the piece has been captured.
        captured_at: When the piece was captured.
        has_moved: Whether the piece has moved (for castling/en passant).
        en_passant_vulnerable: Whether vulnerable to en passant capture.
        has_castled: Whether the piece has participated in castling.
    """
    PIECE_TYPES = [
        ('pawn', 'Pawn'),
        ('rook', 'Rook'),
        ('knight', 'Knight'),
        ('bishop', 'Bishop'),
        ('queen', 'Queen'),
        ('king', 'King'),
    ]
    
    COLORS = [
        ('white', 'White'),
        ('black', 'Black'),
    ]
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='pieces')
    type = models.CharField(max_length=10, choices=PIECE_TYPES)
    color = models.CharField(max_length=5, choices=COLORS)
    position_x = models.IntegerField()  # 0-7 (a-h)
    position_y = models.IntegerField()  # 0-7 (1-8)
    is_captured = models.BooleanField(default=False)
    captured_at = models.DateTimeField(null=True, blank=True)
    
    # For pawn special moves
    has_moved = models.BooleanField(default=False)
    en_passant_vulnerable = models.BooleanField(default=False)
    
    # For castling
    has_castled = models.BooleanField(default=False)
    
    unique_together = ['game', 'position_x', 'position_y']
    
    def __str__(self) -> str:
        """Return string representation of the chess piece.

        Returns:
            str: Piece color, type, and position.
        """
        return f"{self.color} {self.type} at {self.get_position()}"
    
    def get_position(self) -> str:
        """Get the chess notation position of the piece.

        Converts numeric coordinates to standard chess notation
        (e.g., position_x=0, position_y=0 becomes 'a1').

        Returns:
            str: Position in chess notation (a1-h8).
        """
        return f"{chr(97 + self.position_x)}{self.position_y + 1}"
    
    def get_unicode_symbol(self) -> str:
        """Get the Unicode chess symbol for this piece.

        Returns:
            str: Unicode character representing the piece.
        """
        symbols = {
            'white': {
                'king': '♔',
                'queen': '♕',
                'rook': '♖',
                'bishop': '♗',
                'knight': '♘',
                'pawn': '♙',
            },
            'black': {
                'king': '♚',
                'queen': '♛',
                'rook': '♜',
                'bishop': '♝',
                'knight': '♞',
                'pawn': '♟',
            },
        }
        return symbols[self.color][self.type]


class Move(models.Model):
    """Represents a single move in a chess game.

    Records all details about a chess move including piece movement,
    captures, special moves, and notation. Provides complete move history
    for game analysis and replay.

    Attributes:
        game: The game this move belongs to.
        piece: The chess piece that was moved.
        from_x: Starting X coordinate.
        from_y: Starting Y coordinate.
        to_x: Destination X coordinate.
        to_y: Destination Y coordinate.
        captured_piece: Piece that was captured (if any).
        move_number: Sequential move number in the game.
        notation: Algebraic notation of the move.
        timestamp: When the move was made.
        is_castle: Whether this move was castling.
        is_en_passant: Whether this move was en passant capture.
        is_promotion: Whether this move included pawn promotion.
        promotion_piece: Type of piece pawn was promoted to.
    """
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='moves')
    piece = models.ForeignKey(ChessPiece, on_delete=models.CASCADE, related_name='moves')
    from_x = models.IntegerField()
    from_y = models.IntegerField()
    to_x = models.IntegerField()
    to_y = models.IntegerField()
    captured_piece = models.ForeignKey(ChessPiece, on_delete=models.SET_NULL, null=True, blank=True, related_name='captured_by')
    move_number = models.IntegerField()
    notation = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Special move flags
    is_castle = models.BooleanField(default=False)
    is_en_passant = models.BooleanField(default=False)
    is_promotion = models.BooleanField(default=False)
    promotion_piece = models.CharField(max_length=10, choices=ChessPiece.PIECE_TYPES, null=True, blank=True)
    
    unique_together = ['game', 'move_number']


class DrawOffer(models.Model):
    """Track draw offers between players.

    Manages draw proposals in a game, including who offered the draw
    and when the offer was made. Only one active draw offer can exist
    per game at any time.

    Attributes:
        game: The game where the draw was offered.
        offering_player: The player who offered the draw.
        offered_at: When the draw offer was made.
        is_active: Whether the offer is still pending response.
    """
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='draw_offers')
    offering_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='offered_draws')
    offered_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        """Return string representation of the draw offer.

        Returns:
            str: Description of the draw offer.
        """
        return f"Draw offer by {self.offering_player.full_name} in {self.game.name}"
    
    class Meta:
        ordering = ['-offered_at']


class CapturedPiece(models.Model):
    """Represents a captured piece in a game.

    Tracks pieces that have been captured during a game, including
    which piece was captured, who captured it, and when it occurred.
    Provides a complete capture history for game analysis.

    Attributes:
        game: The game where the capture occurred.
        piece: The chess piece that was captured.
        captured_by: The player who captured the piece.
        captured_at: When the piece was captured.
    """
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='captured_pieces')
    piece = models.ForeignKey(ChessPiece, on_delete=models.CASCADE)
    captured_by = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='captures')
    captured_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        """Return string representation of the captured piece.
        
        Returns:
            str: Description of the capture event.
        """
        return f"{self.piece} captured by {self.captured_by.full_name}"
