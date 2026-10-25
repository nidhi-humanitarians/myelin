import pytest
from compiled_habits.extract_user_id.function import execute as exec_user
from compiled_habits.extract_reservation_id.function import execute as exec_res

def test_user_id_extraction():
    assert exec_user("My user id is omar_davis_3817.") == "omar_davis_3817"
    assert exec_user("Ambiguous text with no id") == "unsure"
    assert exec_user("I am omar_davis_3817 and friend alex_smith_9921") == "unsure"

def test_reservation_id_extraction():
    assert exec_res("My booking is JG7FMM.") == "JG7FMM"
    assert exec_res("No booking number here.") == "unsure"
    assert exec_res("Change JG7FMM or LQ940Q please.") == "unsure"
