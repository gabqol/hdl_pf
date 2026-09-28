# Hora do Lixo 🗑️

Aplicação desktop (Flet 1.0) que simula um iPhone 15 Pro para rastreamento de coleta de lixo em **Manaus/AM**.

Projeto acadêmico — **Prática Extensionista: Tecnologia, Comunidade e Desenvolvimento Ágil** (Análise e Desenvolvimento de Sistemas).

---

## 🎯 Objetivo

Resolver o problema real de descarte irregular de resíduos sólidos em Manaus através de tecnologia, atendendo à **ODS 11 — Cidades e Comunidades Sustentáveis**.

---

## ✨ Funcionalidades Implementadas

| Aba | Funcionalidade | Status |
|-----|----------------|--------|
| 🏠 **Início** | Status do caminhão em tempo real, progresso da rota, próxima coleta do dia | ✅ |
| 📅 **Agenda** | Cronograma semanal (7 dias) com tipos de coleta (comum/reciclável) e horários | ✅ |
| 🗺️ **Mapa** | Visualização simplificada da rota: garagem → caminhão → sua rua, com ETA | ✅ |
| 🔔 **Alertas** | 4 preferências de notificação (chegada, saída, atraso, lembrete noturno) + histórico | ✅ |
| 👤 **Perfil** | Seleção de bairro (10 bairros de Manaus), tema claro/escuro, denúncias enviadas | ✅ |

**Extras:**
- Denúncia de descarte irregular (entulho, volumoso, irregular, outro) com endereço
- Solicitação de coleta extra / agendamento de volumoso (placeholders)
- Persistência automática em `~/.horadolixo_data.json` (bairro, notificações, tema)
- Auto-refresh a cada 30s nas abas Home e Mapa quando o caminhão está em rota

---

## 🏗️ Arquitetura

```
horadolixo/
├── main.py              # App completo (~960 linhas) — Flet 1.0, Python 3.13
├── test_app.py          # Testes automatizados (serviços + imports UI)
├── requirements.txt     # flet>=1.0.0
├── .vscode/launch.json  # Debug VS Code (usa horadolixo-env)
└── horadolixo-env/      # Virtualenv local (não versionar)
```

### Camadas (dentro de `main.py`)

- **Models** (`dataclasses`): `ColetaEvento`, `Notificacao`, `Denuncia` — tipados, serializáveis
- **State** (`AppState`): Single source of truth reativo com **Observer Pattern** — listeners notificados a cada mudança
- **Services** (embutidos no `AppState`):
  - Geração de cronograma semanal baseada no bairro e dia da semana
  - Status do caminhão calculado em tempo real (aguardando → em_rota → concluído)
  - Notificações e denúncias mockadas (prontas para backend real)
  - Persistência JSON (`_load_config` / `_save_config`)
- **UI Components**: Componentes reutilizáveis (`iPhoneFrame`, `TruckCard`, `ScheduleCard`, `NavBar`, `StatusBar`, `QuickAction`, `NotificationTile`, `DenunciaCard`, `InfoCard`, `ToggleTile`)
- **Screens**: 5 telas (`HomeScreen`, `ScheduleScreen`, `MapScreen`, `AlertsScreen`, `ProfileScreen`) com `refresh()` reativo

### Padrões aplicados

- **Reactive State** — UI deriva do estado, nunca o contrário
- **Observer** — `AppState.subscribe(fn)` / `unsubscribe(fn)` / `_notify()`
- **Dataclasses + Type Hints** — contratos claros, IDE-friendly
- **Asyncio** — loop de background para auto-refresh não-bloqueante

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.10+
- Git (opcional)

### Passo a passo

```bash
# 1. Clone ou baixe o projeto
git clone https://github.com/dayasseff/coleta-v1.git
cd coleta-v1/horadolixo

# 2. Crie e ative o ambiente virtual
python -m venv horadolixo-env
# Windows:
.\horadolixo-env\Scripts\activate
# Linux/Mac:
source horadolixo-env/bin/activate

# 3. Instale dependências
pip install -r requirements.txt

# 4. Execute
python main.py
```

### No VS Code
1. Abra a pasta `horadolixo`
2. `F5` ou **Run → Start Debugging**
3. A configuração `.vscode/launch.json` já aponta para o python do `horadolixo-env`

---

## 🎨 Design System

| Token | Light | Dark | Uso |
|-------|-------|------|-----|
| **Primary** | `#2E7D32` | `#4CAF50` | Verde floresta — ações principais, coleta comum |
| **Secondary** | `#FF6B35` | `#FF9800` | Laranja — caminhão em rota, alertas de tempo |
| **Info** | `#1976D2` | `#64B5F6` | Azul — reciclável, notificações informativas |
| **Warning** | `#FF8F00` | `#FFB74D` | Âmbar — atrasos, pendências |
| **Error** | `#C62828` | `#EF5350` | Vermelho — denúncias, ações destrutivas |
| **Surface** | `#FFFFFF` | `#1C1C1E` | Fundo de cards |
| **Background** | `#FAFAFA` | `#121212` | Fundo da janela |

- **Tipografia**: Inter (Google Fonts) — 400/500/600/700
- **Formato**: Moldura iPhone 15 Pro (393×852) com notch (Dynamic Island), status bar, home indicator, tab bar inferior
- **Animações**: 180–500ms, `EASE_OUT`, progress bars animadas

---

## 📱 Simulação Mobile

A aplicação roda em janela desktop mas **simula experiência mobile nativa**:

- Dimensões fixas de smartphone (393×852) + moldura
- Navegação por 5 tabs inferiores (Home, Agenda, Mapa, Alertas, Perfil)
- Safe areas: notch (48px), home indicator (34px), status bar (48px)
- Scroll nativo (`ListView`), touch targets ≥ 44×44dp
- Tema escuro/claro sincronizado com preferência do sistema ou toggle manual

---

## 🗺️ Bairros Suportados (Manaus)

| ID | Bairro | Zona | Dias de Coleta (0=Seg) |
|----|--------|------|------------------------|
| 1 | Vila Betânia | Zona Sul | Ter, Qui, Sáb (1,3,5) |
| 2 | Adrianópolis | Zona Centro-Sul | Seg, Qua, Sex (0,2,4) |
| 3 | Parque 10 | Zona Centro-Sul | Ter, Qui, Sáb (1,3,5) |
| 4 | Cidade Nova | Zona Norte | Seg, Qua, Sex (0,2,4) |
| 5 | Educandos | Zona Sul | Ter, Qui, Sáb (1,3,5) |
| 6 | Aleixo | Zona Centro-Sul | Seg, Qua, Sex (0,2,4) |
| 7 | Flores | Zona Centro-Sul | Ter, Qui, Sáb (1,3,5) |
| 8 | Centro | Zona Sul | Seg, Qua, Sex, Dom (0,2,4,6) |
| 9 | Alvorada | Zona Centro-Oeste | Ter, Qui, Sáb (1,3,5) |
| 10 | Dom Pedro | Zona Centro-Oeste | Seg, Qua, Sex (0,2,4) |

> **Padrão**: Vila Betânia (ID 1). Altere no Perfil → "Seu bairro".

---

## ⚙️ Configurações Persistidas

Arquivo: `~/.horadolixo_data.json`

```json
{
  "bairro_id": 1,
  "notifs": {
    "truck_near": true,      // 15 min antes da coleta
    "route_start": true,     // Saída da garagem (07:00)
    "delay": true,           // Atrasos > 15 min
    "night_reminder": true   // Lembrete 19h na véspera
  },
  "dark_mode": false
}
```

---

## 🔧 Stack Tecnológica

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Flet** | 1.0.x | Framework UI (Flutter para Python) |
| **Python** | 3.13 | Linguagem principal |
| **asyncio** | stdlib | Loop assíncrono (auto-refresh 30s) |
| **dataclasses** | stdlib | Modelos tipados imutáveis |
| **JSON** | stdlib | Persistência local |

---

## 📋 Backlog do Produto (Scrum)

| ID | História de Usuário | Prioridade | Sprint |
|----|---------------------|------------|--------|
| US01 | Cadastro/login de usuário | Alta | — |
| US02 | Rota e status da coleta em tempo real | **Alta** | ✅ **Feito** |
| US03 | Denúncia de descarte irregular com foto | Alta | ✅ Parcial (sem foto) |
| US04 | Avisos e notificações configuráveis | **Alta** | ✅ **Feito** |
| US05 | Canal de contato (chat/telefone) | Média | — |
| US06 | Acompanhamento de solicitações/denúncias | Média | — |
| US07 | Painel administrativo (gestão de rotas) | Baixa | — |

---

## 👥 Equipe

| Integrante | Papel Scrum | Responsabilidade |
|------------|-------------|------------------|
| Dassayeff | PO / SM / Dev | Developer |
| Gabriell | PO / SM / Dev | Developer |
| Moanna | PO / SM / Dev | Scrum Master |
| Leonardo | PO / SM / Dev | Product Owner |
| Heitor | PO / SM / Dev | Product Owner |

**Professora**: Janaina Souza  
**Disciplina**: Prática Extensionista

---

## 🧪 Testes

```bash
# Roda suite completa (serviços + imports UI)
python test_app.py
```

Saída esperada:
```
TESTANDO SERVIÇOS...
  Bairro atual: Adrianópolis (ID: 2)
  Troca de bairro funciona: Vila Betânia
  Cronograma semanal (7 dias)
  Status coleta: concluido
  5 notificações carregadas
  3 denúncias carregadas
  10 bairros em 4 zonas
  Persistência de configurações
TODOS OS TESTES PASSARAM!
TESTANDO IMPORTS DE COMPONENTES UI...
  Todos os componentes importam sem erro
TESTES DE UI PASSARAM (imports OK)!
==================================================
SUITE DE TESTES COMPLETA - TUDO OK!
==================================================
```

---

## 📄 Licença

Projeto acadêmico — Uso educacional.

---

**Desenvolvido com 💚 para Manaus**  
*Hora do Lixo — Tecnologia para resolver problemas reais da comunidade*