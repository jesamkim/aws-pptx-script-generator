"""Basic functionality tests."""

def test_imports():
    """Test that all modules can be imported."""
    try:
        from src.processors.pptx_processor import PowerPointProcessor
        from src.analysis.multimodal_analyzer import MultimodalAnalyzer
        from src.script_generation.script_engine import ScriptEngine
        from src.export.markdown_generator import MarkdownGenerator
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic component initialization."""
    try:
        from src.processors.pptx_processor import PowerPointProcessor
        from src.script_generation.script_engine import ScriptEngine
        
        # Test processor initialization
        processor = PowerPointProcessor()
        assert processor is not None
        
        # Test script engine initialization
        engine = ScriptEngine()
        assert engine is not None
        
        print("✅ Basic functionality test passed")
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running Basic Tests...")
    
    success = True
    success &= test_imports()
    success &= test_basic_functionality()
    
    if success:
        print("✅ All basic tests passed!")
    else:
        print("❌ Some tests failed")
