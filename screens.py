"""Telas extras do Hora do Lixo conforme APP.MD."""

import random
import math
import urllib.parse
from datetime import datetime, timedelta

import flet as ft

from data import (
    BAIRROS, DIAS, DIAS_FULL, PALETA, PONTOS_SELETIVOS, RUAS,
    ColetaEvento, Notificacao, Ocorrencia, Solicitacao,
)

TIPO_ICONE = {
    "comum": ft.Icons.DELETE_OUTLINE,
    "reciclavel": ft.Icons.RECYCLING,
    "organico": ft.Icons.COMPOST,
    "volumoso": ft.Icons.CHAIR,
    "sem_coleta": ft.Icons.REMOVE_CIRCLE_OUTLINE,
    "lixo_acumulado": ft.Icons.WARNING_AMBER_ROUNDED,
    "descarte_irregular": ft.Icons.DELETE_FOREVER,
    "ponto_vistoriado": ft.Icons.LOCATION_SEARCHING,
    "coleta_comum": ft.Icons.DELETE_OUTLINE,
    "coleta_reciclavel": ft.Icons.RECYCLING,
}

TIPO_LABEL = {
    "comum": "Coleta comum",
    "reciclavel": "Reciclável",
    "organico": "Orgânico",
    "volumoso": "Volumoso",
    "sem_coleta": "Sem coleta",
    "lixo_acumulado": "Lixo acumulado",
    "descarte_irregular": "Descarte irregular",
    "ponto_vistoriado": "Ponto vistoriado",
}

STATUS_LABEL = {
    "pendente": "Pendente",
    "em_rota": "Em rota",
    "concluido": "Concluída",
    "nao_coletada": "Não coletada",
    "sem_coleta": "Sem coleta",
    "em_analise": "Em análise",
    "agendada": "Agendada",
    "solicitada": "Solicitada",
    "concluida": "Concluída",
    "atrasada": "Atrasada",
    "cancelada": "Cancelada",
}

STATUS_COR = {
    "pendente": PALETA["accent_lime"],
    "em_rota": PALETA["accent_lime"],
    "concluido": PALETA["accent_lime"],
    "concluida": PALETA["accent_lime"],
    "nao_coletada": PALETA["accent_red"],
    "sem_coleta": PALETA["text_secondary"],
    "em_analise": PALETA["accent_orange"],
    "agendada": PALETA["accent_lime"],
    "solicitada": PALETA["accent_lime"],
    "atrasada": PALETA["accent_orange"],
    "cancelada": PALETA["accent_red"],
}


def cor_status(status):
    return STATUS_COR.get(status, PALETA["text_secondary"])


def card_bg(dark):
    return PALETA["bg_card"] if dark else PALETA["card_light"]


def texto_cor(dark):
    return PALETA["text_primary"] if dark else PALETA["text_light"]


def texto2_cor(dark):
    return PALETA["text_secondary"] if dark else PALETA["text_light_2"]


def divider_cor(dark):
    return PALETA["divider"] if dark else "#E3E8E4"


def tipo_badge(tipo):
    if tipo in ("reciclavel",):
        return ft.Colors.BLUE_400
    if tipo in ("organico",):
        return ft.Colors.GREEN_400
    if tipo in ("comum",):
        return ft.Colors.AMBER_400
    if tipo in ("volumoso",):
        return ft.Colors.ORANGE_400
    if tipo in ("sem_coleta",):
        return ft.Colors.GREY_500
    if tipo in ("lixo_acumulado",):
        return ft.Colors.RED_400
    if tipo in ("descarte_irregular",):
        return ft.Colors.RED_300
    if tipo in ("ponto_vistoriado",):
        return ft.Colors.PURPLE_300
    return ft.Colors.BLUE_GREY_300


def badge(tipo):
    return ft.Container(
        content=ft.Row([
            ft.Icon(TIPO_ICONE.get(tipo, ft.Icons.CIRCLE), color=tipo_badge(tipo), size=13),
            ft.Text(TIPO_LABEL.get(tipo, tipo), size=11, color=ft.Colors.BLACK_87, weight=ft.FontWeight.W_600),
        ], spacing=4, tight=True),
        bgcolor=ft.Colors.with_opacity(0.14, tipo_badge(tipo)),
        border_radius=8,
        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
    )


def card(dark, content, padding=14, on_click=None):
    return ft.Container(
        content=content,
        bgcolor=card_bg(dark),
        border_radius=16,
        padding=ft.Padding.all(padding),
        border=ft.Border.all(1, divider_cor(dark)),
        on_click=on_click,
        ink=True if on_click else None,
    )


def titulo_secao(dark, texto, subtitle=None):
    return ft.Column([
        ft.Text(texto, size=17, weight=ft.FontWeight.BOLD, color=texto_cor(dark)),
        *([ft.Text(subtitle, size=12, color=texto2_cor(dark))] if subtitle else []),
    ], spacing=2, tight=True)


def campo_texto(dark, label, hint_text="", password=False, icon=None, dense=False):
    return ft.TextField(
        label=label,
        hint=hint,
        password=password,
        dense=dense,
        visible_password=False,
        color=texto_cor(dark),
        label_style=ft.TextStyle(color=texto2_cor(dark), size=12),
        hint_style=ft.TextStyle(color=texto2_cor(dark), size=12),
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK if dark else ft.Colors.WHITE),
        border_radius=12,
        prefix_icon=icon,
        border_color=divider_cor(dark),
        focused_border_color=PALETA["accent_lime"],
    )


def botao(dark, texto, on_click=None, icon=None, bg=None, fg=None, full=False, outline=False):
    cores_bg = bg or PALETA["accent_green"]
    cores_fg = fg or ft.Colors.WHITE
    return ft.Button(
        content=ft.Row([
            *([ft.Icon(icon, size=17, color=cores_fg)] if icon else []),
            ft.Text(texto, size=13, weight=ft.FontWeight.W_600, color=cores_fg),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=6, tight=True),
        on_click=on_click,
        bgcolor=cores_bg,
        color=cores_fg,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            elevation=0,
            padding=ft.Padding.symmetric(horizontal=24, vertical=12),
        ),
    )


def item_vazio(dark, icone, texto, subtexto=""):
    return ft.Container(
        content=ft.Column([
            ft.Icon(icone, size=44, color=texto2_cor(dark)),
            ft.Text(texto, size=14, weight=ft.FontWeight.W_600, color=texto_cor(dark)),
            *([ft.Text(subtexto, size=12, color=texto2_cor(dark))] if subtexto else []),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
        padding=ft.Padding.symmetric(vertical=28),
        bgcolor=card_bg(dark),
        border_radius=16,
        border=ft.Border.all(1, divider_cor(dark)),
    )


def linha_agenda(dark, evento: ColetaEvento):
    hoje = datetime.now().weekday()
    dia_sel = evento.dia_semana
    ativo = dia_sel == hoje
    cor_t = PALETA["accent_lime"] if evento.tipo != "sem_coleta" else PALETA["text_secondary"]
    return ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text(DIAS[dia_sel].upper(), size=10, weight=ft.FontWeight.BOLD, color=PALETA["text_secondary"]),
                    ft.Text(evento.horario, size=13, weight=ft.FontWeight.BOLD, color=cor_t),
                ], spacing=1, tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=54, padding=ft.Padding.symmetric(vertical=6), border_radius=10,
                bgcolor=ft.Colors.with_opacity(0.12, PALETA["accent_lime"] if ativo else ft.Colors.GREY),
            ),
            ft.VerticalDivider(width=12, color=divider_cor(dark)),
            ft.Column([
                ft.Row([
                    ft.Icon(TIPO_ICONE.get(evento.tipo, ft.Icons.CIRCLE), size=15, color=cor_t),
                    ft.Text(TIPO_LABEL.get(evento.tipo, evento.tipo), size=13, weight=ft.FontWeight.W_600, color=texto_cor(dark)),
                    ft.Text(" · " + DIAS_FULL[dia_sel], size=12, color=texto2_cor(dark)),
                ], spacing=4, tight=True),
                ft.Text(
                    f"{evento.horario} · {evento.rua_atual if evento.status == 'em_rota' else 'sua rua'}",
                    size=11, color=texto2_cor(dark),
                ),
            ], spacing=2, tight=True, expand=True),
            ft.Container(
                content=ft.Text(STATUS_LABEL.get(evento.status, evento.status), size=10, weight=ft.FontWeight.W_600,
                                color=ft.Colors.BLACK_87 if cor_status(evento.status) != PALETA["text_secondary"] else PALETA["text_secondary"]),
                bgcolor=ft.Colors.with_opacity(0.15, cor_status(evento.status)),
                border_radius=8, padding=ft.Padding.symmetric(horizontal=7, vertical=3),
            ),
        ], spacing=8),
        bgcolor=card_bg(dark),
        border_radius=14,
        padding=ft.Padding.all(12),
        border=ft.Border.all(1, PALETA["accent_green"] if ativo else divider_cor(dark)),
    )


def make_screen(dark, controls, padding=None, **kwargs):
    return ft.Container(
        content=ft.ListView(controls=controls, spacing=0, expand=True),
        bgcolor=PALETA["bg_primary"] if dark else PALETA["bg_light"],
        padding=padding or ft.Padding.symmetric(horizontal=16, vertical=14),
    )


def make_view(dark, controls):
    return ft.View(
        controls=controls,
        bgcolor=PALETA["bg_primary"] if dark else PALETA["bg_light"],
        padding=ft.Padding.symmetric(horizontal=16, vertical=14),
    )


def tela_onboarding(state, page, ao_continuar):
    dark = state.dark_mode
    nome = ft.TextField(
        label="Como podemos te chamar?",
        hint_text="Seu nome",
        color=texto_cor(dark),
        label_style=ft.TextStyle(color=texto2_cor(dark), size=12),
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
        border_radius=12, border_color=divider_cor(dark), focused_border_color=PALETA["accent_lime"],
    )
    sel_bairro = ft.Dropdown(
        label="Seu bairro",
        value=state.get_bairro()["nome"],
        options=[ft.dropdown.Option(b["nome"]) for b in BAIRROS],
        border_color=divider_cor(dark),
        focused_border_color=PALETA["accent_lime"],
        text_style=ft.TextStyle(color=texto_cor(dark)),
        label_style=ft.TextStyle(color=texto2_cor(dark)),
    )
    sel_rua = ft.Dropdown(
        label="Rua de referência",
        value=state.rua,
        options=[ft.dropdown.Option(r) for r in RUAS],
        border_color=divider_cor(dark),
        focused_border_color=PALETA["accent_lime"],
        text_style=ft.TextStyle(color=texto_cor(dark)),
        label_style=ft.TextStyle(color=texto2_cor(dark)),
    )
    
    def on_comecar(e):
        print(f"[DEBUG] on_comecar chamado: nome={nome.value}, bairro={sel_bairro.value}, rua={sel_rua.value}")
        ao_continuar(nome.value, sel_bairro.value, sel_rua.value)
    
    return ft.Container(
        content=ft.Column([
            ft.Container(height=40),
            ft.Row([
                ft.Container(content=ft.Icon(ft.Icons.DELETE_OUTLINE, color=PALETA["accent_lime"], size=30),
                             width=62, height=62, border_radius=18,
                             bgcolor=ft.Colors.with_opacity(0.15, PALETA["accent_lime"]),
                             alignment=ft.Alignment.CENTER),
                ft.Column([
                    ft.Text("Hora do Lixo", size=24, weight=ft.FontWeight.BOLD, color=texto_cor(dark)),
                    ft.Text("Manaus, AM", size=13, color=texto2_cor(dark)),
                ], spacing=1, tight=True, expand=True),
            ], spacing=12),
            ft.Container(height=24),
            ft.Text("Bem-vindo ao",
                    size=13, color=texto2_cor(dark)),
            ft.Text("Hora do Lixo", size=30, weight=ft.FontWeight.BOLD, color=texto_cor(dark)),
            ft.Container(height=8),
            ft.Text("Acompanhe a coleta de lixo da sua rua em tempo real, "
                    "agende volumosos e denuncie descarte irregular.",
                    size=13, color=texto2_cor(dark)),
            ft.Container(height=28),
            nome, sel_bairro, sel_rua,
            ft.Container(height=14),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ARROW_FORWARD, size=17, color=ft.Colors.WHITE),
                    ft.Text("Começar", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=6, tight=True),
                on_click=on_comecar,
                ink=True,
                bgcolor=PALETA["accent_green"],
                border_radius=12,
                padding=ft.Padding.symmetric(horizontal=24, vertical=12),
                alignment=ft.Alignment.CENTER,
            ),
        ], spacing=0),
        bgcolor=PALETA["bg_primary"] if dark else PALETA["bg_light"],
        padding=ft.Padding.symmetric(horizontal=20, vertical=16),
    )


def tela_selecao_rua(state, page, ao_confirmar):
    dark = state.dark_mode
    busca = ft.TextField(
        label="Buscar rua", hint_text="Digite o nome da rua",
        prefix_icon=ft.Icons.SEARCH,
        color=texto_cor(dark),
        label_style=ft.TextStyle(color=texto2_cor(dark), size=12),
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
        border_radius=12, border_color=divider_cor(dark), focused_border_color=PALETA["accent_lime"],
        on_change=lambda e: atualizar_lista(e.control.value),
    )
    lista = ft.Column(spacing=8)
    bairro = state.get_bairro()

    def item_rua(r):
        sel = r == state.rua
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=17, color=PALETA["accent_lime"] if sel else texto2_cor(dark)),
                ft.Text(r, size=13, weight=ft.FontWeight.W_600 if sel else ft.FontWeight.W_400, color=texto_cor(dark)),
                ft.Container(expand=True),
                ft.Icon(ft.Icons.CHECK_CIRCLE, size=18, color=PALETA["accent_lime"], visible=sel),
            ], spacing=10),
            bgcolor=ft.Colors.with_opacity(0.10, PALETA["accent_green"]) if sel else card_bg(dark),
            border_radius=12, padding=ft.Padding.all(12),
            border=ft.Border.all(1, PALETA["accent_green"] if sel else divider_cor(dark)),
            on_click=lambda e, r=r: ao_confirmar(r),
            ink=True,
        )

    def atualizar_lista(q):
        q = (q or "").lower().strip()
        items = [r for r in RUAS if not q or q in r.lower()]
        lista.controls = [item_rua(r) for r in items]
        page.update()

    atualizar_lista("")
    return make_screen(dark, [
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, icon_color=texto_cor(dark), on_click=lambda e: page.go("/home")),
                ft.Text("Selecionar rua", size=18, weight=ft.FontWeight.BOLD, color=texto_cor(dark), expand=True),
            ], spacing=4),
            ft.Container(height=10),
            card(dark, ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.MAP_OUTLINED, size=16, color=PALETA["accent_lime"]),
                    ft.Text(f"{bairro['nome']} · {bairro['zona']}", size=13, weight=ft.FontWeight.W_600, color=texto_cor(dark)),
                ], spacing=6),
                ft.Text("Coleta comum: Seg, Qua, Sex · Reciclável: Ter, Qui, Sáb",
                        size=11, color=texto2_cor(dark)),
            ], spacing=4)),
            ft.Container(height=12),
            busca,
            ft.Container(height=10),
            lista,
        ],
        padding=ft.Padding.symmetric(horizontal=16, vertical=14),
        vertical_scroll=ft.ScrollMode.AUTO,
    )


def tela_volumosos(state, page, ao_salvar, ao_voltar):
    dark = state.dark_mode
    tipos = [
        ("movel", "Móveis", ft.Icons.CHAIR),
        ("eletronico", "Eletrônicos", ft.Icons.DEVICES),
        ("branco", "Eletrodomésticos", ft.Icons.KITCHEN),
        ("madeira", "Madeira", ft.Icons.CARPENTER),
        ("ferro", "Ferro e metal", ft.Icons.HARDWARE),
        ("pneus", "Pneus", ft.Icons.TIRE_REPAIR),
        ("outros", "Outros", ft.Icons.CATEGORY),
    ]
    sel_tipo = ft.dropdown.Option("movel")
    grid = ft.Column(spacing=8)
    sel = {"v": "movel"}

    def chip_tipo(key, label, icone):
        ativo = sel["v"] == key
        return ft.Container(
            content=ft.Row([
                ft.Icon(icone, size=17, color=PALETA["accent_lime"] if ativo else texto2_cor(dark)),
                ft.Text(label, size=12, weight=ft.FontWeight.W_600 if ativo else ft.FontWeight.W_400, color=texto_cor(dark)),
            ], spacing=6, tight=True),
            bgcolor=ft.Colors.with_opacity(0.12, PALETA["accent_green"]) if ativo else card_bg(dark),
            border_radius=12, padding=ft.Padding.symmetric(horizontal=12, vertical=9),
            border=ft.Border.all(1, PALETA["accent_green"] if ativo else divider_cor(dark)),
            on_click=lambda e, k=key: trocar(k),
            ink=True,
        )

    def trocar(k):
        sel["v"] = k
        grid.controls = [ft.Row([chip_tipo(*t) for t in tipos[:3]], spacing=8),
                         ft.Row([chip_tipo(*t) for t in tipos[3:6]], spacing=8),
                         ft.Row([chip_tipo(*t) for t in tipos[6:]], spacing=8)]
        page.update()

    trocar("movel")
    data_pref = ft.TextField(
        label="Data preferida", hint_text="dd/mm/aaaa",
        color=texto_cor(dark),
        label_style=ft.TextStyle(color=texto2_cor(dark), size=12),
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
        border_radius=12, border_color=divider_cor(dark), focused_border_color=PALETA["accent_lime"],
    )
    qtd = ft.Dropdown(
        label="Quantidade", value="1 item",
        options=[ft.dropdown.Option(x) for x in ["1 item", "2 itens", "3 itens", "4+ itens"]],
        border_color=divider_cor(dark), focused_border_color=PALETA["accent_lime"],
        text_style=ft.TextStyle(color=texto_cor(dark)),
        label_style=ft.TextStyle(color=texto2_cor(dark)),
    )
    obs = ft.TextField(
        label="Observações", hint_text="Ex.: deixar na calçada, portão azul",
        multiline=True, min_lines=2, max_lines=4,
        color=texto_cor(dark),
        label_style=ft.TextStyle(color=texto2_cor(dark), size=12),
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
        border_radius=12, border_color=divider_cor(dark), focused_border_color=PALETA["accent_lime"],
    )
    return make_screen(dark, [
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, icon_color=texto_cor(dark), on_click=lambda e: ao_voltar()),
                ft.Text("Coleta de Volumosos", size=18, weight=ft.FontWeight.BOLD, color=texto_cor(dark), expand=True),
            ], spacing=4),
            ft.Container(height=6),
            ft.Text("Agende a retirada de itens volumosos. A equipe entra em contato "
                    "para confirmar o melhor horário.",
                    size=12, color=texto2_cor(dark)),
            ft.Container(height=14),
            ft.Text("Tipo de item", size=13, weight=ft.FontWeight.W_600, color=texto_cor(dark)),
            ft.Container(height=8),
            grid,
            ft.Container(height=14),
            data_pref, qtd, obs,
            ft.Container(height=16),
            botao(dark, "Solicitar coleta", icon=ft.Icons.EVENT_AVAILABLE,
                  on_click=lambda e: ao_salvar(sel["v"], data_pref.value, qtd.value, obs.value)),
        ],
        padding=ft.Padding.symmetric(horizontal=16, vertical=16),
        vertical_scroll=ft.ScrollMode.AUTO,
    )


def tela_ocorrencia(state, page, ao_salvar, ao_voltar):
    dark = state.dark_mode
    tipos = [
        ("lixo_acumulado", "Lixo acumulado", ft.Icons.WARNING_AMBER_ROUNDED),
        ("descarte_irregular", "Descarte irregular", ft.Icons.DELETE_FOREVER),
        ("ponto_vistoriado", "Ponto de descarte clandestino", ft.Icons.LOCATION_SEARCHING),
    ]
    sel = {"v": "lixo_acumulado"}
    grid = ft.Column(spacing=8)
    endereco = ft.TextField(
        label="Endereço", hint_text="Rua, número",
        prefix_icon=ft.Icons.LOCATION_ON_OUTLINED,
        color=texto_cor(dark),
        label_style=ft.TextStyle(color=texto2_cor(dark), size=12),
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
        border_radius=12, border_color=divider_cor(dark), focused_border_color=PALETA["accent_lime"],
    )
    desc = ft.TextField(
        label="Descrição", hint_text="Descreva o problema",
        multiline=True, min_lines=3, max_lines=5,
        color=texto_cor(dark),
        label_style=ft.TextStyle(color=texto2_cor(dark), size=12),
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
        border_radius=12, border_color=divider_cor(dark), focused_border_color=PALETA["accent_lime"],
    )
    foto_path = {"v": ""}
    preview = ft.Container(content=ft.Text("Nenhuma foto anexada", size=11, color=texto2_cor(dark)))
    coords = ft.Text(f"GPS: {state.get_bairro()['lat']:.4f}, {state.get_bairro()['lon']:.4f}",
                     size=11, color=texto2_cor(dark))

    def chip_tipo(key, label, icone):
        ativo = sel["v"] == key
        return ft.Container(
            content=ft.Row([
                ft.Icon(icone, size=17, color=PALETA["accent_lime"] if ativo else texto2_cor(dark)),
                ft.Text(label, size=12, weight=ft.FontWeight.W_600 if ativo else ft.FontWeight.W_400, color=texto_cor(dark)),
            ], spacing=6, tight=True),
            bgcolor=ft.Colors.with_opacity(0.12, PALETA["accent_green"]) if ativo else card_bg(dark),
            border_radius=12, padding=ft.Padding.symmetric(horizontal=12, vertical=9),
            border=ft.Border.all(1, PALETA["accent_green"] if ativo else divider_cor(dark)),
            on_click=lambda e, k=key: trocar(k),
            ink=True,
        )

    def trocar(k):
        sel["v"] = k
        grid.controls = [
            ft.Row([chip_tipo(*tipos[0]), chip_tipo(*tipos[1])], spacing=8),
            ft.Row([chip_tipo(*tipos[2])], spacing=8),
        ]
        page.update()

    def anexar_foto():
        async def handler(e):
            files = await ft.FilePicker.get_file_paths()
            if files:
                foto_path["v"] = files[0]
                preview.content = ft.Column([
                    ft.Icon(ft.Icons.IMAGE, size=20, color=PALETA["accent_lime"]),
                    ft.Text("Foto anexada", size=11, color=texto_cor(dark)),
                    ft.Text(files[0].split("\\")[-1].split("/")[-1], size=10, color=texto2_cor(dark)),
                ], spacing=4, tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                page.update()

        page.run_task(handler)

    trocar("lixo_acumulado")
    return make_screen(dark, [
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, icon_color=texto_cor(dark), on_click=lambda e: ao_voltar()),
                ft.Text("Nova ocorrência", size=18, weight=ft.FontWeight.BOLD, color=texto_cor(dark), expand=True),
            ], spacing=4),
            ft.Container(height=6),
            ft.Text("Registre problemas na coleta. Cada denúncia vira protocolo rastreável.",
                    size=12, color=texto2_cor(dark)),
            ft.Container(height=14),
            ft.Text("Tipo de ocorrência", size=13, weight=ft.FontWeight.W_600, color=texto_cor(dark)),
            ft.Container(height=8),
            grid,
            ft.Container(height=14),
            endereco, desc,
            ft.Container(height=10),
            ft.Row([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ADD_A_PHOTO_OUTLINED, size=16, color=PALETA["accent_lime"]),
                        ft.Text("Anexar foto", size=12, color=texto_cor(dark)),
                    ], spacing=6, tight=True),
                    bgcolor=card_bg(dark), border_radius=12,
                    padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                    border=ft.Border.all(1, divider_cor(dark)),
                    on_click=lambda e: anexar_foto(), ink=True,
                ),
                ft.Container(expand=True),
            ], spacing=10),
            ft.Container(height=6),
            preview,
            ft.Container(height=6),
            coords,
            ft.Container(height=16),
            botao(dark, "Enviar denúncia", icon=ft.Icons.SEND_ROUNDED,
                  on_click=lambda e: ao_salvar(sel["v"], endereco.value, desc.value, foto_path["v"])),
        ],
        padding=ft.Padding.symmetric(horizontal=16, vertical=16),
        vertical_scroll=ft.ScrollMode.AUTO,
    )



def _abrir_mapa_nativo(page, lat, lon, label="Local"):
    """Abre mapa nativo Android (Google Maps) via intent"""
    try:
        # Tenta Google Maps primeiro via intent geo:
        uri = f"geo:{lat},{lon}?q={lat},{lon}({urllib.parse.quote(label)})"
        page.launch_url(uri)
    except Exception as e:
        print(f"Erro ao abrir mapa nativo: {e}")
        # Fallback: OSM web
        try:
            page.launch_url(f"https://www.openstreetmap.org/#map=16/{lat}/{lon}")
        except:
            pass


def tela_mapa_bairro(state, page, ao_voltar):
    """Mapa com preview estático + abertura no navegador (OSM/Google Maps) - 100% funcional no Android"""
    dark = state.dark_mode
    bairro = state.get_bairro()
    pontos = [dict(p) for p in PONTOS_SELETIVOS]
    
    # Coordenadas do centro do bairro
    bairro_coords = {
        1: (-3.1190, -60.0217),   # Centro
        2: (-3.0878, -60.0156),   # Adrianópolis
        3: (-3.1389, -60.0217),   # Vila Betânia
        4: (-3.1000, -59.9800),   # Cidade Nova
        5: (-3.0500, -60.0500),   # Parque 10
        6: (-3.1500, -60.0000),   # Educandos
    }
    user_lat, user_lon = bairro_coords.get(state.bairro_id, (-3.1389, -60.0217))
    
    # URLs para abrir no navegador
    osm_url = f"https://www.openstreetmap.org/#map=15/{user_lat}/{user_lon}"
    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={user_lat},{user_lon}"
    
    # Tile estático do OpenStreetMap (preview)
    tile_size = 512
    zoom = 15
    
    def latlon_to_tile(lat, lon, z):
        n = 2.0 ** z
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n)
        return x, y
    
    tx, ty = latlon_to_tile(user_lat, user_lon, zoom)
    
    # Pega 3x3 tiles para cobrir a área
    tile_urls = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            tile_urls.append(f"https://tile.openstreetmap.org/{zoom}/{tx+dx}/{ty+dy}.png")
    
    # Preview do mapa (grid de tiles)
    tile_widgets = []
    for i, url in enumerate(tile_urls):
        row = i // 3
        col = i % 3
        tile_widgets.append(
            ft.Container(
                content=ft.Image(
                    src=url,
                    fit=ft.BoxFit.COVER,
                    width=tile_size//3,
                    height=tile_size//3,
                    error_content=ft.Icon(ft.Icons.MAP_OUTLINED, size=30, color=texto2_cor(dark)),
                ),
                width=tile_size//3,
                height=tile_size//3,
                border_radius=8 if (row == 1 and col == 1) else 0,
                border=ft.Border.all(1, divider_cor(dark)) if (row == 1 and col == 1) else None,
            )
        )
    
    mapa_preview = ft.Container(
        content=ft.Column([
            ft.Row(tile_widgets[0:3], spacing=0),
            ft.Row(tile_widgets[3:6], spacing=0),
            ft.Row(tile_widgets[6:9], spacing=0),
        ], spacing=0),
        border_radius=12,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        border=ft.Border.all(1, divider_cor(dark)),
        on_click=lambda e: _abrir_mapa_nativo(page, user_lat, user_lon, "Pontos seletivos - " + bairro["nome"]),
        ink=True,
        tooltip="Mapa do bairro - toque para abrir",
    )
    
    # Botões de ação - usam intent nativo Android
    def abrir_google_maps(e):
        _abrir_mapa_nativo(page, user_lat, user_lon, "Pontos seletivos - " + bairro["nome"])
    
    def abrir_osm(e):
        page.launch_url(osm_url)
    
    # Botões como Container - o texto está no content (Row com Text)
    btn_google = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.MAP_OUTLINED, size=18, color='#1976D2'),
            ft.Text("Abrir no Google Maps", size=13, weight=ft.FontWeight.W_600, color='#1976D2'),
        ], spacing=8, tight=True, alignment=ft.MainAxisAlignment.CENTER),
        on_click=abrir_google_maps,
        bgcolor=ft.Colors.with_opacity(0.12, '#1976D2'),
        border_radius=10,
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        border=ft.Border.all(1, '#1976D2'),
        ink=True,
        height=50,
        tooltip="Abrir no Google Maps",
    )
    
    btn_osm = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.PUBLIC, size=18, color=PALETA["accent_lime"]),
            ft.Text("OpenStreetMap", size=13, weight=ft.FontWeight.W_600, color=PALETA["accent_lime"]),
        ], spacing=8, tight=True, alignment=ft.MainAxisAlignment.CENTER),
        on_click=abrir_osm,
        bgcolor=ft.Colors.with_opacity(0.12, PALETA["accent_lime"]),
        border_radius=10,
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        border=ft.Border.all(1, PALETA["accent_lime"]),
        ink=True,
        height=50,
        tooltip="OpenStreetMap",
    )
    
    # Usar Column para garantir layout
    botoes_mapa = ft.Column([
        ft.Container(
            content=ft.Row([btn_google, btn_osm], spacing=10),
            padding=ft.Padding.symmetric(horizontal=0, vertical=6),
        ),
    ], spacing=0, tight=True)
    return make_screen(dark, [
        ft.Row([
            ft.IconButton(ft.Icons.ARROW_BACK, icon_color=texto_cor(dark), on_click=lambda e: ao_voltar()),
            ft.Text("Mapa do bairro", size=18, weight=ft.FontWeight.BOLD, color=texto_cor(dark), expand=True),
        ], spacing=4),
        ft.Container(height=8),
        ft.Text(f"{bairro['nome']} · {len(pontos)} pontos seletivos", size=12, color=texto2_cor(dark)),
        ft.Container(height=8),
        # Preview do mapa (clicável)
        ft.Container(
            content=ft.Column([
                ft.Text("Toque para abrir mapa completo", size=11, color=texto2_cor(dark), text_align=ft.TextAlign.CENTER),
                ft.Container(height=6),
                mapa_preview,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            border_radius=12, border=ft.Border.all(1, divider_cor(dark)),
        ),
        ft.Container(height=12),
        botoes_mapa,
        ft.Container(height=12),
        ft.Text("Pontos seletivos", size=14, weight=ft.FontWeight.W_600, color=texto_cor(dark)),
        ft.Container(height=8),
        *[card(dark, ft.Row([
            ft.Icon(TIPO_ICONE.get(p["tipo"], ft.Icons.CIRCLE), size=16, color=ft.Colors.with_opacity(0.9, tipo_badge(p["tipo"]))),
            ft.Column([
                ft.Text(p["nome"], size=13, weight=ft.FontWeight.W_600, color=texto_cor(dark)),
                ft.Text(f"{p['bairro']} · {p['dist']}", size=11, color=texto2_cor(dark)),
            ], spacing=2, tight=True, expand=True),
            ft.Container(content=ft.Text(p["dist"], size=11, color=PALETA["accent_lime"]),
                         bgcolor=ft.Colors.with_opacity(0.14, PALETA["accent_lime"]),
                         border_radius=8, padding=ft.Padding.symmetric(horizontal=8, vertical=3)),
        ], spacing=10)) for p in pontos],
    ], padding=ft.Padding.symmetric(horizontal=16, vertical=14))
def tela_feedback(state, page, ao_registrar, ao_voltar):
    dark = state.dark_mode
    sel = {"v": "sim"}
    opcoes = [
        ("sim", "Sim, coletado", ft.Icons.CHECK_CIRCLE),
        ("nao", "Não, não coletou", ft.Icons.CANCEL),
    ]
    linha = ft.Row([], spacing=10)

    def chip(key, label, icone):
        ativo = sel["v"] == key
        return ft.Container(
            content=ft.Row([
                ft.Icon(icone, size=19, color=PALETA["accent_lime"] if ativo else texto2_cor(dark)),
                ft.Text(label, size=13, weight=ft.FontWeight.W_600, color=texto_cor(dark)),
            ], spacing=6, tight=True),
            bgcolor=ft.Colors.with_opacity(0.12, PALETA["accent_green"]) if ativo else card_bg(dark),
            border_radius=12, padding=ft.Padding.symmetric(horizontal=14, vertical=11),
            border=ft.Border.all(1, PALETA["accent_green"] if ativo else divider_cor(dark)),
            on_click=lambda e, k=key: trocar(k), ink=True,
        )

    def trocar(k):
        sel["v"] = k
        linha.controls = [chip(*o) for o in opcoes]
        page.update()

    trocar("sim")
    return make_screen(dark, [
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, icon_color=texto_cor(dark), on_click=lambda e: ao_voltar()),
                ft.Text("A coleta foi realizada?", size=18, weight=ft.FontWeight.BOLD, color=texto_cor(dark), expand=True),
            ], spacing=4),
            ft.Container(height=10),
            card(dark, ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.DELETE_OUTLINE, size=17, color=PALETA["accent_lime"]),
                    ft.Text("Coleta comum", size=14, weight=ft.FontWeight.W_600, color=texto_cor(dark)),
                ], spacing=6),
                ft.Text(f"{state.get_bairro()['nome']} · {state.rua}", size=12, color=texto2_cor(dark)),
                ft.Text("Previsto para 08:00 · protocolo #2841", size=11, color=texto2_cor(dark)),
            ], spacing=4)),
            ft.Container(height=18),
            ft.Text("O caminhão passou na sua rua?", size=15, weight=ft.FontWeight.W_600, color=texto_cor(dark)),
            ft.Container(height=10),
            linha,
            ft.Container(height=18),
            ft.Text("Comentário (opcional)", size=13, weight=ft.FontWeight.W_600, color=texto_cor(dark)),
            ft.Container(height=8),
            ft.TextField(
                label="Comentário", hint_text="Ex.: deixou tudo coletado, mas o caminhão veio tarde",
                multiline=True, min_lines=3, max_lines=5,
                color=texto_cor(dark),
                label_style=ft.TextStyle(color=texto2_cor(dark), size=12),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                border_radius=12, border_color=divider_cor(dark), focused_border_color=PALETA["accent_lime"],
            ),
            ft.Container(height=18),
            botao(dark, "Enviar resposta", icon=ft.Icons.SEND_ROUNDED,
                  on_click=lambda e: ao_registrar(sel["v"], True)),
        ],
        padding=ft.Padding.symmetric(horizontal=16, vertical=16),
        vertical_scroll=ft.ScrollMode.AUTO,
    )


def tela_offline(state, page, ao_voltar):
    dark = state.dark_mode
    return make_screen(dark, [
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, icon_color=texto_cor(dark), on_click=lambda e: ao_voltar()),
                ft.Text("Modo offline", size=18, weight=ft.FontWeight.W_600, color=texto_cor(dark), expand=True),
            ], spacing=4),
            ft.Container(height=16),
            card(dark, ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CLOUD_OFF, size=20, color=PALETA["accent_orange"]),
                    ft.Text("Sem conexão com a internet", size=14, weight=ft.FontWeight.W_600, color=texto_cor(dark)),
                ], spacing=8),
                ft.Text("Você pode continuar usando o app. As informações exibidas são o último "
                        "estado sincronizado e os dados que você enviar serão enviados quando "
                        "a conexão voltar.", size=12, color=texto2_cor(dark)),
            ], spacing=8)),
            ft.Container(height=14),
            ft.Text("O que funciona offline", size=14, weight=ft.FontWeight.W_600, color=texto_cor(dark)),
            ft.Container(height=10),
            ft.Column([
                ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=16, color=PALETA["accent_lime"]),
                        ft.Text("Consultar cronograma e histórico", size=13, color=texto_cor(dark))], spacing=8),
                ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=16, color=PALETA["accent_lime"]),
                        ft.Text("Ver timeline e notificações já recebidas", size=13, color=texto_cor(dark))], spacing=8),
                ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=16, color=PALETA["accent_lime"]),
                        ft.Text("Registrar ocorrências (fila offline)", size=13, color=texto_cor(dark))], spacing=8),
                ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=16, color=PALETA["accent_lime"]),
                        ft.Text("Solicitar coleta de volumosos (fila offline)", size=13, color=texto_cor(dark))], spacing=8),
            ], spacing=10),
        ],
        padding=ft.Padding.symmetric(horizontal=16, vertical=14),
        vertical_scroll=ft.ScrollMode.AUTO,
    )
