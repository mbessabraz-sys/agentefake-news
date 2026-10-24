# Assistente de Fake News (RAG)

API educacional que recupera trechos relevantes de uma base local usando TF-IDF e
envia o contexto à API de mensagens da Anthropic para gerar respostas.

## Configuração

Requer Python 3.9 ou superior. Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

Configure a chave da Anthropic no arquivo `.env` (na raiz do projeto):

```dotenv
ANTHROPIC_API_KEY=sua-chave
```

O arquivo `.env` é carregado automaticamente. Uma variável já definida no
ambiente do sistema tem precedência sobre o valor do arquivo.

## Execução

Inicie a API com:

```powershell
python -m src.main
```

Ou, para iniciar com recarga automática durante o desenvolvimento:

```powershell
uvicorn api:app --reload
```

Abra http://localhost:8000. O endpoint `POST /perguntar` recebe
`{"pergunta": "..."}` e retorna a resposta e as fontes recuperadas.

## Testes

```powershell
python -m unittest discover -s tests
```
