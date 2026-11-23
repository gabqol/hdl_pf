"""Dados, modelos e servicos do Hora do Lixo.

Baseado na especificacao APP.MD (app.md).
"""

import json
import os
import random
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional

# Diretório de dados - compatível com Desktop e Android
def _get_data_dir():
    """Retorna diretório gravável para dados persistentes"""
    # Tenta variáveis de ambiente do Flet/Android
    for env_var in ["FLET_APP_STORAGE_DATA", "ANDROID_APP_DATA", "APPDATA", "HOME"]:
        val = os.environ.get(env_var)
        if val:
            test_dir = os.path.join(val, ".horadolixo")
            try:
                os.makedirs(test_dir, exist_ok=True)
                test_file = os.path.join(test_dir, ".write_test")
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
                return test_dir
            except Exception:
                pass
    # Fallback: diretório atual
    fallback = os.path.join(os.getcwd(), ".horadolixo_data")
    os.makedirs(fallback, exist_ok=True)
    return fallback

DATA_DIR = _get_data_dir()
DATA_FILE = os.path.join(DATA_DIR, "dados.json")

DIAS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
DIAS_FULL = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

PALETA = {
    "bg_primary": "#0D1A14",
    "bg_card": "#1A2D22",
    "accent_green": "#2E6B42",
    "accent_lime": "#5CDB6F",
    "accent_orange": "#E8812A",
    "accent_red": "#C94040",
    "text_primary": "#F0F4F1",
    "text_secondary": "#8FA898",
    "divider": "#243B2D",
    "bg_light": "#F5F7F5",
    "card_light": "#FFFFFF",
    "text_light": "#14201A",
    "text_light_2": "#5A6B60",
}

RUAS = [
    "Rua das Orquídeas", "Rua das Bromélias", "Rua das Hortênsias",
    "Rua das Flores", "Rua dos Lírios", "Rua das Violetas",
    "Rua dos Jasmins", "Rua das Acácias", "Rua dos Ipês",
    "Avenida Djalma Batista", "Rua Cinco de Setembro", "Rua Joaquim Nabuco",
]

PONTOS_SELETIVOS = [
    {"id": 1, "nome": "Ecoponto Centro", "tipo": "reciclavel", "lat": -3.1190, "lon": -60.0217, "bairro": "Centro", "dist": "0,4 km"},
    {"id": 2, "nome": "Ecoponto Vila Betânia", "tipo": "reciclavel", "lat": -3.1389, "lon": -60.0217, "bairro": "Vila Betânia", "dist": "0,8 km"},
    {"id": 3, "nome": "Ponto de Compostagem Educandos", "tipo": "organico", "lat": -3.1456, "lon": -60.0123, "bairro": "Educandos", "dist": "1,2 km"},
    {"id": 4, "nome": "Ecoponto Parque 10", "tipo": "reciclavel", "lat": -3.0925, "lon": -60.0289, "bairro": "Parque 10", "dist": "1,6 km"},
    {"id": 5, "nome": "Área de Recebimento Volumosos", "tipo": "volumoso", "lat": -3.0878, "lon": -60.0156, "bairro": "Adrianópolis", "dist": "2,1 km"},
    {"id": 6, "nome": "Ecoponto Cidade Nova", "tipo": "organico", "lat": -2.9987, "lon": -60.0134, "bairro": "Cidade Nova", "dist": "2,9 km"},
]

BAIRROS = [
    {"id": 1, "nome": "Vila Betânia", "zona": "Zona Sul", "lat": -3.1389, "lon": -60.0217, "coleta_dias": [1, 3, 5]},
    {"id": 2, "nome": "Adrianópolis", "zona": "Zona Centro-Sul", "lat": -3.0878, "lon": -60.0156, "coleta_dias": [0, 2, 4]},
    {"id": 3, "nome": "Parque 10", "zona": "Zona Centro-Sul", "lat": -3.0925, "lon": -60.0289, "coleta_dias": [1, 3, 5]},
    {"id": 4, "nome": "Cidade Nova", "zona": "Zona Norte", "lat": -2.9987, "lon": -60.0134, "coleta_dias": [0, 2, 4]},
    {"id": 5, "nome": "Educandos", "zona": "Zona Sul", "lat": -3.1456, "lon": -60.0123, "coleta_dias": [1, 3, 5]},
    {"id": 6, "nome": "Aleixo", "zona": "Zona Centro-Sul", "lat": -3.0956, "lon": -60.0112, "coleta_dias": [0, 2, 4]},
    {"id": 7, "nome": "Flores", "zona": "Zona Centro-Sul", "lat": -3.0898, "lon": -60.0178, "coleta_dias": [1, 3, 5]},
    {"id": 8, "nome": "Centro", "zona": "Zona Sul", "lat": -3.1190, "lon": -60.0217, "coleta_dias": [0, 2, 4, 6]},
    {"id": 9, "nome": "Alvorada", "zona": "Zona Centro-Oeste", "lat": -3.0678, "lon": -60.0334, "coleta_dias": [1, 3, 5]},
    {"id": 10, "nome": "Dom Pedro", "zona": "Zona Centro-Oeste", "lat": -3.0723, "lon": -60.0389, "coleta_dias": [0, 2, 4]},
]

CAUSAS_ATRASO = [
    "Trânsito na Av. Djalma Batista",
    "Manutenção mecânica do veículo",
    "Chuva forte na região",
    "Bloqueio por obras na via",
    "Acúmulo de material acima da capacidade",
]


@dataclass
class ColetaEvento:
    id: int
    tipo: str
    horario: str
    dia_semana: int
    bairro_id: int
    status: str = "pendente"
    rua_atual: str = ""
    progresso: float = 0.0
    data_iso: str = ""
    causa: str = ""
    ruas_restantes: int = 0

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d):
        known = {f for f in ColetaEvento.__dataclass_fields__}
        return ColetaEvento(**{k: v for k, v in d.items() if k in known})


@dataclass
class Notificacao:
    id: int
    titulo: str
    mensagem: str
    horario: str
    tipo: str
    lida: bool = False
    bairro: str = ""
    coleta: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class Ocorrencia:
    id: int
    tipo: str
    endereco: str
    bairro: str
    rua: str = ""
    descricao: str = ""
    foto: str = ""
    status: str = "pendente"
    protocolo: str = ""
    horario: str = ""
    lat: float = 0.0
    lon: float = 0.0

    def to_dict(self):
        return asdict(self)


@dataclass
class Solicitacao:
    id: int
    tipo_item: str
    endereco: str
    bairro: str
    data_preferida: str = ""
    quantidade: str = ""
    observacoes: str = ""
    status: str = "solicitada"
    protocolo: str = ""
    criado_em: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class ColetaHistorico:
    id: int
    data: str
    tipo: str
    bairro: str
    status: str
    causa: str = ""
    coletada: bool = False

    def to_dict(self):
        return asdict(self)


def bairro_lon(bairro):
    return bairro.get("lon", 0.0)


class AppState:
    """Estado global reativo com persistencia em disco."""

    def __init__(self):
        self._listeners: List[Callable] = []
        self.bairro_id = 1
        self.rua = RUAS[3]
        self.nome_usuario = ""
        self.onboarding_feito = False
        self.dark_mode = True
        self.alerta_15min = True
        self.notif_prefs = {
            "route_start": True,
            "delay": False,
            "night_reminder": True,
        }
        self.coletas: List[ColetaEvento] = []
        self.notificacoes: List[Notificacao] = []
        self.ocorrencias: List[Ocorrencia] = []
        self.solicitacoes: List[Solicitacao] = []
        self.historico: List[ColetaHistorico] = []
        self.caminhao = {}
        self.carregado = False
        self._carregar()
        if not self.carregado or not self.notificacoes or not self.historico or not self.ocorrencias:
            self._semear()
        self.refresh_all()

    def _semear(self):
        self.notificacoes = [
            Notificacao(1, "Caminhão a 30 min", "Coleta comum · sua rua em ≈30 min", "Hoje 07:30", "truck", bairro="Vila Betânia", coleta="comum"),
            Notificacao(2, "Coleta concluída", "Reciclável coletado com sucesso", "Ontem 08:30", "success", bairro="Vila Betânia", coleta="reciclavel"),
            Notificacao(3, "Coleta atrasou 25 min", "Trânsito na Av. Djalma Batista", "Seg 08:20", "warning", bairro="Vila Betânia", coleta="comum"),
            Notificacao(4, "Rota iniciada", "Caminhão saiu da garagem às 07:00", "Hoje 07:00", "info", bairro="Vila Betânia", coleta="comum"),
            Notificacao(5, "Lembrete: separar reciclável", "Coleta de reciclável amanhã às 07:00", "Ontem 19:00", "info", bairro="Vila Betânia", coleta="reciclavel"),
        ]
        self.historico = [
            ColetaHistorico(1, "Hoje", "comum", "Vila Betânia", "em_rota"),
            ColetaHistorico(2, "Ontem", "reciclavel", "Vila Betânia", "concluida"),
            ColetaHistorico(3, "Seg 08:20", "comum", "Vila Betânia", "atrasada", causa="Trânsito na Av. Djalma Batista"),
            ColetaHistorico(4, "Sex", "reciclavel", "Vila Betânia", "concluida"),
            ColetaHistorico(5, "Qui", "comum", "Vila Betânia", "cancelada", causa="Chuva forte na região"),
        ]
        self.ocorrencias = [
            Ocorrencia(1, "lixo_acumulado", "Rua 15, 245", "Vila Betânia", rua="Rua das Flores", descricao="Entulho accumulate na esquina", status="em_analise", protocolo="#2841", horario="Hoje 06:30", lat=-3.1389, lon=-60.0217),
            Ocorrencia(2, "descarte_irregular", "Av. Getúlio Vargas, 1200", "Centro", rua="Av. Getúlio Vargas", descricao="Descarte irregular de entulho", status="pendente", protocolo="#2836", horario="Ontem 14:20", lat=-3.1190, lon=-60.0217),
            Ocorrencia(3, "ponto_vistoriado", "Rua das Flores, s/n", "Adrianópolis", rua="Rua das Flores", descricao="Ponto de descarte clandestino", status="em_analise", protocolo="#2819", horario="Seg 09:10", lat=-3.0878, lon=-60.0156),
        ]
        self.solicitacoes = [
            Solicitacao(1, "movel", "Rua 15, 245 - Vila Betânia", "Vila Betânia", data_preferida="2026-11-25", quantidade="1 sofá", observacoes="Deixar na calçada", status="agendada", protocolo="#V1042", criado_em="Ontem 14:20"),
        ]

    def _carregar(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            return
        self.bairro_id = d.get("bairro_id", 1)
        self.rua = d.get("rua", RUAS[3])
        self.nome_usuario = d.get("nome_usuario", "")
        self.onboarding_feito = d.get("onboarding_feito", False)
        self.dark_mode = d.get("dark_mode", True)
        self.alerta_15min = d.get("alerta_15min", True)
        self.notif_prefs = d.get("notif_prefs", self.notif_prefs)
        self.notificacoes = [Notificacao(**n) for n in d.get("notificacoes", [])]
        self.ocorrencias = [Ocorrencia(**o) for o in d.get("ocorrencias", [])]
        self.solicitacoes = [Solicitacao(**s) for s in d.get("solicitacoes", [])]
        self.historico = [ColetaHistorico(**h) for h in d.get("historico", [])]
        self.carregado = True

    def _salvar(self):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "bairro_id": self.bairro_id,
                    "rua": self.rua,
                    "nome_usuario": self.nome_usuario,
                    "onboarding_feito": self.onboarding_feito,
                    "dark_mode": self.dark_mode,
                    "alerta_15min": self.alerta_15min,
                    "notif_prefs": self.notif_prefs,
                    "notificacoes": [n.to_dict() for n in self.notificacoes],
                    "ocorrencias": [o.to_dict() for o in self.ocorrencias],
                    "solicitacoes": [x.to_dict() for x in self.solicitacoes],
                    "historico": [h.to_dict() for h in self.historico],
                }, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        self._notify()

    def refresh_all(self):
        self.coletas = self._gerar_coletas()
        self.caminhao = self._gerar_caminhao()
        self._notify()

    def _gerar_coletas(self) -> List[ColetaEvento]:
        hoje = datetime.now().weekday()
        bairro = self.get_bairro()
        saida = self._horario_saida()
        chegada = self._horario_chegada()
        eventos = []
        for i in range(14):
            dia = (hoje + i) % 7
            data = datetime.now() + timedelta(days=i)
            if dia not in bairro["coleta_dias"]:
                eventos.append(ColetaEvento(i + 1, "sem_coleta", "--:--", dia, self.bairro_id, "sem_coleta", data_iso=data.strftime("%Y-%m-%d")))
                continue
            tipo = "reciclavel" if dia % 2 == 0 else "comum"
            horario = "07:30" if tipo == "reciclavel" else "08:00"
            status = "pendente"
            rua_atual = ""
            progresso = 0.0
            causa = ""
            if i == 0:
                agora = datetime.now()
                hc = datetime.strptime(horario, "%H:%M").replace(year=agora.year, month=agora.month, day=agora.day)
                if agora >= hc:
                    status = "concluido"
                    progresso = 1.0
                elif agora >= hc - timedelta(minutes=60):
                    status = "em_rota"
                    progresso = min(0.92, (hc - agora).total_seconds() / -3600)
                    rua_atual = self._rua_atual(progresso)
                elif agora >= saida:
                    status = "em_rota"
                    progresso = 0.05
                    rua_atual = self._rua_atual(0.05)
            if status == "pendente" and i > 0 and random.random() < 0.12:
                causa = random.choice(CAUSAS_ATRASO)
            eventos.append(ColetaEvento(
                i + 1, tipo, horario, dia, self.bairro_id, status, rua_atual,
                progresso, data.strftime("%Y-%m-%d"), causa,
                max(0, int((1 - progresso) * 8)) if status == "em_rota" else 0))
        return eventos

    def _horario_saida(self):
        agora = datetime.now()
        return agora.replace(hour=7, minute=0, second=0, microsecond=0)

    def _horario_chegada(self):
        agora = datetime.now()
        return agora.replace(hour=8, minute=0, second=0, microsecond=0)

    def _rua_atual(self, progresso: float):
        ordem = RUAS[:8]
        idx = min(len(ordem) - 1, int(progresso * len(ordem)))
        return ordem[idx]

    def _gerar_caminhao(self) -> dict:
        agora = datetime.now()
        saida = self._horario_saida()
        chegada = self._horario_chegada()
        rotas = self.get_coleta_hoje()
        if rotas is None or rotas.status == "sem_coleta":
            return {"status": "sem_coleta", "progresso": 0.0, "msg": "Sem coleta hoje", "eta": "--", "rua_atual": "", "proxima": "", "saida": "07:00", "atraso": 0, "ruas_restantes": 0}
        if agora < saida:
            return {"status": "aguardando", "progresso": 0.0, "msg": "Saindo da garagem às 07:00", "eta": "≈ 60 min", "rua_atual": "", "proxima": RUAS[0], "saida": "07:00", "atraso": 0, "ruas_restantes": 8}
        if agora >= chegada:
            return {"status": "concluido", "progresso": 1.0, "msg": "Coleta finalizada na sua rua", "eta": "Concluído", "rua_atual": self.rua, "proxima": "", "saida": "07:00", "atraso": 0, "ruas_restantes": 0}
        p = max(0.05, min(0.95, (agora - saida).total_seconds() / (chegada - saida).total_seconds()))
        eta_min = int((1 - p) * 60)
        atraso = 0
        if eta_min > 20 and random.random() < 0.3:
            atraso = random.choice([21, 25, 32, 40])
        return {
            "status": "em_rota",
            "progresso": p,
            "msg": f"Faltam {max(1, int((1-p)*8))} ruas",
            "eta": f"≈ {eta_min} min",
            "rua_atual": self._rua_atual(p),
            "proxima": self.rua,
            "saida": "07:00",
            "atraso": atraso,
            "ruas_restantes": max(1, int((1 - p) * 8)),
        }

    def get_bairro(self):
        return next((b for b in BAIRROS if b["id"] == self.bairro_id), BAIRROS[0])

    def get_coleta_hoje(self):
        hoje = datetime.now().weekday()
        return next((c for c in self.coletas if c.dia_semana == hoje), None)

    def proxima_coleta(self):
        for c in self.coletas:
            if c.status in ("pendente", "em_rota"):
                return c
        return self.coletas[0] if self.coletas else None

    def set_bairro(self, bid: int):
        self.bairro_id = bid
        self.refresh_all()
        self._salvar()

    def set_rua(self, rua: str):
        self.rua = rua
        self._salvar()

    def set_nome(self, nome: str):
        self.nome_usuario = nome
        self._salvar()

    def concluir_onboarding(self):
        self.onboarding_feito = True
        self._salvar()

    def toggle_notif(self, key: str, val: bool):
        self.notif_prefs[key] = val
        self._salvar()

    def toggle_alerta_15min(self, val: bool):
        self.alerta_15min = val
        self._salvar()

    def toggle_dark(self, val: bool):
        self.dark_mode = val
        self._salvar()

    def add_ocorrencia(self, tipo: str, endereco: str, rua: str = "", descricao: str = "", foto: str = "") -> Ocorrencia:
        bairro = self.get_bairro()
        protocolo = f"#{random.randint(2800, 2999)}"
        oc = Ocorrencia(
            id=len(self.ocorrencias) + 1,
            tipo=tipo,
            endereco=endereco,
            bairro=bairro["nome"],
            rua=rua or self.rua,
            descricao=descricao,
            foto=foto,
            status="pendente",
            protocolo=protocolo,
            horario=datetime.now().strftime("%d/%m %H:%M"),
            lat=bairro["lat"],
            lon=bairro_lon(bairro),
        )
        self.ocorrencias.insert(0, oc)
        self._salvar()
        return oc

    def add_solicitacao(self, tipo_item: str, data_preferida: str, quantidade: str, observacoes: str = "") -> Solicitacao:
        bairro = self.get_bairro()
        sol = Solicitacao(
            id=len(self.solicitacoes) + 1,
            tipo_item=tipo_item,
            endereco=f"{self.rua} - {bairro['nome']}",
            bairro=bairro["nome"],
            data_preferida=data_preferida,
            quantidade=quantidade,
            observacoes=observacoes,
            status="solicitada",
            protocolo=f"#V{random.randint(1000, 1999)}",
            criado_em=datetime.now().strftime("%d/%m %H:%M"),
        )
        self.solicitacoes.insert(0, sol)
        self._salvar()
        return sol

    def registrar_feedback(self, event_id: int, coletada: bool):
        for c in self.coletas:
            if c.id == event_id:
                c.status = "concluido" if coletada else "nao_coletada"
                break
        self.historico.insert(0, ColetaHistorico(
            id=len(self.historico) + 1,
            data="Agora",
            tipo="comum",
            bairro=self.get_bairro()["nome"],
            status="concluida" if coletada else "nao_coletada",
        ))
        self._salvar()

    def subscribe(self, fn: Callable):
        if fn not in self._listeners:
            self._listeners.append(fn)

    def unsubscribe(self, fn: Callable):
        if fn in self._listeners:
            self._listeners.remove(fn)

    def _notify(self):
        for fn in list(self._listeners):
            try:
                fn()
            except Exception:
                pass


def exportar_csv_ocorrencias(path: str = None) -> str:
    """Exporta as ocorrencias registradas em CSV (prototipo, sem integracao SEMULSP)."""
    import csv
    path = path or os.path.join(DATA_DIR, "ocorrencias.csv")
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["protocolo", "tipo", "endereco", "rua", "bairro", "descricao", "status", "horario"])
            for oc in AppState().ocorrencias:
                w.writerow([oc.protocolo, oc.tipo, oc.endereco, oc.rua, oc.bairro, oc.descricao, oc.status, oc.horario])
        return path
    except Exception:
        return ""


def pontos_por_bairro(bairro_id: int):
    bairro = next((b for b in BAIRROS if b["id"] == bairro_id), BAIRROS[0])
    pontos = [dict(p) for p in PONTOS_SELETIVOS]
    for p in pontos:
        p["dist"] = f"{abs(p['lat'] - bairro['lat']) * 111:.1f} km"
    return pontos


def determinar_tipo_coleta(dia_semana: int, bairro_id: int) -> str:
    bairro = next((b for b in BAIRROS if b["id"] == bairro_id), BAIRROS[0])
    if dia_semana not in bairro["coleta_dias"]:
        return "sem_coleta"
    return "reciclavel" if dia_semana % 2 == 0 else "comum"
