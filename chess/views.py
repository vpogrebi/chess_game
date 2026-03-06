"""Django views for the chess game application.

This module contains view functions and class-based views that handle HTTP requests
and responses for the chess game. It provides the main interface between the
frontend and the chess game logic.

Views handle:
- Game creation and management
- Move validation and execution
- Game state updates
- Player interactions (resignation, draw offers)
- Board rendering and game display

"""

from typing import Any
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views import View
from .models import Game, Player, ChessPiece, Move, CapturedPiece, DrawOffer
from .game_logic import ChessGameLogic


def chess_home(request: HttpRequest) -> HttpResponse:
    """Render the main chess home page.

    Displays the landing page with navigation to game creation
    and game listing options.

    Args:
        request: HTTP request object.

    Returns:
        HttpResponse: Rendered home page template.
    """
    return render(request, 'chess/home.html')


def create_game(request: HttpRequest) -> HttpResponse:
    """Create a new chess game.

    Handles both GET and POST requests:
    - GET: Display the game creation form
    - POST: Process form data and create a new game with players

    Creates or updates players with the provided names and randomly assigns
    them to white and black pieces based on random color assignment.
    Then creates a new game instance.

    Args:
        request: HTTP request object containing form data.

    Returns:
        HttpResponse: Game creation form (GET) or redirect to game (POST).
    """
    if request.method == 'POST':
        # Get player names from form (without color specification)
        player1_first_name = request.POST.get('player1_first_name', 'Player')
        player1_last_name = request.POST.get('player1_last_name', 'One')
        player2_first_name = request.POST.get('player2_first_name', 'Player')
        player2_last_name = request.POST.get('player2_last_name', 'Two')
        
        # Randomly assign colors to players
        import random
        player1_is_white = random.choice([True, False])
        
        if player1_is_white:
            # Player 1 is white, Player 2 is black
            white_first_name, white_last_name = player1_first_name, player1_last_name
            black_first_name, black_last_name = player2_first_name, player2_last_name
        else:
            # Player 1 is black, Player 2 is white
            white_first_name, white_last_name = player2_first_name, player2_last_name
            black_first_name, black_last_name = player1_first_name, player1_last_name
        
        # Get or create players with assigned colors
        white_player, _ = Player.objects.get_or_create(
            color='white',
            defaults={
                'first_name': white_first_name,
                'last_name': white_last_name
            }
        )
        black_player, _ = Player.objects.get_or_create(
            color='black',
            defaults={
                'first_name': black_first_name,
                'last_name': black_last_name
            }
        )
        
        # Update player names if they exist
        white_player.first_name = white_first_name
        white_player.last_name = white_last_name
        white_player.save()
        
        black_player.first_name = black_first_name
        black_player.last_name = black_last_name
        black_player.save()
        
        # Create game with descriptive name showing color assignment
        game = Game.objects.create(
            white_player=white_player,
            black_player=black_player,
            name=f"{white_player.full_name} (white) vs {black_player.full_name} (black)"
        )
        
        # Store color assignment info in session for display
        request.session['color_assignment'] = {
            'player1': {
                'name': f"{player1_first_name} {player1_last_name}",
                'color': 'white' if player1_is_white else 'black'
            },
            'player2': {
                'name': f"{player2_first_name} {player2_last_name}",
                'color': 'black' if player1_is_white else 'white'
            }
        }
        
        return redirect('chess:game', game_id=game.id)
    
    return render(request, 'chess/create_game.html')


def game_view(request: HttpRequest, game_id: int) -> HttpResponse:
    """Display and manage a chess game.

    Renders the game board with all current pieces, move history,
    and captured pieces. Creates a board representation optimized
    for frontend display with proper coordinate mapping.

    Args:
        request: HTTP request object.
        game_id: ID of the game to display.

    Returns:
        HttpResponse: Rendered game template with board state.
    """
    game = get_object_or_404(Game, id=game_id)
    pieces = ChessPiece.objects.filter(game=game, is_captured=False).order_by('position_y', 'position_x')
    captured_pieces = ChessPiece.objects.filter(game=game, is_captured=True)
    moves = Move.objects.filter(game=game).order_by('move_number')
    
    # Create board representation with coordinates
    board = [[None for _ in range(8)] for _ in range(8)]
    for piece in pieces:
        board[piece.position_y][piece.position_x] = piece
    
    # Serialize moves for JavaScript
    moves_data = []
    for move in moves:
        moves_data.append({
            'notation': move.notation,
            'move_number': move.move_number
        })
    
    # Create coordinate mapping for frontend (reversed board)
    # visual_row 0 (top) should map to database row 7
    # visual_row 6 should map to database row 1 (where e2 pawn is)
    # visual_row 7 (bottom) should map to database row 0
    board_with_coords = []
    for visual_row in range(8):
        db_row = 7 - visual_row  # Map visual row to database row
        board_row = []
        for col in range(8):
            piece_with_coord = {
                'piece': board[db_row][col],
                'db_y': db_row  # Store the database y-coordinate
            }
            board_row.append(piece_with_coord)
        board_with_coords.append(board_row)
    
    context = {
        'game': game,
        'board': board_with_coords,
        'pieces': pieces,
        'captured_pieces': captured_pieces,
        'moves': moves,
        'moves_json': json.dumps(moves_data),
        'color_assignment': request.session.pop('color_assignment', None)
    }
    
    return render(request, 'chess/game.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class StartGameView(View):
    """Handle game start requests.

    Processes POST requests to start a game and initialize
    all chess pieces in their starting positions.
    """
    
    def post(self, request: HttpRequest, game_id: int) -> JsonResponse:
        """Start the specified game.

        Args:
            request: HTTP request object.
            game_id: ID of the game to start.

        Returns:
            JsonResponse: Success status and game state.
        """
        try:
            game = get_object_or_404(Game, id=game_id)
            game.start_game()
            return JsonResponse({'status': 'success', 'game_status': game.status})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
class MoveView(View):
    """Handle chess piece move requests.

    Processes POST requests for piece movement, validates moves,
    executes legal moves, and updates game state including
    special moves like castling and en passant.
    """
    
    def post(self, request: HttpRequest, game_id: int) -> JsonResponse:
        """Process a chess move.

        Validates the move, checks turn order, executes the move,
        and returns updated game state. Handles special moves
        including pawn promotion.

        Args:
            request: HTTP request containing move data.
            game_id: ID of the game.

        Returns:
            JsonResponse: Move result and updated game state.
        """
        # Write to a file to test if this code is being executed
        game = get_object_or_404(Game, id=game_id)
        
        if game.status in ['checkmate', 'stalemate']:
            return JsonResponse({'status': 'error', 'message': 'Game is over'})
        
        try:
            data = json.loads(request.body)
            from_x = data['from_x']
            from_y = data['from_y']
            to_x = data['to_x']
            to_y = data['to_y']
            promotion_piece = data.get('promotion_piece', None)
            
            piece = ChessPiece.objects.get(
                game=game, 
                position_x=from_x, 
                position_y=from_y, 
                is_captured=False
            )
            
            if piece.color != game.current_turn:
                return JsonResponse({'status': 'error', 'message': 'Not your turn'})
            
            logic = ChessGameLogic(game)
            legal_moves = logic.get_legal_moves(piece)
            
            if (to_x, to_y) not in legal_moves:
                return JsonResponse({'status': 'error', 'message': 'Invalid move'})
            
            try:
                move = logic.make_move(piece, to_x, to_y, promotion_piece)
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
            
            return JsonResponse({
                'status': 'success',
                'move': {
                    'from': {'x': from_x, 'y': from_y},
                    'to': {'x': to_x, 'y': to_y},
                    'notation': move.notation,
                    'captured': move.captured_piece.type if move.captured_piece else None,
                    'is_en_passant': move.is_en_passant,
                    'promotion_piece': move.promotion_piece if hasattr(move, 'promotion_piece') else None
                },
                'game_status': game.status,
                'current_turn': game.current_turn,
                'winner': game.winner.full_name if game.winner else None
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
class GetValidMovesView(View):
    """Handle requests for valid moves of a specific piece.

    Returns all legal moves for a given piece, including
    special moves like en passant captures.
    """
    
    def post(self, request: HttpRequest, game_id: int) -> JsonResponse:
        """Get valid moves for a piece at the specified position.

        Args:
            request: HTTP request containing piece coordinates.
            game_id: ID of the game.

        Returns:
            JsonResponse: List of valid move coordinates.
        """
        game = get_object_or_404(Game, id=game_id)
        
        try:
            data = json.loads(request.body)
            x = data['x']
            y = data['y']
            
            piece = ChessPiece.objects.get(
                game=game, 
                position_x=x, 
                position_y=y, 
                is_captured=False
            )
            
            if piece.color != game.current_turn:
                return JsonResponse({'status': 'error', 'message': 'Not your turn'})
            
            logic = ChessGameLogic(game)
            legal_moves = logic.get_legal_moves_with_en_passant(piece)
            
            # Convert to frontend format (already in correct format from get_legal_moves_with_en_passant)
            formatted_moves = legal_moves
            
            return JsonResponse({
                'status': 'success',
                'moves': formatted_moves
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


class CheckStatusView(View):
    """Check game status including check and checkmate conditions.

    Evaluates the current game state to determine if a player
    is in check, checkmate, or if the game has ended.
    """
    
    def post(self, request: HttpRequest, game_id: int) -> JsonResponse:
        """Check the current game status.

        Evaluates check conditions and checks for checkmate
        or stalemate scenarios.

        Args:
            request: HTTP request object.
            game_id: ID of the game to check.

        Returns:
            JsonResponse: Current game status and check information.
        """
        try:
            game = get_object_or_404(Game, id=game_id)
            
            # Always return game status, even if game is not active
            logic = ChessGameLogic(game)
            
            # If game is not active, return the current status without further checks
            if game.status != 'active':
                response_data = {
                    'status': 'success',
                    'game_status': game.status,
                    'current_turn': game.current_turn,
                    'winner': game.winner.full_name if game.winner else None,
                    'is_in_check': False
                }
                return JsonResponse(response_data)
            
            # For active games, check if current player is in check
            is_in_check = logic.is_in_check(game.current_turn)
            
            # Check for checkmate if the current player is in check
            if is_in_check:
                # Check if the OPPONENT is in checkmate (not the current player)
                opponent_color = 'black' if game.current_turn == 'white' else 'white'
                if logic.is_checkmate(opponent_color):
                    game.status = 'checkmate'
                    game.winner = game.white_player if game.current_turn == 'black' else game.black_player
                    game.ended_at = timezone.now()
                    game.save()
            
            return JsonResponse({
                'status': 'success',
                'is_in_check': is_in_check,
                'current_turn': game.current_turn,
                'game_status': game.status,
                'winner': game.winner.full_name if game.winner else None
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


def game_list(request: HttpRequest) -> HttpResponse:
    """Display a list of all chess games.

    Shows all games in the system ordered by creation date,
    with the most recent games appearing first.

    Args:
        request: HTTP request object.

    Returns:
        HttpResponse: Rendered game list template.
    """
    games = Game.objects.all().order_by('-created_at')
    return render(request, 'chess/game_list.html', {'games': games})


def delete_game(request: HttpRequest, game_id: int) -> HttpResponse:
    """Delete a game and all related data.

    Handles POST requests to permanently delete a game,
    including all associated pieces, moves, and game data.

    Args:
        request: HTTP request object.
        game_id: ID of the game to delete.

    Returns:
        HttpResponse: Redirect to game list after deletion.
    """
    if request.method == 'POST':
        game = get_object_or_404(Game, id=game_id)
        game.delete()
        return redirect('chess:game_list')

@method_decorator(csrf_exempt, name='dispatch')
class ResignView(View):
    """Handle player resignation requests.

    Processes resignation from the current player, ending the game
    and declaring the opponent as the winner.
    """
    
    def post(self, request: HttpRequest, game_id: int) -> JsonResponse:
        """Process player resignation.

        Determines which player is resigning based on the current turn,
        ends the game, and declares the opponent as winner.

        Args:
            request: HTTP request object.
            game_id: ID of the game.

        Returns:
            JsonResponse: Resignation result and winner information.
        """
        game = get_object_or_404(Game, id=game_id)
        
        if game.status in ['checkmate', 'stalemate']:
            return JsonResponse({'status': 'error', 'message': 'Game is already over'})
        
        try:
            # Determine which player is resigning based on current turn
            resigning_player = game.white_player if game.current_turn == 'white' else game.black_player
            
            # Set game status to indicate resignation (not checkmate)
            game.status = 'resigned'
            # Winner is the OPPONENT of the resigning player
            game.winner = game.black_player if game.current_turn == 'white' else game.white_player
            game.ended_at = timezone.now()
            game.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'{resigning_player.full_name} resigned. {game.winner.full_name} wins!'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class DrawView(View):
    """Handle draw offers and responses.

    Manages the draw offer system including creating offers,
    accepting draws, and declining offers. Handles turn management
    and game state updates for draw scenarios.
    """
    
    def post(self, request: HttpRequest, game_id: int) -> JsonResponse:
        """Process draw-related actions.

        Handles three types of draw actions:
        - offer: Create a new draw offer
        - accept: Accept an existing draw offer
        - deny: Decline a draw offer

        Args:
            request: HTTP request containing action data.
            game_id: ID of the game.

        Returns:
            JsonResponse: Draw action result and updated game state.
        """
        game = get_object_or_404(Game, id=game_id)
        
        if game.status in ['checkmate', 'stalemate', 'resigned']:
            return JsonResponse({'status': 'error', 'message': 'Game is already over'})
        
        try:
            data = json.loads(request.body)
            action = data.get('action', 'offer')  # 'offer', 'accept', 'deny'
            
            if action == 'offer':
                # Create draw offer
                # Check if there's already an active draw offer
                existing_offer = DrawOffer.objects.filter(game=game, is_active=True).first()
                if existing_offer:
                    return JsonResponse({'status': 'error', 'message': 'Draw offer already active'})
                
                # Determine which player is offering the draw
                offering_player = game.white_player if game.current_turn == 'white' else game.black_player
                
                DrawOffer.objects.create(
                    game=game,
                    offering_player=offering_player
                )
                
                # Switch turn to opponent after offering draw
                game.current_turn = 'black' if game.current_turn == 'white' else 'white'
                game.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Draw offer sent to opponent!',
                    'action': 'offered',
                    'current_turn': game.current_turn
                })
                
            elif action == 'accept':
                # Accept draw offer
                active_offer = DrawOffer.objects.filter(game=game, is_active=True).first()
                if not active_offer:
                    return JsonResponse({'status': 'error', 'message': 'No active draw offer to accept'})
                
                # End game as draw
                game.status = 'draw'
                game.ended_at = timezone.now()
                game.save()
                
                # Deactivate the draw offer
                active_offer.is_active = False
                active_offer.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Draw accepted! Game ends in draw.',
                    'action': 'accepted'
                })
                
            elif action == 'deny':
                # Deny draw offer
                active_offer = DrawOffer.objects.filter(game=game, is_active=True).first()
                if not active_offer:
                    return JsonResponse({'status': 'error', 'message': 'No active draw offer to deny'})
                
                # Just deactivate the offer, game continues
                active_offer.is_active = False
                active_offer.save()
                
                # Switch turn back to the offering player
                game.current_turn = 'white' if game.current_turn == 'black' else 'black'
                game.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Draw offer denied. Game continues.',
                    'action': 'denied',
                    'current_turn': game.current_turn
                })
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class CheckDrawOfferView(View):
    """Check for active draw offers.

    Determines if there's an active draw offer that the current
    player can respond to, providing information about who made
    the offer.
    """
    
    def get(self, request: HttpRequest, game_id: int) -> JsonResponse:
        """Check for active draw offers for the current game.

        Returns information about any active draw offers and whether
        the current player is the intended recipient.

        Args:
            request: HTTP request object.
            game_id: ID of the game to check.

        Returns:
            JsonResponse: Draw offer status and information.
        """
        game = get_object_or_404(Game, id=game_id)
        
        try:
            # Check if there's an active draw offer
            active_offer = DrawOffer.objects.filter(game=game, is_active=True).first()
            
            if active_offer:
                # Determine if the current player is the one who should respond
                current_player = game.white_player if game.current_turn == 'white' else game.black_player
                
                # The offer is for the opponent of the offering player
                if active_offer.offering_player != current_player:
                    return JsonResponse({
                        'status': 'success',
                        'has_offer': True,
                        'offering_player': active_offer.offering_player.full_name
                    })
            
            return JsonResponse({
                'status': 'success',
                'has_offer': False
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
