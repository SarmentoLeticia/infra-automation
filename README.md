# Projeto: Gerenciador de VMs com oVirt + FastAPI

Este projeto é uma API construída com **FastAPI** para gerenciar máquinas virtuais utilizando o **oVirt SDK para Python**.

## Funcionalidades Principais

A API permite executar as seguintes operações:

* Criar uma nova VM a partir de um template
* Iniciar a VM
* Adicionar interface de rede
* Obter IP da VM
* Consultar informações completas da VM
* Obter ID da VM
* Editar configurações de uma VM
* Deletar a VM

## Estrutura do Projeto

* `scripts.py`: Contém todas as funções de interação com o oVirt: criação, edição, deleção e consulta de VMs.
* `main.py`: Define os endpoints da API que chamam as funções do `scripts.py`.
* `login.json`: Arquivo de configuração contendo as credenciais e informações de conexão com o ambiente oVirt.

## Exemplo de `login.json`

```json
{
  "url": "https://seu-ovirt.example.com/ovirt-engine/api",
  "username": "admin@internal",
  "password": "sua_senha",
  "ca_file": "/caminho/para/ca.pem"
}
```

## Requisitos

* Python 3.8+
* FastAPI
* Uvicorn
* oVirt SDK 4 para Python
* Pydantic

Instale as dependências com:

```bash
pip install -r requirements.txt
```

## Executando a API

```bash
uvicorn main:app --reload --port 3000
```

Acesse: [http://localhost:3000/docs](http://localhost:3000/docs) para testar os endpoints via Swagger UI.

## Contato

Desenvolvido por Letícia Sarmento da Silva

## 📝 Licença

Este projeto está licenciado sob a licença MIT.  
Consulte o arquivo [LICENSE](LICENSE) para obter mais detalhes.
