from openai import OpenAI
from utils.tags import tags
import json
from config import Config

client = OpenAI(api_key=Config.OPENAI_KEY)

BASE_PROMPT = """
Você é um classificador semântico RIGOROSO para um projeto educacional que conecta estudantes a oportunidades e pessoas.
Você deve seguir as regras abaixo de maneira estrita — o objetivo é produzir SAÍDA ESTRUTURADA e CONFIÁVEL.

---- INSTRUÇÕES GERAIS (obrigatórias) ----
1) Retorne SOMENTE JSON válido, estritamente no formato pedido (sem texto extra).
2) Use apenas índices 0-based (inteiros) referindo-se à lista de tags fornecida em {tags_list}.
3) Não invente tags. Só marque uma tag se houver **evidência clara** no texto do usuário (fields `subjects`, `level`, `interests`).
4) Seja conservador:
   - Se a informação for vaga, contraditória, insuficiente ou ambígua, retorne {{ "appropriate": false, "tags": [] }}.
   - Quando em dúvida entre duas tags, NÃO marque nenhuma.
5) Não repita índices; retorne uma lista única e ordenada de índices.
6) Se o campo `name` for ofensivo, sexual, insultuoso, claramente falso (trocadilho ofensivo) ou conter palavrões, retorne {{ "appropriate": false, "tags": [] }}.

---- COMO LIDAR COM TEXTOS LONGOS / INTERESTS ----
- O campo `interests` pode ser longo; leia-o completamente.
- Extraia apenas o que está explicitamente indicado ou claramente inferível.
- Ignore afirmações vagas do tipo "gosto de tudo" ou "talvez" — essas não contam como evidência.

---- EXEMPLOS DE RESPOSTAS INAPROPRIADAS (faça o modelo BLOQUEAR) ----
- Nome com palavrões ou trocadilhos insultuosos (ex.: "João Pica Dura") → inappropriate.
- Respostas vazias ou “não sei” em campos críticos (ex.: subjects vazio, interests vazio) → inappropriate.
- Contradição direta (ex.: diz "ensino fundamental" e em outro campo "terceiro ano do ensino médio") → inappropriate.
- Afirmação fantasiosa / fabricada sem prova (ex.: "sou medalhista IMO" sem contexto) → inappropriate.
- Texto irrelevante (spam, links, propaganda) → inappropriate.

---- FORMATO DE SAÍDA (obrigatório) ----
Você deve retornar EXATAMENTE:
{{
  "appropriate": boolean,
  "tags": [inteiros]
}}

- `appropriate`: true somente se os campos fornecem informações coerentes e suficientes para etiquetar; caso contrário, false.
- `tags`: lista de índices 0-based (inteiros), sem repetições, ordenada. Se `appropriate` for false, deve ser [].

---- FEW-SHOT (apenas 3 exemplos para ancorar o comportamento) ----

# Exemplo Aceitável (claro e consistente)
Entrada:
{{
  "name": "Mariana Alves",
  "subjects": "Gosto de história, sociologia e português; participo de debates e escrevo redações.",
  "level": "Terceiro ano do ensino médio, escola pública",
  "interests": "Redação, interpretação de texto, projetos sociais, liderança estudantil"
}}
Resposta esperada:
{{ "appropriate": true, "tags": [1, 5, 6, 64, 65, 85, 86, 87, 88, 89] }}

# Exemplo Inapropriado 1 (nome ofensivo)
Entrada:
{{
  "name": "João Pica Dura",
  "subjects": "Matemática",
  "level": "Ensino médio",
  "interests": "OBMEP"
}}
Resposta esperada:
{{ "appropriate": false, "tags": [] }}

# Exemplo Inapropriado 2 (vago/contraditório)
Entrada:
{{
  "name": "Carlos",
  "subjects": "",
  "level": "ensino fundamental (mas sou universitário)",
  "interests": "talvez programação, talvez nada"
}}
Resposta esperada:
{{ "appropriate": false, "tags": [] }}

---- EXPLICAÇÃO DETALHADA DOS CAMPOS (entrada) ----
- `name`: nome completo ou apelido do usuário. Usado apenas para checagem de ofensa/validade.
- `subjects`: As matérias acadêmicas que o usuário tem interesse (ex.: "matemática, física" ou "história, sociologia"). Pode ser curto ou longo.
- `level`: O nível de estudos do usuário (ex.: "segundo ano ensino médio", "ensino médio técnico", "universitário"). Seja literal; se houver contradição, marque `appropriate=false`.
- `interests`: Interesses pessoais e acadêmicos — pode ser uma resposta longa que frequentemente define o perfil. Inclui objetivos (ex.: "quero estudar para OBMEP", "interesse em pesquisa científica", "curioso por programação").
- `opportunities` (se fornecido): boolean que indica se o usuário quer receber oportunidades. NÃO é obrigatório para decidir tags mas pode ajudar.
- `matching` (se fornecido): boolean sobre querer conexões; NÃO altera marcação de tags.

---- EXPLICAÇÃO DO JSON DE SAÍDA ----
- `appropriate`:
  - true: quando há informação coerente e suficiente para atribuir tags.
  - false: quando dados são vagos, contraditórios, ofensivos ou insuficientes.
- `tags`: lista de índices (0-based) das tags relevantes. Só inclua uma tag se houver EVIDÊNCIA.

---- REGRAS DE PRIORIZAÇÃO (casos práticos) ----
- Se o usuário mencionar explicitamente uma olimpíada (ex.: "OBMEP"), marque a tag correspondente (ex.: `obmep`).
- Se o usuário disser "gosto de matemática" sem nível, marque apenas a tag geral de matéria (ex.: `matematica iniciante` ou `matematica intermediario`) somente se houver indicação do nível; caso contrário, seja conservador (não marque).
- Se o usuário listar várias áreas, marque todas que têm evidência direta.
- Não deduza proficiência a partir de entusiasmo; só marque níveis (iniciante/intermediario/avancado) se houver sinal claro ("faço aulas avançadas", "resolvo problemas de olimpíada").

---- OUTRAS REGRAS TÉCNICAS ----
- Remova duplicatas e ordene os índices em ordem crescente.
- Nunca retorne texto adicional, explicações, ou metadados — apenas JSON.

---- AGORA: execute a tarefa para os dados que serão inseridos no placeholder {student_json} ----
"""


def offensive(name: str) -> bool:
    blacklist = ["pica", "puta", "caralho", "foda"]  # ajuste
    n = name.lower()
    return any(word in n for word in blacklist)


def classify_student(session):
    if offensive(session.name):
        return {"appropriate": False, "tags": []}

    student_data = {
        "name": session.name,
        "subjects": session.subjects,
        "level": session.level,
        "interests": session.interests,
    }

    tags_list = "\n".join(f"{i}. {tag}" for i, tag in enumerate(tags))

    prompt = BASE_PROMPT.format(
        tags_list=tags_list,
        student_json=json.dumps(student_data, ensure_ascii=False)
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    text = response.output_text.strip()

    try:
        result = json.loads(text)
        assert isinstance(result["appropriate"], bool)
        assert isinstance(result["tags"], list)
        return result
    except Exception:
        return {"appropriate": False, "tags": []}
