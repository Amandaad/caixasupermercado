# Super AS — MVP 0.1.0

Sistema inicial de gestão para supermercado com 1 caixa, React + TypeScript, FastAPI e PostgreSQL.

## O que está implementado

- Docker Compose com PostgreSQL 16, API FastAPI e interface React.
- Inicialização do administrador a partir de variáveis de ambiente.
- Login com senha armazenada usando Argon2 e token JWT com expiração.
- Cadastro, consulta e pesquisa de produtos.
- Validação de código de barras duplicado.
- Valores monetários como `NUMERIC` no PostgreSQL.
- Testes automatizados básicos da API.
- Painel web inicial para cadastrar e pesquisar produtos.

## Ainda não está implementado

O MVP **não está pronto para operar vendas reais**. Ainda faltam PDV, transações de venda/pagamento/baixa de estoque, movimentações auditáveis, compras completas, devoluções, emissão fiscal, integração de pagamento, backup/restauração testados, gestão de usuários, migrações Alembic e endurecimento de segurança para produção. A integração fiscal não está configurada nem validada.

## Requisitos

- Ubuntu/Linux atualizado.
- Docker Engine e Docker Compose plugin.
- Git (opcional para uso local).
- Portas locais 5173, 8000 e 5433 livres.

## 1. Configurar segredos

```bash
cp .env.example .env
python3 - <<'PY'
from pathlib import Path
import secrets
p = Path(".env")
s = p.read_text()
s = s.replace("SUBSTITUA_POR_SENHA_FORTE_UNICA", secrets.token_urlsafe(32), 1)
s = s.replace("SUBSTITUA_POR_SEGREDO_ALEATORIO_COM_PELO_MENOS_32_BYTES", secrets.token_urlsafe(48))
s = s.replace("SUBSTITUA_POR_SENHA_FORTE_UNICA", secrets.token_urlsafe(32), 1)
p.write_text(s)
print("Segredos gerados no .env. Guarde a senha do administrador em um gerenciador de senhas.")
PY
chmod 600 .env
```

A senha inicial do administrador é a variável `BOOTSTRAP_ADMIN_PASSWORD` dentro de `.env`. Para descobri-la, execute `grep '^BOOTSTRAP_ADMIN_PASSWORD=' .env` localmente e guarde-a com segurança. Não envie essa saída em chats nem a publique no GitHub. Se trocar a senha no `.env` depois que o administrador já foi criado, isso **não** troca automaticamente a senha no banco.

## 2. Iniciar

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f api
```

Abra:
- Interface: http://localhost:5173
- Documentação da API: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## 3. Verificar saúde

```bash
curl -fsS http://localhost:8000/health
```

Resposta esperada:

```json
{"status":"ok","service":"super-as-api"}
```

## 4. Login pela API e cadastrar produto

Copie a senha inicial do `.env` e defina-a no terminal sem gravá-la no histórico:

```bash
read -rsp "Senha do administrador: " ADMIN_PASSWORD; echo
TOKEN=$(curl -fsS http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d "$(python3 -c 'import json,os; print(json.dumps({"username":"admin","password":os.environ["ADMIN_PASSWORD"]}))')" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')
```

Antes de executar, exporte a variável no shell sem colocar a senha literal no comando:
```bash
export ADMIN_PASSWORD
```

Cadastro de exemplo (código de barras de teste, não usar para mercadoria real):
```bash
curl -fsS -X POST http://localhost:8000/api/products \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "barcode":"TESTE-ARROZ-001",
    "name":"Arroz exemplo 5 kg",
    "unit":"UN",
    "cost_price":"20.00",
    "sale_price":"27.90",
    "stock_qty":"10.000",
    "min_stock":"2.000"
  }'
```

Pesquisar:
```bash
curl -fsS 'http://localhost:8000/api/products?search=Arroz' \
  -H "Authorization: Bearer $TOKEN"
```

## 5. Executar testes da API

O teste usa SQLite isolado, não o banco de operação. Execute de dentro de `backend/` em um ambiente Python 3.12 virtual:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

## 6. Comandos úteis

```bash
docker compose logs -f
docker compose restart api
docker compose down
```

`docker compose down` preserva o volume do banco. **Não** use `docker compose down -v` em ambiente com dados que queira manter.

## Segurança e produção

- Não exponha PostgreSQL diretamente à internet.
- Use HTTPS via proxy reverso e firewall antes de acesso externo.
- Rotacione segredos por procedimento controlado.
- Configure backups externos e teste restauração regularmente.
- Use migrações Alembic antes de evoluir o esquema em produção.
- Crie contas individuais para operadores; não compartilhe o administrador.
- Antes de emitir documento fiscal, selecione e valide um provedor compatível com o estado, regime tributário, certificado e operação da loja com o contador.
