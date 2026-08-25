import ast
from pathlib import Path


SOURCE_PATH = Path(__file__).resolve().parents[1] / "api" / "logs.py"
SOURCE_TEXT = SOURCE_PATH.read_text(encoding="utf-8")
MODULE = ast.parse(SOURCE_TEXT)
FUNC_NODE = next(
    node for node in MODULE.body if isinstance(node, ast.FunctionDef) and node.name == "_display_confidence"
)
FUNC_CODE = ast.get_source_segment(SOURCE_TEXT, FUNC_NODE)
NS = {}
exec(FUNC_CODE, NS)
_display_confidence = NS["_display_confidence"]


def test_display_confidence_handles_percentage_values():
    assert _display_confidence(78) == 78
    assert _display_confidence(0.78) == 78
    assert _display_confidence(None) == 0
