# Dashboard de sono e bem-estar acadêmico

Aplicação em desenvolvimento para a Atividade 2 da disciplina, usando dados fictícios sobre hábitos de sono e rotina acadêmica de estudantes universitários.

## Objetivo

O projeto atende ao **Perfil 3 — Assistência estudantil**. Seu objetivo é apoiar a identificação de grupos de estudantes com indicadores menos favoráveis de sono e cansaço, para orientar ações de promoção de bem-estar.

A pergunta central da atividade é:

> Quais grupos de estudantes apresentam os piores indicadores de sono e cansaço?

A visualização deve priorizar comparações por curso e período do curso, observando indicadores como horas de sono, horário habitual de dormir e percepção de cansaço durante o dia. Outras variáveis podem ser incluídas se ajudarem a responder à pergunta sem sobrecarregar o painel.

Os registros são fictícios e foram criados para fins didáticos. As relações observadas não representam causalidade nem devem ser interpretadas como diagnóstico sobre estudantes reais.

## Dados

A planilha fornecida para a atividade fica em:

```text
data/raw/dados_habitos_sono_rotina_academica.xlsx
```

Mantenha o arquivo original nessa pasta. O projeto usa a aba `Dados` como fonte principal; as abas `Dicionario`, `Perfis` e `Leia-me` contêm informações de apoio.

## Requisitos

- Python 3.11 ou superior
- `pip`

As dependências diretas e suas versões estão listadas em `requirements.txt`.

## Instalação

Execute os comandos abaixo na raiz do projeto.

### Linux ou macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Se o ambiente `.venv` já existir, basta ativá-lo e instalar ou atualizar as dependências:

```bash
python -m pip install -r requirements.txt
```

## Como executar

O ponto de entrada planejado para a aplicação Streamlit é `src/app.py`. Quando a interface do dashboard estiver implementada, inicie-a pela raiz do projeto com:

```bash
streamlit run src/app.py
```

O Streamlit mostrará no terminal o endereço local para abrir no navegador, normalmente `http://localhost:8501`.

**Estado atual:** `src/app.py` apresenta a estrutura inicial do painel, com filtros por curso e período e indicadores-resumo. Os gráficos ainda serão desenvolvidos em `src/plots.py`.

O carregamento da planilha está isolado em `src/data_loader.py`. A função `load_data()` lê a aba `Dados` sem alterar os valores originais.
