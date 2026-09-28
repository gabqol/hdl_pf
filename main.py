#!/usr/bin/env python3
"""
Hora do Lixo - App Mobile iPhone 15 Pro Mockup (Flet 1.0)
Arquitetura reativa, abas funcionais, UX iFood-style
"""

import flet as ft
from datetime import datetime, timedelta
import asyncio
import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Callable
import random


# ===================== CONSTANTES & TEMA =====================

COLORS = {
    "primary": "#2E7D32",
    "primary_light": "#4CAF50",
    "primary_dark": "#1B5E20",
    "primary_container": "#E8F5E9",
    "secondary": "#FF6B35",
    "secondary_light": "#FF9800",
    "secondary_container": "#FFF3E0",
    "surface": "#FFFFFF",
    "surface_variant": "#F5F5F5",
    "background": "#FAFAFA",
    "on_surface": "#1A1A2E",
    "on_surface_variant": "#4A4A5A",
    "outline": "#E0E0E0",
    "outline_variant": "#F0F0F0",
    "success": "#2E7D32",
    "warning": "#FF8F00",
    "error": "#C62828",
    "info": "#1976D2",
    "comum": "#2E7D32",
    "reciclavel": "#1976D2",
    "volumoso": "#FF8F00",
    "sem_coleta": "#9E9E9E",
}

PHONE_W = 393
PHONE_H = 852
SB_H = 48
HI_H = 34
NAV_H = 90

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

DIAS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
DIAS_FULL = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]


# ===================== MODELOS =====================

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

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d):
        return ColetaEvento(**d)


@dataclass
class Notificacao:
    id: int
    titulo: str
    mensagem: str
    horario: str
    tipo: str
    lida: bool = False


@dataclass
class Denuncia:
    id: int
    tipo: str
    endereco: str
    bairro: str
    foto: str = ""
    status: str = "pendente"
    horario: str = ""


# ===================== STATE MANAGEMENT =====================

class AppState:
    """Estado global reativo - single source of truth"""
    
    def __init__(self):
        self._listeners: List[Callable] = []
        self._load_config()
        self._init_data()
    
    def _load_config(self):
        path = os.path.join(os.path.expanduser("~"), ".horadolixo_data.json")
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                    self.bairro_id = d.get("bairro_id", 1)
                    self.notif_prefs = d.get("notifs", {
                        "truck_near": True, "route_start": True, "delay": True, "night_reminder": True
                    })
                    self.dark_mode = d.get("dark_mode", False)
            except:
                self._defaults()
        else:
            self._defaults()
    
    def _defaults(self):
        self.bairro_id = 1
        self.notif_prefs = {"truck_near": True, "route_start": True, "delay": True, "night_reminder": True}
        self.dark_mode = False
    
    def _save_config(self):
        path = os.path.join(os.path.expanduser("~"), ".horadolixo_data.json")
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({
                    "bairro_id": self.bairro_id,
                    "notifs": self.notif_prefs,
                    "dark_mode": self.dark_mode,
                }, f, ensure_ascii=False, indent=2)
        except:
            pass
        self._notify()
    
    def _init_data(self):
        self.coletas: List[ColetaEvento] = []
        self.notificacoes: List[Notificacao] = []
        self.denuncias: List[Denuncia] = []
        self.caminhao = {}
        self.refresh_all()
    
    def refresh_all(self):
        self.coletas = self._gen_coletas()
        self.notificacoes = self._gen_notificacoes()
        self.denuncias = self._gen_denuncias()
        self.caminhao = self._gen_caminhao()
        self._notify()
    
    def _gen_coletas(self) -> List[ColetaEvento]:
        hoje = datetime.now().weekday()
        bairro = next(b for b in BAIRROS if b["id"] == self.bairro_id)
        out = []
        for i in range(7):
            dia = (hoje + i) % 7
            is_coleta = dia in bairro["coleta_dias"]
            if is_coleta:
                tipo = "reciclavel" if dia % 2 == 0 else "comum"
                horario = "07:00" if tipo == "reciclavel" else "08:00"
                if i == 0:
                    agora = datetime.now()
                    hc = datetime.strptime(horario, "%H:%M").replace(year=agora.year, month=agora.month, day=agora.day)
                    if agora < hc - timedelta(minutes=30): status = "pendente"
                    elif agora < hc: status = "em_rota"
                    else: status = "concluido"
                else:
                    status = "pendente" if i > 0 else "concluido"
                out.append(ColetaEvento(i+1, tipo, horario, dia, self.bairro_id, status,
                    "Rua das Flores" if status == "em_rota" else "",
                    0.6 if status == "em_rota" else (1.0 if status == "concluido" else 0.0)))
            else:
                out.append(ColetaEvento(i+1, "sem_coleta", "--:--", dia, self.bairro_id, "sem_coleta"))
        return out
    
    def _gen_notificacoes(self) -> List[Notificacao]:
        return [
            Notificacao(1, "Caminhão se aproximando", "Coleta comum em 15 min", "Hoje 07:45", "truck"),
            Notificacao(2, "Rota iniciada", "Caminhão saiu da garagem às 07:00", "Hoje 07:00", "info"),
            Notificacao(3, "Coleta concluída", "Reciclável coletado com sucesso", "Ontem 08:30", "success"),
            Notificacao(4, "Atraso detectado", "Trânsito na Av. Djalma - +20 min", "Seg 08:15", "warning"),
            Notificacao(5, "Lembrete: separar reciclável", "Coleta de reciclável amanhã às 07:00", "Ontem 19:00", "info"),
        ]
    
    def _gen_denuncias(self) -> List[Denuncia]:
        return [
            Denuncia(1, "entulho", "Rua 15, 245 - Vila Betânia", "Vila Betânia", "", "pendente", "Hoje 06:30"),
            Denuncia(2, "volumoso", "Av. Getúlio Vargas, 1200 - Centro", "Centro", "", "agendado", "Ontem 14:20"),
            Denuncia(3, "irregular", "Rua das Flores, s/n - Adrianópolis", "Adrianópolis", "", "em_analise", "Seg 09:10"),
        ]
    
    def _gen_caminhao(self) -> dict:
        agora = datetime.now()
        saida = agora.replace(hour=7, minute=0, second=0, microsecond=0)
        chegada = agora.replace(hour=8, minute=0, second=0, microsecond=0)
        if agora < saida:
            return {"status": "aguardando", "progresso": 0, "msg": "Saindo da garagem às 07:00", "eta": "15 min"}
        elif agora < chegada:
            p = (agora - saida).total_seconds() / (chegada - saida).total_seconds()
            return {"status": "em_rota", "progresso": min(p, 0.95), "msg": "A 3 ruas da sua casa",
                "eta": f"{int((1-p)*60)} min", "rua_atual": "Rua das Orquídeas", "proxima": "Rua das Flores (sua rua)"}
        return {"status": "concluido", "progresso": 1.0, "msg": "Coleta finalizada", "eta": "Concluído"}
    
    # --- Actions ---
    def set_bairro(self, bid: int):
        self.bairro_id = bid
        self.refresh_all()
        self._save_config()
    
    def toggle_notif(self, key: str, val: bool):
        self.notif_prefs[key] = val
        self._save_config()
    
    def toggle_dark(self, val: bool):
        self.dark_mode = val
        self._save_config()
    
    def add_denuncia(self, tipo: str, endereco: str):
        nova = Denuncia(len(self.denuncias)+1, tipo, endereco,
            next(b for b in BAIRROS if b["id"] == self.bairro_id)["nome"],
            "", "pendente", datetime.now().strftime("%d/%m %H:%M"))
        self.denuncias.insert(0, nova)
        self._notify()
    
    def get_bairro(self):
        return next(b for b in BAIRROS if b["id"] == self.bairro_id)
    
    def get_coleta_hoje(self):
        hoje = datetime.now().weekday()
        return next((c for c in self.coletas if c.dia_semana == hoje), None)
    
    # --- Observer pattern ---
    def subscribe(self, fn: Callable):
        self._listeners.append(fn)
    
    def unsubscribe(self, fn: Callable):
        if fn in self._listeners:
            self._listeners.remove(fn)
    
    def _notify(self):
        for fn in self._listeners:
            try:
                fn()
            except:
                pass


# ===================== COMPONENTES BASE =====================

def C(*controls, **kwargs):
    return ft.Container(*controls, **kwargs)

def Row(*controls, **kwargs):
    return ft.Row(*controls, **kwargs)

def Col(*controls, **kwargs):
    return ft.Column(*controls, **kwargs)

def T(text, **kwargs):
    return ft.Text(text, **kwargs)

def I(icon, **kwargs):
    return ft.Icon(icon, **kwargs)

def Btn(text, on_click, **kwargs):
    return ft.ElevatedButton(text, on_click=on_click, **kwargs)

def IBtn(icon, on_click, **kwargs):
    return ft.IconButton(icon, on_click=on_click, **kwargs)

def Switch(val, on_change, color, **kwargs):
    return ft.Switch(value=val, on_change=on_change, active_color=color, **kwargs)


# ===================== COMPONENTES UI =====================

class iPhoneFrame(ft.Container):
    def __init__(self, content: ft.Control, dark: bool):
        bg = COLORS["surface"] if not dark else "#1C1C1E"
        island = ft.Container(
            width=126, height=37, bgcolor="#000000", border_radius=19,
            alignment=ft.Alignment.CENTER,
            content=ft.Row([
                ft.Container(width=6, height=6, bgcolor="#333", border_radius=3),
                ft.Container(expand=True),
                ft.Container(width=6, height=6, bgcolor="#333", border_radius=3),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            margin=ft.Margin.only(top=8),
        )
        super().__init__(
            content=ft.Stack([
                ft.Container(
                    content=ft.Column([
                        ft.Container(height=45),
                        ft.Container(content=content, expand=True, clip_behavior=ft.ClipBehavior.HARD_EDGE),
                        ft.Container(
                            content=ft.Container(width=134, height=5,
                                bgcolor="#FFFFFF" if not dark else "#333333",
                                border_radius=2.5, opacity=0.4),
                            alignment=ft.Alignment.CENTER, height=HI_H),
                    ], spacing=0),
                    width=PHONE_W, height=PHONE_H, bgcolor=bg, border_radius=56,
                    border=ft.Border.all(2, "#E5E5EA" if not dark else "#333"),
                    shadow=ft.BoxShadow(spread_radius=-10, blur_radius=60,
                        color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK), offset=ft.Offset(0, 20)),
                ),
                ft.Container(content=island, alignment=ft.Alignment.TOP_CENTER),
            ]),
            width=PHONE_W + 20, height=PHONE_H + 20, alignment=ft.Alignment.CENTER,
        )


class StatusBar(ft.Container):
    def __init__(self, dark: bool):
        tc = "#000000" if not dark else "#FFFFFF"
        super().__init__(
            content=ft.Row([
                T("09:41", size=15, weight=ft.FontWeight.W_600, color=tc),
                ft.Container(expand=True),
                ft.Row([
                    I(ft.Icons.SIGNAL_CELLULAR_4_BAR, size=16, color=tc),
                    ft.Container(width=4),
                    I(ft.Icons.WIFI, size=16, color=tc),
                    ft.Container(width=4),
                    I(ft.Icons.BATTERY_FULL, size=20, color=tc),
                ], spacing=0),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            height=SB_H, padding=ft.Padding.symmetric(horizontal=24, vertical=8),
        )


class NavBar(ft.Container):
    def __init__(self, current: int, on_change: Callable, dark: bool):
        items = [
            (ft.Icons.HOME_ROUNDED, ft.Icons.HOME_OUTLINED, "Início"),
            (ft.Icons.CALENDAR_MONTH_ROUNDED, ft.Icons.CALENDAR_MONTH_OUTLINED, "Agenda"),
            (ft.Icons.MAP_ROUNDED, ft.Icons.MAP_OUTLINED, "Mapa"),
            (ft.Icons.NOTIFICATIONS_ROUNDED, ft.Icons.NOTIFICATIONS_OUTLINED, "Alertas"),
            (ft.Icons.PERSON_ROUNDED, ft.Icons.PERSON_OUTLINED, "Perfil"),
        ]
        btns = []
        for i, (is_sel, is_unsel, label) in enumerate(items):
            sel = i == current
            bg = COLORS["primary_container"] if (sel and not dark) else (COLORS["primary_dark"] if sel else ft.Colors.TRANSPARENT)
            clr = COLORS["primary"] if (sel and not dark) else (COLORS["primary_light"] if sel else COLORS["on_surface_variant"])
            btns.append(C(
                content=ft.Column([I(is_sel if sel else is_unsel, size=24, color=clr),
                    T(label, size=10, weight=ft.FontWeight.W_500, color=clr)],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                on_click=lambda e, idx=i: on_change(idx),
                expand=True, alignment=ft.Alignment.CENTER,
                padding=ft.Padding.symmetric(vertical=10),
                border_radius=18, bgcolor=bg,
                animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
                ink=True,
            ))
        super().__init__(
            content=C(content=ft.Row(btns, spacing=6),
                padding=ft.Padding.symmetric(horizontal=16, vertical=10),
                bgcolor=COLORS["surface"] if not dark else "#1C1C1E",
                border=ft.Border.only(top=ft.BorderSide(0.5, COLORS["outline"])),
                border_radius=ft.BorderRadius.only(top_left=28, top_right=28),
            ),
            height=NAV_H,
        )


class TruckCard(ft.Container):
    def __init__(self, caminhao: dict, coleta_hoje: Optional[ColetaEvento], dark: bool, on_refresh: Callable):
        super().__init__()
        self.cam = caminhao
        self.col = coleta_hoje
        self.dark = dark
        self.on_refresh = on_refresh
        self._build()
    
    def _build(self):
        s = self.cam["status"]
        if s == "em_rota":
            ic, ic_c, ic_bg = ft.Icons.LOCAL_SHIPPING, COLORS["secondary"], COLORS["secondary_container"]
            title, sub = "Caminhão a caminho", self.cam["msg"]
        elif s == "aguardando":
            ic, ic_c, ic_bg = ft.Icons.SCHEDULE, COLORS["info"], COLORS["primary_container"]
            title, sub = "Aguardando saída", self.cam["msg"]
        else:
            ic, ic_c, ic_bg = ft.Icons.CHECK_CIRCLE, COLORS["success"], COLORS["primary_container"]
            title, sub = "Coleta finalizada", self.cam["msg"]
        
        p = self.cam.get("progresso", 0)
        progress_bar = ft.Container(
            width=f"{p*100}%", height=8, bgcolor=COLORS["primary"], border_radius=4,
            animate=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
        )
        
        content = ft.Column([
            ft.Row([
                C(content=I(ic, size=24, color=ic_c), width=48, height=48, bgcolor=ic_bg, border_radius=14, alignment=ft.Alignment.CENTER),
                ft.Column([T(title, size=16, weight=ft.FontWeight.W_600, color=COLORS["on_surface"]),
                    T(sub, size=13, color=COLORS["on_surface_variant"])], spacing=2, expand=True),
                C(content=T(self.cam.get("eta", "--"), size=13, weight=ft.FontWeight.W_600, color=COLORS["primary"]),
                    padding=ft.Padding.symmetric(horizontal=14, vertical=7), bgcolor=COLORS["primary_container"], border_radius=22),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Container(height=16),
            ft.Row([T("Progresso da rota", size=12, color=COLORS["on_surface_variant"]),
                T(f"{int(p*100)}%", size=12, weight=ft.FontWeight.W_600, color=COLORS["primary"]),
                ft.Container(expand=True),
                IBtn(ft.Icons.REFRESH, lambda e: self.on_refresh(), icon_size=18, icon_color=COLORS["on_surface_variant"]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=6),
            ft.Stack([
                C(height=8, bgcolor=COLORS["outline_variant"], border_radius=4),
                progress_bar,
            ]),
            *([
                ft.Container(height=12),
                C(content=ft.Row([I(ft.Icons.LOCATION_ON, size=14, color=COLORS["secondary"]),
                    T(f"Agora: {self.cam['rua_atual']}", size=13, color=COLORS["on_surface"])], spacing=6),
                    padding=12, bgcolor=COLORS["secondary_container"], border_radius=12),
                ft.Container(height=8),
                C(content=ft.Row([I(ft.Icons.NAVIGATION, size=14, color=COLORS["primary"]),
                    T(f"Próxima: {self.cam['proxima']}", size=13, color=COLORS["on_surface_variant"])], spacing=6),
                    padding=12, bgcolor=COLORS["primary_container"], border_radius=12),
            ] if s == "em_rota" else []),
            *([
                ft.Container(height=16),
                ft.Row([
                    C(width=10, height=10, bgcolor=COLORS[self.col.tipo], border_radius=5),
                    T(f"Hoje: {self.col.tipo.capitalize()} às {self.col.horario}", size=14, weight=ft.FontWeight.W_500, color=COLORS["on_surface"]),
                ], spacing=10),
            ] if self.col else []),
        ], spacing=0)
        
        super().__init__(
            content=content, padding=20,
            bgcolor=COLORS["surface"] if not self.dark else "#2C2C2E",
            border_radius=20, border=ft.Border.all(1, COLORS["outline"]),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=20,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK), offset=ft.Offset(0, 4)),
        )


class ScheduleCard(ft.Container):
    def __init__(self, eventos: List[ColetaEvento], dark: bool):
        super().__init__()
        self.eventos = eventos
        self.dark = dark
        self.rows = []
        self._build()
        self.content = ft.Column(self.rows, spacing=8)
        self.padding = ft.Padding.only(bottom=8)
    
    def _build(self):
        hoje = datetime.now().weekday()
        self.rows = []
        for ev in self.eventos:
            is_hoje = ev.dia_semana == hoje
            is_passado = ev.dia_semana < hoje and ev.dia_semana != 6
            
            if ev.tipo == "sem_coleta":
                tc, tl = COLORS["sem_coleta"], "—"
            else:
                tc, tl = COLORS[ev.tipo], ev.tipo.capitalize()
            
            if is_hoje and ev.status == "em_rota":
                badge = C(content=T("EM ROTA", size=9, weight=ft.FontWeight.W_700, color=COLORS["secondary"]),
                    padding=ft.Padding.symmetric(horizontal=8, vertical=2), bgcolor=COLORS["secondary_container"], border_radius=10)
            elif is_hoje and ev.status == "concluido":
                badge = C(content=T("CONCLUÍDO", size=9, weight=ft.FontWeight.W_700, color=COLORS["success"]),
                    padding=ft.Padding.symmetric(horizontal=8, vertical=2), bgcolor=COLORS["primary_container"], border_radius=10)
            elif is_passado:
                badge = C(content=T("OK", size=9, weight=ft.FontWeight.W_700, color=COLORS["on_surface_variant"]),
                    padding=ft.Padding.symmetric(horizontal=8, vertical=2), bgcolor=COLORS["surface_variant"], border_radius=10)
            else:
                badge = C(content=T(ev.horario, size=12, weight=ft.FontWeight.W_500, color=COLORS["on_surface_variant"]),
                    padding=ft.Padding.symmetric(horizontal=8, vertical=2))
            
            dia_num = (datetime.now() + timedelta(days=(ev.dia_semana-hoje)%7)).day
            
            self.rows.append(C(
                content=ft.Row([
                    C(content=ft.Column([
                        T(DIAS[ev.dia_semana], size=14, weight=ft.FontWeight.W_600, color=COLORS["primary"] if is_hoje else COLORS["on_surface"]),
                        T(str(dia_num), size=11, color=COLORS["on_surface_variant"]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0), width=50, alignment=ft.Alignment.CENTER),
                    C(content=ft.Row([C(width=10, height=10, bgcolor=tc, border_radius=5), T(tl, size=13, color=COLORS["on_surface"])], spacing=8), expand=True),
                    badge,
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding.symmetric(vertical=12, horizontal=16),
                bgcolor=COLORS["primary_container"] if is_hoje else (COLORS["surface"] if not self.dark else "#2C2C2E"),
                border_radius=14, border=ft.Border.all(1, COLORS["primary"] if is_hoje else COLORS["outline"]),
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            ))
    
    def update_eventos(self, eventos: List[ColetaEvento]):
        self.eventos = eventos
        self._build()
        self.content = ft.Column(self.rows, spacing=8)
        self.update()


class QuickAction(ft.Container):
    def __init__(self, icon, label, color, on_click, dark: bool):
        super().__init__(
            content=ft.Column([
                C(content=I(icon, size=24, color=COLORS["surface"]), width=56, height=56, bgcolor=color, border_radius=16, alignment=ft.Alignment.CENTER),
                ft.Container(height=8),
                T(label, size=12, weight=ft.FontWeight.W_500, color=COLORS["on_surface"], text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            on_click=on_click, width=88, alignment=ft.Alignment.CENTER, ink=True, border_radius=16,
        )


class NotificationTile(ft.Container):
    def __init__(self, n: Notificacao, dark: bool):
        self.dark = dark
        icons = {
            "truck": (ft.Icons.LOCAL_SHIPPING, COLORS["secondary"], COLORS["secondary_container"]),
            "info": (ft.Icons.INFO_OUTLINE, COLORS["info"], "#E3F2FD"),
            "success": (ft.Icons.CHECK_CIRCLE_OUTLINE, COLORS["success"], COLORS["primary_container"]),
            "warning": (ft.Icons.WARNING_AMBER, COLORS["warning"], COLORS["secondary_container"]),
        }
        ic, clr, bg = icons.get(n.tipo, icons["info"])
        super().__init__(
            content=ft.Row([
                C(content=I(ic, size=20, color=clr), width=40, height=40, bgcolor=bg if not self.dark else clr+"20", border_radius=12, alignment=ft.Alignment.CENTER),
                ft.Column([T(n.titulo, size=14, weight=ft.FontWeight.W_600, color=COLORS["on_surface"]),
                    T(n.mensagem, size=12, color=COLORS["on_surface_variant"])], spacing=2, expand=True),
                T(n.horario, size=11, color=COLORS["on_surface_variant"]),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
            padding=ft.Padding.symmetric(vertical=10, horizontal=16),
            bgcolor=COLORS["surface"] if not self.dark else "#2C2C2E",
            border=ft.Border.only(bottom=ft.BorderSide(0.5, COLORS["outline"])),
        )


class DenunciaCard(ft.Container):
    def __init__(self, d: Denuncia, dark: bool):
        self.dark = dark
        sc = {"pendente": (COLORS["warning"], "Pendente"), "em_analise": (COLORS["info"], "Em análise"),
              "agendado": (COLORS["primary"], "Agendado"), "concluido": (COLORS["success"], "Concluído")}
        clr, lbl = sc.get(d.status, (COLORS["outline"], d.status))
        ics = {"entulho": ft.Icons.LUGGAGE, "volumoso": ft.Icons.CHAIR_OUTLINED,
               "irregular": ft.Icons.REPORT_PROBLEM, "outro": ft.Icons.HELP_OUTLINE}
        super().__init__(
            content=ft.Column([
                ft.Row([
                    C(content=I(ics.get(d.tipo, ft.Icons.HELP_OUTLINE), size=20, color=clr), width=44, height=44,
                        bgcolor=clr+"15" if not self.dark else clr+"30", border_radius=12, alignment=ft.Alignment.CENTER),
                    ft.Column([T(d.tipo.capitalize(), size=14, weight=ft.FontWeight.W_600, color=COLORS["on_surface"]),
                        T(d.endereco, size=12, color=COLORS["on_surface_variant"])], spacing=2, expand=True),
                    C(content=T(lbl, size=10, weight=ft.FontWeight.W_600, color=COLORS["surface"]),
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4), bgcolor=clr, border_radius=10),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Container(height=8),
                T(d.horario, size=11, color=COLORS["on_surface_variant"]),
            ], spacing=0),
            padding=16, bgcolor=COLORS["surface"] if not self.dark else "#2C2C2E", border_radius=16, border=ft.Border.all(1, COLORS["outline"]),
        )


class InfoCard(ft.Container):
    def __init__(self, label, value, icon, color, dark: bool):
        super().__init__(
            content=ft.Column([I(icon, size=20, color=color), ft.Container(height=4),
                T(value, size=16, weight=ft.FontWeight.W_700, color=COLORS["on_surface"]),
                T(label, size=11, color=COLORS["on_surface_variant"])], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            expand=True, padding=ft.Padding.symmetric(vertical=16),
            bgcolor=COLORS["surface_variant"] if not dark else "#3A3A3C", border_radius=16,
        )


class ToggleTile(ft.Container):
    def __init__(self, title, desc, key, color, val: bool, on_change: Callable, dark: bool, last: bool = False):
        super().__init__(
            content=ft.Row([
                ft.Column([T(title, size=14, weight=ft.FontWeight.W_500, color=COLORS["on_surface"]),
                    T(desc, size=12, color=COLORS["on_surface_variant"])], spacing=2, expand=True),
                Switch(val, on_change, color, thumb_color=COLORS["surface"]),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding.symmetric(vertical=14),
            border=ft.Border.only(bottom=ft.BorderSide(0.5, COLORS["outline"])) if not last else None,
        )


# ===================== TELA PRINCIPAL =====================

class HoraDoLixoApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.state = AppState()
        self.state.subscribe(self._on_state_change)
        self.current_tab = 0
        self.dark = self.state.dark_mode
        self._screen_refs = {}
        self._setup_page()
        self._build_ui()
        self.page.run_task(self._auto_refresh_loop)
    
    def _setup_page(self):
        self.page.title = "Hora do Lixo"
        self.page.theme_mode = ft.ThemeMode.DARK if self.dark else ft.ThemeMode.LIGHT
        self.page.window_width = PHONE_W + 40
        self.page.window_height = PHONE_H + 100
        self.page.window_min_width = PHONE_W + 40
        self.page.window_min_height = PHONE_H + 100
        self.page.window_resizable = True
        self.page.padding = 0
        self.page.bgcolor = "#F0F0F0" if not self.dark else "#121212"
        self.page.fonts = {"Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"}
        self.page.theme = ft.Theme(font_family="Inter")
        self.page.run_task(self._center_window)
    
    async def _center_window(self):
        await self.page.window.center()
    
    def _on_state_change(self):
        if self.current_tab in self._screen_refs:
            self._screen_refs[self.current_tab].refresh()
        self.page.update()
    
    def _build_ui(self):
        self.phone_view = ft.Container(content=self._build_screen(0), expand=True)
        self.main_stack = ft.Stack([
            iPhoneFrame(
                ft.Column([
                    StatusBar(self.dark),
                    ft.Container(content=self.phone_view, expand=True, clip_behavior=ft.ClipBehavior.HARD_EDGE),
                    NavBar(self.current_tab, self._on_tab_change, self.dark),
                ], spacing=0), self.dark
            )
        ], expand=True)
        bg = ft.Container(
            content=ft.Column([ft.Container(height=30), self.main_stack], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True, bgcolor=self.page.bgcolor, alignment=ft.Alignment.CENTER,
        )
        self.page.add(bg)
    
    def _on_tab_change(self, idx: int):
        if idx == self.current_tab:
            return
        self.current_tab = idx
        self.phone_view.content = self._build_screen(idx)
        self.page.update()
    
    def _build_screen(self, idx: int):
        builders = [
            self._build_home,
            self._build_schedule,
            self._build_map,
            self._build_alerts,
            self._build_profile,
        ]
        screen = builders[idx]()
        self._screen_refs[idx] = screen
        return ft.Container(content=screen, expand=True)
    
    def _build_home(self):
        bairro = self.state.get_bairro()
        coleta_hoje = self.state.get_coleta_hoje()
        
        class HomeScreen(ft.ListView):
            def __init__(inner_self):
                super().__init__(controls=inner_self._build_controls(), padding=ft.Padding.only(bottom=100), expand=True)
                inner_self.truck_card = None
            
            def _build_controls(inner_self):
                inner_self.truck_card = TruckCard(
                    self.state.caminhao, coleta_hoje, self.dark, self._refresh_truck)
                return [
                    C(content=ft.Row([
                        ft.Column([T("Bom dia! 👋", size=14, color=COLORS["on_surface_variant"]),
                            ft.Row([T(bairro["nome"], size=22, weight=ft.FontWeight.W_700, color=COLORS["on_surface"]),
                                I(ft.Icons.KEYBOARD_ARROW_DOWN, size=18, color=COLORS["on_surface_variant"])], spacing=4)], expand=True),
                        C(content=I(ft.Icons.NOTIFICATIONS_NONE, size=24, color=COLORS["on_surface_variant"]), width=44, height=44,
                            bgcolor=COLORS["surface_variant"], border_radius=12, alignment=ft.Alignment.CENTER,
                            on_click=lambda e: self._on_tab_change(3), ink=True),
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.Padding.only(left=20, top=8, right=20, bottom=16)),
                    C(content=inner_self.truck_card, padding=ft.Padding.symmetric(horizontal=20, vertical=8)),
                    C(content=ft.Row([
                        QuickAction(ft.Icons.ADD_ALERT, "Denunciar", COLORS["error"], lambda e: self._show_denuncia_dialog(), self.dark),
                        QuickAction(ft.Icons.LOCAL_SHIPPING, "Solicitar Coleta", COLORS["primary"], lambda e: self._show_solicitar_dialog(), self.dark),
                        QuickAction(ft.Icons.SCHEDULE, "Agendar Volumoso", COLORS["secondary"], lambda e: self._show_agendar_dialog(), self.dark),
                        QuickAction(ft.Icons.MAP, "Ver Mapa", COLORS["info"], lambda e: self._on_tab_change(2), self.dark),
                    ], spacing=12, alignment=ft.MainAxisAlignment.CENTER), padding=ft.Padding.symmetric(horizontal=20, vertical=16)),
                    C(content=ft.Column([
                        ft.Row([T("Próximas coletas", size=18, weight=ft.FontWeight.W_700, color=COLORS["on_surface"]),
                            ft.TextButton("Ver tudo", on_click=lambda e: self._on_tab_change(1), style=ft.ButtonStyle(color=COLORS["primary"]))],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(height=8),
                        ScheduleCard(self.state.coletas, self.dark),
                    ]), padding=ft.Padding.symmetric(horizontal=20, vertical=8)),
                    ft.Container(height=20),
                ]
            
            def refresh(inner_self):
                inner_self.controls = inner_self._build_controls()
                inner_self.update()
        
        return HomeScreen()
    
    def _refresh_truck(self):
        self.state.caminhao = self.state._gen_caminhao()
        self._on_state_change()
    
    def _build_schedule(self):
        bairro = self.state.get_bairro()
        
        class ScheduleScreen(ft.ListView):
            def __init__(inner_self):
                super().__init__(controls=inner_self._build_controls(), padding=ft.Padding.only(bottom=100), expand=True)
            
            def _build_controls(inner_self):
                return [
                    C(content=ft.Column([
                        ft.Row([T("Agenda da semana", size=22, weight=ft.FontWeight.W_700, color=COLORS["on_surface"])], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        T(bairro["nome"], size=14, color=COLORS["on_surface_variant"]),
                    ]), padding=ft.Padding.only(left=20, top=16, right=20, bottom=8)),
                    C(content=ScheduleCard(self.state.coletas, self.dark), padding=ft.Padding.symmetric(horizontal=20, vertical=8)),
                    C(content=C(content=ft.Row([I(ft.Icons.INFO_OUTLINE, size=18, color=COLORS["info"]),
                        T("Horários estimados. O caminhão pode chegar até 30 min antes ou depois. Ative alertas para ser avisado em tempo real.", size=13, color=COLORS["on_surface_variant"])], spacing=10),
                        padding=16, bgcolor=COLORS["primary_container"], border_radius=16), padding=ft.Padding.symmetric(horizontal=20, vertical=16)),
                    ft.Container(height=20),
                ]
            
            def refresh(inner_self):
                inner_self.controls = inner_self._build_controls()
                inner_self.update()
        
        return ScheduleScreen()
    
    def _build_map(self):
            cam = self.state.caminhao
            p = cam.get("progresso", 0)
            agora = datetime.now()
        
            # Simular dados de minutagem e percurso
            saida_garagem = agora.replace(hour=7, minute=0, second=0, microsecond=0)
            tempo_decorrido = max(0, int((agora - saida_garagem).total_seconds() / 60)) if agora > saida_garagem else 0
            tempo_total_estimado = 60  # 1 hora total de rota
            tempo_restante = max(0, tempo_total_estimado - tempo_decorrido)
        
            # Ruas do percurso (simulado)
            ruas_percurso = [
                {"nome": "Rua das Orquídeas", "status": "concluida", "horario": "07:12", "tempo": "12 min"},
                {"nome": "Rua das Bromélias", "status": "concluida", "horario": "07:24", "tempo": "24 min"},
                {"nome": "Rua das Hortênsias", "status": "concluida", "horario": "07:35", "tempo": "35 min"},
                {"nome": "Rua das Orquídeas (trecho 2)", "status": "concluida", "horario": "07:42", "tempo": "42 min"},
                {"nome": "Rua das Flores", "status": "atual", "horario": "07:48", "tempo": "48 min"},
                {"nome": "Rua dos Lírios", "status": "proxima", "horario": "07:55", "tempo": "55 min"},
                {"nome": "Rua das Violetas", "status": "proxima", "horario": "08:02", "tempo": "1h 02 min"},
                {"nome": "Rua dos Jasmins", "status": "proxima", "horario": "08:10", "tempo": "1h 10 min"},
            ]

            class MapScreen(ft.ListView):
                def __init__(inner_self):
                    super().__init__(controls=inner_self._build_controls(), padding=ft.Padding.only(bottom=100), expand=True)

                def _build_controls(inner_self):
                    # Header com resumo da minutagem
                    header_cards = ft.Row([
                        InfoCard("Saída da garagem", "07:00", ft.Icons.PLAY_CIRCLE, COLORS["primary"], self.dark),
                        InfoCard("Tempo decorrido", f"{tempo_decorrido} min", ft.Icons.TIMER, COLORS["secondary"], self.dark),
                        InfoCard("ETA sua rua", cam.get("eta", "--"), ft.Icons.SCHEDULE, COLORS["info"], self.dark),
                    ], spacing=12)
                
                    # Barra de progresso principal
                    progress_section = ft.Column([
                        ft.Row([
                            T("Progresso da Rota", size=14, weight=ft.FontWeight.W_600, color=COLORS["on_surface"]),
                            T(f"{int(p*100)}%", size=14, weight=ft.FontWeight.W_700, color=COLORS["primary"]),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(height=8),
                        ft.Stack([
                            C(height=10, bgcolor=COLORS["outline_variant"], border_radius=5),
                            C(width=f"{p*100}%", height=10, bgcolor=COLORS["primary"], border_radius=5,
                                animate=ft.Animation(500, ft.AnimationCurve.EASE_OUT)),
                        ]),
                        ft.Container(height=8),
                        ft.Row([
                            C(content=ft.Row([C(width=8, height=8, bgcolor=COLORS["primary"], border_radius=4),
                                T("Garagem 07:00", size=11, color=COLORS["on_surface_variant"])], spacing=6)),
                            ft.Container(expand=True),
                            C(content=ft.Row([I(ft.Icons.LOCAL_SHIPPING, size=16, color=COLORS["secondary"]),
                                T("Aqui", size=11, weight=ft.FontWeight.W_600, color=COLORS["secondary"])], spacing=6)),
                            ft.Container(expand=True),
                            C(content=ft.Row([T("Você 08:00", size=11, color=COLORS["on_surface_variant"]),
                                C(width=8, height=8, bgcolor=COLORS["error"], border_radius=4)], spacing=6)),
                        ]),
                    ], spacing=0)

                    # Lista de ruas do percurso (timeline)
                    rua_items = []
                    for i, rua in enumerate(ruas_percurso):
                        is_last = i == len(ruas_percurso) - 1
                    
                        if rua["status"] == "concluida":
                            icone = ft.Icons.CHECK_CIRCLE
                            icone_cor = COLORS["success"]
                            linha_cor = COLORS["success"]
                            bg_cor = COLORS["primary_container"] if not self.dark else "#1B5E2033"
                            status_text = "Concluída"
                            status_cor = COLORS["success"]
                        elif rua["status"] == "atual":
                            icone = ft.Icons.LOCAL_SHIPPING
                            icone_cor = COLORS["secondary"]
                            linha_cor = COLORS["secondary"]
                            bg_cor = COLORS["secondary_container"] if not self.dark else "#FF6B3533"
                            status_text = "EM ROTA"
                            status_cor = COLORS["secondary"]
                        else:  # proxima
                            icone = ft.Icons.RADIO_BUTTON_UNCHECKED
                            icone_cor = COLORS["outline"]
                            linha_cor = COLORS["outline"]
                            bg_cor = COLORS["surface_variant"] if not self.dark else "#3A3A3C"
                            status_text = "Pendente"
                            status_cor = COLORS["on_surface_variant"]
                    
                        # Linha de conexão vertical
                        linha_conexao = ft.Container(
                            width=2,
                            expand=True,
                            bgcolor=linha_cor,
                            margin=ft.Margin.only(left=19, top=0, right=0, bottom=0),
                        ) if not is_last else ft.Container()
                    
                        rua_items.append(
                            ft.Row([
                                # Coluna da timeline (ícone + linha)
                                ft.Stack([
                                    ft.Container(
                                        content=ft.Column([
                                            ft.Container(height=20),
                                            linha_conexao,
                                        ], spacing=0),
                                        width=40,
                                    ),
                                    ft.Container(
                                        content=I(icone, size=20, color=icone_cor),
                                        width=40,
                                        height=40,
                                        alignment=ft.Alignment.CENTER,
                                    ),
                                ], width=40),
                            
                                # Conteúdo da rua
                                ft.Container(
                                    content=ft.Column([
                                        ft.Row([
                                            T(rua["nome"], size=14, weight=ft.FontWeight.W_500, color=COLORS["on_surface"], expand=True),
                                            C(content=T(status_text, size=9, weight=ft.FontWeight.W_700, color=COLORS["surface"]),
                                                padding=ft.Padding.symmetric(horizontal=8, vertical=2), bgcolor=status_cor, border_radius=10),
                                        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                        ft.Container(height=2),
                                        ft.Row([
                                            I(ft.Icons.ACCESS_TIME, size=12, color=COLORS["on_surface_variant"]),
                                            T(f"Previsto: {rua['horario']}", size=12, color=COLORS["on_surface_variant"]),
                                            ft.Container(width=16),
                                            I(ft.Icons.STRAIGHTEN, size=12, color=COLORS["on_surface_variant"]),
                                            T(f"+{rua['tempo']} de rota", size=12, color=COLORS["on_surface_variant"]),
                                        ], spacing=4),
                                    ], spacing=0),
                                    expand=True,
                                    padding=ft.Padding.symmetric(vertical=10, horizontal=4),
                                    bgcolor=bg_cor,
                                    border_radius=ft.BorderRadius.only(top_right=12, bottom_right=12),
                                ),
                            ], spacing=0)
                        )
                
                    timeline = ft.Column(rua_items, spacing=0)

                    return [
                        C(content=ft.Column([
                            T("Rota do Caminhão", size=22, weight=ft.FontWeight.W_700, color=COLORS["on_surface"]),
                            T("Minutagem e percurso em tempo real", size=14, color=COLORS["on_surface_variant"]),
                        ]), padding=ft.Padding.only(left=20, top=16, right=20, bottom=8)),
                    
                        # Cards de resumo
                        C(content=header_cards, padding=ft.Padding.symmetric(horizontal=20, vertical=8)),
                    
                        # Progresso
                        C(content=progress_section, padding=ft.Padding.symmetric(horizontal=20, vertical=16),
                            bgcolor=COLORS["surface"] if not self.dark else "#2C2C2E", border_radius=20, 
                            border=ft.Border.all(1, COLORS["outline"]), margin=ft.Margin.symmetric(horizontal=20)),
                    
                        ft.Container(height=16),
                    
                        # Timeline das ruas
                        C(content=ft.Column([
                            ft.Row([
                                T("Percurso Detalhado", size=18, weight=ft.FontWeight.W_700, color=COLORS["on_surface"]),
                                ft.Container(expand=True),
                                C(content=ft.Row([
                                    C(width=10, height=10, bgcolor=COLORS["success"], border_radius=5),
                                    T("Concluída", size=11, color=COLORS["on_surface_variant"]),
                                    ft.Container(width=12),
                                    C(width=10, height=10, bgcolor=COLORS["secondary"], border_radius=5),
                                    T("Atual", size=11, color=COLORS["on_surface_variant"]),
                                    ft.Container(width=12),
                                    C(width=10, height=10, bgcolor=COLORS["outline"], border_radius=5),
                                    T("Pendente", size=11, color=COLORS["on_surface_variant"]),
                                ], spacing=4), padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                                    bgcolor=COLORS["surface_variant"] if not self.dark else "#3A3A3C", border_radius=12),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Container(height=12),
                            timeline,
                        ]), padding=ft.Padding.symmetric(horizontal=20, vertical=16),
                            bgcolor=COLORS["surface"] if not self.dark else "#2C2C2E", border_radius=20, 
                            border=ft.Border.all(1, COLORS["outline"]), margin=ft.Margin.symmetric(horizontal=20)),
                    
                        ft.Container(height=20),
                    ]

                def refresh(inner_self):
                    inner_self.controls = inner_self._build_controls()
                    inner_self.update()

            return MapScreen()
    
    def _build_alerts(self):
        class AlertsScreen(ft.ListView):
            def __init__(inner_self):
                super().__init__(controls=inner_self._build_controls(), padding=ft.Padding.only(bottom=100), expand=True)
            
            def _build_controls(inner_self):
                prefs = self.state.notif_prefs
                toggles = [
                    ("🚛 Avisar quando caminhão chegar", "15 min antes da coleta", "truck_near", COLORS["secondary"]),
                    ("🔔 Avisar na saída da garagem", "Início da rota do dia", "route_start", COLORS["info"]),
                    ("⚠️ Avisar atrasos", "Mudanças acima de 15 min", "delay", COLORS["warning"]),
                    ("🌙 Lembrete noturno", "Separar lixo na véspera", "night_reminder", COLORS["primary"]),
                ]
                toggle_controls = [
                    ToggleTile(t, d, k, c, prefs.get(k, True), lambda e, kk=k: self.state.toggle_notif(kk, e.control.value), self.dark, i==3)
                    for i, (t, d, k, c) in enumerate(toggles)
                ]
                return [
                    C(content=ft.Column([ft.Row([T("Alertas & Notificações", size=22, weight=ft.FontWeight.W_700, color=COLORS["on_surface"])],)]), padding=ft.Padding.only(left=20, top=16, right=20, bottom=8)),
                    C(content=ft.Column([T("Preferências", size=16, weight=ft.FontWeight.W_600, color=COLORS["on_surface"]),
                        ft.Container(height=12), *toggle_controls], spacing=0),
                        padding=ft.Padding.symmetric(horizontal=20, vertical=16),
                        bgcolor=COLORS["surface"] if not self.dark else "#2C2C2E", border_radius=20, border=ft.Border.all(1, COLORS["outline"]), margin=ft.Margin.symmetric(horizontal=20)),
                    ft.Container(height=20),
                    C(content=ft.Column([ft.Row([T("Histórico", size=18, weight=ft.FontWeight.W_700, color=COLORS["on_surface"])]), ft.Container(height=12),
                        ft.Column([NotificationTile(n, self.dark) for n in self.state.notificacoes], spacing=0)]),
                        padding=ft.Padding.symmetric(horizontal=20, vertical=16),
                        bgcolor=COLORS["surface"] if not self.dark else "#2C2C2E", border_radius=20, border=ft.Border.all(1, COLORS["outline"]), margin=ft.Margin.symmetric(horizontal=20)),
                    ft.Container(height=20),
                ]
            
            def refresh(inner_self):
                inner_self.controls = inner_self._build_controls()
                inner_self.update()
        
        return AlertsScreen()
    
    def _build_profile(self):
        bairro = self.state.get_bairro()
        
        class ProfileScreen(ft.ListView):
            def __init__(inner_self):
                super().__init__(controls=inner_self._build_controls(), padding=ft.Padding.only(bottom=100), expand=True)
            
            def _build_controls(inner_self):
                return [
                    C(content=ft.Column([T("Perfil & Configurações", size=22, weight=ft.FontWeight.W_700, color=COLORS["on_surface"])]), padding=ft.Padding.only(left=20, top=16, right=20, bottom=8)),
                    C(content=ft.Row([
                        C(content=I(ft.Icons.LOCATION_CITY, size=24, color=COLORS["primary"]), width=52, height=52, bgcolor=COLORS["primary_container"], border_radius=14, alignment=ft.Alignment.CENTER),
                        ft.Column([T("Seu bairro", size=12, color=COLORS["on_surface_variant"]),
                            T(bairro["nome"], size=18, weight=ft.FontWeight.W_600, color=COLORS["on_surface"]),
                            T(bairro["zona"], size=13, color=COLORS["on_surface_variant"])], spacing=2, expand=True),
                        I(ft.Icons.CHEVRON_RIGHT, color=COLORS["on_surface_variant"]),
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=16, bgcolor=COLORS["surface"] if not self.dark else "#2C2C2E", border_radius=16, border=ft.Border.all(1, COLORS["outline"]), margin=ft.Margin.symmetric(horizontal=20), on_click=self._show_bairro_selector, ink=True),
                    ft.Container(height=16),
                    C(content=ft.Column([
                        ft.Row([T("Minhas denúncias", size=18, weight=ft.FontWeight.W_700, color=COLORS["on_surface"]),
                            ft.TextButton("Nova denúncia", on_click=lambda e: self._show_denuncia_dialog(), style=ft.ButtonStyle(color=COLORS["error"]))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(height=8),
                        ft.Column([DenunciaCard(d, self.dark) for d in self.state.denuncias], spacing=12),
                    ]), padding=ft.Padding.symmetric(horizontal=20, vertical=16)),
                    ft.Container(height=16),
                    C(content=ft.Column([
                        T("App", size=16, weight=ft.FontWeight.W_600, color=COLORS["on_surface"]),
                        ft.Container(height=12),
                        C(content=ft.Row([I(ft.Icons.DARK_MODE, size=22, color=COLORS["on_surface_variant"]),
                            T("Tema escuro", size=14, color=COLORS["on_surface"]), ft.Container(expand=True),
                            Switch(self.dark, self._toggle_theme, COLORS["primary"])], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=ft.Padding.symmetric(vertical=14), border=ft.Border.only(bottom=ft.BorderSide(0.5, COLORS["outline"]))),
                        C(content=ft.Row([I(ft.Icons.INFO_OUTLINE, size=22, color=COLORS["on_surface_variant"]),
                            T("Versão do app", size=14, color=COLORS["on_surface"]), ft.Container(expand=True),
                            T("1.0.0", size=14, color=COLORS["on_surface_variant"])], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER), padding=ft.Padding.symmetric(vertical=14)),
                    ]), padding=ft.Padding.symmetric(horizontal=20, vertical=16), bgcolor=COLORS["surface"] if not self.dark else "#2C2C2E", border_radius=20, border=ft.Border.all(1, COLORS["outline"]), margin=ft.Margin.symmetric(horizontal=20)),
                    ft.Container(height=20),
                ]
            
            def refresh(inner_self):
                inner_self.controls = inner_self._build_controls()
                inner_self.update()
        
        return ProfileScreen()
    
    def _show_bairro_selector(self, e):
        def on_select(b):
            self.state.set_bairro(b["id"])
            self.phone_view.content = self._build_screen(self.current_tab)
            self.page.close(dlg)
            self.page.open(ft.SnackBar(content=T(f"Bairro alterado para {b['nome']}", color=COLORS["surface"]), bgcolor=COLORS["primary"], behavior=ft.SnackBarBehavior.FLOATING))
            self.page.update()
        
        items = []
        for b in BAIRROS:
            sel = b["id"] == self.state.bairro_id
            items.append(ft.ListTile(
                leading=C(width=24, height=24, border=ft.Border.all(2, COLORS["primary"] if sel else COLORS["outline"]), border_radius=12,
                    content=C(width=12, height=12, bgcolor=COLORS["primary"], border_radius=6) if sel else None, alignment=ft.Alignment.CENTER),
                title=T(b["nome"], weight=ft.FontWeight.W_600 if sel else ft.FontWeight.W_400),
                subtitle=T(b["zona"]), on_click=lambda e, br=b: on_select(br),
            ))
        dlg = ft.AlertDialog(title=T("Selecionar bairro", weight=ft.FontWeight.W_600),
            content=C(content=ft.ListView(items, spacing=4), width=350, height=400),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dlg))])
        self.page.open(dlg)
    
    def _show_denuncia_dialog(self):
        tipo_field = ft.Dropdown(label="Tipo de problema", options=[
            ft.dropdown.Option("entulho", "Entulho/Resíduos de construção"),
            ft.dropdown.Option("volumoso", "Móvel/Eletrodoméstico volumoso"),
            ft.dropdown.Option("irregular", "Descarte irregular"),
            ft.dropdown.Option("outro", "Outro"),
        ], width=300)
        endereco_field = ft.TextField(label="Endereço completo", hint_text="Rua, número, bairro", width=300, multiline=True, min_lines=2)
        
        def submit(e):
            if not tipo_field.value or not endereco_field.value:
                return
            self.state.add_denuncia(tipo_field.value, endereco_field.value)
            self.page.close(dlg)
            if self.current_tab == 4:
                self.phone_view.content = self._build_screen(4)
            self.page.open(ft.SnackBar(content=T("Denúncia enviada! Acompanhe na aba Perfil", color=COLORS["surface"]), bgcolor=COLORS["success"], behavior=ft.SnackBarBehavior.FLOATING))
            self.page.update()
        
        dlg = ft.AlertDialog(title=T("Nova denúncia", weight=ft.FontWeight.W_600),
            content=ft.Column([tipo_field, endereco_field], tight=True, spacing=16, width=320),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dlg)),
                     ft.ElevatedButton("Enviar", on_click=submit, bgcolor=COLORS["error"], color=COLORS["surface"])])
        self.page.open(dlg)
    
    def _show_solicitar_dialog(self):
        self.page.open(ft.SnackBar(content=T("Solicitação de coleta extra registrada! Entraremos em contato.", color=COLORS["surface"]), bgcolor=COLORS["primary"], behavior=ft.SnackBarBehavior.FLOATING))
    
    def _show_agendar_dialog(self):
        self.page.open(ft.SnackBar(content=T("Agendamento de volumoso aberto! Escolha data e horário.", color=COLORS["surface"]), bgcolor=COLORS["secondary"], behavior=ft.SnackBarBehavior.FLOATING))
    
    def _toggle_theme(self, e):
        self.dark = e.control.value
        self.state.toggle_dark(self.dark)
        self.page.theme_mode = ft.ThemeMode.DARK if self.dark else ft.ThemeMode.LIGHT
        self.page.bgcolor = "#121212" if self.dark else "#F0F0F0"
        self.main_stack.controls[0] = iPhoneFrame(
            ft.Column([StatusBar(self.dark), ft.Container(content=self.phone_view.content, expand=True, clip_behavior=ft.ClipBehavior.HARD_EDGE), NavBar(self.current_tab, self._on_tab_change, self.dark)], spacing=0), self.dark)
        self.page.update()
    
    async def _auto_refresh_loop(self):
            while True:
                await asyncio.sleep(30)
                self.state.caminhao = self.state._gen_caminhao()
                if self.current_tab in [0, 2]:
                    if self.current_tab in self._screen_refs:
                        screen = self._screen_refs[self.current_tab]
                        try:
                            screen.refresh()
                        except RuntimeError:
                            # Screen no longer attached to page (tab was switched)
                            pass
                    self.page.update()


def main(page: ft.Page):
    HoraDoLixoApp(page)


if __name__ == "__main__":
    ft.run(main)
