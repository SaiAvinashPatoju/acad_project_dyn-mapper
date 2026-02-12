import pytest
from playwright.sync_api import Page, expect

def test_app_loads(page: Page):
    page.goto("http://localhost:8501")
    expect(page.locator("h1")).to_contain_text("AI Map Coloring System")
    # Check if map selection is visible
    expect(page.get_by_text("Map Source")).to_be_visible()

def test_solve_map(page: Page):
    page.goto("http://localhost:8501")
    
    # Wait for the sidebar to load and select map
    page.get_by_text("🚀 Solve Map").click()
    
    # Check for success message or "Performance Results" header
    expect(page.get_by_text("Performance Results")).to_be_visible(timeout=10000)
    
    # Verify metrics appear (via custom cards)
    expect(page.get_by_text("⏱️ Time")).to_be_visible()
    expect(page.get_by_text("🔍 Nodes")).to_be_visible()

def test_compare_algorithms(page: Page):
    page.goto("http://localhost:8501")
    
    # Click compare
    page.get_by_text("📊 Compare All Algorithms").click()
    
    # Wait for comparison to finish
    expect(page.get_by_text("Algorithm Speed Comparison")).to_be_visible(timeout=15000)
    
    # Verify comparison data appears
    expect(page.locator("[data-testid='stDataFrame']")).to_be_visible()

def test_custom_map_upload_ui(page: Page):
    page.goto("http://localhost:8501")
    
    # Switch to Custom Map (click the text label of the radio button)
    page.get_by_text("Custom Map (JSON)").click()
    
    # Verify file uploader appears
    expect(page.get_by_text("Upload JSON Map")).to_be_visible()
