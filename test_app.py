#!/usr/bin/env python3
"""
Script de teste automatizado para Hora do Lixo
Executa validações dos serviços sem abrir a UI
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import (
    AppState, BAIRROS, DIAS,
    ColetaEvento, Notificacao, Denuncia
)
from datetime import datetime


def test_services():
    """Testa todos os serviços principais"""
    print("TESTANDO SERVIÇOS...")
    
    svc = AppState()
    
    # Teste 1: Bairro padrão (usa o que está salvo no config)
    bairro = next(b for b in BAIRROS if b["id"] == svc.bairro_id)
    print(f"  Bairro atual: {bairro['nome']} (ID: {svc.bairro_id})")
    
    # Teste 2: Troca de bairro
    original_id = svc.bairro_id
    svc.set_bairro(2 if original_id != 2 else 1)
    bairro = next(b for b in BAIRROS if b["id"] == svc.bairro_id)
    assert bairro["nome"] in [b["nome"] for b in BAIRROS]
    print(f"  Troca de bairro funciona: {bairro['nome']}")
    
    # Teste 3: Cronograma da semana
    cronograma = svc.coletas
    assert len(cronograma) == 7
    assert all(isinstance(e, ColetaEvento) for e in cronograma)
    print("  Cronograma semanal (7 dias)")
    
    # Teste 4: Status coleta
    status = svc.caminhao
    assert "status" in status
    assert status["status"] in ["aguardando", "em_rota", "concluido"]
    print(f"  Status coleta: {status['status']}")
    
    # Teste 5: Notificações
    notifs = svc.notificacoes
    assert len(notifs) >= 3
    assert all(isinstance(n, Notificacao) for n in notifs)
    print(f"  {len(notifs)} notificações carregadas")
    
    # Teste 6: Denúncias
    denuncias = svc.denuncias
    assert len(denuncias) >= 3
    assert all(isinstance(d, Denuncia) for d in denuncias)
    print(f"  {len(denuncias)} denúncias carregadas")
    
    # Teste 7: Bairros de Manaus
    assert len(BAIRROS) == 10
    zonas = set(b["zona"] for b in BAIRROS)
    assert "Zona Sul" in zonas
    assert "Zona Norte" in zonas
    assert "Zona Centro-Sul" in zonas
    print(f"  {len(BAIRROS)} bairros em {len(zonas)} zonas")
    
    # Teste 8: Persistência
    svc._save_config()
    svc2 = AppState()
    assert svc2.bairro_id == svc.bairro_id
    print("  Persistência de configurações")
    
    print("TODOS OS TESTES PASSARAM!")


def test_ui_components():
    """Testa se componentes UI podem ser importados (sem instanciar sem Page)"""
    print("TESTANDO IMPORTS DE COMPONENTES UI...")
    
    # Testa imports dos componentes
    from main import (
        iPhoneFrame, StatusBar, NavBar, TruckCard, ScheduleCard,
        QuickAction, NotificationTile, DenunciaCard,
        AppState, ColetaEvento, Notificacao, Denuncia
    )
    
    print("  Todos os componentes importam sem erro")
    print("TESTES DE UI PASSARAM (imports OK)!")


if __name__ == "__main__":
    try:
        test_services()
        test_ui_components()
        print("="*50)
        print("SUITE DE TESTES COMPLETA - TUDO OK!")
        print("="*50)
        sys.exit(0)
    except Exception as e:
        print(f"FALHA: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
