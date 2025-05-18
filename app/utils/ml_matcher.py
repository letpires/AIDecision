import joblib
import numpy as np
import json
from openai import OpenAI
import pandas as pd
# from processing import BooleanConverter


# Carregue o modelo uma vez só
ML_MODEL = joblib.load('/app/utils/modelo_rf_completo.joblib')

MODEL_FEATURES = [
    'perfil_vaga_vaga_especifica_para_pcd', 'possui_certificacao', 'remuneracao_limpa',
    'perfil_vaga_pais', 'perfil_vaga_estado', 'perfil_vaga_cidade', 'titulo',
    'perfil_vaga_nivel profissional', 'perfil_vaga_nivel_academico', 'perfil_vaga_nivel_ingles',
    'perfil_vaga_nivel_espanhol', 'perfil_vaga_outro_idioma',
    'informacoes_profissionais_nivel_profissional',
    'formacao_e_idiomas_nivel_academico', 'formacao_e_idiomas_nivel_ingles',
    'formacao_e_idiomas_nivel_espanhol', 'formacao_e_idiomas_outro_idioma',
    'infos_basicas_local', 'match_backend_candidato', 'match_backend_vaga',
    'match_frontend_candidato', 'match_frontend_vaga', 'match_banco_dados_candidato',
    'match_banco_dados_vaga', 'match_devops_infra_candidato', 'match_devops_infra_vaga',
    'match_bi_dados_candidato', 'match_bi_dados_vaga', 'match_erp_sap_candidato',
    'match_erp_sap_vaga', 'match_mainframe_legado_candidato', 'match_mainframe_legado_vaga',
    'match_design_ux_candidato', 'match_design_ux_vaga', 'match_gestao_agil_candidato',
    'match_gestao_agil_vaga', 'match_ciencia_dados_ia_candidato', 'match_ciencia_dados_ia_vaga',
    'match_habilidades_comportamentais_candidato', 'match_habilidades_comportamentais_vaga',
    'score_total'
]



def montar_features(profile, job, extra_data):
    features = {}
    for feat in MODEL_FEATURES:
        value = profile.get(feat) or job.get(feat) or extra_data.get(feat)
        if value is None:
            value = "Não informado" if isinstance(feat, str) else 0
        features[feat] = value

    return pd.DataFrame([features])

def score_ml(features_vector):
    """Retorna a probabilidade de match do modelo ML"""

    assert isinstance(features_vector, pd.DataFrame), "Entrada deve ser um DataFrame"
    assert features_vector.shape[1] == 41, "Número de colunas incorreto"
    assert not features_vector.isnull().any().any(), "Existem valores nulos"
    
    return ML_MODEL.predict_proba(features_vector)[0][1]



def gerar_features_com_llm(curriculo: str, vaga: str, feature_list: list = MODEL_FEATURES) -> dict:
    """
    Usa LLM para gerar um dicionário com os valores das features necessárias para o modelo.
    """
    prompt = f"""
Você é um assistente de machine learning. Com base no currículo e na vaga abaixo,
gere um dicionário JSON com os seguintes campos:

{feature_list}

Se um campo não estiver disponível, use "Não informado", False ou 0, conforme apropriado.

Currículo:
{curriculo}

Vaga:
{vaga}
"""

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um extrator de features para machine learning."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )

    # Interpretar a resposta como JSON
    return json.loads(response.choices[0].message.content)
