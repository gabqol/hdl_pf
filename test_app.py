"""Testes automatizados do Hora do Lixo.

Rodar: .\\horadolixo-env\\Scripts\\python.exe test_app.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data import (
    BAIRROS, DIAS, PALETA, RUAS,
    AppState, ColetaEvento, Notificacao, Ocorrencia, Solicitacao,
    pontos_por_bairro, determinar_tipo_coleta, exportar_csv_ocorrencias,
)


class TestDados(unittest.TestCase):

    def test_10_bairros_cadastrados(self):
        self.assertEqual(len(BAIRROS), 10)
        nomes = [b["nome"] for b in BAIRROS]
        self.assertIn("Vila Betânia", nomes)
        self.assertIn("Cidade Nova", nomes)
        self.assertEqual(len(set(nomes)), 10)

    def test_bairro_tem_coordenadas_e_dias(self):
        for b in BAIRROS:
            self.assertIn("lat", b)
            self.assertIn("lon", b)
            self.assertGreater(len(b["coleta_dias"]), 0)
            self.assertLess(abs(b["lat"]), 4)
            self.assertLess(abs(b["lon"]), 61)

    def test_ruas_cadastradas(self):
        self.assertGreaterEqual(len(RUAS), 10)
        self.assertTrue(all(r.startswith("Rua ") or r.startswith("Avenida ") for r in RUAS))

    def test_paleta_com_paleta_dark_do_spec(self):
        self.assertEqual(PALETA["bg_primary"], "#0D1A14")
        self.assertEqual(PALETA["bg_card"], "#1A2D22")
        self.assertEqual(PALETA["accent_green"], "#2E6B42")
        self.assertEqual(PALETA["accent_lime"], "#5CDB6F")
        self.assertEqual(PALETA["accent_orange"], "#E8812A")
        self.assertEqual(PALETA["accent_red"], "#C94040")

    def test_dias_da_semana(self):
        self.assertEqual(len(DIAS), 7)
        self.assertEqual(DIAS[0], "Seg")


class TestEstado(unittest.TestCase):

    def setUp(self):
        self.state = AppState()

    def test_inicializa_com_dados(self):
        self.assertIsNotNone(self.state.get_bairro())
        self.assertGreater(len(self.state.coletas), 0)
        self.assertGreater(len(self.state.notificacoes), 0)
        self.assertGreater(len(self.state.historico), 0)
        self.assertGreater(len(self.state.ocorrencias), 0)

    def test_14_dias_de_coleta(self):
        self.assertEqual(len(self.state.coletas), 14)

    def test_troca_bairro_atualiza_coletas(self):
        self.state.set_bairro(4)
        self.assertEqual(self.state.get_bairro()["id"], 4)
        self.assertEqual(len(self.state.coletas), 14)

    def test_define_tipo_por_dia(self):
        bairro = self.state.get_bairro()
        for dia in range(7):
            tipo = determinar_tipo_coleta(dia, bairro["id"])
            if dia in bairro["coleta_dias"]:
                self.assertIn(tipo, ("comum", "reciclavel"))
            else:
                self.assertEqual(tipo, "sem_coleta")

    def test_caminhao_tem_estado_valido(self):
        cam = self.state.caminhao
        self.assertIn(cam["status"], ("aguardando", "em_rota", "concluido", "sem_coleta"))
        self.assertGreaterEqual(cam["progresso"], 0.0)
        self.assertLessEqual(cam["progresso"], 1.0)

    def test_troca_rua(self):
        self.state.set_rua("Rua Joaquim Nabuco")
        self.assertEqual(self.state.rua, "Rua Joaquim Nabuco")

    def test_toggle_notificacoes(self):
        antes = self.state.notif_prefs["delay"]
        self.state.toggle_notif("delay", not antes)
        self.assertEqual(self.state.notif_prefs["delay"], not antes)

    def test_toggle_alerta_15min(self):
        antes = self.state.alerta_15min
        self.state.toggle_alerta_15min(not antes)
        self.assertEqual(self.state.alerta_15min, not antes)

    def test_toggle_dark_mode(self):
        antes = self.state.dark_mode
        self.state.toggle_dark(not antes)
        self.assertEqual(self.state.dark_mode, not antes)

    def test_criacao_de_ocorrencia_com_protocolo(self):
        total = len(self.state.ocorrencias)
        oc = self.state.add_ocorrencia("lixo_acumulado", "Rua 15, 245", "Rua das Flores", "Teste")
        self.assertEqual(len(self.state.ocorrencias), total + 1)
        self.assertTrue(oc.protocolo.startswith("#"))
        self.assertEqual(oc.status, "pendente")
        self.assertNotEqual(oc.lat, 0.0)

    def test_criacao_de_solicitacao_volumoso(self):
        total = len(self.state.solicitacoes)
        sol = self.state.add_solicitacao("movel", "25/11/2026", "1 item", "na calcada")
        self.assertEqual(len(self.state.solicitacoes), total + 1)
        self.assertTrue(sol.protocolo.startswith("#V"))
        self.assertEqual(sol.status, "solicitada")

    def test_registrar_feedback(self):
        ev = self.state.get_coleta_hoje()
        if ev:
            self.state.registrar_feedback(ev.id, True)
            self.assertEqual(self.state.historico[0].status, "concluida")

    def test_onboarding_e_nome(self):
        self.state.set_nome("Teste")
        self.assertEqual(self.state.nome_usuario, "Teste")
        self.state.concluir_onboarding()
        self.assertTrue(self.state.onboarding_feito)

    def test_persistencia_em_disco(self):
        self.state.set_nome("Persistencia")
        self.state.set_rua("Rua das Acacias")
        novo = AppState()
        self.assertEqual(novo.nome_usuario, "Persistencia")
        self.assertEqual(novo.rua, "Rua das Acacias")
        self.state.set_nome("")
        self.state.set_rua(RUAS[3])

    def test_subscribe_notify(self):
        chamadas = []
        self.state.subscribe(lambda: chamadas.append(1))
        self.state.refresh_all()
        self.assertGreater(len(chamadas), 0)

    def test_ocorrencias_persistidas_em_disco(self):
        oc = self.state.add_ocorrencia("descarte_irregular", "Rua Persistida 99", "Rua X", "teste")
        novo = AppState()
        protocolos = [o.protocolo for o in novo.ocorrencias]
        self.assertIn(oc.protocolo, protocolos)

    def test_solicitacoes_persistidas_em_disco(self):
        sol = self.state.add_solicitacao("eletronico", "30/11/2026", "1 item", "")
        novo = AppState()
        protocolos = [x.protocolo for x in novo.solicitacoes]
        self.assertIn(sol.protocolo, protocolos)

    def test_exportar_csv(self):
        caminho = exportar_csv_ocorrencias()
        self.assertTrue(os.path.exists(caminho))
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()
        self.assertIn("protocolo", conteudo)


class TestPontosSeletivos(unittest.TestCase):

    def test_pontos_por_bairro(self):
        pts = pontos_por_bairro(1)
        self.assertGreater(len(pts), 0)
        for p in pts:
            self.assertIn("nome", p)
            self.assertIn("tipo", p)
            self.assertIn("dist", p)

    def test_dois_ou_mais_ecopontos(self):
        pts = pontos_por_bairro(1)
        reciclaveis = [p for p in pts if p["tipo"] == "reciclavel"]
        self.assertGreaterEqual(len(reciclaveis), 2)


class TestTelas(unittest.TestCase):

    def setUp(self):
        self.state = AppState()

    def _page_fake(self):
        class FakePage:
            web = True

            def __init__(self):
                self.snack_bar = None
                self.updates = 0

            def update(self):
                self.updates += 1

            async def run_task(self, fn, *a):
                pass

            def show_dialog(self, d):
                pass

            def close_dialog(self):
                pass
        return FakePage()

    def test_construcao_de_todas_as_telas(self):
        import screens as S
        page = self._page_fake()
        telas = [
            S.tela_onboarding(self.state, page, lambda *a: None),
            S.tela_selecao_rua(self.state, page, lambda *a: None),
            S.tela_volumosos(self.state, page, lambda *a: None, lambda: None),
            S.tela_ocorrencia(self.state, page, lambda *a: None, lambda: None),
            S.tela_mapa_bairro(self.state, page, lambda: None),
            S.tela_feedback(self.state, page, lambda *a: None, lambda: None),
            S.tela_offline(self.state, page, lambda: None),
        ]
        self.assertEqual(len(telas), 7)
        for t in telas:
            self.assertIsNotNone(t)

    def test_construcao_das_5_abas(self):
        import main as M

        class FakePage:
            web = True

            def __init__(self):
                self.snack_bar = None
                self.updates = 0
                self.theme_mode = None
                self.bgcolor = None
                self.title = ""
                self.window_width = 0
                self.window_height = 0
                self.window_min_width = 0
                self.window_min_height = 0
                self.window_resizable = True
                self.padding = 0
                self.fonts = {}
                self.theme = None
                self.controls = []

            def update(self):
                self.updates += 1

            async def run_task(self, fn, *a):
                pass

            def add(self, *c):
                self.controls.extend(c)

            def show_dialog(self, d):
                pass

            def close_dialog(self):
                pass

        app = M.HoraDoLixoApp(FakePage())
        for i in range(5):
            self.assertIsNotNone(app._build_screen(i))


if __name__ == "__main__":
    unittest.main(verbosity=2)
