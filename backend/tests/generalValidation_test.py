import pytest
from etapa2_validatingData import cnpj_validation, general_validation
import pandas as pd


def test_cnpj_validation():
    cnpj_real = "00366982000130"
    assert cnpj_validation(cnpj_real) is True


def test_cnpj_invalid_size():
    assert cnpj_validation("123") is False


def test_cnpj_equal_digits():
    assert cnpj_validation("11111111111111") is False


def test_cnpj_invalid_logic():
    assert cnpj_validation("87827689000104") is False


def test_general_validation_success():
    row = {
        "RegistroANS": "344800",
        "CNPJ": "00366982000130",
        "RazaoSocial": "ADM LIFE - ADMINISTRADORA DE BENEFÍCIOS LTDA.",
        "ValorDespesas": "230068808.69",
        "Trimestre": "3",
    }
    assert general_validation(row) == "Válido"


def test_general_validation_invalid_cnpj():
    row = {
        "RegistroANS": "344800",
        "CNPJ": "11111111111111",
        "RazaoSocial": "ADM LIFE - ADMINISTRADORA DE BENEFÍCIOS LTDA.",
        "ValorDespesas": "230068808.69",
        "Trimestre": "3",
    }
    resultado = general_validation(row)
    assert "CNPJ Inválido" in resultado


def test_general_validation_valor_negativo():
    row = {
        "RegistroANS": "344800",
        "CNPJ": "00366982000130",
        "RazaoSocial": "ADM LIFE - ADMINISTRADORA DE BENEFÍCIOS LTDA.",
        "ValorDespesas": "-230068808.69",
        "Trimestre": "3",
    }
    resultado = general_validation(row)
    assert "Valor Negativo" in resultado


def test_general_validation_blank_razaoSocial():
    row = {
        "RegistroANS": "344800",
        "CNPJ": "00366982000130",
        "RazaoSocial": "",
        "ValorDespesas": "230068808.69",
        "Trimestre": "3",
    }
    resultado = general_validation(row)
    assert "Razão Social Vazia" in resultado


def test_general_validation_errors():
    row = {
        "RegistroANS": "344800",
        "CNPJ": "11111111111111",
        "RazaoSocial": "",
        "ValorDespesas": "-230068808.69",
        "Trimestre": "3",
    }
    resultado = general_validation(row)
    assert "CNPJ Inválido" in resultado
    assert "Razão Social Vazia" in resultado
    assert "Valor Negativo" in resultado
