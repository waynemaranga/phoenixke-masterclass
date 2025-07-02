# test_webscraper_io.py
from typing import LiteralString
import pytest
from unittest.mock import Mock, patch, mock_open
import httpx
from pathlib import Path
import tempfile
import csv

# Import the functions to test
from webscraper_io import scrape_page, main, BASE_URL, OUTPUT

class TestScrapePage:
    """Test the scrape_page function"""
    
    @patch('webscraper_io.httpx.get')
    def test_scrape_page_success(self, mock_get) -> None:
        """Test successful scraping of a page"""
        # Mock HTML response
        mock_response = Mock(spec=httpx.Response)
        mock_response.text = """
        <html>
            <body>
                <div class="thumbnail">
                    <div class="title" title="Test Laptop 1">Test Laptop 1</div>
                    <div class="price">$999.99</div>
                    <div class="description">Great laptop for testing</div>
                </div>
                <div class="thumbnail">
                    <div class="title" title="Test Laptop 2">Test Laptop 2</div>
                    <div class="price">$1299.99</div>
                    <div class="description">Another great laptop</div>
                </div>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = scrape_page(1)
        
        # Verify the request was made correctly
        expected_url = BASE_URL.format(1)
        mock_get.assert_called_once_with(expected_url, timeout=10)
        
        # Verify the parsed results
        assert len(result) == 2 # type: ignore
        assert result[0] == ["Test Laptop 1", "$999.99", "Great laptop for testing"] # type: ignore
        assert result[1] == ["Test Laptop 2", "$1299.99", "Another great laptop"] # type: ignore
    
    @patch('webscraper_io.httpx.get')
    def test_scrape_page_empty_response(self, mock_get) -> None:
        """Test scraping a page with no products"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.text = "<html><body><div>No products here</div></body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = scrape_page(1)
        
        assert result == []
    
    @patch('webscraper_io.httpx.get')
    def test_scrape_page_malformed_html(self, mock_get) -> None:
        """Test scraping a page with malformed product HTML"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.text = """
        <html>
            <body>
                <div class="thumbnail">
                    <div class="title" title="Complete Laptop">Complete Laptop</div>
                    <div class="price">$999.99</div>
                    <div class="description">Complete description</div>
                </div>
                <div class="thumbnail">
                    <!-- Missing title attribute -->
                    <div class="title">Incomplete Laptop</div>
                    <div class="price">$799.99</div>
                    <div class="description">Incomplete description</div>
                </div>
                <div class="thumbnail">
                    <!-- Missing price -->
                    <div class="title" title="No Price Laptop">No Price Laptop</div>
                    <div class="description">No price description</div>
                </div>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = scrape_page(1)
        
        # Should only return the complete product
        assert len(result) == 1 # type: ignore
        assert result[0] == ["Complete Laptop", "$999.99", "Complete description"] # type: ignore
    
    @patch('webscraper_io.httpx.get')
    def test_scrape_page_http_error(self, mock_get) -> None:
        """Test scraping when HTTP request fails"""
        mock_get.side_effect = httpx.HTTPStatusError("404 Not Found", request=Mock(), response=Mock())
        
        result = scrape_page(1)
        
        assert result == []
    
    @patch('webscraper_io.httpx.get')
    def test_scrape_page_timeout_error(self, mock_get) -> None:
        """Test scraping when request times out"""
        mock_get.side_effect = httpx.TimeoutException("Request timed out")
        
        result = scrape_page(1)
        
        assert result == []
    
    @patch('webscraper_io.httpx.get')
    def test_scrape_page_connection_error(self, mock_get) -> None:
        """Test scraping when connection fails"""
        mock_get.side_effect = httpx.ConnectError("Connection failed")
        
        result = scrape_page(1)
        
        assert result == []
    
    @patch('webscraper_io.httpx.get')
    def test_scrape_page_url_format(self, mock_get) -> None:
        """Test that URL is formatted correctly for different page numbers"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Test different page numbers
        scrape_page(1)
        scrape_page(5)
        scrape_page(10)
        
        # Verify URLs were formatted correctly
        expected_calls = [
            (("https://webscraper.io/test-sites/e-commerce/static/computers/laptops?page=1",), {"timeout": 10}),
            (("https://webscraper.io/test-sites/e-commerce/static/computers/laptops?page=5",), {"timeout": 10}),
            (("https://webscraper.io/test-sites/e-commerce/static/computers/laptops?page=10",), {"timeout": 10})
        ]
        
        actual_calls = mock_get.call_args_list
        assert actual_calls == expected_calls

class TestMain:
    """Test the main function"""
    
    @patch('webscraper_io.scrape_page')
    @patch('webscraper_io.time.sleep')
    def test_main_scrapes_until_empty_page(self, mock_sleep, mock_scrape) -> None:
        """Test that main function scrapes pages until empty page is found"""
        # Mock scrape_page to return data for first 3 pages, then empty
        mock_scrape.side_effect = [
            [["Laptop 1", "$999", "Description 1"], ["Laptop 2", "$1299", "Description 2"]],  # Page 1
            [["Laptop 3", "$799", "Description 3"]],  # Page 2
            [["Laptop 4", "$1499", "Description 4"], ["Laptop 5", "$899", "Description 5"]],  # Page 3
            []  # Page 4 - empty, should stop
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            # Patch the OUTPUT constant to use our temp file
            with patch('webscraper_io.OUTPUT', Path(temp_filename)):
                main()
            
            # Verify scraping was called for pages 1-4
            expected_calls = [1, 2, 3, 4]
            actual_calls = [call[0][0] for call in mock_scrape.call_args_list]
            assert actual_calls == expected_calls
            
            # Verify sleep was called between pages
            assert mock_sleep.call_count == 3  # Should sleep after pages 1, 2, 3
            
            # Verify CSV file was created with correct content
            with open(temp_filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                # Check headers
                assert rows[0] == ["Title", "Price", "Description"]
                
                # Check data rows (5 products total)
                assert len(rows) == 6  # Header + 5 data rows
                assert rows[1] == ["Laptop 1", "$999", "Description 1"]
                assert rows[2] == ["Laptop 2", "$1299", "Description 2"]
                assert rows[3] == ["Laptop 3", "$799", "Description 3"]
                assert rows[4] == ["Laptop 4", "$1499", "Description 4"]
                assert rows[5] == ["Laptop 5", "$899", "Description 5"]
        
        finally:
            Path(temp_filename).unlink(missing_ok=True)
    
    @patch('webscraper_io.scrape_page')
    @patch('webscraper_io.time.sleep')
    def test_main_handles_empty_first_page(self, mock_sleep, mock_scrape) -> None:
        """Test that main function handles empty first page"""
        mock_scrape.return_value = []  # First page is empty
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            with patch('webscraper_io.OUTPUT', Path(temp_filename)):
                main()
            
            # Should only call scrape_page once
            mock_scrape.assert_called_once_with(1)
            
            # Should not call sleep
            mock_sleep.assert_not_called()
            
            # Verify CSV file was created with only headers
            with open(temp_filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                assert len(rows) == 1  # Only header
                assert rows[0] == ["Title", "Price", "Description"]
        
        finally:
            Path(temp_filename).unlink(missing_ok=True)
    
    @patch('webscraper_io.scrape_page')
    @patch('webscraper_io.time.sleep')
    def test_main_handles_single_page(self, mock_sleep, mock_scrape) -> None:
        """Test that main function handles single page with data"""
        mock_scrape.side_effect = [
            [["Single Laptop", "$999", "Only laptop"]],  # Page 1
            []  # Page 2 - empty, should stop
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            with patch('webscraper_io.OUTPUT', Path(temp_filename)):
                main()
            
            # Should call scrape_page twice
            assert mock_scrape.call_count == 2
            
            # Should call sleep once (after page 1)
            mock_sleep.assert_called_once_with(1)
            
            # Verify CSV file content
            with open(temp_filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                assert len(rows) == 2  # Header + 1 data row
                assert rows[1] == ["Single Laptop", "$999", "Only laptop"]
        
        finally:
            Path(temp_filename).unlink(missing_ok=True)
    
    @patch('webscraper_io.scrape_page')
    @patch('webscraper_io.time.sleep')
    def test_main_creates_output_directory(self, mock_sleep, mock_scrape) -> None:
        """Test that main function creates output directory if it doesn't exist"""
        mock_scrape.return_value = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_output_dir: Path = Path(temp_dir) / "test_output"
            temp_output_file: Path = temp_output_dir / "test_laptops.csv"
            
            # Directory should not exist initially
            assert not temp_output_dir.exists()
            
            with patch('webscraper_io.OUTPUT', temp_output_file):
                main()
            
            # Directory should be created by the function
            assert temp_output_dir.exists()
            assert temp_output_file.exists()

# Fixtures for common test data
@pytest.fixture
def sample_html() -> LiteralString:
    """Fixture providing sample HTML for testing"""
    return """
    <html>
        <body>
            <div class="thumbnail">
                <div class="title" title="Test Laptop">Test Laptop</div>
                <div class="price">$999.99</div>
                <div class="description">Great laptop for testing</div>
            </div>
        </body>
    </html>
    """

@pytest.fixture
def sample_laptops() -> list[list[str]]:
    """Fixture providing sample laptop data for tests"""
    return [
        ["Laptop 1", "$999", "Description 1"],
        ["Laptop 2", "$1299", "Description 2"],
        ["Laptop 3", "$799", "Description 3"]
    ]

@pytest.fixture
def mock_httpx_response() -> Mock:
    """Fixture providing a mock httpx response"""
    response = Mock(spec=httpx.Response)
    response.raise_for_status = Mock()
    return response