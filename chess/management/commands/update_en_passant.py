from django.core.management.base import BaseCommand
from chess.models import ChessPiece, Game

class Command(BaseCommand):
    help = 'Update en passant vulnerability for white pawn at B4 in game 75'

    def handle(self, *args, **options):
        try:
            game = Game.objects.get(id=75)
            self.stdout.write(f'Found game: {game.id}')
            
            pawn = ChessPiece.objects.filter(
                game=game, 
                type='pawn', 
                color='white', 
                position_x=1, 
                position_y=3
            ).first()
            
            if pawn:
                self.stdout.write(f'Found white pawn at B4: {pawn}')
                self.stdout.write(f'Current en_passant_vulnerable: {pawn.en_passant_vulnerable}')
                
                pawn.en_passant_vulnerable = True
                pawn.save()
                
                self.stdout.write(self.style.SUCCESS(f'Updated en_passant_vulnerable to: {pawn.en_passant_vulnerable}'))
                self.stdout.write(self.style.SUCCESS('White pawn at B4 is now en passant vulnerable!'))
            else:
                self.stdout.write('White pawn at B4 not found')
                pawns = ChessPiece.objects.filter(game=game, type='pawn', color='white')
                self.stdout.write(f'All white pawns in game {game.id}:')
                for p in pawns:
                    self.stdout.write(f'  Pawn at ({p.position_x}, {p.position_y}) - en_passant_vulnerable: {p.en_passant_vulnerable}')
                    
        except Game.DoesNotExist:
            self.stdout.write(self.style.ERROR('Game 75 not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
