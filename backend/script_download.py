import requests
import os

base_url_demoContabeis = (
    "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/2025/"
)
base_url_cadop = (
    "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/"
)

year = "2025"
trimesters = ["1T", "2T", "3T"]


def download_files_fromDemoContabeis():
    for trimester in trimesters:
        file_name = f"{trimester}{year}.zip"
        url_download = f"{base_url_demoContabeis}/{file_name}"
        path_join = os.path.join("./assets", file_name)

        try:
            response = requests.get(url_download, stream=True, timeout=30)

            if response.status_code == 200:
                with open(path_join, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                print(f"Sucesso: {file_name} salvo em {path_join}")
            else:
                print(f"Não encontrado (Erro {response.status_code}): {file_name}")
        except Exception as err:
            print(f"Erro de conexão ao tentar baixar {file_name}: {err}")


def download_files_fromCadop():
    file_name = "Relatorio_cadop.csv"
    url_download = f"{base_url_cadop}{file_name}"
    path_join = os.path.join("./assets", file_name)

    try:
        response = requests.get(url_download, stream=True, timeout=30)

        if response.status_code == 200:
            with open(path_join, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Sucesso: {file_name} salvo em {path_join}")
        else:
            print(f"Não encontrado (Erro {response.status_code}): {file_name}")
    except Exception as err:
        print(f"Erro de conexão ao tentar baixar {file_name}: {err}")


def download_files():
    if not os.path.exists("./assets"):
        os.makedirs("./assets")
        print("Pasta de downloads criada")

    download_files_fromDemoContabeis()
    download_files_fromCadop()


if __name__ == "__main__":
    download_files()
