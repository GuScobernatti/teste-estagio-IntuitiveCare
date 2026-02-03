import pandas as pd
import glob
import re
import zipfile


def zipFile():
    print("Compactando arquivo")

    try:
        with zipfile.ZipFile(
            "./files/Teste_Gustavo_Luiz.zip", "w", zipfile.ZIP_DEFLATED
        ) as zipf:
            zipf.write(
                "./files/despesas_agregadas.csv", arcname="despesas_agregadas.csv"
            )
        print("Sucesso! Arquivo 'despesas_agregadas.zip' criado.")
    except Exception as err:
        print(f"Erro ao criar ZIP final: {err}")


def cnpj_validation(cnpj):
    cnpj = re.sub(r"\D", "", str(cnpj))

    cnpj = cnpj.zfill(14)
    if len(cnpj) != 14 or len(set(cnpj)) == 1:
        return False

    firstDigit = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum1 = sum(int(a) * b for a, b in zip(cnpj[:12], firstDigit))
    digit1 = 11 - (sum1 % 11)
    if digit1 >= 10:
        digit1 = 0

    secondDigit = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum2 = sum(int(a) * b for a, b in zip(cnpj[:13], secondDigit))
    digit2 = 11 - (sum2 % 11)
    if digit2 >= 10:
        digit2 = 0

    return cnpj[-2:] == f"{digit1}{digit2}"


def general_validation(row):
    errors = []

    if pd.isna(row["CNPJ"]) or row["CNPJ"] == "":
        errors.append("CNPJ Ausente")
    elif not cnpj_validation(row["CNPJ"]):
        errors.append("CNPJ Inválido")

    if pd.isna(row["RazaoSocial"]) or str(row["RazaoSocial"]).strip() == "":
        errors.append("Razão Social Vazia")

    floatValueExpenses = float(row["ValorDespesas"])
    if floatValueExpenses < 0:
        errors.append("Valor Negativo")

    if not errors:
        return "Válido"
    else:
        return "Inválido: " + ", ".join(errors)


def enrichmentData():
    try:
        df_expenses = pd.read_csv(
            "./files/consolidado_despesas.csv",
            sep=";",
            decimal=",",
            encoding="utf-8-sig",
            dtype={"RegistroANS": str},
        )
    except:
        print("Erro: arquivo 'consolidado_despesas.csv' não encontrado.")
        return

    files_cadop = glob.glob("*Relatorio_cadop*.csv") + glob.glob(
        "./assets/*Relatorio_cadop.csv"
    )
    if not files_cadop:
        print("Relatorio de dados cadastrais das operadoras ativas não encontrado!")
        return

    try:
        df_cadop = pd.read_csv(
            files_cadop[0],
            sep=";",
            encoding="utf-8",
            dtype={"REGISTRO_OPERADORA": str, "CNPJ": str},
            on_bad_lines="skip",
        )
    except:
        df_cadop = pd.read_csv(
            files_cadop[0],
            sep=";",
            encoding="latin1",
            dtype={"REGISTRO_OPERADORA": str, "CNPJ": str},
            on_bad_lines="skip",
        )

    columns_cadop_toRename = {
        "REGISTRO_OPERADORA": "RegistroANS",
        "Razao_Social": "RazaoSocial",
    }
    df_cadop.rename(columns=columns_cadop_toRename, inplace=True)

    columns_cadop_selected = ["RegistroANS", "RazaoSocial", "CNPJ", "Modalidade", "UF"]

    isColumnExisting = [
        column for column in columns_cadop_selected if column in df_cadop.columns
    ]
    copyColumn = (
        df_cadop[isColumnExisting].copy().drop_duplicates(subset=["RegistroANS"])
    )

    df_expenses = df_expenses.drop(columns=["CNPJ", "RazaoSocial"], errors="ignore")
    df_merged = pd.merge(df_expenses, copyColumn, on="RegistroANS", how="left")

    mismatches = df_merged["CNPJ"].isna().sum()
    total = len(df_merged)
    print(f"\nRelatório de Consistência")
    print(f"Total de Despesas Processadas: {total}")
    print(f"Operadoras encontradas no cadastro: {total - mismatches}")
    print(f"Operadoras NÃO encontradas no cadastro: {mismatches}")

    df_merged["ValorDespesas"] = pd.to_numeric(
        df_merged["ValorDespesas"], errors="coerce"
    ).fillna(0)
    df_merged["Status_Validacao"] = df_merged.apply(general_validation, axis=1)

    print("\nResumo da Validação:")
    print(df_merged["Status_Validacao"].value_counts())

    df_merged.to_csv(
        "./files/relatorio_final.csv",
        index=False,
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
    )
    print("Arquivo 'relatorio_final.csv' gerado com sucesso.")

    df_clean = df_merged[df_merged["Status_Validacao"] == "Válido"].copy()

    df_aggregated_sum = (
        df_clean.groupby(["RazaoSocial", "UF", "Trimestre"])["ValorDespesas"]
        .sum()
        .reset_index()
    )
    df_calculations = (
        df_aggregated_sum.groupby(["RazaoSocial", "UF"])["ValorDespesas"]
        .agg(TotalExpensives="sum", TrimestralMean="mean", Deviation="std")
        .reset_index()
    )

    df_calculations = df_calculations.sort_values(by="TotalExpensives", ascending=False)
    df_calculations["Deviation"] = df_calculations["Deviation"].fillna(0)
    df_calculations["TrimestralMean"] = df_calculations["TrimestralMean"].round(2)
    df_calculations["Deviation"] = df_calculations["Deviation"].round(2)

    df_calculations.to_csv(
        "./files/despesas_agregadas.csv",
        index=False,
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
    )
    print("Arquivo 'despesas_agregadas.csv' gerado com sucesso!")

    zipFile()


if __name__ == "__main__":
    enrichmentData()
