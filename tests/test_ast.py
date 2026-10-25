from myelin.synthesis.ast_validator import ASTValidator

def test_ast_validator_safe_code():
    safe_code = '''
def execute(text: str):
    import re
    return "ok"
'''
    valid, errors, nodes = ASTValidator.validate(safe_code)
    assert valid is True
    assert len(errors) == 0
    assert nodes > 0

def test_ast_validator_banned_modules():
    malicious = '''
def execute(text: str):
    import subprocess
    return "bad"
'''
    valid, errors, nodes = ASTValidator.validate(malicious)
    assert valid is False
    assert any("banned" in err.lower() for err in errors)
