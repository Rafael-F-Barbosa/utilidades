import streamlit as st

ASSUNTOS = ["Tecnologia", "Pessoas", "Processos"]
DIRETORIAS = {
    "Tecnologia": ["Desenvolvimento", "Operação"],
    "Pessoas": ["Manutenção", "Contratação"],
    "Processos": ["Análise", "Evolução"],
}


def filtrar_jobs(assunto="Todos", diretoria="Todas", jobs=None):
    jobs = jobs if jobs is not None else []
    return [
        j
        for j in jobs
        if (assunto == "Todos" or j.get("assunto") == assunto)
        and (diretoria == "Todas" or j.get("diretoria") == diretoria)
    ]


def limpar_filtros(key_prefix="seletor"):
    st.session_state[f"{key_prefix}_assunto"] = "Todos"
    st.session_state[f"{key_prefix}_diretoria"] = "Todas"


def seletor(
    jobs=None,
    key_prefix="seletor",
    placeholder="Filtrar por nome do job, diretoria ou assunto...",
):
    """Navegacao por pasta (assunto -> diretoria) + busca, com filtro dos jobs.

    Renderiza os widgets e retorna um dicionario com a lista filtrada:
    {"jobs": [...], "assunto": str, "diretoria": str, "busca": str,
     "termo": str, "caminho": str}.
    Se nenhum job for encontrado, mostra aviso (com sugestao de limpar
    filtros) e interrompe a execucao via st.stop().
    """
    jobs = jobs if jobs is not None else []
    k_assunto = f"{key_prefix}_assunto"
    k_diretoria = f"{key_prefix}_diretoria"

    assunto = st.segmented_control("Assunto", ["Todos"] + ASSUNTOS, default="Todos", key=k_assunto)

    if assunto == "Todos":
        diretoria = "Todas"
    else:
        diretoria = st.segmented_control(
            "Diretoria", ["Todas"] + DIRETORIAS[assunto], default="Todas", key=k_diretoria
        )

    busca = st.text_input("Buscar", placeholder=placeholder, key=f"{key_prefix}_busca")

    filtrados = filtrar_jobs(assunto, diretoria, jobs)
    termo = busca.strip().lower() if busca else ""
    if termo:
        filtrados = [
            j
            for j in filtrados
            if termo in j["nome"].lower()
            or termo in j.get("assunto", "").lower()
            or termo in j.get("diretoria", "").lower()
        ]

    caminho = " / ".join(
        p
        for p in ["Todos" if assunto == "Todos" else assunto, "" if diretoria == "Todas" else diretoria]
        if p
    )
    sufixo = f' &middot; busca "{busca.strip()}"' if termo else ""
    st.caption(f"Pasta: <b>{caminho}</b> &middot; {len(filtrados)} jobs{sufixo}", unsafe_allow_html=True)

    if not filtrados:
        if termo and (assunto != "Todos" or diretoria != "Todas"):
            st.warning(
                f'Nenhum job encontrado com a busca "{busca.strip()}" na pasta "{caminho}". '
                "A busca pode conflitar com os filtros de assunto e diretoria."
            )
            st.button(
                "Remover filtros de assuntos e diretoria",
                key=f"{key_prefix}_btn_limpar",
                on_click=limpar_filtros,
                args=(key_prefix,),
            )
        else:
            st.warning("Nenhum job encontrado com a busca atual.")
        st.stop()

    return {
        "jobs": filtrados,
        "assunto": assunto,
        "diretoria": diretoria,
        "busca": busca,
        "termo": termo,
        "caminho": caminho,
    }
