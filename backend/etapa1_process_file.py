import pandas as pd
import glob
import zipfile
import os


def unzipFile():
    print("Descompactando arquivo")

    if not os.path.exists("./files"):
        os.makedirs("./files")

    zips_file = glob.glob("*.zip") + glob.glob("./assets/*.zip")

    if not zips_file:
        print(
            "Nenhum arquivo ZIP encontrado para extrair. Verificando se já existem CSVs"
        )
        return

    for zip_file in zips_file:
        print(f"Descompactando: {zip_file}")
        try:
            with zipfile.ZipFile(zip_file, "r") as zip_ref:
                zip_ref.extractall("./files")
                print(f"Sucesso: {zip_file} extraído.")
        except zipfile.BadZipFile:
            print(f"Erro: O arquivo {zip_file} parece estar corrompido.")


def zipFile():
    print("Compactando arquivo")
    try:
        with zipfile.ZipFile(
            "./files/consolidado_despesas.zip", "w", zipfile.ZIP_DEFLATED
        ) as zipf:
            zipf.write(
                "./files/consolidado_despesas.csv", arcname="consolidado_despesas.csv"
            )
        print("Sucesso! Arquivo 'consolidado_despesas.zip' criado.")
    except Exception as err:
        print(f"Erro ao criar ZIP final: {err}")


def read_files():
    unzipFile()
    dados_consolidados = []

    files = glob.glob("**/*.csv", recursive=True)

    generated_files = [
        "consolidado_despesas.csv",
        "despesas_agregadas.csv",
        "relatorio_final.csv",
    ]
    input_files = [
        file for file in files if os.path.basename(file) not in generated_files
    ]

    input_files = list(set(input_files))

    for file in input_files:
        try:
            df = pd.read_csv(
                file, sep=";", encoding="utf-8", thousands=".", decimal=","
            )
        except:
            df = pd.read_csv(
                file, sep=";", encoding="latin1", thousands=".", decimal=","
            )

        if "DESCRICAO" not in df.columns:
            continue

        filter_term = df["DESCRICAO"].str.contains(
            "EVENTOS|SINISTROS", case=False, na=False
        )
        df_filtered = df[filter_term].copy()

        if df_filtered.empty:
            continue

        df_filtered["DATA"] = pd.to_datetime(df_filtered["DATA"], errors="coerce")
        df_filtered["Ano"] = df_filtered["DATA"].dt.year
        df_filtered["Trimestre"] = df_filtered["DATA"].dt.quarter
        df_filtered["ValorDespesas"] = pd.to_numeric(
            df_filtered["VL_SALDO_FINAL"], errors="coerce"
        )

        df_filtered.rename(columns={"REG_ANS": "RegistroANS"}, inplace=True)
        df_filtered["CNPJ"] = ""
        df_filtered["RazaoSocial"] = ""

        finalColumns = [
            "RegistroANS",
            "CNPJ",
            "RazaoSocial",
            "Trimestre",
            "Ano",
            "ValorDespesas",
            "DESCRICAO",
        ]
        dados_consolidados.append(df_filtered[finalColumns])

    if dados_consolidados:
        df_final = pd.concat(dados_consolidados, ignore_index=True)

        df_final.to_csv(
            "./files/consolidado_despesas.csv",
            index=False,
            sep=";",
            decimal=",",
            encoding="utf-8-sig",
        )
        print("Arquivo 'consolidado_despesas.csv' gerado com sucesso!")

        zipFile()
    else:
        print("Nenhum dado de sinistro encontrado.")


if __name__ == "__main__":
    read_files()
