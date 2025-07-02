# test_jumia_scraper.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import csv
import json
from selenium.webdriver.chrome.webdriver import WebDriver

# Import the functions to test
from jumia_scraper import (
    setup_driver, 
    parse_appliance_page, 
    save_to_csv, 
    save_to_json, 
    main
)

class TestSetupDriver:
    """Test the setup_driver function"""
    
    @patch('jumia_scraper.selenium.webdriver.Chrome')
    @patch('jumia_scraper.ChromeDriverManager')
    def test_setup_driver_returns_webdriver(self, mock_chrome_manager, mock_chrome) -> None:
        """Test that setup_driver returns a WebDriver instance"""
        mock_driver = Mock(spec=WebDriver)
        mock_chrome.return_value = mock_driver
        mock_chrome_manager.return_value.install.return_value = "/fake/path"
        
        driver: WebDriver = setup_driver()
        
        assert driver == mock_driver
        mock_chrome.assert_called_once()
    
    @patch('jumia_scraper.selenium.webdriver.Chrome')
    @patch('jumia_scraper.ChromeDriverManager')
    def test_setup_driver_configures_options(self, mock_chrome_manager, mock_chrome) -> None:
        """Test that setup_driver configures Chrome options correctly"""
        mock_driver = Mock(spec=WebDriver)
        mock_chrome.return_value = mock_driver
        mock_chrome_manager.return_value.install.return_value = "/fake/path"
        
        setup_driver()
        
        # Verify Chrome was called with options
        args, kwargs = mock_chrome.call_args
        assert 'options' in kwargs
        assert 'service' in kwargs

class TestParseAppliancePage:
    """Test the parse_appliance_page function"""
    
    def test_parse_empty_html(self) -> None:
        """Test parsing empty HTML returns empty list"""
        html = "<html><body></body></html>"
        result = parse_appliance_page(html)
        assert result == []
    
    def test_parse_html_with_no_products(self) -> None:
        """Test parsing HTML with no product cards"""
        html = """
        <html>
            <body>
                <div class="some-other-content">No products here</div>
            </body>
        </html>
        """
        result = parse_appliance_page(html)
        assert result == []
    
    def test_parse_html_with_single_product(self) -> None:
        """Test parsing HTML with a single product"""
        html = """
        <html>
            <body>
                <article class="prd _fb col c-prd">
                    <div class="info">
                        <h3 class="name">Test Appliance</h3>
                        <div class="prc">KSh 1,000</div>
                    </div>
                </article>
            </body>
        </html>
        """
        result = parse_appliance_page(html)
        
        assert len(result) == 1
        product = result[0]
        assert len(product) == 9  # Product_ID, Title, Price, Old Price, Discount, Badge, Rating, Number of Reviews, Shipping
        assert product[1] == "Test Appliance"  # Title
        assert product[2] == "KSh 1,000"  # Price
        assert len(product[0]) == 4  # Product_ID should be 4 characters
    
    def test_parse_html_with_complete_product(self) -> None:
        """Test parsing HTML with a product that has all optional fields"""
        html = """
        <html>
            <body>
                <article class="prd _fb col c-prd">
                    <div class="info">
                        <h3 class="name">Complete Appliance</h3>
                        <div class="prc">KSh 2,000</div>
                        <div class="old">KSh 2,500</div>
                        <div class="bdg _dsct _sm">-20%</div>
                        <div class="bdg _mall _xs">Jumia Mall</div>
                        <div class="rev">
                            <div class="stars _s">4.5 out of 5</div>
                            <span>(123)</span>
                        </div>
                        <svg class="ic xprss"></svg>
                    </div>
                </article>
            </body>
        </html>
        """
        result = parse_appliance_page(html)
        
        assert len(result) == 1
        product = result[0]
        assert product[1] == "Complete Appliance"  # Title
        assert product[2] == "KSh 2,000"  # Price
        assert product[3] == "KSh 2,500"  # Old Price
        assert product[4] == "-20%"  # Discount
        assert product[5] == "Jumia Mall"  # Badge
        assert product[6] == "4.5"  # Rating
        assert product[7] == "123"  # Number of Reviews
        assert product[8] == "Express"  # Shipping
    
    def test_parse_html_with_multiple_products(self) -> None:
        """Test parsing HTML with multiple products"""
        html = """
        <html>
            <body>
                <article class="prd _fb col c-prd">
                    <div class="info">
                        <h3 class="name">Product 1</h3>
                        <div class="prc">KSh 1,000</div>
                    </div>
                </article>
                <article class="prd _fb col c-prd">
                    <div class="info">
                        <h3 class="name">Product 2</h3>
                        <div class="prc">KSh 2,000</div>
                    </div>
                </article>
            </body>
        </html>
        """
        result = parse_appliance_page(html)
        
        assert len(result) == 2
        assert result[0][1] == "Product 1"
        assert result[1][1] == "Product 2"
    
    def test_parse_html_removes_quotes_from_text(self) -> None:
        """Test that quotes are removed from product text"""
        html = """
        <html>
            <body>
                <article class="prd _fb col c-prd">
                    <div class="info">
                        <h3 class="name">"Quoted" Appliance</h3>
                        <div class="prc">KSh "1,000"</div>
                        <div class="old">KSh "1,500"</div>
                    </div>
                </article>
            </body>
        </html>
        """
        result = parse_appliance_page(html)
        
        assert len(result) == 1
        product = result[0]
        assert product[1] == "Quoted Appliance"  # Title without quotes
        assert product[2] == "KSh 1000"  # Price without quotes and commas
        assert product[3] == "KSh 1500"  # Old price without quotes

class TestSaveToCsv:
    """Test the save_to_csv function"""
    
    def test_save_to_csv_creates_file(self) -> None:
        """Test that save_to_csv creates a CSV file with correct content"""
        products = [
            ["A1B2", "Test Product", "KSh 1,000", "", "", "", "", "", ""],
            ["C3D4", "Another Product", "KSh 2,000", "KSh 2,500", "-20%", "Jumia Mall", "4.5", "123", "Express"]
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            save_to_csv(products, temp_filename)
            
            # Verify file was created and has correct content
            with open(temp_filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                # Check headers
                expected_headers = ["Product_ID", "Title", "Price", "Old Price", "Discount", "Badge", "Rating", "Number of Reviews", "Shipping"]
                assert rows[0] == expected_headers
                
                # Check data rows
                assert len(rows) == 3  # Header + 2 data rows
                assert rows[1] == products[0]
                assert rows[2] == products[1]
        
        finally:
            Path(temp_filename).unlink(missing_ok=True)
    
    def test_save_to_csv_empty_products(self) -> None:
        """Test save_to_csv with empty products list"""
        products = []
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            save_to_csv(products, temp_filename)
            
            # Verify file was created with only headers
            with open(temp_filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                assert len(rows) == 1  # Only header row
                expected_headers = ["Product_ID", "Title", "Price", "Old Price", "Discount", "Badge", "Rating", "Number of Reviews", "Shipping"]
                assert rows[0] == expected_headers
        
        finally:
            Path(temp_filename).unlink(missing_ok=True)

class TestSaveToJson:
    """Test the save_to_json function"""
    
    def test_save_to_json_creates_file(self) -> None:
        """Test that save_to_json creates a JSON file with correct structure"""
        products = [
            ["A1B2", "Test Product", "KSh 1,000", "", "", "", "", "", ""],
            ["C3D4", "Another Product", "KSh 2,000", "KSh 2,500", "-20%", "Jumia Mall", "4.5", "123", "Express"]
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            save_to_json(products, temp_filename)
            
            # Verify file was created and has correct content
            with open(temp_filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                assert len(data) == 2
                assert "A1B2" in data
                assert "C3D4" in data
                
                # Check structure of first product
                product1 = data["A1B2"]
                assert product1["Title"] == "Test Product"
                assert product1["Price"] == "KSh 1,000"
                assert "Product_ID" not in product1  # Should not include Product_ID in nested data
                
                # Check structure of second product
                product2 = data["C3D4"]
                assert product2["Title"] == "Another Product"
                assert product2["Old Price"] == "KSh 2,500"
                assert product2["Discount"] == "-20%"
        
        finally:
            Path(temp_filename).unlink(missing_ok=True)
    
    def test_save_to_json_empty_products(self) -> None:
        """Test save_to_json with empty products list"""
        products = []
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            save_to_json(products, temp_filename)
            
            # Verify file was created with empty object
            with open(temp_filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert data == {}
        
        finally:
            Path(temp_filename).unlink(missing_ok=True)

class TestMain:
    """Test the main function"""
    
    @patch('jumia_scraper.setup_driver')
    @patch('jumia_scraper.parse_appliance_page')
    @patch('jumia_scraper.save_to_csv')
    @patch('jumia_scraper.save_to_json')
    @patch('jumia_scraper.time.sleep')
    def test_main_scrapes_multiple_pages(self, mock_sleep, mock_save_json, mock_save_csv, mock_parse, mock_setup) -> None:
        """Test that main function scrapes multiple pages successfully"""
        # Setup mocks
        mock_driver = Mock(spec=WebDriver)
        mock_setup.return_value = mock_driver
        mock_driver.page_source = "<html>test</html>"
        
        # Mock parse_appliance_page to return products for first 2 pages, empty for 3rd
        mock_parse.side_effect = [
            [["A1B2", "Product 1", "KSh 1,000", "", "", "", "", "", ""]],  # Page 1
            [["C3D4", "Product 2", "KSh 2,000", "", "", "", "", "", ""]],  # Page 2
            []  # Page 3 - empty, should stop
        ]
        
        main()
        
        # Verify driver setup and cleanup
        mock_setup.assert_called_once()
        mock_driver.quit.assert_called_once()
        
        # Verify pages were scraped
        assert mock_driver.get.call_count == 3
        expected_urls = [
            "https://www.jumia.co.ke/home-office-appliances/?page=1#catalog-listing",
            "https://www.jumia.co.ke/home-office-appliances/?page=2#catalog-listing",
            "https://www.jumia.co.ke/home-office-appliances/?page=3#catalog-listing"
        ]
        actual_urls = [call[0][0] for call in mock_driver.get.call_args_list]
        assert actual_urls == expected_urls
        
        # Verify parsing was called for each page
        assert mock_parse.call_count == 3
        
        # Verify save functions were called
        mock_save_csv.assert_called_once()
        mock_save_json.assert_called_once()
        
        # Verify sleep was called between pages
        assert mock_sleep.call_count >= 2  # At least 2 calls for delays
    
    @patch('jumia_scraper.setup_driver')
    @patch('jumia_scraper.parse_appliance_page')
    @patch('jumia_scraper.save_to_csv')
    @patch('jumia_scraper.save_to_json')
    def test_main_handles_no_products(self, mock_save_json, mock_save_csv, mock_parse, mock_setup):
        """Test that main function handles case when no products are found"""
        # Setup mocks
        mock_driver = Mock(spec=WebDriver)
        mock_setup.return_value = mock_driver
        mock_driver.page_source = "<html>test</html>"
        mock_parse.return_value = []  # No products found
        
        main()
        
        # Verify driver setup and cleanup
        mock_setup.assert_called_once()
        mock_driver.quit.assert_called_once()
        
        # Verify save functions were not called
        mock_save_csv.assert_not_called()
        mock_save_json.assert_not_called()
    
    @patch('jumia_scraper.setup_driver')
    def test_main_handles_driver_exception(self, mock_setup) -> None:
        """Test that main function handles exceptions during scraping"""
        # Setup mock to raise exception
        mock_driver = Mock(spec=WebDriver)
        mock_setup.return_value = mock_driver
        mock_driver.get.side_effect = Exception("Connection error")
        
        # Should not raise exception
        main()
        
        # Verify driver cleanup is called even on exception
        mock_driver.quit.assert_called_once()

# Fixtures for common test data
@pytest.fixture
def sample_products() -> list[list[str]]:
    """Fixture providing sample product data for tests"""
    return [
        ["A1B2", "Test Appliance 1", "KSh 1,000", "", "", "", "", "", ""],
        ["C3D4", "Test Appliance 2", "KSh 2,000", "KSh 2,500", "-20%", "Jumia Mall", "4.5", "123", "Express"],
        ["E5F6", "Test Appliance 3", "KSh 3,000", "", "", "", "3.8", "45", ""]
    ]

@pytest.fixture
def sample_html():
    """Fixture providing sample HTML for testing"""
    return """
    <html>
        <body>
            <article class="prd _fb col c-prd">
                <div class="info">
                    <h3 class="name">Test Product</h3>
                    <div class="prc">KSh 1,000</div>
                </div>
            </article>
        </body>
    </html>
    """