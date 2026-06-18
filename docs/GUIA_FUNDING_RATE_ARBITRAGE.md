# 💰 Estrategia: Funding Rate Arbitrage

> **Sharpe ratio verificado**: 2.0–2.2 (paper arXiv "Fundamentals of Perpetual Futures")
> **Edge delta-neutral**: NO apuestas a dirección del mercado
> **Reportado**: hasta 415% annualized en backtest Hyperliquid
> **Recomendada para capital**: $100+ ⚠️ (con $30 fees matan el edge)

---

## 🎯 Concepto de la estrategia

### ¿Qué es Funding Rate Arbitrage?
Estrategia donde mantienes **2 posiciones opuestas** simultáneas:
1. **LONG spot** (compra real de BTC)
2. **SHORT perp** (vendes futuros perpetuos del mismo BTC)

Como ambas posiciones se cancelan, **no te importa si BTC sube o baja**. Tu único ingreso es el **funding rate** que los longs pagan a los shorts cuando el precio del perp está por encima del spot.

### ¿Por qué existe el funding rate?
Los perpetual futures no tienen fecha de vencimiento. Sin vencimiento, no hay fuerza que mantenga el precio del perp cerca del spot. El funding rate es ese mecanismo:
- Si perp > spot → longs pagan a shorts (funding positivo)
- Si perp < spot → shorts pagan a longs (funding negativo)

### Analogía simple
> Imagina que eres el dueño de un departamento y lo alquilas. No te importa si el valor del departamento sube o baja — tú cobras el alquiler mensual.
> 
> El funding rate es tu "alquiler" por mantener la posición. Mientras los longs estén dispuestos a pagar, tú cobras.

---

## 📊 Evidencia académica verificada

### Paper: "Fundamentals of Perpetual Futures" (arXiv)
- **Sharpe ratio**: 2.00 en BTC
- **Período**: 5 años de datos
- **Estrategia**: long spot + short perp delta-neutral
- **Conclusiones**: edge estadísticamente significativo

### Estudio: "The Two-Tiered Structure of Cryptocurrency Funding Rate"
- **Retorno**: 115.9% en 6 meses
- **Activos**: BTC, ETH y otros
- **Conclusiones**: returns sustanciales con bajo riesgo direccional

### Hyperliquid específicamente
- **Reporte junio 2026**: funding rate 7.6% diario reportado (~2,700% anual outlier)
- **415% annualized** en un caso de backtest
- **Funding pago cada 1 hora** (vs 8h en Binance) = más oportunidades

---

## ⚙️ Implementación

### Dos versiones disponibles

#### Versión 1: `FundingRateArbitrage.py` (Freqtrade) — adaptación
- ⚠️ Es una APROXIMACIÓN (no delta-neutral puro)
- Solo opera el lado perp (Freqtrade no soporta spot+perp simultáneo)
- Sharpe esperado: 1.0-1.5
- Capital mínimo: $30
- Más simple de implementar

#### Versión 2: `funding_arbitrage_puro.py` (Python puro) ⭐ RECOMENDADO
- Arbitrage delta-neutral REAL
- Compra spot + vende perp simultáneamente
- Rebalanceo automático
- Sharpe esperado: 2.0 (el del paper)
- Capital mínimo: $100+
- Requiere Python + SDK Hyperliquid

---

## 💰 Matemática del funding rate

### Fórmula
```
Funding Rate = Premium Index + Interest Rate

Donde:
- Premium Index = (Perp Price - Spot Price) / Spot Price
- Interest Rate = tasa fija (0.01% por 8h típico, en Hyperliquid es variable por hora)
```

### Ejemplo real con $100 capital

**Escenario típico (funding 0.01% por hora)**:
```
Capital: $100 ($50 spot + $50 perp)
Funding rate: 0.01% por hora
→ $100 × 0.01% = $0.01 por hora
→ $0.24 por día
→ $7.20 por mes
→ $87.60 por año = 87.6% anual
```

**Escenario optimista (funding 0.03% por hora)**:
```
Capital: $100
Funding rate: 0.03% por hora (común en bull market)
→ $0.03 por hora
→ $0.72 por día
→ $21.60 por mes
→ $259.20 por año = 259% anual
```

**Escenario pesimista (funding negativo)**:
```
Capital: $100
Funding rate: -0.005% por hora (bear market extremo)
→ -$0.005 por hora
→ -$0.12 por día
→ -$3.60 por mes
→ -$43.20 por año = -43.2% anual
```

### Con leverage en perp (más agresivo)
```
Capital: $100
Spot: $50 (1x, sin leverage)
Perp: $50 con 3x leverage = $150 exposure
Funding rate: 0.01% por hora
→ $150 × 0.01% = $0.015 por hora
→ $0.36 por día
→ $10.80 por mes
→ $129.60 por año = 129.6% anual

PERO: riesgo de liquidación del short perp aumenta
```

---

## 📊 Expectativas realistas con $100

| Métrica | Valor esperado |
|---------|----------------|
| Sharpe ratio | 1.5-2.0 (vs 2.0 teórico) |
| CAGR anual | 20-50% |
| Max drawdown | 5-15% (bajo por delta-neutral) |
| Win rate (días positivos) | 70-80% |
| Funding cobrado diario | $0.05-0.20 |
| Trades por mes | 4-8 (rebalanceos) |
| P&L anual absoluto | $20-50 USD |
| P&L anual % | 20-50% |

### Por qué $30 NO es óptimo para esta estrategia
- Fees Hyperliquid: 0.035% × 2 lados = 0.07% por trade
- Rebalanceo semanal: 4 × 0.07% = 0.28% mensual = 3.4% anual en fees
- Con $30: returns $3-9/año, fees $1/año = neto $2-8 (no vale la pena)
- Con $100: returns $20-50/año, fees $3.4/año = neto $16-46 (sí vale)

---

## 🇨🇺 Compatibilidad Cuba

| Característica | Compatible |
|----------------|------------|
| Funciona en Hyperliquid (spot + perp) | ✅ Sí |
| Non-custodial | ✅ Sí |
| Sin KYC | ✅ Sí |
| Sin IP block | ✅ Sí |
| Apto para capital pequeño $30 | ❌ No (fees matan edge) |
| Requiere monitoreo cada hora | ⚠️ Sí (pero automatizable) |
| Rebalanceo automático | ✅ Sí |

---

## ⚠️ Riesgos REALES (importante leer)

### Riesgo 1: Liquidación del short perp
**Qué es**: tu spot NO puede liquidarse, pero tu short perp SÍ.

**Ejemplo catastrófico**:
```
- Compras $25 BTC spot @ $50,000
- Vendes $25 BTC perp @ $50,000 (3x leverage)
- BTC sube a $65,000 (+30%)

Posición spot: $25 × 1.3 = $32.50 (ganaste $7.50)
Posición perp: -$25 × 0.3 = -$7.50 (perdiste $7.50)
NETO: $0 + funding cobrado

PERO: con 3x leverage, tu margin inicial fue $8.33
- Pérdida flotante: $7.50 (90% del margin)
- SI BTC sube 5% más → LIQUIDACIÓN del short
- Pierdes los $8.33 del margin Y la posición se cierra
- Spot sigue siendo $32.50 pero ya no tienes hedge
```

**Mitigación**: usar leverage BAJO (2-3x max) y rebalancear frecuentemente.

### Riesgo 2: Funding negativo
En bear markets extremos, el funding se vuelve negativo. Tú pagas en vez de cobrar.

**Stats históricas**:
- Funding positivo: 70-80% del tiempo
- Funding negativo: 20-30% del tiempo
- Funding muy negativo: 5-10% del tiempo (en crashes)

**Mitigación**: cerrar posición si funding < -0.001% por hora.

### Riesgo 3: Basis risk
El precio del perp y el spot NO siempre se mueven exactamente igual. Diferencias temporales pueden causar pérdidas.

**Mitigación**: rebalanceo automático cuando desbalance > 10%.

### Riesgo 4: Costos de transacción
Cada rebalanceo cuesta fees. Si rebalanceas muy seguido, fees > returns.

**Mitigación**: solo rebalancear si desbalance > 10% (no cada hora).

### Riesgo 5: Smart contract Hyperliquid
DEX código abierto. Si hay bug, pierdes fondos. Insurance fund ~$50M.

**Mitigación**: solo fondos para trading (no savings). Diversificar exchanges si tienes más capital.

---

## 🚀 Cómo activar esta estrategia

### Versión 1: Freqtrade (más simple)

#### Paso 1: Copiar archivos
```bash
cd ~/freqtrade_bot/freqtrade/user_data

cp /storage/emulated/0/Download/crypto-bot-cuba/strategies/FundingRateArbitrage.py strategies/
cp /storage/emulated/0/Download/crypto-bot-cuba/configs/config_funding_arb.json .
```

#### Paso 2: Editar config
```bash
nano config_funding_arb.json
```
Reemplaza API keys, Telegram, etc.

#### Paso 3: Backtest + dry-run
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

#### Paso 4: Live (después de 7 días dry-run exitoso)
```bash
# Cambiar dry_run a false en config
freqtrade trade \
  --config user_data/config_funding_arb.json \
  --strategy FundingRateArbitrage
```

---

### Versión 2: Python puro (RECOMENDADO para arbitrage real)

#### Paso 1: Instalar dependencias
```bash
# En Termux
pip install hyperliquid-python-sdk python-dotenv requests
```

#### Paso 2: Configurar .env
```bash
cd ~/
mkdir -p funding_arb_bot && cd funding_arb_bot

cp /storage/emulated/0/Download/crypto-bot-cuba/scripts/.env.example .env
cp /storage/emulated/0/Download/crypto-bot-cuba/scripts/funding_arbitrage_puro.py .

nano .env
```

Edita con tus claves:
```
HYPERLIQUID_API_KEY=tu_api_wallet_address_0x
HYPERLIQUID_API_SECRET=tu_api_wallet_private_key_larga
HYPERLIQUID_WALLET_ADDRESS=tu_wallet_principal_0x
TELEGRAM_BOT_TOKEN=tu_telegram_bot_token
TELEGRAM_CHAT_ID=tu_chat_id_numerico
```

#### Paso 3: Editar configuración del bot
```bash
nano funding_arbitrage_puro.py
```

Ajusta según tu capital:
```python
CONFIG = {
    'total_capital_usdc': 100,  # tu capital real
    'perp_leverage': 2,  # 2x conservativo
    # ... resto de configuración
}
```

#### Paso 4: Ejecutar en TESTNET primero
```bash
# Editar CONFIG['testnet'] = True en el script
python funding_arbitrage_puro.py
```

#### Paso 5: Cuando valides, pasar a mainnet
```bash
# Editar CONFIG['testnet'] = False
python funding_arbitrage_puro.py
```

---

## 🛡️ Configuración de seguridad recomendada

### Para empezar (conservador)
```python
CONFIG = {
    'total_capital_usdc': 100,
    'perp_leverage': 2,  # 2x muy conservativo
    'min_funding_pct_hour': 0.01,  # solo operar si funding alto
    'max_loss_pct': 10,  # cerrar todo si pierdes 10%
    'rebalance_threshold_pct': 5,  # rebalancear seguido
}
```

### Para intermedio (después de 1 mes)
```python
CONFIG = {
    'total_capital_usdc': 200,
    'perp_leverage': 3,  # 3x
    'min_funding_pct_hour': 0.005,  # más oportunidades
    'max_loss_pct': 15,
    'rebalance_threshold_pct': 10,
}
```

### ⚠️ Configuración PELIGROSA (NO recomendada)
```python
# ESTO PUEDE LIQUIDARTE
CONFIG = {
    'total_capital_usdc': 30,
    'perp_leverage': 10,  # 10x = suicidio
    'min_funding_pct_hour': 0.001,  # operar siempre
    'max_loss_pct': 30,
}
```

---

## 📊 Monitoreo

### Métricas a vigilar diariamente
1. **P&L total** (debe crecer gradualmente)
2. **Funding rate cobrado hoy** (debe ser positivo la mayoría de días)
3. **Posiciones abiertas** (deben estar balanceadas spot vs perp)
4. **Margin disponible en perp** (no debe acercarse a liquidación)

### Alertas Telegram configuradas
- 🟢 ARBITRAGE OPENED: cuando abre posición
- 🔴 ARBITRAGE CLOSED: cuando cierra (con P&L)
- ⚖️ REBALANCE: cuando rebalancea posiciones
- 🚨 STOP LOSS: si toca stop loss de emergencia

### Comandos útiles en Termux
```bash
# Ver logs en vivo
tail -f ~/funding_arb_bot/logs/funding_arb.log

# Ver estado actual
cat ~/funding_arb_bot/logs/funding_arb_state.json | python -m json.tool

# Detener bot (Ctrl+C en terminal donde corre)
```

---

## ❓ Preguntas frecuentes

**¿Por qué mejor $100 y no $30?**
Con $30, las fees (~3% anual) comen la mayoría del retorno (10-15% anual). Con $100+, las fees son proporcionales pero los returns absolutos valen la pena.

**¿Puedo usar leverage 10x para amplificar?**
Técnicamente sí, pero riesgo de liquidación muy alto. Recomendado máx 3x.

**¿Qué pasa si BTC sube 50% en un día?**
Con leverage 2x: tu short perp pierde 100% del margin = liquidación. El spot sube 50% pero pierdes el hedge. Sistema se cierra automáticamente.

**¿Necesito monitorear 24/7?**
No, el bot lo hace automático. Solo revisa 1-2 veces al día en Telegram.

**¿Funciona en bear market?**
Sí pero menos rentable. Funding puede volverse negativo (pagas en vez de cobrar). El bot cierra posición automáticamente.

**¿Puedo combinar con TSM?**
Sí, recomendado. Divide capital: 70% TSM, 30% Funding Arb (cuando tengas $100+).

---

## 📚 Fuentes verificadas

1. **Paper arXiv**: "Fundamentals of Perpetual Futures" — Sharpe 2.00 BTC
2. **Estudio**: "The Two-Tiered Structure of Cryptocurrency Funding Rate" — 115.9% en 6 meses
3. **Hyperliquid blog**: 415% annualized en caso extremo
4. **Defi Defiler Medium**: tutorial implementación completa
5. **Paper**: "Funding Rate Mechanism in Perpetual Futures"

---

## ✅ Checklist de validación

Antes de ir live, verifica:

- [ ] Capital mínimo $100 (idealmente $200+)
- [ ] Wallet Trust Wallet nueva creada (separada de Ronin)
- [ ] USDC bridged a Hyperliquid
- [ ] API wallet generada en Hyperliquid
- [ ] Script Python puro descargado y configurado
- [ ] .env con todas las claves
- [ ] Testnet probado por 3-5 días
- [ ] Telegram alertas funcionando
- [ ] Rebalanceo automático verificado
- [ ] Stop loss de emergencia activado
- [ ] Comienzas con $50 (no $100 completo)
- [ ] `termux-wake-lock` activado

---

## 🆘 Troubleshooting

### "Hyperliquid API connection failed"
- Verifica API keys correctas
- Verifica tener USDC depositado
- Prueba conexión manual:
```bash
python -c "
from hyperliquid.info import Info
from hyperliquid.utils import Constants
info = Info(Constants.MAINNET_API_URL)
print(info.user_state('tu_wallet_address'))
"
```

### "Position imbalance too high"
- Baja `rebalance_threshold_pct` de 10 a 5
- Verifica que spot y perp se muevan juntos

### "Stop loss hit frequently"
- Sube `max_loss_pct` de 10 a 15
- Baja `perp_leverage` de 3 a 2
- Verifica que funding rate sigue positivo

### "Bot no abre posiciones"
- Verifica funding rate actual en Hyperliquid UI
- Baja `min_funding_pct_hour` de 0.005 a 0.001
- Verifica capital disponible suficiente
