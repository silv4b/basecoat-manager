# UV + Poethepoet

## 1. Instalando o uv e Inicializando o Projeto

Se você ainda não tem o `uv`, instale-o e crie um novo projeto:

```bash
# Instalação rápida (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Criando um novo projeto
uv init meu-projeto
cd meu-projeto
```

## 2. Adicionando o PoeThePoet

Em vez de instalar o `poe` globalmente, vamos adicioná-lo como uma **dependência de desenvolvimento** do seu projeto. Isso garante que qualquer pessoa que clone seu repositório tenha a mesma ferramenta.

```bash
uv add --dev poethepoet
```

## 3. Configurando os Comandos no `pyproject.toml`

O `poe` lê as configurações diretamente do seu arquivo `pyproject.toml`. Abra o arquivo e adicione uma seção `[tool.poe.tasks]`.

Aqui está um exemplo prático de tarefas comuns:

```toml
[tool.poe.tasks]
# Comando simples
test = "pytest"

# Comando com múltiplos passos
lint = ["ruff check .", "mypy ."]

# Comando com argumentos
serve = "python -m flask run --port=5000"

# Comando formatado (estilo shell)
clean = """
rm -rf .venv
rm -rf .pytest_cache
rm -rf .mypy_cache
"""
```

## 4. Rodando os Comandos com `uv run`

Como instalamos o `poe` dentro do ambiente do projeto, a forma correta de chamá-lo é através do `uv run`. Isso garante que o `uv` ative o ambiente virtual automaticamente antes de executar a tarefa.

| Objetivo | Comando |
| --- | --- |
| **Listar todas as tarefas** | `uv run poe --help` |
| **Rodar testes** | `uv run poe test` |
| **Rodar o linter** | `uv run poe lint` |
| **Rodar servidor** | `uv run poe serve` |

### Dica de Ouro: Atalho de Shell

Se você acha `uv run poe` muito longo, pode criar um alias no seu `.bashrc` ou `.zshrc`:

```bash
alias p="uv run poe"

```

Agora, basta digitar `p test` para rodar seus testes.
