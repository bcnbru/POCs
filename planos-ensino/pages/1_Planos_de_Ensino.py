"""Streamlit app para gerar Planos de Ensino."""

# Import from standard library
import logging

# Import from 3rd party libraries
import streamlit as st
import streamlit.components.v1 as components
import streamlit_analytics

# Import modules
import oai

# Configure logger
logging.basicConfig(format="\n%(asctime)s\n%(message)s", level=logging.INFO, force=True)


template_plano = """
#Template para criação de Plano de Ensino
---
## 1. IDENTIFICAÇÃO
### 1.1. Curso: 
### 1.2. Disciplina: 
### 1.3. Responsável pela Disciplina: 

## 2. EMENTA
(Instruções: Utilize as seguintes expressões: Estudo de...; caracterização de...; Elaboração de...; Construção de...; Introdução à...)

## 3. OBJETIVOS DA DISCIPLINA
(Intruções:
Exemplos:
- Apresentar o conceito de x...
- Discutir os aspectos de x no que diz respeito a y...
- Aplicar os conhecimentos de x...
- Articular o x com o y...
- Avaliar as possibilidades de x e planejar y...
Usar somente um verbo por objetivo.
Atenção:
Os verbos da base da pirâmide (CONHECIMENTO) podem ser utilizados quando o docente pretende introduzir um novo conceito/técnica/procedimento.
Os verbos de COMPREENSÃO devem ser utilizados sempre que o autor tiver como propósito uma compreensão do conceito/técnica/procedimento discutido na disciplina.
Os verbos de APLICAÇÃO e ANÁLISE devem ser utilizados considerando as atividades que serão construídas no momento de prática e reflexão, uma vez que o aluno terá que analisar o que foi apresentado e aplicar os conceitos discutidos.
Os verbos de SINTESE e AVALIAÇÃO devem ser utilizados considerando as atividades que serão construídas no momento da atividade individual, uma vez que o aluno terá que sintetizar o conteúdo apresentado para posteriormente escolher a melhor resposta para a atividade.
Para uma disciplina de Pós-Graduação podemos colocar:
- Um ou dois objetivos de CONHECIMENTO
- Um ou dois objetivos de COMPREENSÃO 
- Um ou dois objetivos de APLICAÇÃO / ANÁLISE
- Um ou dois objetivos de SÍNTESE / AVALIAÇÃO
Lembre-se que os objetivos das disciplinas são construídos da base para o topo da pirâmide, ou seja, primeiro você apresenta algo novo para o aluno, para depois exigir que ele compreenda, aplique, opine ou avalie)

## 4. CONTEÚDO PROGRAMÁTICO DE CADA UNIDADE DE APRENDIZAGEM
(Exemplo:
- **Unidade 1. X**
 - Lorem ipsum dolor sit amet
 - Consectetur adipiscing elit
 - Sed do eiusmod tempor incididunt
 - Ut labore et dolore magna aliqua
- **Unidade 2. Y**
 - Ut enim ad minim veniam
 - Quis nostrud exercitation ullamco
 - Laboris nisi ut aliquip ex ea commodo
 - Duis aute irure dolor in reprehenderit
- **Unidade n. Z**
 - Ut enim ad minim veniam
 - Quis nostrud exercitation ullamco
 - Laboris nisi ut aliquip ex ea commodo
 - Duis aute irure dolor in reprehenderit)

## 5. OBJETOS DE APRENDIZAGEM
(Exemplos:
- Conteúdo instrucional.
- Material interativo.
- Vídeo.
- Momento de prática e reflexão.
- Material complementar.
- Fórum de discussão.
- Web conferência.
- Atividade individual.)

## 6. CRITÉRIOS DE AVALIAÇÃO DA APRENDIZAGEM
(Exemplo:
O aluno será avaliado por meio da realização das atividades de prática e reflexão (40%) e realização da atividade individual (60%). 
As atividades serão somadas e serão aprovados os alunos com aproveitamento maior ou igual a 70%. 
Aos alunos que não obtiverem o aproveitamento necessário, será oferecida uma atividade de segunda chamada.)

## 7. BIBLIOGRAFIA BÁSICA
(Instruções: Usar formatação Vancouver)

## 8. BIBLIOGRAFIA COMPLEMENTAR
(Instruções: Usar formatação Vancouver)
"""

# Define functions
def generate_text(curso, objetivos, disciplinas, bibliografia):
    """Gerar Plano de Ensino"""
    if st.session_state.n_requests >= 5:
        st.session_state.text_error = "Too many requests. Please wait a few seconds."
        logging.info(f"Session request limit reached: {st.session_state.n_requests}")
        st.session_state.n_requests = 1
        return

    st.session_state.text_error = ""

    if not curso:
        st.session_state.text_error = "Informe um curso"
        return

    with text_spinner_placeholder:
        with st.spinner("Aguarde enquanto geramos o plano de ensino."):
            prompt = f"""{template_plano}\n\n
            Usando o template acima crie um plano de ensino formatado em markdown e usando as informações fornecidas abaixo:\n
            Curso: {curso}\n
            Objetivos: {objetivos}\n
            Disciplinas: {disciplinas}\n
            Bibliografia: {bibliografia}\n\n
            """

            openai = oai.Openai()
            flagged = openai.moderate(prompt)
            if flagged:
                st.session_state.text_error = "Input flagged as inappropriate."
                logging.info(f"Curso: {curso}\n")
                return

            else:
                st.session_state.text_error = ""
                st.session_state.n_requests += 1
                streamlit_analytics.start_tracking()
                st.session_state.plano = (
                    openai.complete(prompt=prompt).strip().replace('"', "")
                )
                logging.info(
                    f"Curso: {curso}\n"
                    f"Plano: {st.session_state.plano}"
                )

# Configure Streamlit page and state
st.set_page_config(page_title="Gerador de Plano de Ensino")

if "plano" not in st.session_state:
    st.session_state.plano = ""
if "text_error" not in st.session_state:
    st.session_state.text_error = ""
if "n_requests" not in st.session_state:
    st.session_state.n_requests = 0

# # Force responsive layout for columns also on mobile
# st.write(
#     """<style>
#     [data-testid="column"] {
#         width: calc(50% - 1rem);
#         flex: 1 1 calc(50% - 1rem);
#         min-width: calc(50% - 1rem);
#     }
#     </style>""",
#     unsafe_allow_html=True,
# )

# Render Streamlit page
streamlit_analytics.start_tracking()
st.title("Gerador de Planos de Ensino")

col1, col2 = st.columns(2)

with col1:
    curso = st.text_input(label="Curso", placeholder="Informe o nome do curso")
    objetivos = st.text_area(label="Objetivos", placeholder="Descreva os principais objetivos do curso")
with col2:
    disciplinas = st.text_area(label="Disciplinas", placeholder="Liste as disciplinas do curso")
    bibliografia = st.text_area(label="Bibliografia", placeholder="Liste a bibliografia do curso")

st.button(
    label="Gerar Plano de Ensino",
    type="primary",
    on_click=generate_text,
    args=[curso, objetivos, disciplinas, bibliografia]
)

st.markdown("""---""")
text_spinner_placeholder = st.empty()
if st.session_state.text_error:
    st.error(st.session_state.text_error)

if st.session_state.plano:
    st.markdown(st.session_state.plano)


streamlit_analytics.stop_tracking()
