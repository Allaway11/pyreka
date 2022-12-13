import pytest

from pyreka import search_score


search_score_examples = [
    pytest.param(
        "Example text containing keywords",
        ["example", "text", "containing", "keywords"],
        1.0,
    ),
    pytest.param(
        "Example text containing keywords", ["exampl", "text", "contain", "key"], 1.0
    ),
    pytest.param("Example text containing keywords", ["no", "matches"], 0.0),
]


@pytest.mark.parametrize("text, keywords, expected", search_score_examples)
def test_search_score(text, keywords, expected):
    actual = search_score(text, keywords)
    assert expected == actual
