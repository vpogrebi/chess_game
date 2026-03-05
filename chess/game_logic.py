"""Core chess game logic and rules implementation.

This module contains the ChessGameLogic class which implements all chess rules,
move validation, special moves, and game state management. It serves as the
engine that powers the chess game by providing valid moves, checking
for check/checkmate conditions, and executing moves.

Key features:
- Complete chess rules implementation
- Special moves: castling, en passant, pawn promotion
- Check and checkmate detection
- Legal move validation
- Move notation generation
- Game state management

"""

from .models import Game, ChessPiece, Move, Player, CapturedPiece
from django.utils import timezone


class ChessGameLogic:
    """Main chess game logic engine.
    
    Handles all chess game rules, move validation, special moves,
    and game state management. Provides methods for calculating
    valid moves, checking game conditions, and executing moves.
    
    Attributes:
        game: The Game instance this logic engine is managing.
    """
    
    def __init__(self, game):
        """Initialize the game logic engine.
        
        Args:
            game: The Game instance to manage.
        """
        self.game = game
    
    def get_piece_at(self, x: int, y: int) -> ChessPiece | None:
        """Get the piece at a specific board position.
        
        Args:
            x: X coordinate (0-7, representing a-h).
            y: Y coordinate (0-7, representing 1-8).
            
        Returns:
            ChessPiece: The piece at the position, or None if empty.
        """
        try:
            return ChessPiece.objects.get(game=self.game, position_x=x, position_y=y, is_captured=False)
        except ChessPiece.DoesNotExist:
            return None
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if a position is within the chess board bounds.
        
        Args:
            x: X coordinate to check.
            y: Y coordinate to check.
            
        Returns:
            bool: True if position is valid (0-7 for both coordinates).
        """
        return 0 <= x <= 7 and 0 <= y <= 7
    
    def get_valid_moves(self, piece: ChessPiece) -> list[tuple[int, int]]:
        """Get all valid moves for a chess piece.
        
        Delegates to the appropriate piece-specific move generation
        method based on the piece type.
        
        Args:
            piece: The ChessPiece to get moves for.
            
        Returns:
            list: List of (x, y) tuples representing valid moves.
        """
        if piece.type == 'pawn':
            return self.get_pawn_moves(piece)
        elif piece.type == 'rook':
            return self.get_rook_moves(piece)
        elif piece.type == 'knight':
            return self.get_knight_moves(piece)
        elif piece.type == 'bishop':
            return self.get_bishop_moves(piece)
        elif piece.type == 'queen':
            return self.get_queen_moves(piece)
        elif piece.type == 'king':
            king_moves = self.get_king_moves(piece)
            return king_moves
        return []
    
    def get_pawn_moves(self, pawn: ChessPiece) -> list[tuple[int, int]]:
        """Get all valid moves for a pawn including special moves.
        
        Calculates standard pawn moves (forward one, forward two from start),
        captures (diagonal), and en passant captures.
        
        Args:
            pawn: The pawn ChessPiece to get moves for.
            
        Returns:
            list: List of (x, y) tuples representing valid moves.
        """
        moves = []
        direction = 1 if pawn.color == 'white' else -1
        
        # Move forward one square
        new_y = pawn.position_y + direction
        if self.is_valid_position(pawn.position_x, new_y):
            if not self.get_piece_at(pawn.position_x, new_y):
                moves.append((pawn.position_x, new_y))
                
                # Move forward two squares from starting position
                if not pawn.has_moved:
                    new_y2 = pawn.position_y + (2 * direction)
                    if self.is_valid_position(pawn.position_x, new_y2):
                        if not self.get_piece_at(pawn.position_x, new_y2):
                            moves.append((pawn.position_x, new_y2))
                            # Check for en passant captures
                            if pawn.color == 'white' and pawn.position_y == 1:
                                # White pawn on 2nd rank can capture en passant
                                adjacent_files = [-1, 1]
                                for dx in adjacent_files:
                                    adjacent_x = pawn.position_x + dx
                                    vulnerable_y = pawn.position_y
                                    if self.is_valid_position(adjacent_x, vulnerable_y):
                                        vulnerable_pawn = self.get_piece_at(adjacent_x, vulnerable_y)
                                        if (vulnerable_pawn and vulnerable_pawn.type == 'pawn' and 
                                            vulnerable_pawn.color != pawn.color and vulnerable_pawn.en_passant_vulnerable):
                                            # Can capture en passant - move to the square where the vulnerable pawn passed
                                            # This is one square beyond the vulnerable pawn in the same direction
                                            en_passant_y = pawn.position_y + 1
                                            if self.is_valid_position(adjacent_x, en_passant_y):
                                                moves.append((adjacent_x, en_passant_y))
                            elif pawn.color == 'black' and pawn.position_y == 6:
                                # Black pawn on 7th rank can capture en passant
                                adjacent_files = [-1, 1]
                                for dx in adjacent_files:
                                    adjacent_x = pawn.position_x + dx
                                    vulnerable_y = pawn.position_y
                                    if self.is_valid_position(adjacent_x, vulnerable_y):
                                        vulnerable_pawn = self.get_piece_at(adjacent_x, vulnerable_y)
                                        if (vulnerable_pawn and vulnerable_pawn.type == 'pawn' and 
                                            vulnerable_pawn.color != pawn.color and vulnerable_pawn.en_passant_vulnerable):
                                            # Can capture en passant - move to the square where the vulnerable pawn passed
                                            # This is one square beyond the vulnerable pawn in the same direction
                                            en_passant_y = pawn.position_y - 1
                                            if self.is_valid_position(adjacent_x, en_passant_y):
                                                moves.append((adjacent_x, en_passant_y))
        
        # Capture diagonally
        for dx in [-1, 1]:
            new_x = pawn.position_x + dx
            new_y = pawn.position_y + direction  # Diagonal capture position
            if self.is_valid_position(new_x, new_y):
                target = self.get_piece_at(new_x, new_y)
                if target and target.color != pawn.color:
                    moves.append((new_x, new_y))
        
        # Check for en passant captures (separate from regular moves)
        if pawn.color == 'white' and pawn.position_y == 4:
            # White pawn on 5th rank can capture en passant
            adjacent_files = [-1, 1]
            for dx in adjacent_files:
                adjacent_x = pawn.position_x + dx
                vulnerable_y = pawn.position_y
                if self.is_valid_position(adjacent_x, vulnerable_y):
                    vulnerable_pawn = self.get_piece_at(adjacent_x, vulnerable_y)
                    if (vulnerable_pawn and vulnerable_pawn.type == 'pawn' and 
                        vulnerable_pawn.color != pawn.color and vulnerable_pawn.en_passant_vulnerable):
                        # Can capture en passant - move to the square where the vulnerable pawn passed
                        # This is one square beyond the vulnerable pawn in the same direction
                        en_passant_y = pawn.position_y + 1
                        if self.is_valid_position(adjacent_x, en_passant_y):
                            moves.append((adjacent_x, en_passant_y))
        elif pawn.color == 'black' and pawn.position_y == 3:
            # Black pawn on 4th rank can capture en passant
            adjacent_files = [-1, 1]
            for dx in adjacent_files:
                adjacent_x = pawn.position_x + dx
                vulnerable_y = pawn.position_y
                if self.is_valid_position(adjacent_x, vulnerable_y):
                    vulnerable_pawn = self.get_piece_at(adjacent_x, vulnerable_y)
                    if (vulnerable_pawn and vulnerable_pawn.type == 'pawn' and 
                        vulnerable_pawn.color != pawn.color and vulnerable_pawn.en_passant_vulnerable):
                        # Can capture en passant - move to the square where the vulnerable pawn passed
                        # This is one square beyond the vulnerable pawn in the same direction
                        en_passant_y = pawn.position_y - 1
                        if self.is_valid_position(adjacent_x, en_passant_y):
                            moves.append((adjacent_x, en_passant_y))
        
        return moves
    
    def get_rook_moves(self, rook: ChessPiece) -> list[tuple[int, int]]:
        """Get all valid moves for a rook.
        
        Rooks move horizontally and vertically any number of squares
        until blocked by another piece or the board edge.
        
        Args:
            rook: The rook ChessPiece to get moves for.
            
        Returns:
            list: List of (x, y) tuples representing valid moves.
        """
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dx, dy in directions:
            for i in range(1, 8):
                new_x = rook.position_x + (dx * i)
                new_y = rook.position_y + (dy * i)
                
                if not self.is_valid_position(new_x, new_y):
                    break
                
                target = self.get_piece_at(new_x, new_y)
                if target:
                    if target.color != rook.color:
                        moves.append((new_x, new_y))
                    break
                else:
                    moves.append((new_x, new_y))
        
        return moves
    
    def get_knight_moves(self, knight: ChessPiece) -> list[tuple[int, int]]:
        """Get all valid moves for a knight.
        
        Knights move in an L-shape: 2 squares in one direction
        and 1 square perpendicular, jumping over pieces.
        
        Args:
            knight: The knight ChessPiece to get moves for.
            
        Returns:
            list: List of (x, y) tuples representing valid moves.
        """
        moves = []
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for dx, dy in knight_moves:
            new_x = knight.position_x + dx
            new_y = knight.position_y + dy
            
            if self.is_valid_position(new_x, new_y):
                target = self.get_piece_at(new_x, new_y)
                if not target or target.color != knight.color:
                    moves.append((new_x, new_y))
        
        return moves
    
    def get_bishop_moves(self, bishop: ChessPiece) -> list[tuple[int, int]]:
        """Get all valid moves for a bishop.
        
        Bishops move diagonally any number of squares until blocked
        by another piece or the board edge.
        
        Args:
            bishop: The bishop ChessPiece to get moves for.
            
        Returns:
            list: List of (x, y) tuples representing valid moves.
        """
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dx, dy in directions:
            for i in range(1, 8):
                new_x = bishop.position_x + (dx * i)
                new_y = bishop.position_y + (dy * i)
                
                if not self.is_valid_position(new_x, new_y):
                    break
                
                target = self.get_piece_at(new_x, new_y)
                if target:
                    if target.color != bishop.color:
                        moves.append((new_x, new_y))
                    break
                else:
                    moves.append((new_x, new_y))
        
        return moves
    
    def get_queen_moves(self, queen: ChessPiece) -> list[tuple[int, int]]:
        """Get all valid moves for a queen.
        
        Queens combine rook and bishop movement: can move
        horizontally, vertically, or diagonally any number of squares.
        
        Args:
            queen: The queen ChessPiece to get moves for.
            
        Returns:
            list: List of (x, y) tuples representing valid moves.
        """
        # Queen moves like rook + bishop
        return self.get_rook_moves(queen) + self.get_bishop_moves(queen)
    
    def get_king_moves(self, king: ChessPiece) -> list[tuple[int, int]]:
        """Get all valid moves for a king including castling.
        
        Kings move one square in any direction and can castle
        with a rook under specific conditions.
        
        Args:
            king: The king ChessPiece to get moves for.
            
        Returns:
            list: List of (x, y) tuples representing valid moves.
        """
        moves = []
        
        # Get basic king moves (one square in any direction)
        basic_moves = self.get_king_moves_basic(king)
        moves.extend(basic_moves)
        
        # Check for castling
        if not king.has_moved and not self.is_in_check(king.color):
            # Kingside castling (king moves 2 squares right)
            if king.color == 'white':
                rook = self.get_piece_at(7, 0)  # H1 square
            else:
                rook = self.get_piece_at(7, 7)  # H8 square
                       
            if rook and rook.type == 'rook' and not rook.has_moved:
                # Check if squares between king and rook are empty
                squares_empty = True
                for x in range(king.position_x + 1, rook.position_x):
                    piece_at_x = self.get_piece_at(x, king.position_y)
                    if piece_at_x:
                        squares_empty = False
                        break
                
                # Check if king doesn't pass through or end up in check
                if squares_empty:
                    # Check if king passes through check
                    passes_through_check = False
                    for x in range(king.position_x, king.position_x + 3):  # King moves 2 squares
                        would_be_check = self.would_be_in_check(king.color, king.position_x, king.position_y, x, king.position_y)
                        if would_be_check:
                            passes_through_check = True
                            break
                    
                    final_check = self.would_be_in_check(king.color, king.position_x, king.position_y, king.position_x + 2, king.position_y)
                    
                    if not passes_through_check and not final_check:
                        moves.append((king.position_x + 2, king.position_y))  # Kingside castling
            
            # Queenside castling (king moves 2 squares left)
            if king.color == 'white':
                rook = self.get_piece_at(0, 0)  # A1 square
            else:
                rook = self.get_piece_at(0, 7)  # A8 square
            
            if rook and rook.type == 'rook' and not rook.has_moved:
                # Check if squares between king and rook are empty
                squares_empty = True
                for x in range(rook.position_x + 1, king.position_x):
                    piece_at_x = self.get_piece_at(x, king.position_y)
                    if piece_at_x:
                        squares_empty = False
                        break
                
                # Check if king doesn't pass through or end up in check
                if squares_empty:
                    # Check if king passes through check
                    passes_through_check = False
                    for x in range(king.position_x - 2, king.position_x + 1):  # King moves 2 squares left
                        would_be_check = self.would_be_in_check(king.color, king.position_x, king.position_y, x, king.position_y)
                        if would_be_check:
                            passes_through_check = True
                            break
                    
                    final_check = self.would_be_in_check(king.color, king.position_x, king.position_y, king.position_x - 2, king.position_y)
                    
                    if not passes_through_check and not final_check:
                        moves.append((king.position_x - 2, king.position_y))  # Queenside castling
        
        return moves
    
    def is_in_check(self, color: str, exclude_piece: ChessPiece | None = None) -> bool:
        """Check if the king of the given color is in check.
        
        Determines if any opponent piece can attack the king.
        Optionally excludes a specific piece from the check calculation
        to avoid recursion in move validation.
        
        Args:
            color: The color of the king to check ('white' or 'black').
            exclude_piece: Optional piece to exclude from check calculation.
            
        Returns:
            bool: True if the king is in check.
        """
        # Find the king
        king = ChessPiece.objects.filter(game=self.game, type='king', color=color, is_captured=False).first()
        if not king:
            return False
        
        # Check if any opponent piece can attack the king
        opponent_pieces = ChessPiece.objects.filter(game=self.game, color='black' if color == 'white' else 'white', is_captured=False)
        if exclude_piece:
            opponent_pieces = opponent_pieces.exclude(id=exclude_piece.id)
        
        for piece in opponent_pieces:
            # Use basic valid moves without check validation to avoid recursion
            basic_moves = self.get_basic_valid_moves(piece)
            if (king.position_x, king.position_y) in basic_moves:
                return True
        
        return False
    
    def get_basic_valid_moves(self, piece: ChessPiece) -> list[tuple[int, int]]:
        """Get valid moves for a piece without check validation.
        
        Used internally to avoid recursion when checking for check conditions.
        Returns all possible moves based on piece movement rules
        without considering whether the move would leave the king in check.
        
        Args:
            piece: The ChessPiece to get moves for.
            
        Returns:
            list: List of (x, y) tuples representing valid moves.
        """
        if piece.type == 'pawn':
            return self.get_pawn_moves(piece)
        elif piece.type == 'rook':
            return self.get_rook_moves(piece)
        elif piece.type == 'knight':
            return self.get_knight_moves(piece)
        elif piece.type == 'bishop':
            return self.get_bishop_moves(piece)
        elif piece.type == 'queen':
            return self.get_queen_moves(piece)
        elif piece.type == 'king':
            return self.get_king_moves_basic(piece)
        return []
    
    def get_king_moves_basic(self, king: ChessPiece) -> list[tuple[int, int]]:
        """Get valid king moves without castling.
        
        Returns the one-square moves in all directions for the king.
        Used internally to avoid recursion in castling logic.
        
        Args:
            king: The king ChessPiece to get moves for.
            
        Returns:
            list: List of (x, y) tuples representing valid moves.
        """
        moves = []
        king_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        
        for dx, dy in king_moves:
            new_x = king.position_x + dx
            new_y = king.position_y + dy
            
            if self.is_valid_position(new_x, new_y):
                target = self.get_piece_at(new_x, new_y)
                if not target or target.color != king.color:
                    moves.append((new_x, new_y))
        
        return moves
    
    def would_be_in_check(self, color: str, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        """Check if moving a piece would result in check.
        
        Temporarily executes a move to see if it would leave the king of the
        given color in check. Used for move validation.
        
        Args:
            color: The color of the king to check.
            from_x: Starting X coordinate of the move.
            from_y: Starting Y coordinate of the move.
            to_x: Destination X coordinate of the move.
            to_y: Destination Y coordinate of the move.
            
        Returns:
            bool: True if the move would result in check.
        """
        # Get piece to move
        piece = self.get_piece_at(from_x, from_y)
        if not piece:
            return True
        
        # Get captured piece at destination
        captured_piece = self.get_piece_at(to_x, to_y)
        
        # Temporarily move piece to simulate the move
        original_x, original_y = piece.position_x, piece.position_y
        piece.position_x = to_x
        piece.position_y = to_y
        piece.save()
        
        # If capturing, mark the captured piece as captured
        if captured_piece:
            captured_piece.is_captured = True
            captured_piece.save()
        
        # Check if king would be in check after the move
        in_check = self.is_in_check(color)
        
        # Restore the piece to its original position
        piece.position_x, piece.position_y = original_x, original_y
        piece.save()
        
        # Restore the captured piece if it existed
        if captured_piece:
            captured_piece.is_captured = False
            captured_piece.save()
        
        return in_check
    
    def get_legal_moves(self, piece: ChessPiece) -> list[tuple[int, int]]:
        """Get moves that don't result in the king being in check.
        
        Filters out any moves that would leave the player's king in check,
        ensuring only legal chess moves are returned.
        
        Args:
            piece: The ChessPiece to get legal moves for.
            
        Returns:
            list: List of (x, y) tuples representing legal moves.
        """
        valid_moves = self.get_valid_moves(piece)
        legal_moves = []
        
        for to_x, to_y in valid_moves:
            would_be_check = self.would_be_in_check(piece.color, piece.position_x, piece.position_y, to_x, to_y)
            if not would_be_check:
                legal_moves.append((to_x, to_y))
        
        return legal_moves
    
    def get_legal_moves_with_en_passant(self, piece: ChessPiece) -> list[dict[str, int | bool]]:
        """Get legal moves with en passant information for frontend.
        
        Similar to get_legal_moves but includes additional metadata about
        whether each move is an en passant capture.
        
        Args:
            piece: The ChessPiece to get legal moves for.
            
        Returns:
            list: List of dictionaries with x, y, and is_en_passant keys.
        """
        valid_moves = self.get_valid_moves(piece)
        legal_moves = []
        
        for to_x, to_y in valid_moves:
            if not self.would_be_in_check(piece.color, piece.position_x, piece.position_y, to_x, to_y):
                # Check if this is an en passant capture (diagonal move to empty square)
                is_en_passant = False
                if piece.type == 'pawn' and abs(to_x - piece.position_x) == 1:
                    # Check if target square is empty (en passant capture)
                    if not self.get_piece_at(to_x, to_y):
                        # Check if there's a vulnerable pawn diagonally adjacent
                        # For white pawns moving up, vulnerable pawn is at (to_x, to_y - 1)
                        # For black pawns moving down, vulnerable pawn is at (to_x, to_y + 1)
                        if piece.color == 'white':
                            vulnerable_x = to_x
                            vulnerable_y = to_y - 1  # Square behind the destination
                        else:
                            vulnerable_x = to_x
                            vulnerable_y = to_y + 1  # Square behind the destination
                        
                        vulnerable_pawn = self.get_piece_at(vulnerable_x, vulnerable_y)
                        if (vulnerable_pawn and vulnerable_pawn.type == 'pawn' and 
                            vulnerable_pawn.color != piece.color and vulnerable_pawn.en_passant_vulnerable):
                            is_en_passant = True
                
                legal_moves.append({
                    'x': to_x, 
                    'y': to_y, 
                    'is_en_passant': is_en_passant
                })
        
        return legal_moves

    def is_stalemate(self, color: str) -> bool:
        """Check if the given color is in stalemate.

        Stalemate occurs when a player has no legal moves but their king is
        not in check.

        Args:
            color: The color to check for stalemate.

        Returns:
            bool: True if the color is in stalemate.
        """
        # Get all pieces of the given color
        pieces = ChessPiece.objects.filter(game=self.game, color=color, is_captured=False)

        for piece in pieces:
            legal_moves = self.get_legal_moves(piece)
            if legal_moves:
                return False
        
        # If no legal moves, check if the king is in check
        if self.is_in_check(color):
            return False
        else:
            return True
    
    def is_checkmate(self, color: str) -> bool:
        """Check if the given color is in checkmate.
        
        Checkmate occurs when a king is in check and there are
        no legal moves to escape the check.
        
        Args:
            color: The color to check for checkmate.
            
        Returns:
            bool: True if the color is in checkmate.
        """
        if not self.is_in_check(color):
            return False
        
        # Check if any piece can make a legal move
        pieces = ChessPiece.objects.filter(game=self.game, color=color, is_captured=False)
        
        for piece in pieces:
            legal_moves = self.get_legal_moves(piece)
            if legal_moves:
                return False
        
        return True
    
    def make_move(self, piece: ChessPiece, to_x: int, to_y: int, promotion_piece: str | None = None) -> Move:
        """Execute a chess move and update game state.
        
        Handles all aspects of move execution including:
        - Special moves (castling, en passant, pawn promotion)
        - Move recording and notation
        - Piece capture handling
        - Game state updates (check, checkmate, stalemate)
        - Turn switching
        
        Args:
            piece: The ChessPiece to move.
            to_x: Destination X coordinate.
            to_y: Destination Y coordinate.
            promotion_piece: Optional piece type for pawn promotion.
            
        Returns:
            Move: The created Move record.
        """
        from_x, from_y = piece.position_x, piece.position_y
        captured_piece = self.get_piece_at(to_x, to_y)
        
        # Handle special moves (including en passant and castling) BEFORE creating move record
        notation = None
        
        if piece.type == 'pawn':
            # En passant capture - check BEFORE clearing vulnerability
            # Check if this is an en passant capture (diagonal move to empty square)
            if abs(to_x - from_x) == 1 and not captured_piece:
                # For white pawns moving up, captured pawn is at (to_x, to_y - 1) - one square behind
                # For black pawns moving down, captured pawn is at (to_x, to_y + 1) - one square behind
                if piece.color == 'white':
                    # White pawns move up (increasing y)
                    captured_pawn_x = to_x
                    captured_pawn_y = to_y - 1  # One square behind the destination
                    captured_piece = self.get_piece_at(captured_pawn_x, captured_pawn_y)
                else:  # Black pawn
                    # Black pawns move down (decreasing y)
                    captured_pawn_x = to_x
                    captured_pawn_y = to_y + 1  # One square behind the destination
                    captured_piece = self.get_piece_at(captured_pawn_x, captured_pawn_y)
                
                if captured_piece and captured_piece.type == 'pawn' and captured_piece.en_passant_vulnerable:
                    # Mark the captured pawn as captured
                    captured_piece.is_captured = True
                    captured_piece.save()
                else:
                    captured_piece = None  # Reset to None if no valid en passant capture
        elif piece.type == 'king' and abs(to_x - from_x) == 2:
            # Check for castling
            if to_y == from_y and not captured_piece:
                # Kingside castling (king moves 2 squares right)
                if to_x > from_x:
                    if piece.color == 'white':
                        rook = self.get_piece_at(7, 0)  # H1 square
                        rook_to_x = 5  # F1 square
                    else:
                        rook = self.get_piece_at(7, 7)  # H8 square
                        rook_to_x = 5  # F8 square
                # Queenside castling (king moves 2 squares left)
                else:
                    if piece.color == 'white':
                        rook = self.get_piece_at(0, 0)  # A1 square
                        rook_to_x = 3  # D1 square
                    else:
                        rook = self.get_piece_at(0, 7)  # A8 square
                        rook_to_x = 3  # D8 square
                
                if rook and rook.type == 'rook' and not rook.has_moved:
                    rook.position_x = rook_to_x
                    rook.has_moved = True
                    rook.save()
                    notation = f"O-O" if to_x > from_x else f"O-O-O"
        
        # If no special notation set, use standard notation
        if not notation:
            notation = self.get_move_notation(piece, from_x, from_y, to_x, to_y, captured_piece)
        
        # Create move record
        # Chess move numbers represent pairs (1. White move, 1. Black move, 2. White move, 2. Black move, etc.)
        # Count existing moves to determine correct move number
        existing_moves = Move.objects.filter(game=self.game).count()
        move_number = (existing_moves // 2) + 1  # Integer division to get pair number
        
        move = Move.objects.create(
            game=self.game,
            piece=piece,
            from_x=from_x,
            from_y=from_y,
            to_x=to_x,
            to_y=to_y,
            captured_piece=captured_piece,
            move_number=move_number,
            notation=notation
        )
        
        # Handle capture
        if captured_piece:
            captured_piece.is_captured = True
            captured_piece.captured_at = timezone.now()
            # Move captured piece off the board to avoid position conflicts
            # Use unique off-board positions based on capture order
            capture_count = ChessPiece.objects.filter(game=self.game, is_captured=True).count()
            captured_piece.position_x = -10 - capture_count
            captured_piece.position_y = -10 - capture_count
            captured_piece.save()
            
            # Record captured piece
            CapturedPiece.objects.create(
                game=self.game,
                piece=captured_piece,
                captured_by=self.game.white_player if piece.color == 'white' else self.game.black_player
            )
        
        # Actually move the piece to its new position
        piece.position_x = to_x
        piece.position_y = to_y
        piece.has_moved = True
        
        # Handle en passant vulnerability for pawns that move 2 squares
        if piece.type == 'pawn':
            # Check if pawn moved 2 squares forward (from starting position)
            if abs(to_y - from_y) == 2:
                piece.en_passant_vulnerable = True
            else:
                piece.en_passant_vulnerable = False
        
        # Handle pawn promotion
        if piece.type == 'pawn':
            # Check if pawn reached the opposite end
            if (piece.color == 'white' and to_y == 7) or (piece.color == 'black' and to_y == 0):
                promoted_piece_type = promotion_piece if promotion_piece else 'queen'
                piece.type = promoted_piece_type
                piece.save()
                
                # Update the move record to reflect the promotion
                move.is_promotion = True
                move.promotion_piece = promoted_piece_type
                move.save()
        
        piece.save()
        
        # Clear en passant vulnerability for pawns of the same color that just moved
        # This prevents multiple pawns from being en passant vulnerable simultaneously
        # Clear vulnerability for all pawns of the same color EXCEPT the one that just moved
        # The pawn that just moved should remain vulnerable for the opponent's turn
        ChessPiece.objects.filter(game=self.game, type='pawn', color=piece.color, en_passant_vulnerable=True).exclude(id=piece.id).update(en_passant_vulnerable=False)
        
        # Check game status
        opponent_color = 'black' if self.game.current_turn == 'white' else 'white'
        
        if self.is_checkmate(opponent_color):
            self.game.status = 'checkmate'
            # Winner is the player who just made the checkmating move (opponent of the player in checkmate)
            self.game.winner = self.game.black_player if self.game.current_turn == 'black' else self.game.white_player
            self.game.ended_at = timezone.now()
        elif self.is_stalemate(opponent_color):
            self.game.status = 'stalemate'
            self.game.ended_at = timezone.now()
        elif self.is_in_check(opponent_color):
            self.game.status = 'check'
        else:
            self.game.status = 'active'
        
        # Switch turns
        old_turn = self.game.current_turn
        self.game.current_turn = 'black' if self.game.current_turn == 'white' else 'white'
        
        self.game.save()

        return move

    def get_move_notation(self, piece: ChessPiece, from_x: int, from_y: int, to_x: int, to_y: int, captured_piece: ChessPiece | None) -> str:
        """Generate algebraic chess notation for a move.
        
        Creates standard algebraic notation including piece symbols,
        capture indicators, and check/checkmate symbols.
        
        Args:
            piece: The ChessPiece being moved.
            from_x: Starting X coordinate.
            from_y: Starting Y coordinate.
            to_x: Destination X coordinate.
            to_y: Destination Y coordinate.
            captured_piece: The piece being captured (if any).
            
        Returns:
            str: The move in algebraic notation.
        """
        # Piece symbol (N, B, R, Q, K, P for pawn)
        if piece.type == 'pawn':
            piece_symbol = 'P'
        elif piece.type == 'knight':
            piece_symbol = 'N'  # Standard chess notation uses N for knight
        else:
            piece_symbol = piece.type[0].upper()
        
        # Start position
        from_square = chr(97 + from_x) + str(from_y + 1)
        
        # End position  
        to_square = chr(97 + to_x) + str(to_y + 1)
        
        # Capture notation
        capture_symbol = 'x' if captured_piece else '-'
        
        # Combine: Piece + Start + Capture + End
        notation = f"{piece_symbol}{from_square}{capture_symbol}{to_square}"
        
        # Check for check or checkmate
        opponent_color = 'black' if piece.color == 'white' else 'white'
        
        # Make the move temporarily to check for check/checkmate
        # Save current state
        original_to_piece = self.get_piece_at(to_x, to_y)
        original_from_x, original_from_y = piece.position_x, piece.position_y
        captured_piece_was_on_board = original_to_piece and original_to_piece.position_x >= 0
        
        # Make the temporary move
        piece.position_x = to_x
        piece.position_y = to_y
        if original_to_piece and captured_piece_was_on_board:
            original_to_piece.position_x = -10  # Move captured piece off board
        
        # Check for checkmate first (more specific)
        is_checkmate = self.is_checkmate(opponent_color)
        is_check = self.is_in_check(opponent_color)
        
        # Undo the temporary move
        piece.position_x = original_from_x
        piece.position_y = original_from_y
        if original_to_piece and captured_piece_was_on_board:
            original_to_piece.position_x = to_x
        
        # Add check/checkmate notation
        if is_checkmate:
            notation += '#'
        elif is_check:
            notation += '+'
        
        return notation
