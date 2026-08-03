import datetime
import html
import json
from pathlib import Path

import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent

COR_STATUS = {
    "SUCESSO": "#2da44e",
    "ARQUIVADO": "#1a7f37",
    "EXECUTANDO": "#0969da",
    "AGENDADO": "#9a6700",
    "PENDENTE_APROVACAO": "#bc4c00",
    "SUSPENSO": "#8b949e",
    "FALHA": "#cf222e",
}

EST_LABEL = {
    "SUCESSO": {"bg": "#dafbe1", "fg": "#1a7f37"},
    "ARQUIVADO": {"bg": "#dafbe1", "fg": "#1a7f37"},
    "EXECUTANDO": {"bg": "#ddf4ff", "fg": "#0969da"},
    "AGENDADO": {"bg": "#fff8c5", "fg": "#9a6700"},
    "PENDENTE_APROVACAO": {"bg": "#fff1e5", "fg": "#bc4c00"},
    "SUSPENSO": {"bg": "#eaeef2", "fg": "#57606a"},
    "FALHA": {"bg": "#ffebe9", "fg": "#d1242f"},
}

PESOS = {
    "SUCESSO": 100,
    "ARQUIVADO": 100,
    "EXECUTANDO": 50,
    "AGENDADO": 75,
    "PENDENTE_APROVACAO": 65,
    "SUSPENSO": 35,
    "FALHA": 0,
}

CAMPO_ARTEFATOS = {
    "builds": "ultimos_builds",
    "releases": "ultimos_releases",
    "execucoes": "ultimas_execucoes",
}
TITULO_ETAPA = {"builds": "Build", "releases": "Liberacao", "execucoes": "Execucao"}
COR_ETAPA = {"builds": "#3b82f6", "releases": "#8b5cf6", "execucoes": "#f59e0b"}
BONS = {
    "builds": ["SUCESSO"],
    "releases": ["AGENDADO", "ARQUIVADO", "PENDENTE_APROVACAO"],
    "execucoes": ["SUCESSO", "EXECUTANDO"],
}
RUINS = {
    "builds": ["FALHA"],
    "releases": ["FALHA", "SUSPENSO"],
    "execucoes": ["FALHA"],
}


@st.cache_data
def carregar(nome):
    with open(BASE / f"{nome}.json", encoding="utf-8") as f:
        return json.load(f)


BUILDS = carregar("informacoes-build")
RELEASES = carregar("informacoes-deploy")
EXECUCOES = carregar("informacoes-execucao")

DADOS = {"builds": BUILDS, "releases": RELEASES, "execucoes": EXECUCOES}


def esc(s):
    return html.escape(str(s))


def obter_job(cat, nome):
    return next((j for j in DADOS[cat] if j["nome"] == nome), None)


def artefatos(cat, nome):
    j = obter_job(cat, nome)
    return j.get(CAMPO_ARTEFATOS[cat], []) if j else []


def categorias(nome):
    return [c for c in ["builds", "releases", "execucoes"] if artefatos(c, nome)]


def saude_job(nome):
    soma = n = 0
    for c in categorias(nome):
        for a in artefatos(c, nome):
            soma += PESOS.get(a["status"], 50)
            n += 1
    return round(soma / n) if n else 0


def saude_geral():
    vals = [saude_job(j["nome"]) for j in BUILDS]
    return round(sum(vals) / len(vals)) if vals else 0


def estado_saude(v):
    if v >= 80:
        return {"rotulo": "SAUDAVEL", "cor": "#2da44e", "bg": "#dafbe1", "fg": "#1a7f37"}
    if v >= 55:
        return {"rotulo": "ATENCAO", "cor": "#bf8700", "bg": "#fff8c5", "fg": "#9a6700"}
    if v >= 30:
        return {"rotulo": "INSTAVEL", "cor": "#bc4c00", "bg": "#fff1e5", "fg": "#bc4c00"}
    return {"rotulo": "CRITICO", "cor": "#cf222e", "bg": "#ffebe9", "fg": "#cf222e"}


def resumo_etapa(cat, nome):
    arts = artefatos(cat, nome)
    bons = sum(1 for a in arts if a["status"] in BONS[cat])
    ruins = sum(1 for a in arts if a["status"] in RUINS[cat])
    total = len(arts)
    return {
        "total": total,
        "bons": bons,
        "ruins": ruins,
        "outros": total - bons - ruins,
        "taxa": round(bons / total * 100) if total else 0,
    }


def resumo_geral_etapa(cat):
    rs = [resumo_etapa(cat, j["nome"]) for j in BUILDS]
    total = sum(r["total"] for r in rs)
    bons = sum(r["bons"] for r in rs)
    ruins = sum(r["ruins"] for r in rs)
    return {
        "total": total,
        "bons": bons,
        "ruins": ruins,
        "outros": total - bons - ruins,
        "taxa": round(bons / total * 100) if total else 0,
    }


def pct_agendado(nome):
    arts = artefatos("releases", nome)
    total = len(arts)
    agend = sum(1 for a in arts if a["status"] == "AGENDADO")
    return round(agend / total * 100) if total else 0


def pct_agendado_geral():
    total = sum(len(artefatos("releases", j["nome"])) for j in BUILDS)
    agend = sum(
        1 for j in BUILDS for a in artefatos("releases", j["nome"]) if a["status"] == "AGENDADO"
    )
    return round(agend / total * 100) if total else 0


def fmt_data(iso):
    if not iso:
        return "-"
    d = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(datetime.timezone.utc)
    return d.strftime("%d/%m %H:%M")


def badge(status):
    l = EST_LABEL.get(status, {"bg": "#eaeef2", "fg": "#57606a"})
    return (
        f'<span class="badge" style="background:{l["bg"]};color:{l["fg"]}">'
        f'{esc(status)}</span>'
    )


def label_saude(saude):
    est = estado_saude(saude)
    return (
        f'<span class="badge" style="background:{est["bg"]};color:{est["fg"]}">'
        f'{est["rotulo"]} {saude}%</span>'
    )


def gauge_html(saude):
    est = estado_saude(saude)
    return (
        f'<div class="gauge" style="background:conic-gradient({est["cor"]} 0 {saude}%, #eaeef2 {saude}% 100%)">'
        f'<span style="color:{est["cor"]}">{saude}</span></div>'
    )


def pizza_html(ok, falha, tam=62):
    total = ok + falha
    if total == 0:
        return (
            f'<div class="pizza" style="width:{tam}px;height:{tam}px;background:#eaeef2">'
            '<span style="color:#57606a">0%</span></div>'
        )
    ok_pct = round(ok / total * 100)
    return (
        f'<div class="pizza" style="width:{tam}px;height:{tam}px;'
        f'background:conic-gradient(#2da44e 0 {ok_pct}%, #cf222e {ok_pct}% 100%)">'
        f'<span style="color:#fff">{ok_pct}%</span></div>'
    )


def matrix_html():
    etaps = ["builds", "releases", "execucoes"]
    partes = ['<div class="pgrade cabecalho">']
    partes.append('<div class="cel-nome">Job</div>')
    for c in etaps:
        rg = resumo_geral_etapa(c)
        partes.append(
            f'<div class="cel-etapa">{TITULO_ETAPA[c]}'
            f'<small>{rg["total"]} no total</small></div>'
        )
    partes.append("</div>")

    for j in BUILDS:
        nome = j["nome"]
        saude = saude_job(nome)
        est = estado_saude(saude)
        partes.append('<div class="pgrade">')
        partes.append(
            f'<div class="cel-nome"><b>{esc(nome)}</b>'
            f'<span class="badge" style="background:{est["bg"]};color:{est["fg"]}">'
            f'{est["rotulo"]} {saude}%</span></div>'
        )
        for c in etaps:
            r = resumo_etapa(c, nome)
            if r["total"] == 0:
                cor = "#afb8c1"
            elif r["taxa"] >= 80:
                cor = "#2da44e"
            elif r["taxa"] >= 55:
                cor = "#bf8700"
            else:
                cor = "#cf222e"
            if c == "releases":
                pct_txt = f"{pct_agendado(nome)}% agendadas"
            else:
                pct_txt = f"{r['taxa']}% de sucesso"
            partes.append(
                f'<div class="cel-dados">{lista_artefatos_html(c, nome)}'
                f'<div class="bloco" style="background:{cor}">'
                f'<b>{r["total"]}</b>'
                f"<small>{pct_txt}</small></div></div>"
            )
        partes.append("</div>")
    return "".join(partes)


def cartao_html(titulo, valor, det, cor):
    return (
        f'<div class="cartao" style="border-top:4px solid {cor}">'
        f'<div class="ctit">{titulo}</div>'
        f'<div class="cnum">{valor}</div>'
        f'<div class="cdet">{det}</div></div>'
    )


def lista_artefatos_html(cat, nome):
    arts = artefatos(cat, nome)
    titulo = {"builds": "Builds", "releases": "Releases", "execucoes": "Execuções"}[cat]
    itens = "".join(
        f'<div class="tip-item"><span style="color:{COR_STATUS.get(a["status"], "#8b949e")}">&#9679;</span> '
        f'#{a.get("id_build", a.get("id_release", a.get("id_execucao")))} &middot; {esc(a["versao"])} '
        f'&middot; {esc(a["status"])}</div>'
        for a in arts
    )
    return f'<div class="tip"><div class="tip-tit">{titulo} ({len(arts)})</div>{itens}</div>'


def fluxo_html(rel, b, exs):
    ok = sum(1 for e in exs if e["status"] == "SUCESSO")
    falha = sum(1 for e in exs if e["status"] == "FALHA")
    versao = b["versao"] if b else rel["versao"]
    id_build = f"#{b['id_build']}" if b else "-"
    status_build = badge(b["status"]) if b else ""
    fim_build = fmt_data(b["data_fim"]) if b else "-"
    return (
        f'<div class="fluxo">'
        f'<div class="no" style="--ncor:{COR_ETAPA["builds"]}">'
        f'<div class="no-cab">Build</div>'
        f'<div class="versao">{esc(versao)}</div>'
        f'<div class="det">{id_build} {status_build}</div>'
        f'<div class="data">fim {fim_build}</div></div>'
        f'<div class="seta">&#10148;</div>'
        f'<div class="no" style="--ncor:{COR_ETAPA["releases"]}">'
        f'<div class="no-cab">Release</div>'
        f'<div class="versao">{esc(rel["versao"])}</div>'
        f'<div class="det">#{rel["id_release"]} {badge(rel["status"])}</div>'
        f'<div class="data">aprovacao {fmt_data(rel["data_aprovacao"])}</div></div>'
        f'<div class="seta">&#10148;</div>'
        f'<div class="no" style="--ncor:{COR_ETAPA["execucoes"]}">'
        f'<div class="no-cab">Execucoes ({len(exs)})</div>'
        f'<div class="no-corpo">{pizza_html(ok, falha)}'
        f'<div class="legenda-pizza"><b class="ok">{ok} sucesso</b>'
        f'<br><b class="ruim">{falha} falha</b></div></div></div>'
        f"</div>"
    )


CSS = """
<style>
.pgrade {
    display: grid;
    grid-template-columns: 1.4fr repeat(3, 1fr);
    align-items: stretch;
    border: 1px solid #d0d7de;
    border-top: none;
}
.pgrade.cabecalho { border-top: 1px solid #d0d7de; background: #f6f8fa; }
.pgrade > div { padding: 8px 12px; border-right: 1px solid #d0d7de; }
.pgrade > div:last-child { border-right: none; }
.cel-dados { position: relative; }
.tip {
    display: none;
    position: absolute;
    bottom: calc(100% + 8px);
    left: 50%;
    transform: translateX(-50%);
    z-index: 100;
    min-width: 230px;
    max-width: 360px;
    max-height: 280px;
    overflow-y: auto;
    background: #24292f;
    color: #f6f8fa;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 12px;
    line-height: 1.6;
    box-shadow: 0 8px 24px rgba(66, 74, 83, 0.35);
    text-align: left;
}
.tip-tit { font-weight: 700; border-bottom: 1px solid rgba(246, 248, 250, 0.25); padding-bottom: 6px; margin-bottom: 6px; }
.tip-item { white-space: nowrap; }
.cel-dados:hover .tip { display: block; }
.cel-nome { display: flex; flex-direction: column; gap: 4px; justify-content: center; }
.cel-nome b { font-size: 14px; }
.cel-etapa { font-weight: 600; font-size: 13px; color: #24292f; display: flex; flex-direction: column; gap: 2px; }
.cel-etapa small, .bloco small { color: rgba(255,255,255,0.92); font-weight: 400; }
.bloco {
    border-radius: 6px; color: #fff; padding: 6px 10px;
    display: flex; flex-direction: column; gap: 1px; min-height: 46px; justify-content: center;
}
.bloco b { font-size: 17px; line-height: 1.1; }
.badge {
    display: inline-block; padding: 0 8px; font-size: 11px; font-weight: 600;
    line-height: 20px; border-radius: 999px; width: max-content;
}
.gauge {
    width: 64px; height: 64px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; flex: 0 0 auto;
}
.gauge span {
    width: 46px; height: 46px; border-radius: 50%; background: #fff;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 16px;
}
.pizza {
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center; flex: 0 0 auto;
}
.pizza span { font-size: 12px; font-weight: 700; text-shadow: 0 1px 2px rgba(0,0,0,0.35); }
.cartao {
    background: #fff; border: 1px solid #d0d7de; border-radius: 8px;
    padding: 12px 14px; display: flex; flex-direction: column; gap: 2px;
    height: 100%;
}
.ctit { font-size: 12px; font-weight: 600; color: #57606a; text-transform: uppercase; letter-spacing: .3px; }
.cnum { font-size: 26px; font-weight: 700; color: #24292f; line-height: 1.1; }
.cdet { font-size: 12px; color: #57606a; }
.fluxo {
    display: grid; grid-template-columns: 1fr auto 1fr auto 1.3fr; gap: 10px;
    align-items: stretch; padding: 10px; border: 1px solid #d0d7de; border-radius: 8px;
    background: #fff; margin-bottom: 8px;
}
.no {
    border: 1px solid #d0d7de; border-top: 3px solid var(--ncor);
    border-radius: 6px; padding: 8px 10px; display: flex; flex-direction: column; gap: 2px;
    min-width: 0;
}
.no-cab { font-size: 11px; font-weight: 700; color: #57606a; text-transform: uppercase; letter-spacing: .3px; }
.versao { font-size: 14px; font-weight: 600; color: #24292f; }
.det { font-size: 12px; color: #57606a; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.data { font-size: 11px; color: #8b949e; }
.seta { display: flex; align-items: center; color: #8b949e; font-size: 18px; }
.no-corpo { display: flex; align-items: center; gap: 14px; }
.legenda-pizza { font-size: 12px; color: #57606a; }
.ok { color: #1a7f37; }
.ruim { color: #cf222e; }
.sem-dados { color: #57606a; font-style: italic; padding: 12px 0; }
</style>
"""

st.set_page_config(page_title="Esteira ", page_icon="\u2b26", layout="wide")

st.markdown(CSS, unsafe_allow_html=True)

col_titulo, col_metricas = st.columns([3, 2], vertical_alignment="center")
with col_titulo:
    st.caption("Release de software e dados &middot; últimos 7 dias")
with col_metricas:
    r_b = resumo_geral_etapa("builds")
    r_r = resumo_geral_etapa("releases")
    r_e = resumo_geral_etapa("execucoes")
    m1, m2, m3 = st.columns(3)
    m1.metric("Builds", r_b["total"], f"{r_b['taxa']}% sucesso")
    m2.metric("Releases", r_r["total"], f"{pct_agendado_geral()}% agendadas")
    m3.metric("Execuções", r_e["total"], f"{r_e['taxa']}% sucesso")

st.subheader("Pipeline Global")
st.markdown(
    '<div style="font-size:13px;color:#57606a;margin-bottom:8px">'
    'Jobs × etapas. Passe o mouse sobre um card para listar os itens; selecione o job abaixo para ver o caminho dos dados (build → release → execuções).</div>',
    unsafe_allow_html=True,
)
st.markdown(matrix_html(), unsafe_allow_html=True)

st.caption(
    "\u25cf Saudável (\u226580% de sucesso)   \u25cf Atenção (55-79%)   "
    "\u25cf Crítico (<55%)   · releases: % de agendadas   · passe o mouse sobre um card para listar os itens."
)

st.divider()

nome = st.selectbox("Job", [j["nome"] for j in BUILDS])

st.subheader("Caminho dos Dados")
st.caption("Para cada versão fechada com sucesso (build → release), as execuções relacionadas com percentual de sucessos e falhas.")

cols = st.columns(3)
rb = resumo_etapa("builds", nome)
re = resumo_etapa("execucoes", nome)
rels = artefatos("releases", nome)
fechadas = [r for r in rels if r["status"] in ("AGENDADO", "ARQUIVADO")]

with cols[0]:
    st.markdown(cartao_html("Builds", rb["total"], f'{rb["taxa"]}% de sucesso', COR_ETAPA["builds"]), unsafe_allow_html=True)
with cols[1]:
    st.markdown(cartao_html("Releases fechadas", len(fechadas), f"de {len(rels)} releases &middot; versões com execução", COR_ETAPA["releases"]), unsafe_allow_html=True)
with cols[2]:
    st.markdown(
        f'<div class="cartao" style="border-top:4px solid {COR_ETAPA["execucoes"]}">'
        f'<div class="ctit">Execuções</div>'
        f'<div class="cnum" style="display:flex;align-items:center;gap:10px">{re["total"]}'
        f'{pizza_html(re["bons"], re["ruins"], tam=34)}</div>'
        f'<div class="cdet">{re["taxa"]}% de sucesso &middot; '
        f'<span class="ok">{re["bons"]} sucesso</span> &middot; '
        f'<span class="ruim">{re["ruins"]} falha</span></div></div>',
        unsafe_allow_html=True,
    )

st.markdown("#### Versões fechadas")
builds_map = {b["id_build"]: b for b in artefatos("builds", nome)}
execs = artefatos("execucoes", nome)

if fechadas:
    fluxos = "".join(
        fluxo_html(rel, builds_map.get(rel["id_build"]), [e for e in execs if e["id_release"] == rel["id_release"]])
        for rel in fechadas
    )
    st.markdown(fluxos, unsafe_allow_html=True)
else:
    st.markdown('<div class="sem-dados">Nenhuma versão fechada encontrada para este job.</div>', unsafe_allow_html=True)