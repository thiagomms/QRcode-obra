from flask import Flask, render_template, Response, request
import qrcode, io, base64
import pyodbc
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

app = Flask(__name__)

# Valores padrão "test" — substitua via .env em ambiente real
SERVER   = os.getenv("DB_SERVER", "test")
DATABASE = os.getenv("DB_NAME", "test")
DB_USER  = os.getenv("DB_USER", "test")
DB_PASS  = os.getenv("DB_PASS", "test")
DB_VIEW  = os.getenv("DB_VIEW", "VW_QRCODE_OBRA")

COLS = (
    "CODCOLIGADA,CHAPA,NOME,CPF,CODPESSOA,DATAADMISSAO,DATADEMISSAO,"
    "CODSITUACAO,CODFUNCAO,CODSECAO,RUA,TELEFONE1,TELEFONE2,EMAIL,"
    "GRAUINSTRUCAO,CODHORARIO"
)


def get_conn():
    """Abre conexão somente leitura com o SQL Server usando credenciais do .env."""
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};"
        f"UID={DB_USER};PWD={DB_PASS};"
        f"TrustServerCertificate=yes;ApplicationIntent=ReadOnly;"
    )


def consultar_funcionario(coligada, chapa):
    """Busca dados do colaborador na view configurada por coligada e chapa."""
    conn = get_conn()
    sql = f"SELECT {COLS} FROM dbo.{DB_VIEW} WHERE CHAPA = ? AND CODCOLIGADA = ?"
    df = pd.read_sql(sql, conn, params=[chapa, coligada])
    conn.close()
    if df.empty:
        return None
    return df.iloc[0].to_dict()


@app.route("/")
def home():
    """Página inicial com instrução de uso da rota de consulta."""
    return "<h2>QR Code Obra</h2><p>Use: /funcionario/COLIGADA/CHAPA</p>"


@app.route("/funcionario/<coligada>/<chapa>")
def funcionario(coligada, chapa):
    """Exibe ficha do colaborador escaneado via QR Code."""
    dados = consultar_funcionario(coligada, chapa)
    if not dados:
        return render_template("nao_encontrado.html"), 404
    return render_template("funcionario.html", funcionario=dados, coligada=coligada)


@app.route("/foto/<coligada>/<chapa>")
def foto(coligada, chapa):
    """Retorna a foto do colaborador armazenada no banco."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT IMAGEM FROM dbo.{DB_VIEW} WHERE CHAPA = ? AND CODCOLIGADA = ?",
        chapa, coligada
    )
    row = cursor.fetchone()
    conn.close()
    if not row or not row[0]:
        return '', 404
    return Response(bytes(row[0]), mimetype='image/jpeg')


@app.route("/gerar", methods=["GET", "POST"])
def gerar():
    """Gera QR Code para colar no capacete ou crachá do colaborador."""
    qr_base64 = None
    url_funcionario = None
    coligada = None
    chapa = None
    erro = None

    if request.method == "POST":
        coligada = request.form.get("coligada", "").strip()
        chapa = request.form.get("chapa", "").strip()

        dados = consultar_funcionario(coligada, chapa)
        if not dados:
            erro = f"Funcionário com chapa {chapa} não encontrado na coligada {coligada}."
        else:
            host = request.host
            url_funcionario = f"http://{host}/funcionario/{coligada}/{chapa}"
            buf = io.BytesIO()
            qrcode.make(url_funcionario).save(buf, format="PNG")
            qr_base64 = base64.b64encode(buf.getvalue()).decode()

    return render_template(
        "gerar.html",
        qr_base64=qr_base64,
        url_funcionario=url_funcionario,
        coligada=coligada,
        chapa=chapa,
        erro=erro,
    )


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug)
