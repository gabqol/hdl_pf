#!/usr/bin/env python3
"""
Hora do Lixo - App de acompanhamento de coleta de residuos (Manaus/AM)
Flet 1.0 - Layout mobile nativo Android - funcionalidades conforme APP.MD
"""

import asyncio
from datetime import datetime, timedelta
from typing import Callable

import flet as ft

from data import (
    BAIRROS, DIAS, DIAS_FULL, PALETA, RUAS,
    AppState, ColetaEvento,
    pontos_por_bairro,
)
import screens as S

COLORS = {
    "primary": "#2E6B42",
    "primary_light": "#5CDB6F",
    "primary_dark": "#1A2D22",
    "primary_container": "#E8F5E9",
    "secondary": "#E8812A",
    "surface": "#FFFFFF",
    "surface_variant": "#F5F7F5",
    "background": "#F0F2F0",
    "on_surface": "#14201A",
    "on_surface_variant": "#5A6B60",
    "outline": "#E3E8E4",
    "success": "#2E6B42",
    "warning": "#FF8F00",
    "error": "#C94040",
    "info": "#1976D2",
}


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


def Switch(val, on_change, color, **kwargs):
    return ft.Switch(value=val, on_change=on_change, active_color=color, **kwargs)


class TopBar(ft.Container):
    def __init__(self, title: str, dark: bool, action_icon=None, action_click=None):
        tc = PALETA["text_primary"] if dark else COLORS["on_surface"]
        bg = PALETA["bg_card"] if dark else COLORS["surface"]
        super().__init__(
            content=ft.Row([
                T(title, size=20, weight=ft.FontWeight.W_700, color=tc, expand=True),
                *([ft.IconButton(icon=action_icon, icon_color=tc, on_click=action_click, tooltip="Ações")] if action_icon else []),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            height=64, padding=ft.Padding.symmetric(horizontal=16, vertical=8), bgcolor=bg,
            border=ft.Border.only(bottom=ft.BorderSide(1, PALETA["divider"] if dark else COLORS["outline"])),
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
            btns.append(ft.Container(
                content=ft.Column([I(is_sel if sel else is_unsel, size=24, color=clr),
                    T(label, size=11, weight=ft.FontWeight.W_500, color=clr)],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2, tight=True),
                on_click=lambda e, idx=i: on_change(idx), expand=True, alignment=ft.Alignment.CENTER,
                padding=ft.Padding.symmetric(vertical=10), border_radius=20, bgcolor=bg, ink=True,
            ))
        super().__init__(content=ft.Row(btns, spacing=4), height=80,
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            bgcolor=COLORS["surface"] if not dark else PALETA["bg_card"],
            border=ft.Border.only(top=ft.BorderSide(1, COLORS["outline"] if not dark else PALETA["divider"])),
        )


class QuickAction(ft.Container):
    def __init__(self, icon, label, color, on_click, dark: bool):
        super().__init__(content=ft.Column([
            C(content=I(icon, size=24, color=color), width=52, height=52, border_radius=18,
              bgcolor=ft.Colors.with_opacity(0.12, color), alignment=ft.Alignment.CENTER),
            T(label, size=11, weight=ft.FontWeight.W_500,
              color=COLORS["on_surface"] if not dark else PALETA["text_primary"], text_align=ft.TextAlign.CENTER),
        ], spacing=6, tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            on_click=on_click, ink=True, expand=True)


class SectionTitle(ft.Container):
    def __init__(self, title, action_text=None, on_action=None, dark: bool = True):
        tc = PALETA["text_primary"] if dark else COLORS["on_surface"]
        super().__init__(content=ft.Row([
            T(title, size=18, weight=ft.FontWeight.W_700, color=tc, expand=True),
            *([ft.TextButton(action_text, on_click=on_action, style=ft.ButtonStyle(color=COLORS["primary"] if not dark else PALETA["accent_lime"]))] if action_text else []),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), padding=ft.Padding.symmetric(horizontal=16, vertical=8))


class Card(ft.Container):
    def __init__(self, content, dark: bool, on_click=None, padding=16):
        super().__init__(content=content, bgcolor=PALETA["bg_card"] if dark else COLORS["surface"],
            border_radius=16, padding=ft.Padding.all(padding),
            border=ft.Border.all(1, PALETA["divider"] if dark else COLORS["outline"]),
            on_click=on_click, ink=True if on_click else None)


class HoraDoLixoApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.state = AppState()
        self.state.subscribe(self._on_state_change)
        self.current_tab = 0
        self.dark = self.state.dark_mode
        self.sub_screen = None
        self._setup_page()
        self._build_ui()
        self.page.run_task(self._auto_refresh_loop)

    def _setup_page(self):
        self.page.title = "Hora do Lixo"
        self.page.theme_mode = ft.ThemeMode.DARK if self.dark else ft.ThemeMode.LIGHT
        self.page.window_width = 393
        self.page.window_height = 852
        self.page.window_min_width = 360
        self.page.window_min_height = 700
        self.page.window_resizable = True
        self.page.padding = 0
        self.page.bgcolor = PALETA["bg_primary"] if self.dark else COLORS["background"]
        self.page.fonts = {"Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"}
        self.page.theme = ft.Theme(font_family="Inter")

    def _on_state_change(self):
        try: self.page.update()
        except Exception: pass

    def _build_ui(self):
        if not self.state.onboarding_feito:
            self.content_area = ft.Container(content=S.tela_onboarding(self.state, self.page, self._concluir_onboarding),
                expand=True, bgcolor=PALETA["bg_primary"] if self.dark else COLORS["background"])
            self.page.add(self.content_area)
            return
        self.content_area = ft.Container(content=self._build_screen(0), expand=True,
            bgcolor=PALETA["bg_primary"] if self.dark else COLORS["background"])
        self.nav_bar = NavBar(self.current_tab, self._on_tab_change, self.dark)
        main_layout = ft.Column([ft.Container(content=self.content_area, expand=True), self.nav_bar], spacing=0, expand=True)
        self.page.add(main_layout)

    def _concluir_onboarding(self, nome, bairro_nome, rua):
        print(f"[DEBUG] _concluir_onboarding: nome={nome}, bairro={bairro_nome}, rua={rua}")
        if nome: self.state.set_nome(nome)
        if bairro_nome:
            bid = next((b["id"] for b in BAIRROS if b["nome"] == bairro_nome), self.state.bairro_id)
            self.state.set_bairro(bid)
        if rua: self.state.set_rua(rua)
        self.state.concluir_onboarding()
        self.page.controls.clear()
        self._build_ui()
        self.page.update()

    def _on_tab_change(self, idx: int):
        self.current_tab = idx
        self.sub_screen = None
        self.content_area.content = self._build_screen(idx)
        self.nav_bar.content = NavBar(idx, self._on_tab_change, self.dark).content
        self.page.update()

    def _open_sub(self, view: ft.Control):
        self.sub_screen = view
        self.content_area.content = ft.Container(content=view, expand=True)
        self.page.update()

    def _close_sub(self):
        self.sub_screen = None
        self.content_area.content = self._build_screen(self.current_tab)
        self.page.update()

    def _build_screen(self, idx: int):
        builders = [self._build_home, self._build_schedule, self._build_map, self._build_alerts, self._build_profile]
        return ft.Container(content=builders[idx](), expand=True)

    def _build_home(self):
        st = self.state; bairro = st.get_bairro(); caminhao = st.caminhao; dark = self.dark
        cor_status = {"aguardando": COLORS["info"], "em_rota": COLORS["primary"], "concluido": COLORS["success"], "sem_coleta": COLORS["outline"]}.get(caminhao.get("status"), COLORS["primary"])
        truck_card = Card(ft.Column([
            ft.Row([C(content=I(ft.Icons.LOCAL_SHIPPING_ROUNDED, size=22, color=cor_status), width=48, height=48, border_radius=16,
                  bgcolor=ft.Colors.with_opacity(0.14, cor_status), alignment=ft.Alignment.CENTER),
                ft.Column([T("Caminhão de coleta", size=15, weight=ft.FontWeight.W_700, color=S.texto_cor(dark)),
                    T(caminhao.get("msg", ""), size=12, color=S.texto2_cor(dark))], spacing=2, expand=True),
                C(content=ft.Column([T(caminhao.get("eta", "--"), size=16, weight=ft.FontWeight.W_700, color=cor_status),
                    T("tempo", size=10, color=S.texto2_cor(dark))], spacing=0, tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.Colors.with_opacity(0.12, cor_status), border_radius=14, padding=ft.Padding.symmetric(horizontal=16, vertical=10)),
            ], spacing=12), ft.Container(height=10),
            ft.ProgressBar(value=caminhao.get("progresso", 0), bgcolor=S.divider_cor(dark), color=cor_status, height=8, border_radius=4),
            ft.Container(height=8), ft.Row([T(f"Rua atual: {caminhao.get('rua_atual') or '-'}", size=12, color=S.texto2_cor(dark), expand=True),
                T(f"{caminhao.get('ruas_restantes', 0)} ruas restantes", size=12, color=S.texto2_cor(dark))], spacing=8),
            *([ft.Container(content=ft.Row([I(ft.Icons.WARNING_AMBER_ROUNDED, size=16, color=PALETA["accent_orange"]),
                T(f"Atraso de {caminhao['atraso']} min - {caminhao.get('causa', 'trânsito')}", size=12, color=PALETA["accent_orange"], expand=True)], spacing=8),
                bgcolor=ft.Colors.with_opacity(0.10, PALETA["accent_orange"]), border_radius=10, padding=ft.Padding.symmetric(horizontal=12, vertical=8))
            ] if caminhao.get("atraso") else []),
        ]), dark, padding=16)

        agenda = ft.Column(spacing=8)
        for ev in st.coletas[:3]: agenda.controls.append(self._linha_agenda(ev))

        return ft.ListView(controls=[
            C(content=ft.Row([ft.Column([T(f"Olá, {st.nome_usuario}" if st.nome_usuario else "Bom dia!", size=14, color=S.texto2_cor(dark)),
                ft.Row([T(bairro["nome"], size=22, weight=ft.FontWeight.W_700, color=S.texto_cor(dark)),
                    I(ft.Icons.KEYBOARD_ARROW_DOWN, size=20, color=S.texto2_cor(dark))], spacing=4)], expand=True),
                ft.IconButton(icon=ft.Icons.NOTIFICATIONS_NONE, icon_color=S.texto2_cor(dark), icon_size=24,
                    on_click=lambda e: self._on_tab_change(3), tooltip="Alertas"),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER), padding=ft.Padding.only(left=16, top=12, right=16, bottom=8)),
            C(content=truck_card, padding=ft.Padding.symmetric(horizontal=16, vertical=4)),
            C(content=ft.Row([QuickAction(ft.Icons.ADD_ALERT, "Denunciar", COLORS["error"], lambda e: self._open_ocorrencia(), dark),
                QuickAction(ft.Icons.LOCAL_SHIPPING, "Coleta\nVolumosa", COLORS["primary"], lambda e: self._open_sub(S.tela_volumosos(self.state, self.page, self._salvar_volumoso, self._close_sub)), dark),
                QuickAction(ft.Icons.SCHEDULE, "Agendar", PALETA["accent_orange"], lambda e: self._open_sub(S.tela_volumosos(self.state, self.page, self._salvar_volumoso, self._close_sub)), dark),
                QuickAction(ft.Icons.MAP, "Ver Mapa", COLORS["info"], lambda e: self._on_tab_change(2), dark)], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                padding=ft.Padding.symmetric(horizontal=16, vertical=12)),
            C(content=ft.Column([SectionTitle("Próximas coletas", "Ver tudo", lambda e: self._on_tab_change(1), dark),
                ft.Container(height=8), agenda]), padding=ft.Padding.symmetric(horizontal=16, vertical=8)),
            C(content=ft.Column([SectionTitle("Pontos seletivos", "Ver mapa", lambda e: self._on_tab_change(2), dark),
                ft.Container(height=8), *[self._ponto_row(p) for p in pontos_por_bairro(st.bairro_id)[:3]]]),
                padding=ft.Padding.symmetric(horizontal=16, vertical=8)),
            ft.Container(height=90)], spacing=0, padding=ft.Padding.only(top=4), expand=True)

    def _linha_agenda(self, ev: ColetaEvento):
        dark = self.dark; ativo = ev.dia_semana == datetime.now().weekday()
        cor_t = PALETA["accent_lime"] if ev.tipo != "sem_coleta" else PALETA["text_secondary"]
        return Card(ft.Row([ft.Container(content=ft.Column([T(DIAS[ev.dia_semana].upper(), size=10, weight=ft.FontWeight.BOLD, color=PALETA["text_secondary"]),
            T(ev.horario, size=14, weight=ft.FontWeight.BOLD, color=cor_t)], spacing=1, tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=60, padding=ft.Padding.symmetric(vertical=8), border_radius=12,
            bgcolor=ft.Colors.with_opacity(0.12, PALETA["accent_lime"] if ativo else ft.Colors.GREY)),
            ft.VerticalDivider(width=14, color=S.divider_cor(dark)),
            ft.Column([ft.Row([I(S.TIPO_ICONE.get(ev.tipo, ft.Icons.CIRCLE), size=16, color=cor_t),
                T(S.TIPO_LABEL.get(ev.tipo, ev.tipo), size=13, weight=ft.FontWeight.W_600, color=S.texto_cor(dark)),
                T(" · " + DIAS_FULL[ev.dia_semana], size=12, color=S.texto2_cor(dark))], spacing=4, tight=True),
            T(f"{ev.horario} · {ev.rua_atual if ev.status == 'em_rota' else 'sua rua'}", size=11, color=S.texto2_cor(dark))], spacing=2, expand=True),
            T(S.STATUS_LABEL.get(ev.status, ev.status), size=11, weight=ft.FontWeight.W_600, color=S.cor_status(ev.status))], spacing=12), dark, padding=14)

    def _ponto_row(self, ponto):
        dark = self.dark
        return Card(ft.Row([C(content=I(S.TIPO_ICONE.get(ponto["tipo"], ft.Icons.LOCATION_ON), size=20, color=S.tipo_badge(ponto["tipo"])),
            width=44, height=44, border_radius=14, bgcolor=ft.Colors.with_opacity(0.12, S.tipo_badge(ponto["tipo"])), alignment=ft.Alignment.CENTER),
            ft.Column([T(ponto["nome"], size=13, weight=ft.FontWeight.W_600, color=S.texto_cor(dark)),
                T(f"{ponto['dist']} · {S.TIPO_LABEL.get(ponto['tipo'], ponto['tipo'])}", size=11, color=S.texto2_cor(dark))], spacing=1, expand=True),
            I(ft.Icons.CHEVRON_RIGHT, size=20, color=S.texto2_cor(dark))], spacing=12), dark, on_click=lambda e: self._open_sub(S.tela_mapa_bairro(self.state, self.page, self._close_sub)), padding=16)

    def _build_schedule(self):
        dark = self.dark; st = self.state
        return ft.ListView(controls=[C(content=ft.Row([ft.Column([T("Agenda de coletas", size=18, weight=ft.FontWeight.W_700, color=S.texto_cor(dark)),
            T(f"{st.get_bairro()['nome']} · {st.rua}", size=12, color=S.texto2_cor(dark))], expand=True),
            ft.IconButton(ft.Icons.LOCATION_ON, icon_color=S.texto2_cor(dark), on_click=lambda e: self._open_sub(S.tela_selecao_rua(st, self.page, self._mudar_rua, self._close_sub)), tooltip="Trocar rua")],
            spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER), padding=ft.Padding.symmetric(horizontal=16, vertical=12)),
            C(content=ft.Column([SectionTitle("Próximos 14 dias", dark=dark), ft.Container(height=8),
                ft.Column([self._linha_agenda(ev) for ev in st.coletas], spacing=8)]), padding=ft.Padding.symmetric(horizontal=16, vertical=8)),
            ft.Container(height=90)], spacing=0, expand=True, padding=ft.Padding.only(top=4))

    def _mudar_rua(self, rua):
        self.state.set_rua(rua); self._close_sub()

    def _build_map(self):
        dark = self.dark; st = self.state; bairro = st.get_bairro()
        return ft.ListView(controls=[C(content=ft.Row([ft.Column([T("Mapa do bairro", size=18, weight=ft.FontWeight.W_700, color=S.texto_cor(dark)),
            T(f"{bairro['nome']} · {st.rua}", size=12, color=S.texto2_cor(dark))], expand=True),
            ft.IconButton(ft.Icons.LOCATION_ON, icon_color=S.texto2_cor(dark), on_click=lambda e: self._open_sub(S.tela_selecao_rua(st, self.page, self._mudar_rua, self._close_sub)))],
            spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER), padding=ft.Padding.symmetric(horizontal=16, vertical=12)),
            C(content=ft.Column([SectionTitle("Pontos seletivos", "Ver todos", lambda e: self._open_sub(S.tela_mapa_bairro(st, self.page, self._close_sub)), dark),
                ft.Container(height=8), *[self._ponto_row(p) for p in pontos_por_bairro(st.bairro_id)]]),
                padding=ft.Padding.symmetric(horizontal=16, vertical=8)), ft.Container(height=90)], spacing=0, expand=True, padding=ft.Padding.only(top=4))

    def _build_alerts(self):
        dark = self.dark; st = self.state
        return ft.ListView(controls=[C(content=ft.Row([ft.Column([T("Alertas & Notificações", size=18, weight=ft.FontWeight.W_700, color=S.texto_cor(dark)),
            T(f"{len(st.notificacoes)} notificações", size=12, color=S.texto2_cor(dark))], expand=True)],
            spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER), padding=ft.Padding.symmetric(horizontal=16, vertical=12)),
            C(content=ft.Column([SectionTitle("Preferências", dark=dark), ft.Container(height=8),
                self._notif_toggle("Push", "notif_push", "Receber notificações de coleta", dark),
                self._notif_toggle("15 min", "alerta_15min", "Aviso 15 min antes da coleta", dark),
                self._notif_toggle("Atraso", "notif_atraso", "Alertar quando caminhão atrasar", dark),
                self._notif_toggle("Concluída", "notif_concluida", "Confirmar quando coleta finalizar", dark),
                self._notif_toggle("Semanal", "notif_semanal", "Resumo semanal de coletas", dark)]), padding=ft.Padding.symmetric(horizontal=16, vertical=8)),
            C(content=ft.Column([SectionTitle("Histórico", dark=dark), ft.Container(height=8),
                *([self._notif_item(n, dark) for n in st.notificacoes] if st.notificacoes else [
                    S.item_vazio(dark, ft.Icons.NOTIFICATIONS_NONE, "Nenhuma notificação", "As notificações aparecerão aqui")])]),
                padding=ft.Padding.symmetric(horizontal=16, vertical=8)), ft.Container(height=90)], spacing=0, expand=True, padding=ft.Padding.only(top=4))

    def _notif_toggle(self, label, key, subtitle, dark):
        st = self.state
        val = st.alerta_15min if key == "alerta_15min" else st.notif_prefs.get(key, True)
        return Card(ft.Row([ft.Column([T(label, size=14, weight=ft.FontWeight.W_500, color=S.texto_cor(dark)),
            T(subtitle, size=11, color=S.texto2_cor(dark))], spacing=2, expand=True),
            ft.Switch(value=val, on_change=lambda e, k=key: self._toggle_notif(k, e.control.value),
                active_color=PALETA["accent_lime"], inactive_thumb_color=ft.Colors.GREY_400,
                inactive_track_color=ft.Colors.with_opacity(0.3, ft.Colors.GREY))], spacing=14), dark, padding=16)

    def _toggle_notif(self, key, val):
        if key == "alerta_15min": self.state.toggle_alerta_15min(val)
        else: self.state.toggle_notif(key, val)

    def _notif_item(self, notif, dark):
        return Card(ft.Row([C(content=I(S.TIPO_ICONE.get(notif.tipo, ft.Icons.INFO), size=18, color=S.cor_status(notif.tipo)),
            width=40, height=40, border_radius=12, bgcolor=ft.Colors.with_opacity(0.12, S.cor_status(notif.tipo)), alignment=ft.Alignment.CENTER),
            ft.Column([T(notif.titulo, size=13, weight=ft.FontWeight.W_600, color=S.texto_cor(dark)),
                T(notif.mensagem, size=11, color=S.texto2_cor(dark)), T(notif.horario, size=10, color=S.texto2_cor(dark))], spacing=1, expand=True)], spacing=12), dark, padding=16)

    def _build_profile(self):
        dark = self.dark; st = self.state
        return ft.ListView(controls=[C(content=ft.Row([ft.Column([T("Perfil & Configurações", size=18, weight=ft.FontWeight.W_700, color=S.texto_cor(dark)),
            T("Gerencie sua conta e preferências", size=12, color=S.texto2_cor(dark))], expand=True)],
            spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER), padding=ft.Padding.symmetric(horizontal=16, vertical=12)),
            C(content=ft.Column([SectionTitle("Conta", dark=dark), ft.Container(height=8),
                ft.TextField(label="Nome", value=st.nome_usuario, hint_text="Seu nome", on_change=lambda e: self.state.set_nome(e.control.value),
                    color=S.texto_cor(dark), label_style=ft.TextStyle(color=S.texto2_cor(dark), size=12),
                    border_radius=12, border_color=S.divider_cor(dark), focused_border_color=PALETA["accent_lime"], dense=True),
                ft.Container(height=12), ft.Dropdown(label="Bairro", value=st.get_bairro()["nome"],
                    options=[ft.dropdown.Option(b["nome"]) for b in BAIRROS],
                    on_select=lambda e: self.state.set_bairro(next(b["id"] for b in BAIRROS if b["nome"] == e.control.value)),
                    border_color=S.divider_cor(dark), focused_border_color=PALETA["accent_lime"],
                    text_style=ft.TextStyle(color=S.texto_cor(dark)), label_style=ft.TextStyle(color=S.texto2_cor(dark)), dense=True),
                ft.Container(height=12), ft.Dropdown(label="Rua de referência", value=st.rua,
                    options=[ft.dropdown.Option(r) for r in RUAS],
                    on_select=lambda e: self.state.set_rua(e.control.value),
                    border_color=S.divider_cor(dark), focused_border_color=PALETA["accent_lime"],
                    text_style=ft.TextStyle(color=S.texto_cor(dark)), label_style=ft.TextStyle(color=S.texto2_cor(dark)), dense=True)]),
                padding=ft.Padding.symmetric(horizontal=16, vertical=8)),
            C(content=ft.Column([SectionTitle("Aparência", dark=dark), ft.Container(height=8),
                Card(ft.Row([ft.Column([T("Tema escuro", size=14, weight=ft.FontWeight.W_500, color=S.texto_cor(dark)),
                    T("Alterna entre claro e escuro", size=11, color=S.texto2_cor(dark))], spacing=2, expand=True),
                    ft.Switch(value=st.dark_mode, on_change=lambda e: self._toggle_dark(e.control.value), active_color=PALETA["accent_lime"])], spacing=14), dark, padding=16)]),
                padding=ft.Padding.symmetric(horizontal=16, vertical=8)),
            C(content=ft.Column([SectionTitle("Dados & Privacidade", dark=dark), ft.Container(height=8),
                Card(ft.Row([ft.Column([T("Exportar dados (CSV)", size=14, weight=ft.FontWeight.W_500, color=S.texto_cor(dark)),
                    T("Baixar histórico para envio à SEMULSP", size=11, color=S.texto2_cor(dark))], spacing=2, expand=True),
                    I(ft.Icons.DOWNLOAD, size=24, color=COLORS["primary"])], spacing=14), dark, on_click=lambda e: self._exportar_csv(), padding=16),
                ft.Container(height=12), Card(ft.Row([ft.Column([T("Limpar dados locais", size=14, weight=ft.FontWeight.W_500, color=PALETA["accent_red"]),
                    T("Remove histórico e cache do app", size=11, color=S.texto2_cor(dark))], spacing=2, expand=True),
                    I(ft.Icons.DELETE_SWEEP, size=24, color=PALETA["accent_red"])], spacing=14), dark, on_click=lambda e: self._limpar_dados(), padding=16)]),
                padding=ft.Padding.symmetric(horizontal=16, vertical=8)), ft.Container(height=90)], spacing=0, expand=True, padding=ft.Padding.only(top=4))

    def _toggle_dark(self, val):
        self.state.toggle_dark(val); self.dark = val
        self.page.theme_mode = ft.ThemeMode.DARK if val else ft.ThemeMode.LIGHT
        self.page.bgcolor = PALETA["bg_primary"] if val else COLORS["background"]
        self.page.controls.clear(); self._build_ui(); self.page.update()

    def _exportar_csv(self):
        import csv, os; st = self.state
        path = os.path.join(os.path.expanduser("~"), "horadolixo_export.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Data", "Tipo", "Endereço", "Bairro", "Rua", "Descrição", "Status", "Protocolo"])
            for o in st.ocorrencias: w.writerow([o.horario, S.TIPO_LABEL.get(o.tipo, o.tipo), o.endereco, o.bairro, o.rua, o.descricao, S.STATUS_LABEL.get(o.status, o.status), o.protocolo])
            for s in st.solicitacoes: w.writerow([s.horario, "Volumoso", s.endereco, s.bairro, s.rua, s.obs, S.STATUS_LABEL.get(s.status, s.status), s.protocolo])
            for h in st.historico: w.writerow([h.horario, S.TIPO_LABEL.get(h.tipo, h.tipo), h.endereco, h.bairro, h.rua, "", S.STATUS_LABEL.get(h.status, h.status), ""])
        self._show_snack(f"Exportado: {path}")

    def _limpar_dados(self):
        self.state._resetar_tudo(); self.page.controls.clear(); self._build_ui(); self.page.update()

    def _open_ocorrencia(self):
        self._open_sub(S.tela_ocorrencia(self.state, self.page, self._salvar_ocorrencia, self._close_sub))

    def _salvar_ocorrencia(self, tipo, endereco, rua, descricao, foto):
        self.state.add_ocorrencia(tipo, endereco, rua, descricao, foto)
        self._show_snack("Denúncia registrada com protocolo!"); self._close_sub()

    def _salvar_volumoso(self, tipo_item, data, qtd, obs):
        self.state.add_solicitacao(tipo_item, data, qtd, obs)
        self._show_snack("Coleta agendada com protocolo!"); self._close_sub()

    def _show_snack(self, msg):
        self.page.snack_bar = ft.SnackBar(content=T(msg), duration=3000)
        self.page.snack_bar.open = True; self.page.update()

    async def _auto_refresh_loop(self):
        while True:
            await asyncio.sleep(30); self.state.refresh_all()
            try: self.page.update()
            except Exception: pass


def main(page: ft.Page):
    HoraDoLixoApp(page)


if __name__ == "__main__":
    ft.run(main)
