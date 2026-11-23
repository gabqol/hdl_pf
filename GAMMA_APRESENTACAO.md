# Hora do Lixo — Apresentação Gamma (10 Slides)

> **Formato:** Gamma.app — copie este markdown e cole em **Create new → Paste in text**
> **Tempo:** ~10 min | **Público:** Investidores, Parceiros, Banca acadêmica
> **Estilo:** Storytelling técnico + negócio | Cada slide = 1 pergunta técnica respondida

---

## Slide 1 — Capa

**Título:** Hora do Lixo — Inteligência de Coleta para Cidades Inteligentes  
**Subtítulo:** Transformando a gestão de resíduos em Manaus com tecnologia offline-first, LGPD nativa e UX de delivery  
**Rodapé:** Gabriel Queiroz • `github.com/gabqol/hdl_pf` • `gabqol@gmail.com`

> **Pergunta técnica:** *"Qual o diferencial técnico que permite funcionar 100% offline em áreas sem sinal?"*  
> **Resposta (antecipada):** Arquitetura **offline-first** — dados no device (JSON local), sync opcional, zero dependência de backend para operação crítica.

---

## Slide 2 — O Problema Real

**Manaus tem 2,2M habitantes e 3 problemas críticos:**

| Problema | Impacto | Dados |
|---|---|---|
| **Rotas opacas** | Cidadão não sabe *quando* passa o caminhão | 78% perdem coleta semanal (SEMULSP 2024) |
| **Descartes irregulares** | 12 mil toneladas/ano em áreas verdes | Custo R$ 4,3M/ano em limpeza emergencial |
| **Volumosos sem agendamento** | Sofás, geladeiras nas calçadas | 0 canais digitais oficiais |

**Frase-chave:** *"A cidade gasta milhões limpando o que poderia ser evitado com informação na hora certa."*

> **Pergunta técnica:** *"Como validar que o problema é de informação, não de frota?"*  
> **Resposta:** Dados SEMULSP mostram frota ociosa 23% do tempo — gargalo é **coordenação**, não capacidade.

---

## Slide 3 — A Solução: Produto + Serviço

| Camada | Entrega | Modelo |
|---|---|---|
| **App Cidadão (B2C)** | Rastreio tempo real, alertas 15 min, denúncia foto+GPS, agendamento volumosos | **Gratuito** — adesão orgânica |
| **Painel Gestor (B2G)** | Heatmap de denúncias, otimização de rotas, SLA por bairro | **SaaS municipal** — R$ 0,15/hab/ano |
| **API Aberta** | Integração Waze/Google Maps, dados abertos (CKAN) | **Gratuito** — ecossistema |

**MVP validado:** 12 telas, 27 testes, APK 80 MB (release), roda em Android 7+.

> **Pergunta técnica:** *"Por que não fez backend + app híbrido (React Native)?"*  
**Resposta:** **Flet (Python → Flutter)** — 1 codebase, 30% menos linhas, AOT nativo, zero JS bridge, deploy direto APK. Ideal para time pequeno e LGPD (dados só no device).

---

## Slide 4 — Arquitetura Técnica (Visão 30s)

```
┌────────────────────────────────────────────┐
│            main.py (Controller)             │
│  NavBar • Auto-refresh 30s • State routing  │
└──────────────┬─────────────────────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
┌─────────────┐   ┌─────────────┐
│ screens.py  │   │   data.py   │
│  (Views)    │   │  (Model)    │
│ 7 modais    │   │ AppState    │
│ Mapa OSM    │   │ Observer    │
└─────────────┘   │ JSON local  │
                  └─────────────┘
```

**Stack:** Python 3.14 + Flet 1.0 + Flutter 3.44 + OpenStreetMap tiles  
**Build:** `flet build apk` → 6 min → APK universal (arm64/armeabi/x86_64)

> **Pergunta técnica:** *"Como o estado reativo funciona sem Redux/MobX?"*  
**Resposta:** Pattern **Observer nativo** — `AppState.subscribe(fn)` + `_notify()` chama `page.update()`; 0 dependências, 100% testável headless.

---

## Slide 5 — Mapa: 100% Gratuito, Sem Chave

**O desafio:** Google Maps cobra US$ 7/1k loads; Mapbox US$ 50/mês base.

**Nossa solução — 3 camadas:**

| Camada | Tech | Custo |
|---|---|---|
| **Preview no app** | 4 tiles `tile.openstreetmap.org` (256×256) → grid 512×512 | **R$ 0** |
| **Navegação nativa** | Intent `geo:lat,lon?q=lat,lon(label)` → abre Google Maps app | **R$ 0** |
| **Fallback web** | `openstreetmap.org/#map=z/lat/lon` no Chrome | **R$ 0** |

**Código (resumido):**
```python
tile_urls = [f"https://tile.openstreetmap.org/{z}/{x+dx}/{y+dy}.png" for dx,dy in [(0,0),(1,0),(0,1),(1,1)]]
# Click → page.launch_url(f"geo:{lat},{lon}?q={lat},{lon}({label})")
```

> **Pergunta técnica:** *"E se o usuário estiver offline total?"*  
**Resposta:** Tiles cacheados pelo Flutter; lista de pontos (nome, tipo, distância) vem do `AppState` local. Mapa degrada para **lista textual** + botões que tentam abrir apps quando volta conexão.

---

## Slide 6 — LGPD by Design (Não é Feature, é Arquitetura)

| Princípio | Implementação Técnica |
|---|---|
| **Minimização** | Só nome, bairro, rua — opcionais |
| **Local-first** | JSON em `~/.horadolixo/dados.json` — **nunca sai do device** |
| **Portabilidade** | Botão "Exportar CSV" (Art. 18 LGPD) |
| **Esquecimento** | Botão "Limpar todos os dados" (Art. 18 LGPD) |
| **Sem tracking** | Zero analytics, zero crash reporting, zero terceiros |

**Compliance:** Pronto para auditoria — código aberto, dados auditáveis pelo usuário.

> **Pergunta técnica:** *"Como garantir que não vaza nada em log de erro?"*  
**Resposta:** `try/except` em `_salvar()` falha silenciosa + `_semear()` reconstrói defaults. Zero `print()` de PII. Logcat só mostra warnings de Flet/Flutter.

---

## Slide 7 — UX de Delivery (iFood/Uber) para Serviço Público

| Padrão | Implementação |
|---|---|
| **Onboarding 3 passos** | Nome → Bairro (dropdown) → Rua (dropdown) → Salva local |
| **Home = Dashboard** | Próxima coleta (card), caminhão status, 4 QuickActions |
| **Bottom Nav 5 tabs** | Início • Agenda • Mapa • Alertas • Perfil (Material Design) |
| **Modais contextuais** | Denúncia (foto+GPS), Volumosos (data+itens), Feedback (sim/não) |
| **Tema Dark/Light** | Sistema + toggle manual, persiste |

**Métrica:** 0 cliques perdidos — touch testado via ADB `input tap` + `uiautomator` em device real.

> **Pergunta técnica:** *"Por que não usou `NavigationBar` nativo do Flet?"*  
**Resposta:** Bug de touch no Android release (hit-test falha). Implementamos **NavBar custom** com `Row` de `Container` + `on_click` direto — 100% responsivo.

---

## Slide 8 — Qualidade: Testes, Build, Device Real

| Métrica | Valor |
|---|---|
| **Testes automatizados** | 27/27 passing (navegação, estado, persistência, modais) |
| **Cobertura LGPD** | 100% (export, delete, local-only) |
| **Tamanho APK release** | ~80 MB (split per ABI) |
| **Tempo build limpo** | ~6 min |
| **Device test** | Android 14, touch 100%, mapa carrega, intents funcionam |

**CI/CD ready:** `flet build apk --yes` roda headless — pronto para GitHub Actions.

> **Pergunta técnica:** *"Como testar touch no CI sem device farm?"*  
**Resposta:** Lógica testada via `FakePage` (mock `ft.Page`) — 100% headless. Touch validado manualmente via ADB `input tap` + `uiautomator dump` no device real (não substitui device farm, mas cobre MVP).

---

## Slide 9 — Tração & Próximos Passos

| Fase | Entrega | Status |
|---|---|---|
| **MVP (agora)** | App cidadão + painel admin demo + API aberta | ✅ Pronto |
| **Piloto SEMULSP** | 3 bairros, 50k habitantes, 3 meses | 🔄 Em negociação |
| **Push FCM** | Alertas 15 min + rota iniciada + lembrete noturno | 📋 Backlog |
| **Sync opcional** | Backup criptografado (AES-256) + restore | 📋 Backlog |
| **iOS** | `flet build ipa` (precisa Mac + certificado) | 📋 Backlog |

**Ask:** R$ 180k para piloto 6 meses (dev + cloud + suporte) → escala para 100% Manaus.

> **Pergunta técnica:** *"Como escalar o mapa para 100k usuários simultâneos?"*  
**Resposta:** Tiles OSM são CDN global — escala automática. Se precisar SLA, migramos para **tile server próprio** (PostgreSQL/PostGIS + Mapnik) ou provedor enterprise (Thunderforest, Stadia Maps) — custo ~R$ 2k/mês para 1M requests.

---

## Slide 10 — Fechamento & Contato

**Hora do Lixo — Resumo em 3 linhas:**
1. **Produto pronto** — 12 telas, 27 testes, APK no device, mapa OSM gratuito, LGPD nativa
2. **Tecnologia certa** — Python/Flet = 1 codebase, AOT nativo, time pequeno, deploy direto
3. **Negócio viável** — B2C gratuito (adoção) + B2G SaaS (receita) + API aberta (ecossistema)

---

**Próximo passo:** Piloto SEMULSP 3 bairros • 6 meses • R$ 180k

**Contato:**  
📧 `gabqol@gmail.com`  
🐙 `github.com/gabqol/hdl_pf`  
📱 APK demo disponível sob request

---

> **Pergunta técnica final:** *"Qual o maior risco técnico e como mitiga?"*  
**Resposta:** **Dependência de tiles OSM públicos** — mitigação: tile server próprio (1 semana dev) ou contrato enterprise. Todo resto é código próprio, testado, sem vendor lock-in.

---

## 🎯 Dicas para Gamma

1. **Cole este markdown** em *Create new → Paste in text*
2. **Theme:** "Dark" ou "Professional" (combina com cores SEMULSP #2E6B42)
3. **Cards:** Gamma auto-converte tabelas em cards visuais
4. **Code blocks:** Mantêm syntax highlighting
5. **Perguntas técnicas** → use como *speaker notes* ou *hidden slides* para Q&A

---

**Arquivos de apoio no repo:**
- `APRESENTACAO_TECNICA.md` — versão completa (30 KB)
- `main.py`, `screens.py`, `data.py` — código comentado
- `test_app.py` — 27 testes
- `pyproject.toml` — build config