from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    text,
    Date,
    ForeignKey,
    Numeric,
)
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd
import glob
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
db = create_engine(DATABASE_URL)
Session = sessionmaker(bind=db)
session = Session()
Base = declarative_base()


class Operadora(Base):
    __tablename__ = "operadoras"

    registro_ans = Column(String(6), primary_key=True)
    cnpj = Column(String(14), nullable=False)
    razao_social = Column(String, nullable=False)
    nome_fantasia = Column(String)
    modalidade = Column(String)
    uf = Column(String(2))
    cidade = Column(String)
    data_registro_ans = Column(Date)


class Despesa(Base):
    __tablename__ = "despesas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    registro_ans = Column(
        String(6), ForeignKey("operadoras.registro_ans"), nullable=False
    )
    trimestre = Column(Integer, nullable=False)
    ano = Column(Integer, nullable=False)
    valor_despesas = Column(Numeric(30, 2), nullable=False)
    descricao = Column(String)


class Agregado(Base):
    __tablename__ = "agregados"

    id = Column(Integer, primary_key=True, autoincrement=True)
    razao_social = Column(String, nullable=False)
    uf = Column(String(2))
    valorTotal_despesas = Column(Numeric(30, 2), nullable=False)
    media_trimestre = Column(Numeric(30, 2))
    desvio_padrao = Column(Numeric(30, 2))


def add_to_db(df_expenses, df_aggregated, df_cadop):
    try:
        df_cadop.to_sql("operadoras", db, if_exists="append", index=False)
        df_expenses.to_sql("despesas", db, if_exists="append", index=False)
        df_aggregated.to_sql("agregados", db, if_exists="append", index=False)
        print("Sucesso! Banco populado.")
    except Exception as err:
        print(f"Erro ao inserir no banco: {err}")
        return


def read_files():
    file_expenses = glob.glob("./files/consolidado_despesas.csv")
    file_aggregated = glob.glob("./files/despesas_agregadas.csv")
    file_cadop = glob.glob("./assets/Relatorio_cadop*.csv")

    if not file_expenses or not file_aggregated or not file_cadop:
        print("Alguns arquivos não foram encontrados.")
        return

    cols_expenses = ["RegistroANS", "Trimestre", "Ano", "ValorDespesas", "DESCRICAO"]
    cols_cadop = [
        "REGISTRO_OPERADORA",
        "CNPJ",
        "Razao_Social",
        "Nome_Fantasia",
        "Modalidade",
        "UF",
        "Cidade",
        "Data_Registro_ANS",
    ]

    try:
        df_expenses = pd.read_csv(
            file_expenses[0],
            sep=";",
            encoding="utf-8",
            decimal=",",
            usecols=cols_expenses,
            dtype={"RegistroANS": str},
            on_bad_lines="skip",
        )
        df_aggregated = pd.read_csv(
            file_aggregated[0],
            sep=";",
            encoding="utf-8",
            decimal=",",
            on_bad_lines="skip",
        )
        df_cadop = pd.read_csv(
            file_cadop[0],
            sep=";",
            encoding="utf-8",
            usecols=cols_cadop,
            dtype=str,
            on_bad_lines="skip",
        )
    except:
        df_expenses = pd.read_csv(
            file_expenses[0],
            sep=";",
            encoding="latin1",
            decimal=",",
            usecols=cols_expenses,
            dtype={"RegistroANS": str},
            on_bad_lines="skip",
        )
        df_aggregated = pd.read_csv(
            file_aggregated[0],
            sep=";",
            encoding="latin1",
            decimal=",",
            on_bad_lines="skip",
        )
        df_cadop = pd.read_csv(
            file_cadop[0],
            sep=";",
            encoding="latin1",
            usecols=cols_cadop,
            dtype=str,
            on_bad_lines="skip",
        )

    columns_expenses_toRename = {
        "RegistroANS": "registro_ans",
        "Trimestre": "trimestre",
        "Ano": "ano",
        "ValorDespesas": "valor_despesas",
        "DESCRICAO": "descricao",
    }
    columns_aggregated_toRename = {
        "RazaoSocial": "razao_social",
        "UF": "uf",
        "TotalExpensives": "valorTotal_despesas",
        "TrimestralMean": "media_trimestre",
        "Deviation": "desvio_padrao",
    }
    columns_cadop_toRename = {
        "REGISTRO_OPERADORA": "registro_ans",
        "Razao_Social": "razao_social",
        "Nome_Fantasia": "nome_fantasia",
        "Modalidade": "modalidade",
        "UF": "uf",
        "Cidade": "cidade",
        "Data_Registro_ANS": "data_registro_ans",
        "CNPJ": "cnpj",
    }

    df_expenses.rename(columns=columns_expenses_toRename, inplace=True)
    df_aggregated.rename(columns=columns_aggregated_toRename, inplace=True)
    df_cadop.rename(columns=columns_cadop_toRename, inplace=True)
    df_cadop["data_registro_ans"] = pd.to_datetime(
        df_cadop["data_registro_ans"], errors="coerce"
    )
    df_cadop.dropna(subset=["registro_ans", "cnpj", "razao_social"], inplace=True)
    df_cadop.drop_duplicates(subset=["registro_ans"], inplace=True)

    operadoras_validas = set(df_cadop["registro_ans"])
    df_expenses = df_expenses[df_expenses["registro_ans"].isin(operadoras_validas)]

    add_to_db(df_expenses, df_aggregated, df_cadop)


def query1():
    querySQL = text(
        """
    WITH despesas_t1 AS (
        SELECT registro_ans, SUM(valor_despesas) as total_inicial
        FROM despesas 
        WHERE trimestre = 1
        GROUP BY registro_ans
        HAVING SUM(valor_despesas) > 0
    ),
    despesas_t3 AS (
        SELECT registro_ans, SUM(valor_despesas) as total_final
        FROM despesas 
        WHERE trimestre = 3
        GROUP BY registro_ans
    )
    
    SELECT 
        op.razao_social,
        t1.total_inicial,
        t3.total_final,
        ROUND(((t3.total_final - t1.total_inicial) / t1.total_inicial) * 100, 2) as crescimento_percentual
    FROM despesas_t1 t1
    JOIN despesas_t3 t3 ON t1.registro_ans = t3.registro_ans 
    JOIN operadoras op ON t1.registro_ans = op.registro_ans  
    ORDER BY crescimento_percentual DESC
    LIMIT 5;
    """
    )

    with db.connect() as connection:
        maxExpenses = pd.read_sql_query(querySQL, connection)

    print(
        "\nTop 5 Operadoras com Maior Crescimento de Despesas entre o primeiro e ultimo trimestre: "
    )
    print(maxExpenses.to_string(index=False))


def query2():
    querySQL = text(
        """
    SELECT 
        op.uf,
        SUM(despesas.valor_despesas) as despesa_total,
        COUNT(DISTINCT op.registro_ans) as qtd_operadoras,
        (SUM(despesas.valor_despesas) / COUNT(DISTINCT op.registro_ans)) as media_por_operadora
    FROM despesas
    JOIN operadoras op ON despesas.registro_ans = op.registro_ans
    GROUP BY op.uf
    ORDER BY despesa_total DESC
    LIMIT 5;
    """
    )

    with db.connect() as connection:
        avg_sum = pd.read_sql_query(querySQL, connection)

    print("\nTop 5 Estados (UF) com Maiores Despesas: ")
    print(avg_sum.to_string(index=False))


def query3():
    querySQL = text(
        """
    WITH media AS (
        SELECT AVG(valor_despesas) as valor_media FROM despesas
    ),
    despesas_acima_media AS (
        SELECT registro_ans, trimestre
        FROM despesas, media
        WHERE despesas.valor_despesas > media.valor_media
    ),
    operadoras_relacionadas AS (
        SELECT registro_ans
        FROM despesas_acima_media
        GROUP BY registro_ans
        HAVING COUNT(trimestre) >= 2 
    )

    SELECT COUNT(*) FROM operadoras_relacionadas;
    """
    )

    with db.connect() as connection:
        count_opAboveAvg = pd.read_sql_query(querySQL, connection)

    print("\nOperadoras com Despesas Acima da Média em pelo menos dois trimestres: ")
    print(count_opAboveAvg.to_string(index=False))


def analitics_queriesSQL():
    try:
        query1()
        query2()
        query3()
    except Exception as err:
        print(f"Erro ao rodar as queries: {err}")
        return


if __name__ == "__main__":
    Base.metadata.drop_all(bind=db)
    Base.metadata.create_all(bind=db)
    read_files()
    analitics_queriesSQL()
