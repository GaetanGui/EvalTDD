import json
from unittest.mock import mock_open, patch
import pytest
from src.cart import Cart, InvalidPriceError


def test_add_and_total():
    cart = Cart()
    cart.add_product("Café", 3.5)
    cart.add_product("Croissant", 2.0)
    assert cart.get_total() == 5.5


def test_remove_product():
    cart = Cart()
    cart.add_product("Livre", 10)
    cart.add_product("Stylo", 2)
    cart.remove_product("Livre")
    assert cart.get_total() == 2


def test_apply_discount():
    cart = Cart()
    cart.add_product("Livre", 20)
    cart.apply_discount(10)
    assert cart.get_total() == 18.0


def test_invalid_price():
    cart = Cart()
    with pytest.raises(InvalidPriceError):
        cart.add_product("Ordinateur", -100)


@patch("builtins.open", new_callable=mock_open)
@patch("os.makedirs")
def test_save_to_file(mock_makedirs, mock_file):
    cart = Cart()
    cart.add_product("Livre", 10)
    cart.save_to_file("test/panier.json")
    mock_file.assert_called_once_with("test/panier.json", "w", encoding="utf-8")

    handle = mock_file()
    written_data = "".join(call.args[0] for call in handle.write.call_args_list)
    data = json.loads(written_data)

    assert data["products"][0]["name"] == "Livre"
    assert data["products"][0]["price"] == 10
    assert "timestamp" in data


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=json.dumps({"products": [{"name": "Livre", "price": 10}]}),
)
def test_load_from_file(mock_file):
    cart = Cart()
    cart.load_from_file("test/panier.json")
    assert cart.get_total() == 10
