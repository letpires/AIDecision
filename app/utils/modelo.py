import pandas as pd
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
import joblib
from sklearn.pipeline import Pipeline as SklearnPipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score


data = pd.read_csv('/app/data_final.csv')

#Deletar colunas ['id_vaga', 'situacao_candidato', 'info_vaga', 'info_candidato', 'info_limpa_candidato', 'info_limpa_vaga']
data.drop(columns=['id_vaga', 'situacao_candidato', 'info_vaga', 'info_candidato', 'id_candidato', 'info_limpa_candidato', 'info_limpa_vaga'], inplace=True)
data.info()


data['perfil_vaga_vaga_especifica_para_pcd'] = data['perfil_vaga_vaga_especifica_para_pcd'].fillna(False).astype(bool)
data['possui_certificacao'] = data['possui_certificacao'].fillna(False).astype(bool)
data['perfil_vaga_nivel_espanhol'] = data['perfil_vaga_nivel_espanhol'].fillna('Não informado')


#Substituir Não informado em remuneracao_limpa como 0, e converta coluna pra float
data['remuneracao_limpa'] = data['remuneracao_limpa'].replace('Não informado', 0).astype(float)


colunas_categoricas_com_nulos = [
    'infos_basicas_local',
    'perfil_vaga_cidade',
    'perfil_vaga_estado',
    'perfil_vaga_nivel profissional',
    'perfil_vaga_nivel_academico',
    'perfil_vaga_nivel_ingles',
    'perfil_vaga_pais'
]

for col in colunas_categoricas_com_nulos:
    data[col] = data[col].fillna('Não informado')


# === 2. Definindo colunas ===
# colunas_booleans = ['perfil_vaga_vaga_especifica_para_pcd', 'possui_certificacao']
colunas_categoricas = [
    'perfil_vaga_pais', 'perfil_vaga_estado', 'perfil_vaga_cidade', 'titulo',
    'perfil_vaga_nivel profissional', 'perfil_vaga_nivel_academico', 'perfil_vaga_nivel_ingles',
    'perfil_vaga_nivel_espanhol', 'perfil_vaga_outro_idioma',
    'informacoes_profissionais_nivel_profissional',
    'formacao_e_idiomas_nivel_academico', 'formacao_e_idiomas_nivel_ingles',
    'formacao_e_idiomas_nivel_espanhol', 'formacao_e_idiomas_outro_idioma',
    'infos_basicas_local'
]


# === 3. Pré-processador com imputação e encoding ===
preprocessador = ColumnTransformer([
    ('cat', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1), colunas_categoricas)
], remainder='drop')

# === 4. Pipeline completo ===
pipeline = Pipeline([
    ('preprocessamento', preprocessador),
    ('balanceamento', SMOTE(random_state=42)),
    ('modelo', RandomForestClassifier(random_state=42))
])

# === 5. Separar dados e treinar ===
X = data.drop(columns=['match'])  # ajusta se precisar
y = data['match'].astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)

# === 6. Avaliação ===
print("Acurácia:", accuracy_score(y_test, y_pred))
print("\nRelatório de Classificação:\n", classification_report(y_test, y_pred))

# === 7. Salvar modelo completo ===
joblib.dump(pipeline, '/app/utils/modelo_rf_completo.joblib')
