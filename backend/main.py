from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, desc, or_
from etapa3_integratingDB import Session, Operadora, Despesa
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

origins = [
    FRONTEND_URL,
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/operadoras")
def operators(page: int = 1, limit: int = 10, query_search: str = None):
    session = Session()

    try:
        operators = session.query(Operadora)

        if query_search and query_search.strip():
            operators = operators.where(
                or_(
                    Operadora.cnpj.ilike(f"%{query_search}%"),
                    Operadora.razao_social.ilike(f"%{query_search}%"),
                )
            )

        total_operators = operators.count()
        total_pages = (
            (total_operators + limit - 1) // limit if total_operators > 0 else 1
        )
        offset = (page - 1) * limit
        operators = operators.offset(offset).limit(limit).all()

        return {
            "operators": operators,
            "total": total_operators,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
        }
    except Exception as err:
        print(f"Erro: {err}")
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        session.close()


@app.get("/api/operadoras/{cnpj}")
def operator(cnpj: str):
    session = Session()

    try:
        operatorX = session.query(Operadora).where(Operadora.cnpj == cnpj).all()
        if operatorX == []:
            raise HTTPException(status_code=404, detail="Operadora não encontrada")
        return operatorX
    except HTTPException as http_err:
        print(f"Erro: {http_err}")
        raise http_err
    except Exception as err:
        print(f"Erro: {err}")
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        session.close()


@app.get("/api/operadoras/{cnpj}/despesas")
def operator_expenses(cnpj: str):
    session = Session()

    try:
        operatorX_expenses = (
            session.query(Despesa)
            .join(Operadora)
            .where(Operadora.cnpj == cnpj)
            .order_by(Despesa.ano, Despesa.trimestre)
            .all()
        )
        return operatorX_expenses
    except Exception as err:
        print(f"Erro: {err}")
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        session.close()


@app.get("/api/operadoras/{cnpj}/despesas/chart")
def operator_expenses_chart(cnpj: str):
    session = Session()

    try:
        expensesTrimester = (
            session.query(
                Despesa.ano,
                Despesa.trimestre,
                func.sum(Despesa.valor_despesas).label("total_despesas_trimestre"),
            )
            .join(Operadora)
            .where(Operadora.cnpj == cnpj)
            .group_by(Despesa.ano, Despesa.trimestre)
            .order_by(Despesa.ano, Despesa.trimestre)
            .all()
        )

        return {
            "chart": [
                {
                    "ano": row.ano,
                    "trimestre": row.trimestre,
                    "total": row.total_despesas_trimestre,
                }
                for row in expensesTrimester
            ],
        }
    except Exception as err:
        print(f"Erro: {err}")
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        session.close()


@app.get("/api/estatisticas")
def statistcs():
    session = Session()

    try:
        statistcsTotal, statistcsAvg = session.query(
            func.sum(Despesa.valor_despesas), func.avg(Despesa.valor_despesas)
        ).first()

        statistcsTop5Res = (
            session.query(
                Operadora.razao_social,
                func.sum(Despesa.valor_despesas).label("total_despesas"),
            )
            .join(Despesa)
            .group_by(Operadora.razao_social)
            .order_by(desc("total_despesas"))
            .limit(5)
            .all()
        )

        statistcsUF = (
            session.query(
                Operadora.uf,
                func.sum(Despesa.valor_despesas).label("total_despesas2"),
            )
            .join(Despesa)
            .group_by(Operadora.uf)
            .all()
        )
        return {
            "total_geral": statistcsTotal or 0,
            "media_geral": statistcsAvg or 0,
            "top_5_operadoras": [
                {"razao_social": row.razao_social, "total": row.total_despesas}
                for row in statistcsTop5Res
            ],
            "distribuicao_uf": [
                {"uf": row.uf, "despesas": row.total_despesas2} for row in statistcsUF
            ],
        }
    except Exception as err:
        print(f"Erro: {err}")
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        session.close()
