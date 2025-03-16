Alguns detalhes dos dados:
- Os dados estão em formato JSON.
- Todos os dados sensíveis (de clientes, candidatos e analistas) foram anonimizados utilizando, nomes, nº de celulares, e e-mails aleatórios.
 

Sobre os arquivos:

Jobs.json -> É chaveado pelo código da vaga e possui as informações referentes a vaga aberta no nosso ats divididas em Informações básicas, perfil da vaga e benefícios. Aqui temos dados importantes como, por exemplo:

indicação se é vaga SAP ou não
Cliente solicitante
Nível profissional e nível de idiomas requeridos
Principais atividades e competências técnicas requeridas
 

Prospects.json -> Também é chaveado pelo código da vaga e possui todas as prospecções da vaga.

Lista de prospecções com o código, nome, comentário e situação do candidato na vaga em questão
 

Applicants.json -> É chaveado pelo código do candidato e possui todas as informações referentes ao candidato: Informações básicas, pessoais, profissionais, formação e o cv. Informações importantes desse json:

Nível acadêmico, de inglês e espanhol
Conhecimentos técnicos
Área de atuação
Cv completo
 

Utilização: Por exemplo, a vaga 10976 (chave no Jobs.json), possui 25 prospecções (chave 10976 no prospects.json), onde o candidato “Sr. Thales Freitas”  (chave 41496 no applicants.json) foi contratado.

 