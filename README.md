# CodeComplexityAnalyzer

O **CodeComplexityAnalyzer** é uma ferramenta de análise estática de código desenvolvida para avaliar a complexidade e a qualidade de projetos escritos em Python. 

A ferramenta inspeciona os seus arquivos fonte (`.py`), os converte numa Árvore Sintática Abstrata (AST) e gera um relatório `.json` contendo métricas essenciais para ajudar a identificar "hotspots" (funções problemáticas, altamente complexas ou difíceis de manter).

## O que o sistema analisa?

- **Complexidade Ciclomática:** Conta o número de caminhos de execução independentes na função (ramificações como `if`, `for`, `while`, blocos `try/except`).
- **Detecção de Loops e Recursão:** Analisa loops aninhados (profundidade de iterações) e checa se a função invoca a si mesma (recursão).
- **Estimativa de Complexidade de Tempo (Big-O):** Avalia os laços de repetição, recursão e funções conhecidas (ex: `sort`) para fazer uma estimativa assintótica (Ex: `O(1)`, `O(n)`, `O(n^2)`).
- **Métricas Básicas de Qualidade:**
  - Linhas de Código da Função (LOC)
  - Profundidade máxima da Árvore Sintática
  - Contagem de parâmetros fornecidos à função

## Instalação

O projeto utiliza apenas a biblioteca padrão do Python (como `ast`, `os`, `json`, `argparse`). Portanto, **não é necessário instalar nenhuma dependência externa via `pip`**!

### Requisitos
- Python 3.7+ (Recomendado para suporte completo às features modernas da AST)

### Passos
1. Clone este repositório ou faça o download da pasta.
2. Navegue até o diretório do projeto via terminal:
   ```bash
   cd CodeComplexityAnalyzer
   ```

## Como Usar

A interação com a ferramenta é feita através da linha de comando (`cli.py`). Você pode informar o caminho para um arquivo Python isolado ou para um diretório inteiro (ele buscará os arquivos recursivamente).

### Analisar um arquivo específico
```bash
python3 cli.py caminho/do/arquivo.py
```

### Analisar um diretório (um projeto completo)
```bash
python3 cli.py caminho/do/diretorio/
```
*(Dica: para analisar a pasta atual em que você se encontra, rode `python3 cli.py .`)*

### Opções Avançadas e Thresholds

Você pode alterar o comportamento do relatório passando parâmetros extras:

- `-o` ou `--output`: Escolhe o nome/caminho do arquivo de relatório JSON que será salvo. (Padrão: `cc_report.json`)
- `--warn`: Define o limiar (threshold) de aviso de atenção para a complexidade ciclomática. (Padrão: 10)
- `--error`: Define o limiar crítico (falha/erro) para a complexidade ciclomática. (Padrão: 20)

**Exemplo completo com opções:**
```bash
python3 cli.py src/ --output relatorio_final.json --warn 15 --error 30
```

Se desejar visualizar a página de ajuda com os comandos diretamente do terminal:
```bash
python3 cli.py -h
```

## Fontes e Referências Iniciais
As bases teóricas e bibliotecas que ajudaram a fundamentar este projeto:
* [Documentação do Módulo `ast` do Python](https://docs.python.org/pt-br/3.7/library/ast.html#node-classes)
* [Complexidade Assintótica (Big-O Notations)](https://arnaldojr.github.io/computacionalthinking/aulas/ctp/algorithms/big-o-notation.html)
* [Repositório Original CodeComplexityAnalyzer](https://github.com/hpachecjose/CodeComplexityAnalyzer)
* [Documentação CppDepend](https://www.cppdepend.com/documentation/getting-started-with-new-cppdepend?version=linux_cpp)
* [Tree-sitter Parsing](https://tree-sitter.github.io/tree-sitter/using-parsers/1-getting-started.html)
