"use strict";

const COR_STATUS = {
  SUCESSO: "#27ae60",
  ARQUIVADO: "#1abc9c",
  EXECUTANDO: "#3498db",
  AGENDADO: "#8e44ad",
  PENDENTE_APROVACAO: "#f39c12",
  SUSPENSO: "#7f8c8d",
  FALHA: "#e74c3c"
};

const PESOS = {
  SUCESSO: 100,
  ARQUIVADO: 100,
  EXECUTANDO: 50,
  AGENDADO: 75,
  PENDENTE_APROVACAO: 65,
  SUSPENSO: 35,
  FALHA: 0
};

const CAMPO_ARTEFATOS = {
  builds: "ultimos_builds",
  releases: "ultimos_releases",
  execucoes: "ultimas_execucoes"
};

function obterJob(categoria, nome) {
  return (DADOS[categoria] || []).find(function (j) { return j.nome === nome; });
}

function artefatosDe(categoria, nome) {
  var job = obterJob(categoria, nome);
  return job ? (job[CAMPO_ARTEFATOS[categoria]] || []) : [];
}

function categoriasJob(nome) {
  return ["builds", "releases", "execucoes"].filter(function (c) {
    return artefatosDe(c, nome).length > 0;
  });
}

function contarArtefatos(nome) {
  var total = 0;
  categoriasJob(nome).forEach(function (c) {
    total += artefatosDe(c, nome).length;
  });
  return total;
}

function saudeJob(nome) {
  var soma = 0, n = 0;
  categoriasJob(nome).forEach(function (c) {
    artefatosDe(c, nome).forEach(function (a) {
      soma += (PESOS[a.status] !== undefined ? PESOS[a.status] : 50);
      n++;
    });
  });
  return n ? Math.round(soma / n) : 0;
}

function saudeGeral() {
  var nomes = (DADOS.builds || []).map(function (j) { return j.nome; });
  var s = 0;
  nomes.forEach(function (n) { s += saudeJob(n); });
  return nomes.length ? Math.round(s / nomes.length) : 0;
}

function estadoSaude(v) {
  if (v >= 80) return { rotulo: "SAUDAVEL", cor: "#27ae60" };
  if (v >= 55) return { rotulo: "ATENCAO", cor: "#f1c40f" };
  if (v >= 30) return { rotulo: "INSTAVEL", cor: "#e67e22" };
  return { rotulo: "CRITICO", cor: "#e74c3c" };
}

function corPorSaude(v) {
  return estadoSaude(v).cor;
}

function sombrear(hex, amt) {
  var n = parseInt(hex.slice(1), 16);
  var r = Math.min(255, Math.max(0, (n >> 16) + amt));
  var g = Math.min(255, Math.max(0, ((n >> 8) & 0xff) + amt));
  var b = Math.min(255, Math.max(0, (n & 0xff) + amt));
  return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

function esc(s) {
  return String(s).replace(/[&<>"']/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
  });
}

function fmtData(iso) {
  if (!iso) return "-";
  var d = new Date(iso);
  if (isNaN(d)) return iso;
  var p = function (n) { return String(n).padStart(2, "0"); };
  return p(d.getUTCDate()) + "/" + p(d.getUTCMonth() + 1) + " " + p(d.getUTCHours()) + ":" + p(d.getUTCMinutes());
}

function badge(status) {
  var cor = COR_STATUS[status] || "#95a5a6";
  return '<span class="badge" style="background:' + cor + '">' + esc(status) + "</span>";
}

/* ---------- etapas do processo ---------- */
const COR_ETAPA = { builds: "#3b82f6", releases: "#8b5cf6", execucoes: "#f59e0b" };
const TITULO_ETAPA = { builds: "Build", releases: "Liberacao", execucoes: "Execucao" };
const BONS = { builds: ["SUCESSO"], releases: ["AGENDADO", "ARQUIVADO", "PENDENTE_APROVACAO"], execucoes: ["SUCESSO", "EXECUTANDO"] };
const RUINS = { builds: ["FALHA"], releases: ["FALHA", "SUSPENSO"], execucoes: ["FALHA"] };

function resumoEtapa(cat, nome) {
  var arts = artefatosDe(cat, nome);
  var bons = 0, ruins = 0;
  arts.forEach(function (a) {
    if (BONS[cat].indexOf(a.status) >= 0) bons++;
    else if (RUINS[cat].indexOf(a.status) >= 0) ruins++;
  });
  var total = arts.length;
  return { total: total, bons: bons, ruins: ruins, outros: total - bons - ruins, taxa: total ? Math.round(bons / total * 100) : 0 };
}

function resumoGeralEtapa(cat) {
  var total = 0, bons = 0, ruins = 0;
  (DADOS.builds || []).forEach(function (j) {
    var r = resumoEtapa(cat, j.nome);
    total += r.total; bons += r.bons; ruins += r.ruins;
  });
  return { total: total, bons: bons, ruins: ruins, outros: total - bons - ruins, taxa: total ? Math.round(bons / total * 100) : 0 };
}

function barraPilula(bons, ruins, outros, total) {
  function fatia(n, cor) {
    return n > 0 ? "<i style='width:" + (n / total * 100) + "%;background:" + cor + "'></i>" : "";
  }
  return "<div class='barra mini'><span>" + fatia(bons, "#27ae60") + fatia(outros, "#7f8c8d") + fatia(ruins, "#e74c3c") + "</span></div>";
}

/* ---------- dica (tooltip) ---------- */
var dica = null;
function iniciarDica() {
  if (dica) return;
  dica = document.createElement("div");
  dica.className = "dica";
  document.body.appendChild(dica);
}
function mostrarDica(evt, html) {
  iniciarDica();
  dica.innerHTML = html;
  dica.style.left = Math.min(evt.clientX + 14, window.innerWidth - 280) + "px";
  dica.style.top = Math.min(evt.clientY + 14, window.innerHeight - 120) + "px";
  dica.classList.add("visivel");
}
function esconderDica() {
  if (dica) dica.classList.remove("visivel");
}

/* ---------- modal drill-down ---------- */
function abrirModal(nome) {
  var job = obterJob("builds", nome);
  if (!job) return;
  var saude = saudeJob(nome);
  var est = estadoSaude(saude);
  var total = contarArtefatos(nome);

  var linhas = "";
  categoriasJob(nome).forEach(function (c) {
    var cfg = c === "builds" ? ["id_build", "data_inicio", "data_fim"]
             : c === "releases" ? ["id_release", "data_aprovacao", null]
             : ["id_execucao", "data_inicio", "data_fim"];
    var titulo = c === "builds" ? "Builds" : c === "releases" ? "Releases" : "Execucoes";
    var arts = artefatosDe(c, nome);
    linhas += '<h3>' + titulo + ' (' + arts.length + ')</h3><table class="tabela"><thead><tr><th>ID</th><th>Status</th>';
    if (c === "releases") linhas += "<th>Aprovacao</th>";
    else { linhas += "<th>Inicio</th><th>Fim</th>"; }
    linhas += "</tr></thead><tbody>";
    arts.forEach(function (a) {
      linhas += "<tr><td>" + a[cfg[0]] + "</td><td>" + badge(a.status) + "</td>";
      if (c === "releases") linhas += "<td>" + fmtData(a.data_aprovacao) + "</td>";
      else linhas += "<td>" + fmtData(a.data_inicio) + "</td><td>" + fmtData(a.data_fim) + "</td>";
      linhas += "</tr>";
    });
    linhas += "</tbody></table>";
  });

  var bg = document.createElement("div");
  bg.className = "modal-bg";
  bg.innerHTML =
    '<div class="modal"><button class="fechar" aria-label="Fechar">&times;</button>' +
    "<h2>" + esc(nome) + ' <span class="badge" style="background:' + est.cor + '">' + est.rotulo + "</span></h2>" +
    '<div class="sub">id_job: ' + job.id_job + " &middot; artefatos: " + total + "</div>" +
    '<div class="modal-resumo">' +
      '<div class="gauge" style="--v:' + saude + ';--gcor:' + est.cor + '"><span>' + saude + "</span></div>" +
      '<div class="barra"><i style="width:' + saude + "%;background:" + est.cor + '"></i></div>' +
    "</div>" +
    linhas +
    "</div>";

  document.body.appendChild(bg);
  requestAnimationFrame(function () { bg.classList.add("aberto"); });
  bg.addEventListener("click", function (e) { if (e.target === bg || e.target.classList.contains("fechar")) { bg.classList.remove("aberto"); setTimeout(function () { bg.remove(); }, 250); } });
}

