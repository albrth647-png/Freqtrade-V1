# 🚀 Guía General: Conexión Completa del Bot

> **Bot de trading cripto para Cuba** — Open source, non-custodial, sin KYC
> **Stack**: Termux (Android) + Freqtrade + Hyperliquid + Trust Wallet + Telegram
> **Estrategias**: Time Series Momentum + Funding Rate Arbitrage (+ SMA Crossover v4 bonus)

---

## 📋 Tabla de contenidos

1. [Visión general](#visión-general)
2. [Requisitos previos](#requisitos-previos)
3. [Arquitectura del sistema](#arquitectura-del-sistema)
4. [Instalación paso a paso](#instalación-paso-a-paso)
5. [Configuración de wallets y API keys](#configuración-de-wallets-y-api-keys)
6. [Activación de estrategias](#activación-de-estrategias)
7. [Paper trading (obligatorio)](#paper-trading-obligatorio)
8. [Live trading (después de validar)](#live-trading-después-de-validar)
9. [Monitoreo y control desde móvil](#monitoreo-y-control-desde-móvil)
10. [Troubleshooting general](#troubleshooting-general)
11. [Seguridad y mejores prácticas](#seguridad-y-mejores-prácticas)

---

## Visión general

### ¿Qué vas a construir?

```
┌──────────────────────────────────────────────────┐
│  TU TELÉFONO ANDROID                             │
│  ├─ Termux (corre Freqtrade 24/7)               │
│  ├─ Trust Wallet (tus fondos crypto)            │
│  ├─ Telegram (alertas del bot)                  │
│  └─ FreqDroid (app para controlar bot)          │
└──────────────────────────────────────────────────┘
              ↓ (vía internet, sin VPN)
┌──────────────────────────────────────────────────┐
│  HYPERLIQUID L1 (blockchain DEX)                │
│  ├─ Tu wallet con USDC                          │
│  ├─ Positions BTC/ETH/SOL (leverage 3-5x)      │
│  └─ Non-custodial: nadie puede bloquearte       │
└──────────────────────────────────────────────────┘
```

### ¿Por qué esta configuración?
- ✅ **Funciona en Cuba** (Hyperliquid no bloquea IPs ni requiere KYC)
- ✅ **Non-custodial** (tú controlas tus fondos)
- ✅ **Open source** (código auditable)
- ✅ **Mobile-first** (controlas todo desde el celular)
- ✅ **Gratis** (sin suscripciones mensuales)

### Estrategias disponibles

| Estrategia | Sharpe | Capital min | Difficulty | Documentación |
|------------|--------|-------------|------------|---------------|
| **Time Series Momentum** | 1.28-2.21 | $30+ | Media | [Guía TSM](GUIA_TIME_SERIES_MOMENTUM.md) |
| **Funding Rate Arbitrage** | 2.0 | $100+ | Alta | [Guía Funding Arb](GUIA_FUNDING_RATE_ARBITRAGE.md) |
| **SMA Crossover v4** (bonus) | 0.36 | $30+ | Baja | Incluida como backup |

---

## Requisitos previos

### Hard requirements
- ✅ Android smartphone (Android 7+)
- ✅ Conexión internet estable (datos móviles o WiFi)
- ✅ $30-100 USD para empezar
- ✅ 1-2 horas para setup inicial
- ✅ Paciencia para paper trading 1 semana

### Soft requirements
- ⚠️ Power bank (el bot consume batería)
- ⚠️ Cargador siempre conectado cuando sea posible
- ⚠️ Cuenta en QbitPay / QvaPay / BitPapa (para comprar USDC desde Cuba)

### Habilidades necesarias
- ✅ Saber usar Termux (te enseñamos)
- ✅ Editar archivos de texto (nano)
- ✅ Seguir instrucciones paso a paso
- ✅ No paniquear si algo falla (lo resolvemos)

### Lo que NO necesitas
- ❌ No necesitas saber programar
- ❌ No necesitas PC/laptop
- ❌ No necesitas VPN
- ❌ No necesitas KYC
- ❌ No necesitas exchange centralizado

---

## Arquitectura del sistema

### Componentes y sus roles

| Componente | Rol | Costo |
|------------|-----|-------|
| **Termux** | Linux en Android (corre el bot) | Gratis |
| **Freqtrade** | Bot de trading open source | Gratis |
| **Hyperliquid** | DEX donde operas perps | 0.035% por trade |
| **Trust Wallet** | Tu wallet crypto (custodia) | Gratis |
| **Telegram bot** | Recibe alertas del bot | Gratis |
| **FreqDroid** | App Android para controlar Freqtrade | Gratis |
| **Total fijo mensual** | | **$0** |

### Flujo de datos

```
1. Freqtrade (en Termux) se conecta a Hyperliquid API
2. Descarga datos de precios cada 4h (TSM) o 1h (Funding Arb)
3. Calcula indicadores (momentum, ATR, RSI, etc.)
4. Si signal de entrada → envía orden a Hyperliquid
5. Hyperliquid ejecuta orden on-chain
6. Bot monitorea posición abierta
7. Si signal de salida o stop loss → cierra posición
8. Resultados se loguean + envían a Telegram
```

### Flujo de fondos

```
1. Compras USDC en QbitPay/QvaPay (Cuba-friendly)
2. Envías USDC a tu Trust Wallet (red BSC o Arbitrum)
3. Conectas Trust Wallet a Hyperliquid
4. Haces bridge USDC → Hyperliquid (~$0.10 fee)
5. Generas API wallet en Hyperliquid para el bot
6. Bot opera usando tu API wallet
7. Para retirar: Hyperliquid → Arbitrum → Trust Wallet → QbitPay → CUP/MLC
```

---

## Instalación paso a paso

### Fase 1: Instalar Termux (5 min)

#### ⚠️ IMPORTANTE: NO instales Termux desde Google Play
La versión de Play Store está desactualizada y NO funciona bien.

**Opción A (recomendada): F-Droid**
1. Abre navegador en Android
2. Ve a https://f-droid.org/packages/com.termux/
3. Descarga e instala F-Droid
4. Abre F-Droid, busca "Termux"
5. Instálalo

**Opción B: APK directo**
1. Ve a https://github.com/termux/termux-app/releases
2. Descarga el APK más reciente para tu arquitectura (arm64-v8a)
3. Permite "instalar desde fuentes desconocidas"
4. Instala el APK

### Fase 2: Configurar Termux (5 min)

Abre Termux y ejecuta:
```bash
pkg update && pkg upgrade -y
pkg install git python nano curl wget openssh -y
termux-setup-storage
```
Acepta el permiso de almacenamiento.

### Fase 3: Instalar Freqtrade (15 min)

```bash
# Crear directorio
mkdir -p ~/freqtrade_bot
cd ~/freqtrade_bot

# Clonar Freqtrade
git clone https://github.com/freqtrade/freqtrade.git

# Entrar al directorio
cd freqtrade

# Crear entorno virtual Python
python -m venv .venv
source .venv/bin/activate

# Actualizar pip
pip install --upgrade pip wheel setuptools

# Instalar dependencias (10-15 min)
pip install -e .

# Verificar instalación
freqtrade --version

# Crear estructura user_data
freqtrade create-userdir --userdir user_data
```

### Fase 4: Copiar archivos del bot

Conecta tu teléfono a la PC o descarga los archivos a `Download/crypto-bot-cuba/`. Luego:

```bash
# Copiar estrategias
cp /storage/emulated/0/Download/crypto-bot-cuba/strategies/*.py ~/freqtrade_bot/freqtrade/user_data/strategies/

# Copiar configs
cp /storage/emulated/0/Download/crypto-bot-cuba/configs/*.json ~/freqtrade_bot/freqtrade/user_data/

# Copiar script Python puro (para Funding Arb real)
mkdir -p ~/funding_arb_bot
cp /storage/emulated/0/Download/crypto-bot-cuba/scripts/funding_arbitrage_puro.py ~/funding_arb_bot/
cp /storage/emulated/0/Download/crypto-bot-cuba/scripts/.env.example ~/funding_arb_bot/.env
```

Verifica que todo esté en su lugar:
```bash
ls ~/freqtrade_bot/freqtrade/user_data/strategies/
# Deberías ver: FundingRateArbitrage.py  SmaCrossoverV4.py  TimeSeriesMomentum.py

ls ~/freqtrade_bot/freqtrade/user_data/*.json
# Deberías ver: config_tsm.json  config_funding_arb.json
```

---

## Configuración de wallets y API keys

### Paso 1: Crear Trust Wallet (10 min)

1. Instala Trust Wallet desde Play Store
2. **Crea NUEVA wallet** (NO importes Ronin — separar propósitos)
3. **Anota 12 palabras seed en PAPEL** (CRÍTICO)
   - No en screenshot
   - No en notas del celular
   - No en nube
   - Solo papel físico
4. Configura PIN/biometría

⚠️ **Si pierdes las 12 palabras, pierdes TODO**. No hay "olvidé mi contraseña".

### Paso 2: Comprar USDC desde Cuba (variable)

**Opciones Cuba-friendly**:
- **QbitPay**: https://qbitpay.com — acepta MLC
- **QvaPay**: https://qvapay.com — Cuba-specific
- **BitPapa**: https://bitpapa.com — P2P
- **Paxful**: https://paxful.com — P2P global

Compra $35-105 USDC (extra para fees). Envía a tu Trust Wallet (red BSC o Arbitrum).

### Paso 3: Bridge USDC a Hyperliquid (5 min)

1. Abre Trust Wallet
2. Ve a https://app.hyperliquid.xyz (desde navegador de Trust Wallet)
3. Click "Connect Wallet" → "WalletConnect"
4. Escanea QR con Trust Wallet
5. Click "Bridge" → deposita USDC desde Arbitrum a Hyperliquid
6. Fee: ~$0.10, tiempo: 30 segundos

### Paso 4: Generar API wallet en Hyperliquid (3 min)

1. Ve a https://app.hyperliquid.xyz/API
2. Conecta tu Trust Wallet
3. Click "Generate API Wallet"
4. Te dará:
   - **API Wallet Address** (0x...) ← este es tu `HYPERLIQUID_API_KEY`
   - **API Wallet Private Key** (largo string) ← este es tu `HYPERLIQUID_API_SECRET`
5. **Anota estos dos valores** en papel separado (CRÍTICO)

### Paso 5: Crear bot de Telegram (5 min)

1. Abre Telegram, busca `@BotFather`
2. Envía `/newbot`
3. Sigue instrucciones:
   - Nombre: `Mi Bot Trading Cuba` (o el que quieras)
   - Username: `mi_bot_trading_cuba_bot` (debe terminar en `_bot`)
4. BotFather te dará un **token** como:
   ```
   7891234567:AAH-1234567890abcdefghijklmnop
   ```
   ← Este es tu `TELEGRAM_BOT_TOKEN`
5. Busca tu nuevo bot en Telegram, envíale `/start`
6. Visita en navegador (cambia TU_TOKEN):
   ```
   https://api.telegram.org/botTU_TOKEN/getUpdates
   ```
7. Busca `"chat":{"id":123456789,...}` en la respuesta
   ← Ese número es tu `TELEGRAM_CHAT_ID`

### Paso 6: Editar configs con tus claves

#### Para Time Series Momentum:
```bash
nano ~/freqtrade_bot/freqtrade/user_data/config_tsm.json
```

Reemplaza:
- `TU_HYPERLIQUID_API_KEY` → tu API wallet address
- `TU_HYPERLIQUID_API_SECRET` → tu API wallet private key
- `TU_TELEGRAM_BOT_TOKEN` → tu bot token
- `TU_TELEGRAM_CHAT_ID` → tu chat ID (número, sin comillas)

#### Para Funding Rate Arbitrage (Freqtrade version):
```bash
nano ~/freqtrade_bot/freqtrade/user_data/config_funding_arb.json
```
Mismo proceso.

#### Para Funding Rate Arbitrage (Python puro):
```bash
nano ~/funding_arb_bot/.env
```
```
HYPERLIQUID_API_KEY=tu_api_wallet_address_0x
HYPERLIQUID_API_SECRET=tu_api_wallet_private_key_larga
HYPERLIQUID_WALLET_ADDRESS=tu_wallet_principal_0x
TELEGRAM_BOT_TOKEN=tu_telegram_bot_token
TELEGRAM_CHAT_ID=tu_chat_id_numerico
```

---

## Activación de estrategias

### Opción A: Time Series Momentum (recomendado para $30)

#### 1. Descargar datos históricos
```bash
cd ~/freqtrade_bot/freqtrade
source .venv/bin/activate

freqtrade download-data --exchange hyperliquid \
  --pairs BTC/USDC:USDC ETH/USDC:USDC SOL/USDC:USDC \
  --timeframes 4h --days 365
```

#### 2. Backtest
```bash
freqtrade backtesting \
  --config user_data/config_tsm.json \
  --strategy TimeSeriesMomentum \
  --timeframe 4h
```

#### 3. Verificar métricas
El reporte debe mostrar:
- ✅ Profit factor > 1.3
- ✅ Win rate > 40%
- ✅ Max drawdown < 25%
- ✅ Sharpe > 0.8

#### 4. Dry-run (paper trading)
```bash
freqtrade trade \
  --config user_data/config_tsm.json \
  --strategy TimeSeriesMomentum \
  --dry-run
```

### Opción B: Funding Rate Arbitrage (requiere $100+)

#### Versión Freqtrade (simpler):
```bash
freqtrade download-data --exchange hyperliquid \
  --pairs BTC/USDC:USDC ETH/USDC:USDC SOL/USDC:USDC \
  --timeframes 1h --days 365

freqtrade backtesting \
  --config user_data/config_funding_arb.json \
  --strategy FundingRateArbitrage \
  --timeframe 1h

freqtrade trade \
  --config user_data/config_funding_arb.json \
  --strategy FundingRateArbitrage \
  --dry-run
```

#### Versión Python puro (delta-neutral REAL):
```bash
cd ~/funding_arb_bot

# Editar script con tu capital y configuración
nano funding_arbitrage_puro.py
# (ajustar CONFIG['total_capital_usdc'] y otros parámetros)

# Probar en testnet primero (CONFIG['testnet'] = True)
python funding_arbitrage_puro.py
```

### Opción C: Ambas estrategias (diversificación)

Recomendado cuando tengas $100+:
- 70% en TSM ($70)
- 30% en Funding Arb ($30)

Ejecutar los dos bots en paralelo en Termux:
```bash
# Terminal 1: TSM
cd ~/freqtrade_bot/freqtrade
source .venv/bin/activate
freqtrade trade --config user_data/config_tsm.json --strategy TimeSeriesMomentum

# Terminal 2: Funding Arb Python
cd ~/funding_arb_bot
python funding_arbitrage_puro.py
```

(Usa `termux-wake-lock` para que ambos sigan corriendo en background)

---

## Paper trading (obligatorio)

### ⚠️ NO SALTARSE ESTA FASE

**7 días mínimos de paper trading exitoso antes de ir live.**

### Qué verificar durante el paper trading

#### Diario:
- ✅ Bot abre/cierra operaciones (no está freeze)
- ✅ Alertas Telegram llegan correctamente
- ✅ Las señales tienen sentido lógico (no random)
- ✅ Stop loss se ejecuta cuando debe
- ✅ Trailing stop activa correctamente
- ✅ P&L se calcula correctamente

#### Al final de los 7 días:
- ✅ Profit factor > 1.0 (al menos break-even)
- ✅ Win rate > 35% (mínimo estadístico)
- ✅ No hubo errores críticos en logs
- ✅ Celular se mantuvo encendido 24/7 sin problemas

### Si algo falla en paper trading
1. Detén el bot: `Ctrl+C`
2. Revisa logs: `tail -50 freqtrade.log`
3. Identifica el problema
4. Ajústa config si necesario
5. Reinicia paper trading (cuenta 7 días desde cero)

---

## Live trading (después de validar)

### Paso 1: Cambiar a live mode

Edita el config que vayas a usar:
```bash
nano ~/freqtrade_bot/freqtrade/user_data/config_tsm.json
```

Cambia:
```json
"dry_run": false,
```

### Paso 2: Empezar con $10 (NO $30)

Cambia temporalmente:
```json
"dry_run_wallet": 10,
```

Y baja el leverage en la strategy:
```python
# En TimeSeriesMomentum.py
def leverage(self, ...):
    return 3.0  # temporalmente 3x en vez de 5x
```

### Paso 3: Lanzar bot en live

```bash
freqtrade trade \
  --config user_data/config_tsm.json \
  --strategy TimeSeriesMomentum
```

### Paso 4: Monitorear primera semana

- Revisa Telegram cada hora los primeros 3 días
- Si pierdes > 20% en 1 día, detén y revisa
- Si todo va bien, sube capital gradualmente:
  - Día 7: $15
  - Día 14: $20
  - Día 21: $30
  - Día 30: $30 (capital completo)

### Paso 5: Activar termux-wake-lock (CRÍTICO)

Para que Android no cierre Termux en background:
```bash
termux-wake-lock
```

Esto debe estar SIEMPRE activo mientras el bot corre.

---

## Monitoreo y control desde móvil

### App FreqDroid (recomendada)

1. Instala FreqDroid desde Google Play
2. Abre FreqDroid
3. Click "Add Bot"
4. Configura:
   - **Name**: Mi Bot Cuba
   - **URL**: `http://TU_IP_LOCAL:8080` (ver abajo)
   - **Username**: `freqtrade` (de config.json)
   - **Password**: la que pusiste en config.json

Para obtener tu IP local:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

### Funciones de FreqDroid
- ✅ Ver posiciones abiertas en tiempo real
- ✅ Ver historial de trades
- ✅ Ver balance y P&L
- ✅ Cerrar trades manualmente
- ✅ Recibir push notifications
- ✅ Ver gráficos de performance

### Telegram commands útiles

Envía estos comandos a tu bot de Telegram:
- `/status` — ver estado actual
- `/profit` — ver P&L
- `/balance` — ver balance disponible
- `/performance` — performance histórico
- `/daily` — resumen diario
- `/stopentry` — detener nuevas entradas (mantiene posiciones)
- `/stop` — detener bot completamente
- `/start` — reanudar bot
- `/help` — ver todos los comandos

### Comandos Termux útiles

```bash
# Ver logs en vivo
tail -f ~/freqtrade_bot/freqtrade/freqtrade.log

# Ver estado del bot
freqtrade show-trades --config user_data/config_tsm.json

# Reiniciar bot (detener y volver a lanzar)
# Ctrl+C para detener
# Luego: freqtrade trade --config ... --strategy ...

# Apagar wake-lock (cuando no uses bot)
termux-wake-release

# Ver uso de batería
dumpsys batteryinfo | grep -A 20 "com.termux"
```

---

## Troubleshooting general

### Problema: "module not found"
```bash
cd ~/freqtrade_bot/freqtrade
source .venv/bin/activate
pip install -e .
```

### Problema: "Hyperliquid API connection failed"
1. Verifica API keys correctas en config
2. Verifica tener USDC depositado en Hyperliquid
3. Prueba conexión:
```bash
python -c "
import ccxt
ex = ccxt.hyperliquid({'apiKey':'TU_KEY','secret':'TU_SECRET'})
print(ex.fetch_balance())
"
```

### Problema: "Telegram bot doesn't respond"
1. Verifica token y chat_id en config
2. Asegúrate de haber enviado `/start` a tu bot
3. Verifica conexión internet
4. Prueba manualmente:
```bash
curl -s "https://api.telegram.org/botTU_TOKEN/sendMessage" -d "chat_id=TU_CHAT_ID&text=test"
```

### Problema: "Termux se cierra cuando apago la pantalla"
```bash
termux-wake-lock
```
Esto evita que Android cierre Termux en background.

### Problema: batería se agota rápido
- Termux + Freqtrade consumen ~5-10% batería/hora
- Mantén celular conectado al cargador cuando sea posible
- Considera VPS ($5/mes) si el consumo es problema

### Problema: "No internet"
- Verifica tu conexión en Cuba (datos móviles o WiFi)
- Telegram y Hyperliquid deben funcionar en redes cubanas normales
- Si usas VPN, asegúrate que sea estable

### Problema: bot abre muchas posiciones seguidas
- Verifica `max_open_trades` en config (debe ser 1-3)
- Verifica que `process_only_new_candles = True`
- Revisa si hay errores en la strategy

### Problema: bot no abre posiciones
- Verifica que los pares estén en `pair_whitelist`
- Baja thresholds en la strategy (ej: momentum_threshold)
- Verifica tener suficiente balance

---

## Seguridad y mejores prácticas

### 🔒 Reglas CRÍTICAS de seguridad

1. **NUNCA compartas tus 12 palabras seed de Trust Wallet**
2. **NUNCA compartas tu API secret de Hyperliquid**
3. **NUNCA subas tu `.env` o configs con claves a GitHub público**
4. **NUNCA pases a live sin 1 semana de dry-run exitoso**
5. **Empieza con $10, no $30** (valida primero)
6. **Si el bot pierde 30% en un día, detén todo**
7. **Mantén Termux actualizado**: `pkg update && pkg upgrade -y` semanalmente
8. **Backup de configs** en lugar seguro (no en GitHub público)
9. **Tu celular debe estar SIEMPRE encendido** mientras el bot opera
10. **Si pierdes tu celular, pierdes acceso al bot** (ten backup de API keys)

### 📝 Backup recomendado

Mantén en lugar seguro (papel físico + usb encriptado):
- 12 palabras seed de Trust Wallet
- API wallet address + private key de Hyperliquid
- Telegram bot token + chat ID
- Archivos `config_*.json` (sin API keys si los compartes)

### 🎯 Gestión de expectativas

#### Lo que SÍ vas a lograr
- Aprender trading algorítmico real
- Tener un sistema automatizado funcionando
- Returns modestos pero sostenibles (10-40% anual)
- Independencia financiera parcial a largo plazo

#### Lo que NO vas a lograr
- ❌ Hacerte rico en 1 mes
- ❌ Convertir $30 en $1000 rápido
- ❌ Vivir del trading con $30 de capital
- ❌ Garantía de returns (puedes perder todo)

### 📊 Plan de crecimiento sugerido

| Mes | Capital | Estrategia | Expectativa retorno |
|-----|---------|------------|---------------------|
| 1 | $30 | TSM (paper → live $10) | Aprendizaje |
| 2 | $30 | TSM (live $30 completo) | +5-15% |
| 3 | $35 | TSM + empezar ahorrar | +5-15% |
| 4-6 | $50-100 | TSM + Funding Arb | +15-30% |
| 6-12 | $100-300 | Ambas estrategias optimizadas | +20-40% |
| 12+ | $500+ | Diversificar más estrategias | +30-50% |

### ⚠️ Disclaimer

Este software es para fines educativos. El trading de criptomonedas implica riesgo significativo de pérdida total del capital. Performance pasada no garantiza performance futura. Las estrategias pueden dejar de funcionar en cualquier momento. **Solo invierte lo que puedas permitirte perder.**

---

## 📚 Recursos adicionales

- **Freqtrade docs**: https://www.freqtrade.io/
- **Hyperliquid docs**: https://hyperliquid.gitbook.io/
- **Trust Wallet**: https://trustwallet.com
- **Telegram BotFather**: @BotFather en Telegram
- **FreqDroid en Play Store**: búscalo como "FreqDroid"
- **Strategy Time Series Momentum**: [Guía TSM](GUIA_TIME_SERIES_MOMENTUM.md)
- **Strategy Funding Rate Arbitrage**: [Guía Funding Arb](GUIA_FUNDING_RATE_ARBITRAGE.md)

---

## 🆘 Soporte

Si algo no funciona:
1. Revisa el archivo de logs (`tail -50 freqtrade.log`)
2. Busca el error en https://github.com/freqtrade/freqtrade/issues
3. Pregunta en el grupo de Telegram de Freqtrade
4. Revisa la documentación específica de cada estrategia

¡Mucha suerte! Recuerda: trading con leverage es alta varianza. Puedes ganar, pero también puedes perder todo. Solo opera lo que puedas permitirte perder.
