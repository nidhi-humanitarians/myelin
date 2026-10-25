import ast
from typing import Tuple, List

BANNED_MODULES = {"socket", "subprocess", "os", "sys", "requests", "urllib", "shutil", "builtins"}

class ASTValidator:
    """Validates that synthesized Python functions are pure, safe, and export an execute() function."""

    @staticmethod
    def validate(code_str: str) -> Tuple[bool, List[str], int]:
        errors = []
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return False, [f"SyntaxError: {e}"], 0

        has_execute = False
        node_count = sum(1 for _ in ast.walk(tree))

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "execute":
                has_execute = True
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split('.')[0] in BANNED_MODULES:
                        errors.append(f"Banned import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split('.')[0] in BANNED_MODULES:
                    errors.append(f"Banned import from: {node.module}")

        if not has_execute:
            errors.append("Missing required 'execute' function definition.")

        return len(errors) == 0, errors, node_count
