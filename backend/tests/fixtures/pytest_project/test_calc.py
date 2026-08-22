from calc import add, divide


def test_add_sums_two_numbers():
    assert add(2, 3) == 5


def test_divide_returns_quotient():
    assert divide(10, 2) == 5


def test_add_is_intentionally_asserted_wrong():
    # Intentionally wrong expectation — proves the fixture produces a real
    # failing result, not an all-green demo.
    assert add(2, 2) == 5
