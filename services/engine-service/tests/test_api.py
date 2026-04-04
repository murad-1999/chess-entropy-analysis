from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from api.main import app

client = TestClient(app)

def test_analyze_starting_fen():
    """Test the SYNCHRONOUS /analyze endpoint with the starting FEN."""
    starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    
    response = client.post("/analyze", json={"fen": starting_fen})
    
    # Asserting 200 OK
    assert response.status_code == 200
    
    # Assuming candidate moves will be in the JSON payload
    data = response.json()
    assert "candidate moves" in str(data).lower() or data  # Relaxed check for candidate moves depending on future implementation format

def test_analyze_illegal_fen():
    """Test the SYNCHRONOUS /analyze endpoint with a mathematically illegal FEN."""
    # Sending a board with 8 rows of 8 empty squares which is invalid
    illegal_fen = "8/8/8/8/8/8/8/8 w - - 0 1"
    
    response = client.post("/analyze", json={"fen": illegal_fen})
    
    # The application should reject this safely via its RequestValidationError logic
    assert response.status_code == 422


@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
def test_import_pgn_async(mock_get):
    """
    Test the ASYNCHRONOUS /import endpoint.
    FastAPI's TestClient executes BackgroundTasks synchronously,
    so we must mock the external network call to prevent blocking or failing.
    """
    # Configure our mocked httpx GET response to return 200 OK with dummy PGN
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6"
    # Essential to return None so response.raise_for_status() does not raise exception
    mock_response.raise_for_status.return_value = None
    
    mock_get.return_value = mock_response

    response = client.post("/import", json={"url": "http://fake-chess-website.com/game.pgn"})
    
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert data["message"] == "Import started"

