# QR Code Obra

Sistema web para **consulta rápida de colaboradores em canteiros de obras** via QR Code fixado no capacete, crachá ou EPI.

Desenvolvido para apoiar o **técnico de campo** e o **técnico em Segurança do Trabalho** na verificação, no local, se pedreiros, serventes e demais profissionais possuem os documentos e treinamentos necessários para atuar na obra.

Ao escanear o QR Code com o celular, sem instalar aplicativo, o responsável visualiza:

- Foto e identificação do colaborador
- Dados cadastrais (chapa, CPF, função, seção, admissão)
- Contato e endereço
- Status de treinamentos obrigatórios (NR18, NR35, integração, etc.)
- Situação do ASO (Atestado de Saúde Ocupacional)

---

## Para quem é

| Perfil | Uso |
|--------|-----|
| Técnico de Segurança do Trabalho | Conferir documentação e aptidão antes/durante o trabalho na obra |
| Técnico de campo / Encarregado | Validar equipe presente no canteiro |
| RH / SESMT | Gerar e imprimir QR Codes para capacetes e crachás |

---

## Como funciona

1. Cada colaborador recebe um **QR Code único** vinculado à sua chapa e coligada.
2. O código é colado no **capacete**, crachá ou outro local visível.
3. No canteiro, basta **escanear com a câmera do celular**.
4. O navegador abre a ficha do colaborador com dados vindos do ERP (RM/TOTVS).

```
Capacete com QR → Celular escaneia → Página web com ficha do colaborador
```

---

## Tecnologias

- Python 3.11+
- Flask
- PyODBC + Pandas
- Bootstrap 5
- SQL Server (integração RM/TOTVS)

---

## Estrutura do projeto

```
QRcode-obra/
├── app.py
├── requirements.txt
├── .env.example          # modelo de configuração (sem dados reais)
├── .env                  # credenciais locais (não versionar)
└── templates/
    ├── funcionario.html  # ficha exibida após o scan
    ├── gerar.html        # geração e impressão de QR Codes
    └── nao_encontrado.html
```

---

## Configuração

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Criar o arquivo `.env`

Copie o exemplo e ajuste para o seu ambiente:

```bash
cp .env.example .env
```

```env
DB_SERVER=test
DB_NAME=test
DB_USER=test
DB_PASS=test
DB_VIEW=VW_QRCODE_OBRA
FLASK_DEBUG=false
```

> **Importante:** nunca commite o arquivo `.env` com credenciais reais.

### 3. Criar a view no SQL Server

Exemplo de view somente leitura (adapte tabelas e colunas ao seu RM):

```sql
USE seu_banco;
GO

CREATE VIEW VW_QRCODE_OBRA AS
SELECT
    F.CODCOLIGADA,
    F.CHAPA,
    P.NOME,
    P.CPF,
    F.CODPESSOA,
    F.DATAADMISSAO,
    F.DATADEMISSAO,
    F.CODSITUACAO,
    F.CODFUNCAO,
    F.CODSECAO,
    P.RUA,
    P.TELEFONE1,
    P.TELEFONE2,
    P.EMAIL,
    P.GRAUINSTRUCAO,
    F.CODHORARIO,
    G.IMAGEM
FROM PFUNC F
INNER JOIN PPESSOA P ON P.CODIGO = F.CODPESSOA
LEFT JOIN GIMAGEM G ON G.ID = P.IDIMAGEM
WHERE F.CODSITUACAO <> 'D';
```

Use um usuário SQL com permissão **somente leitura** (`db_datareader`).

---

## Execução

```bash
python app.py
```

Acesse no navegador:

| Rota | Descrição |
|------|-----------|
| `/` | Página inicial |
| `/funcionario/<coligada>/<chapa>` | Ficha do colaborador (destino do QR Code) |
| `/foto/<coligada>/<chapa>` | Foto do colaborador |
| `/gerar` | Formulário para gerar e imprimir QR Codes |

Exemplo de URL do QR Code:

```
http://seu-servidor:5000/funcionario/1/000123
```

---

## Geração de QR Code (programático)

```python
import qrcode

url = "http://seu-servidor:5000/funcionario/1/000123"
img = qrcode.make(url)
img.save("qrcode_000123.png")
```

Ou use a rota `/gerar` pela interface web.

---

## Segurança

- Credenciais apenas no `.env` (listado no `.gitignore`)
- Conexão SQL em modo **ReadOnly**
- Nenhuma operação de escrita no banco pela aplicação
- Não exponha dados sensíveis em repositórios públicos
- Em produção, use HTTPS e desative `FLASK_DEBUG`

---

## Repositório

[github.com/thiagomms/QRcode-obra](https://github.com/thiagomms/QRcode-obra)

---

## Licença

Uso interno / projeto pessoal. Adapte conforme a necessidade da sua obra ou empresa.
