# Guia de Configuração do Ambiente de Desenvolvimento

Este guia fornece as instruções necessárias para configurar o ambiente de desenvolvimento do **Kore Product Manager** do zero. Siga estes passos para garantir que todas as ferramentas e dependências estejam instaladas corretamente.

---

## 1. Pré-requisitos

Antes de começar, certifique-se de ter as seguintes ferramentas instaladas no seu sistema:

* **Python 3.14+**: O projeto utiliza funcionalidades e tipagens modernas.
* **UV**: Gerenciador de pacotes e ambientes Python de alta performance.
  * *Instalação (Windows/PowerShell):* `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
  * *Instalação (Linux/macOS):* `curl -LsSf https://astral.sh/uv/install.sh | sh`
* **Node.js & npm**: Necessários para a compilação do CSS (Tailwind v4).
* **Git**: Para controle de versão.
* **Docker Desktop** (Opcional): Apenas se desejar utilizar PostgreSQL localmente via container.

---

## 2. Instalação do Projeto

1. **Clone o repositório:**

    ```bash
    git clone https://github.com/seu-usuario/kore-product-manager.git
    cd kore-product-manager
    ```

2. **Sincronize as dependências Python:**
    Com o `uv`, você não precisa criar um ambiente virtual manualmente. O comando abaixo cria o ambiente e instala tudo (incluindo dependências de desenvolvimento):

    ```bash
    uv sync
    ```

3. **Instale as dependências Frontend:**

    ```bash
    npm install
    ```

---

## 3. Configuração de Variáveis de Ambiente

O projeto usa o arquivo `.env` para gerenciar configurações sensíveis e de ambiente.

1. Copie o arquivo de exemplo:

    ```bash
    cp .env.example .env
    ```

2. Abra o arquivo `.env` e ajuste se necessário. Por padrão, se você não configurar as variáveis de banco de dados, o Django utilizará o **SQLite**.

---

## 4. Banco de Dados e Migrações

Prepare o banco de dados inicial:

```bash
uv run manage.py migrate
```

Opcionalmente, crie um superusuário para acessar o painel administrativo:

```bash
uv run manage.py createsuperuser
```

---

## 5. Fluxo de Trabalho (Desenvolvimento)

Para trabalhar no projeto, você geralmente precisará de dois processos rodando simultaneamente: o servidor Django e o compilador de CSS do Tailwind.

### Usando PoeThePoet (Recomendado)

Configuramos atalhos no `pyproject.toml` para facilitar:

* **Rodar tudo em um comando:**

    ```bash
    uv run poe dev
    ```

    *Nota: Isso rodará o servidor Django e o watch do Tailwind.*

### Comandos Manuais

Se preferir rodar separadamente em terminais diferentes:

1. **Terminal 1 (Tailwind Watch):**

    ```bash
    npm run watch
    ```

2. **Terminal 2 (Django Server):**

    ```bash
    uv run manage.py runserver
    ```

---

## 6. Testes e Qualidade

Mantenha o código saudável rodando os testes regularmente:

* **Rodar todos os testes:**

    ```bash
    uv run poe pytest
    ```

* **Gerar relatório de cobertura (Coverage):**

    ```bash
    uv run poe test
    ```

    *Isso gerará uma pasta `htmlcov/` com um relatório detalhado.*

---

## 7. Dicas de Ferramental

* **VS Code**: Recomendamos as extensões **Pylance**, **Django Health**, **Tailwind CSS IntelliSense** e **Lucide Icons**.
* **Linting**: O projeto está configurado para seguir padrões PEP 8. Recomendamos configurar o VS Code para "format on save" usando ferramentas como `ruff` ou `black` (disponíveis via uv).

---
*Em caso de dúvidas, consulte os outros documentos em `docs/` sobre Docker, Allauth e o Roadmap do projeto.*
