import pytest
from .function import execute

def test_extract_single_user_id():
    assert execute("Well, my user ID is omar_davis_3817, can you look that up?") == "omar_davis_3817"
    assert execute("Sure, it's sofia_kim_7287.") == "sofia_kim_7287"
    assert execute("I don't remember the reservation ID, but I'm omar_rossi_1241.") == "omar_rossi_1241"

def test_extract_case_insensitivity():
    assert execute("My ID is OMAR_DAVIS_3817.") == "omar_davis_3817"

def test_abstain_on_multiple_competing_ids():
    assert execute("I am omar_davis_3817 but checking for friend alex_smith_9921.") == "unsure"

def test_abstain_on_missing_or_invalid():
    assert execute("I don't have my user ID on me.") == "unsure"
    assert execute("") == "unsure"
    assert execute("My name is John Doe.") == "unsure"
