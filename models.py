from django.db import models

class Board(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    dimensions = models.IntegerField(default=8)
    pieces = models.ManyToOneRel('Piece', related_name='board_pieces')
    players = models.ManyToOneRel('Player', related_name='board_players')
                                     
    class Meta:
        db_table = 'board'

    def __str__(self):
        return self.name
    
class ChessPiece(models.Model):
    COLORS = [
        ('white', 'White'),
        ('black', 'Black'),
    ]
    PIECE_TYPES = [
        ('pawn', 'Pawn'),
        ('knight', 'Knight'),
        ('bishop', 'Bishop'),
        ('rook', 'Rook'),
        ('queen', 'Queen'),
        ('king', 'King'),
    ]

    moves = models.CharField(max_length=25)  # Store possible moves as a string (e.g., "e4,e5,d4")

    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=255)
    color = models.CharField(max_length=10)  # 'white' or 'black'
    position_x = models.IntegerField()
    position_y = models.IntegerField()

    class Meta:
        db_table = 'chess_piece'

    def __str__(self):
        return f"{self.color} {self.type} at ({self.position_x}, {self.position_y})"
    
class Pawn(ChessPiece):
    type = ChessPiece.PIECE_TYPES["pawn"]
    moves = models.ManyToManyField('Move', related_name='pawn_moves')
    kill_moves = "diagonal"
    class Meta:
        db_table = 'pawn'