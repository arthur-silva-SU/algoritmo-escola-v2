import os
import easygui
import pandas as pd
from pathlib import Path

# os.environ['R_HOME'] = r'C:\Program Files\R\R-4.4.2'
# import rpy2.robjects as ro
# # Definir a codificação para a do windows poder ler o código em R sem erros de codificação
# ro.r('Sys.setlocale("LC_ALL", "pt_BR.UTF-8")')
#
#
# def install_r_packages(packages):
#     """
#     Instala pacotes do R passados para a função
#     :param packages:
#     :return:
#     """
#     for package in packages:
#         ro.r(f'''
#             if (!requireNamespace("{package}", quietly = TRUE)) {{
#                 install.packages("{package}", dependencies = TRUE, repos = "https://cloud.r-project.org/")
#             }}
#         ''')
#
#
# # Lista dos pacotes R necessários.
# required_packages = ["mirt", "dplyr", "jsonlite"]
# install_r_packages(required_packages)
#
# # Recuperar o caminho onde são instalados os pacotes R no computador
# lib_paths = ro.r('.libPaths()')
# caminho_pacotes_r = lib_paths[0]
# print(f"R packages are installed at: {caminho_pacotes_r}")
#
# # Pedir o usuário selecionar o arquivo com os acertos dos alunos
BASE_DIR = Path(__file__).resolve().parent
# caminho_dados = easygui.fileopenbox(title="Selecione o arquivo com os acertos do alunos")
# if not caminho_dados:
#     raise ValueError("Não foi escolhido um arquivo. Finalizando o programa.")
#
# Definir caminho de saída dos arquivos .csv gerados
caminho_saida_finais = f"{BASE_DIR}/dados_finais.csv"
caminho_saida_parametros = f"{BASE_DIR}/dados_parametros.csv"
#
# # Definir os valores das variáveis no R com os valores dessas variáveis em Python
# ro.r.assign('caminho_dados', caminho_dados)
# ro.r.assign('caminho_saida_finais', caminho_saida_finais)
# ro.r.assign('caminho_saida_parametros', caminho_saida_parametros)
# ro.r('.libPaths')(ro.vectors.StrVector([caminho_pacotes_r]))
#
#
# # Código em R
# r_code = r'''
#     # Load packages
#     library(mirt)
#     library(dplyr)
#     library(jsonlite)
#
#     # Read student data from JSON file
#     dados_alunos <- fromJSON(caminho_dados)
#
#     # Rest of your R code...
#     nomes_alunos <- dados_alunos$aluno
#     dados_tri <- as.matrix(dados_alunos[, -1])
#     modelo_tri <- mirt(dados_tri, 1, itemtype = "3PL")
#     fscores_result <- fscores(modelo_tri, full.scores = TRUE)
#     theta_estimado <- if (is.list(fscores_result)) fscores_result$score else fscores_result
#     total_acertos <- rowSums(dados_tri)
#     media_desejada <- 500
#     desvio_padrao_desejado <- 100
#     media_theta <- mean(theta_estimado)
#     desvio_padrao_theta <- sd(theta_estimado)
#     score_transformado <- (theta_estimado - media_theta) / desvio_padrao_theta * desvio_padrao_desejado + media_desejada
#     score_formatado <- format(round(score_transformado, 2), nsmall = 2, decimal.mark = ",")
#     dados_finais <- data.frame(
#         Aluno = nomes_alunos,
#         Total_Acertos = total_acertos,
#         Score_TRI = theta_estimado,
#         Score_ENEM = score_formatado
#     )
#     write.csv(dados_finais, caminho_saida_finais, row.names = FALSE)
#
#     parametros_questoes <- coef(modelo_tri, IRTpars = TRUE)
#     dados_parametros <- data.frame(Questao = character(0), a = numeric(0), b = numeric(0), g = numeric(0), u = numeric(0))
#     nomes_questoes <- names(parametros_questoes)
#     for (i in seq_along(parametros_questoes)) {
#         if (grepl("GroupPars", nomes_questoes[i])) next
#         dados_questao <- c(Questao = nomes_questoes[i], as.numeric(parametros_questoes[[i]]))
#         dados_parametros <- rbind(dados_parametros, dados_questao)
#     }
#     colnames(dados_parametros)[-1] <- c("a", "b", "g", "u")
#     dados_parametros$Nível <- cut(
#         as.numeric(dados_parametros$b),
#         breaks = c(-Inf, -2, -1, 1, 2, Inf),
#         labels = c("Muito Fácil", "Fácil", "Médio", "Difícil", "Muito Difícil"),
#         include.lowest = TRUE
#     )
#     names(dados_parametros) <- c("questao", "discriminacao", "dificuldade", "adivinhacao", "u", "nivel")
#     dados_parametros$questao <- gsub("X\\.", "", dados_parametros$questao)
#     dados_parametros <- dados_parametros[!grepl("GroupPars", dados_parametros$questao),]
#     write.csv(dados_parametros, caminho_saida_parametros, row.names = FALSE)
# '''
#
# # Execute the R code
# ro.r(r_code)

# Ordenar a tabela por notas
student_data = pd.read_csv(caminho_saida_finais)
student_data = student_data.sort_values(by=['F1.1'], ascending=False)
student_data = student_data.reset_index(drop=True)
print(student_data)

# Definição dos indicadores por visualização por aluno
#============================PAINEL 01============================
# total de participantes
total_students = student_data['Aluno'].count()
print(f"{total_students} estudantes")
# Colocação (prova objetiva)
aluno_aleatorio = student_data.loc[0, 'Aluno']  # No local do 0, colocar a colocação que é desejada baseada no total de alunos.
print(aluno_aleatorio)
# Nota do Enem (prova objetiva)
nota_aleatoria = student_data.loc[0, 'F1.1']  # No local do 0, colocar a colocação que é desejada baseada no total de alunos.
print(nota_aleatoria)
# Quantidade de acertos e erros, distribuídos por dificuldade

# Faixa TRI do aluno
# Concentração de alunos por Faixa TRI
#============================PAINEL 02============================
# Nota em cada competência
# Nota da redação
# Colocação (redação)
# Faixa Redação do aluno
# Concentração de alunos por Faixa de redação
#============================PAINEL 03============================
# Tabela com as colunas: Questão|Reposta Correta|Resposta Aluno|Nível (dificuldade)
#======================================================================PAINEL 04======================================================================
# Tabela para o simulado anterior com as colunas: Aluno | Total de Acertos | TRI | Ranking TRI | Faixa TRI | Redação | Ranking Redação | Faixa Redação
# Tabela para o simulado atual com as colunas: Aluno | Total de Acertos | TRI | Ranking TRI | Faixa TRI | Redação | Ranking Redação | Faixa Redação