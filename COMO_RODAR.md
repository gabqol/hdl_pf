# Hora do Lixo - Guia de execucao

App de acompanhamento de coleta de residuos para Manaus/AM.
Flet 1.0.1 + Flutter 3.44.8 + Python 3.13

## 1. Preview no VS Code (30 segundos)

1. Abra o VS Code na pasta `C:\Users\ge\horadolixo`
2. Aperte **F5**
3. Escolha "Hora do Lixo: Preview (Flet)" se aparecer a lista de debug
4. O app abre em `http://localhost:8550` no navegador (ou em janela desktop)

### Pelo menu Tasks

`Ctrl+Shift+P` -> **Tasks: Run Task** -> escolha:

| Tarefa | Para que serve |
|---|---|
| Hora do Lixo: Rodar App (Preview) | Abre a janela desktop do app |
| Hora do Lixo: Preview no Navegador | Abre so no navegador (localhost:8550) |
| Hora do Lixo: Testes | Roda a suite de 25 testes |
| Hora do Lixo: Gerar APK | Compila o APK Android (~7 min) |
| Hora do Lixo: Instalar APK no Celular | Instala via adb no celular conectado |

## 2. Rodar pelo terminal (PowerShell)

```powershell
cd C:\Users\ge\horadolixo
.\horadolixo-env\Scripts\python.exe main.py
```

Preview no navegador:

```powershell
cd C:\Users\ge\horadolixo
$env:FLET_FORCE_WEB_SERVER="true"
$env:FLET_SERVER_PORT="8550"
.\horadolixo-env\Scripts\python.exe main.py
```

## 3. Testes

```powershell
cd C:\Users\ge\horadolixo
.\horadolixo-env\Scripts\python.exe test_app.py
```

25 testes cobrindo dados, estado, persistencia, pontos seletivos e construcao
de todas as 12 telas.

## 4. Gerar o APK

### Opcao A - pelo VS Code (recomendado)

`Ctrl+Shift+P` -> **Tasks: Run Task** -> **Hora do Lixo: Gerar APK**

### Opcao B - pelo terminal

```powershell
cd C:\Users\ge\horadolixo
$env:JAVA_HOME="C:\Users\ge\AndroidToolchain\jdk-21.0.5"
$env:ANDROID_HOME="C:\Users\ge\AndroidToolchain\android-sdk"
$env:ANDROID_SDK_ROOT=$env:ANDROID_HOME
$env:PATH="$env:JAVA_HOME\bin;C:\Users\ge\flutter\3.44.8\bin;$env:PATH"
.\horadolixo-env\Scripts\flet.exe build apk --yes --product "Hora do Lixo" --org com.horadolixo --bundle-id com.horadolixo.app
```

Sai em:

```
C:\Users\ge\horadolixo\build\apk\hora-do-lixo.apk
```

Alias com nome alternativo (mesmo arquivo):

```
C:\Users\ge\horadolixo\build\apk\hora-do-lixo-release.apk
```

## 5. Instalar no celular Android

### Opcao A - cabo USB

1. No celular: Configuracoes -> Sobre o telefone -> toque 7x em "Numero da versao"
2. Ative **Opcoes do desenvolvedor** e **Depuracao USB**
3. Conecte o cabo USB no PC
4. Rode:

```powershell
C:\Users\ge\AndroidToolchain\android-sdk\platform-tools\adb.exe install -r C:\Users\ge\horadolixo\build\apk\hora-do-lixo-release.apk
```

### Opcao B - sem cabo (mais simples)

1. Copie o arquivo `hora-do-lixo-release.apk` para o celular
   (WhatsApp, Google Drive, e-mail, cabo como armazenamento, etc.)
2. No celular, abra o arquivo com o Gerenciador de Arquivos
3. Toque em **Instalar**
4. Se aparecer aviso, permita "Instalar apps de fontes desconhecidas"
5. Abra o app "Hora do Lixo"

Requisitos: Android 7.0 (API 24) ou superior.

## 6. O que o app faz

### Telas (12 no total)

| # | Tela | Acesso |
|---|---|---|
| 1 | Onboarding (nome, bairro, rua) | primeira execucao |
| 2 | Home - caminhao em tempo real | aba Inicio |
| 3 | Agenda de coleta 14 dias | aba Agenda |
| 4 | Mapa do bairro + pontos seletivos | aba Mapa |
| 5 | Alertas e notificacoes push | aba Alertas |
| 6 | Perfil, preferencias e historico | aba Perfil |
| 7 | Nova ocorrencia (foto + GPS) | Home -> Denunciar |
| 8 | Coleta de volumosos | Home -> Solicitar Coleta / Agendar |
| 9 | Selecao de rua | Agenda -> Trocar rua |
| 10 | Mapa do bairro com filtros | tela do mapa |
| 11 | Feedback pos-coleta | Alertas -> Feedback |
| 12 | Modo offline | Alertas -> Modo offline |

### Funcionalidades

- **Rastreio em tempo real**: caminhao com progresso, rua atual, ETA, ruas restantes
- **Cronograma**: 14 dias, por bairro, com tipo comum/reciclavel e status
- **Agendamento de volumosos**: 7 tipos de item, data preferida, quantidade, observacoes, protocolo
- **Denuncias**: 3 tipos, endereco, descricao, anexo de foto, coordenadas GPS, protocolo rastreavel
- **Pontos seletivos**: 6 pontos com filtro por tipo (reciclavel/organico/volumoso) e distancia
- **Notificacoes**: inicio de rota, atrasos, lembrete noturno, alerta 15 min antes
- **Feedback pos-coleta**: confirma se o caminhao passou
- **Modo offline**: consulta de cronograma e historico funciona sem internet
- **Historico**: coletas concluidas, atrasadas e canceladas com causa
- **Exportacao CSV**: ocorrencias exportaveis para o SEMULSP
- **Tema claro/escuro**: paleta do APP.MD
- **Persistencia**: dados salvos em `~\.horadolixo\dados.json`

## 7. Estrutura do projeto

```
horadolixo/
  main.py          App principal, mockup iPhone 15 Pro, 5 abas
  screens.py       7 telas extras conforme APP.MD
  data.py          Estado, modelos, persistencia, dados de Manaus
  test_app.py      25 testes automatizados
  pyproject.toml   Configuracao do Flet (nome, pacote, overrides)
  .vscode/         launch.json + tasks.json
  build/apk/       APK gerado
```

## 8. Problemas comuns

**Preview nao abre**
Feche processos python duplicados (Gerenciador de Tarefas) e rode de novo.
Se aparecer erro do FastAPI, reinstale:
`.\horadolixo-env\Scripts\python.exe -m pip install fastapi==0.115.14`

**"App nao instalado" no celular**
Apague a versao anterior do app antes de instalar o novo APK.

**App abre mas nao atualiza o caminhao**
O app atualiza a cada 60 segundos. Feche e abra para forcar.

**Quero trocar os dados do bairro**
Meu Perfil -> ou edite `~\.horadolixo\dados.json` e reinicie o app.
