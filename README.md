# AIDecision
Este projeto utiliza dados fornecidos pela Decision para análise e modelagem preditiva no processo de recrutamento e seleção.

## Documentação e Recursos
- [Documentação do Projeto](https://docs.google.com/document/d/17XncF-K0MXrnaBrAUXjxubENoJXcsEpNCWhWKBPh0QM/edit?usp=drive_link)
- [Drive do Datathon](https://drive.google.com/drive/folders/1dYdZww8Y72NdUYHk2G2jtSifQDa1Io_F?usp=drive_link)

## Estrutura do Projeto
```
AIDecision/
├── dados/                    # Diretório com os arquivos de dados
│   ├── applicants.json       # Dados dos candidatos
│   ├── prospects.json        # Dados dos prospects
│   └── vagas.json           # Dados das vagas
├── notebooks/                # Jupyter notebooks de análise
│   ├── eda.ipynb            # Análise exploratória inicial
│   └── merge.ipynb          # Processo de merge das tabelas
├── merged_data.csv          # Dataset final após merge
└── dicionario_dados.csv     # Dicionário de dados com descrição das colunas
```

## Processo de Dados

### Merge das Tabelas
O processo de merge é centralizado na tabela de prospects, que é a tabela principal para o modelo de classificação. O merge é realizado em duas etapas:

1. **Merge Prospects-Vagas**: 
   - Usa o `id` do prospect para fazer o merge com o `id_vaga`
   - Mantém todos os registros de prospects (left join)
   - Adiciona informações sobre as vagas

2. **Merge com Applicants**:
   - Usa o `candidato_codigo` do prospect para fazer o merge com o `id_candidato`
   - Mantém todos os registros (left join)
   - Adiciona informações detalhadas sobre os candidatos

### Dicionário de Dados
O arquivo `dicionario_dados.csv` contém informações detalhadas sobre todas as colunas do dataset final, incluindo:
- Nome da coluna
- Tipo de dados
- Total de registros
- Número de valores únicos
- Quantidade e porcentagem de valores nulos
- Exemplos de valores

## Notebooks

### merge.ipynb
Este notebook realiza o processo de:
1. Carregamento dos arquivos JSON
2. Conversão para DataFrames
3. Merge das três tabelas (prospects, vagas, applicants)
4. Geração do dataset final em CSV
5. Criação do dicionário de dados

## Dados
Os dados utilizados neste projeto foram fornecidos pela Decision e incluem:
- Informações sobre candidatos
- Dados de prospects
- Detalhes das vagas
- Histórico de candidaturas
- Situações dos candidatos no processo seletivo
