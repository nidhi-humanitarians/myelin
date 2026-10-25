import pytest
from .function import execute

def test_extract_single_pnr():
    assert execute("My reservation code is JG7FMM.") == "JG7FMM"
    assert execute("Check flight under 2FBBAH please.") == "2FBBAH"

def test_abstain_on_multiple_pnrs():
    assert execute("Please change reservation JG7FMM or LQ940Q.") == "unsure"

def test_abstain_on_pure_words_or_numbers():
    assert execute("Flight number 123456.") == "unsure"
    assert execute("I am flying to BOSTON.") == "unsure"
