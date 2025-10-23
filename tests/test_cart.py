import json
import pytest
from unittest.mock import patch, mock_open, call
from src.cart import Cart, InvalidPriceError
import datetime


@patch.object(Cart, "get_total", return_value=5.5)
def test_add_and_total(mock_total):
    cart = Cart()
    cart.add_product = lambda name, price: None
    total = cart.get_total()
    assert total == 5.5
    mock_total.assert_called_once()


@patch.object(Cart, "remove_product")
def test_remove_product(mock_remove):
    cart = Cart()
    cart.remove_product("Livre")
    mock_remove.assert_called_once_with("Livre")


@patch.object(Cart, "apply_discount")
def test_apply_discount(mock_discount):
    cart = Cart()
    cart.apply_discount(10)
    mock_discount.assert_called_once_with(10)


def test_invalid_price_raises_exception():
    cart = Cart()
    with pytest.raises(InvalidPriceError):
        cart.add_product("Ordinateur", -100)


@patch("builtins.open", new_callable=mock_open)
@patch("os.makedirs")
def test_save_to_file_creates_json_with_timestamp(mock_makedirs, mock_file):
    cart = Cart()
    cart.products = [{"name": "Livre", "price": 10}]
    with patch("src.cart.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime.datetime(2025, 10, 23, 14, 50, 0)
        cart.save_to_file("test/panier.json")
    mock_file.assert_any_call("test/panier.json", "w", encoding="utf-8")
    handle = mock_file()
    written_data = "".join(
        args[0] for args, _ in handle.write.call_args_list if isinstance(args[0], str)
    )
    data = json.loads(written_data)
    assert data["products"][0]["name"] == "Livre"
    assert data["products"][0]["price"] == 10
    assert "timestamp" in data


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=json.dumps({"products": [{"name": "Livre", "price": 10}]}),
)
def test_load_from_file_reads_json_and_restores_total(mock_file):
    cart = Cart()
    cart.load_from_file("test/panier.json")
    mock_file.assert_called_once_with("test/panier.json", "r", encoding="utf-8")
    assert cart.products[0]["name"] == "Livre"
    assert cart.products[0]["price"] == 10


@patch("builtins.open", new_callable=mock_open)
@patch("os.makedirs")
@patch("src.cart.datetime")
def test_save_to_file_creates_archived_versions(
    mock_datetime, mock_makedirs, mock_file
):
    cart = Cart()
    cart.products = [{"name": "Livre", "price": 10}]

    mock_datetime.now.side_effect = [
        datetime.datetime(2025, 10, 23, 14, 50, 0),
        datetime.datetime(2025, 10, 23, 14, 51, 0),
    ]

    cart.save_to_file("test/panier.json")
    cart.save_to_file("test/panier.json")

    assert mock_file.call_count >= 2

    mock_makedirs.assert_called()
