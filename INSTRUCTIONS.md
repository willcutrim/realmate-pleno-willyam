# INSTRUÇÕES DO PROJETO

## 🔧 Tecnologias Utilizadas
- Python 3.10
- Django 5.1.6
- Django Rest Framework
- Celery
- Redis
- PostgreSQL
- Docker + Docker Compose

## 🚀 Como rodar o projeto

### Pré-requisitos
- Docker e Docker Compose instalados

### Passos
1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/realmate-challenge.git
cd realmate-challenge
```

2. Crie o arquivo `.env` com base no `.env.example`.

3. Execute o projeto:
```bash
sudo docker-compose up --build
```

A aplicação estará disponível em http://localhost:8000

## 🧪 Testando via POSTMAN

### Endpoint:
```
POST /webhook/
```

### Payloads:

#### Criar conversa
```json
{
  "type": "NEW_CONVERSATION",
  "timestamp": "2025-06-04T14:20:00Z",
  "data": {
    "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
  }
}
```

#### Nova mensagem
```json
{
  "type": "NEW_MESSAGE",
  "timestamp": "2025-06-04T14:20:05Z",
  "data": {
    "id": "49108c71-4dca-4af3-9f32-61bc745926e2",
    "content": "Olá, quero informações sobre alugar um apartamento.",
    "conversation_id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
  }
}
```

#### Fechar conversa
```json
{
  "type": "CLOSE_CONVERSATION",
  "timestamp": "2025-06-04T14:25:00Z",
  "data": {
    "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
  }
}
```

### Consultar Conversa:
```
GET /conversations/<id>/
```

## 📦 Notas
- O processamento assíncrono de mensagens é feito via Celery + Redis
- Mensagens INBOUND enviadas com até 5 segundos de diferença são agrupadas
- Uma mensagem OUTBOUND é criada com os IDs agrupados
- Mensagens enviadas antes da conversa ser criada têm 6 segundos de tolerância