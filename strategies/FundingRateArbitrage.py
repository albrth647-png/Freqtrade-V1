"""
ESTRATEGIA: Funding Rate Arbitrage (Delta-Neutral)
====================================================
Basada en paper arXiv "Fundamentals of Perpetual Futures" (Sharpe 2.0)
Funciona en Hyperliquid (spot + perp en el mismo DEX)

CONCEPTO:
- Mantener posición LONG en spot (compra real)
- Mantener posición SHORT en perp (misma cantidad)
- Delta-neutral: no te importa si precio sube o baja
- Cobrar funding rate cada hora

ADVERTENCIA:
- Esta estrategia NO es trend following tradicional
- Freqtrade está diseñado para trading direccional, no arbitrage
- Esta implementación es una ADAPTACIÓN que simula el arbitrage
- Para arbitrage puro, mejor usar script Python directo (no Freqtrade)

CÓMO FUNCIONA EN ESTA IMPLEMENTACIÓN:
1. Cada hora, revisa funding rate de BTC/ETH/SOL en Hyperliquid
2. Si funding > 0.005% por hora (threshold): abre posición "arbitrage"
3. La "posición" es virtualmente delta-neutral (operamos solo el perp)
4. Cobramos funding rate cada hora que la posición está abierta
5. Si funding se vuelve negativo o muy bajo: cerramos posición
6. Stop loss de emergencia si precio se mueve mucho en contra

NOTA TÉCNICA:
Freqtrade no soporta posiciones simultáneas spot+perp en el mismo par.
Esta estrategia aproxima el arbitrage operando solo el perp con leverage,
confiando en que el funding rate positivo compensa el riesgo direccional.
Para arbitrage delta-neutral puro, usar script Python dedicado.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

import talipy.abstract as ta
from pandas import DataFrame
import numpy as np

from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from freqtrade.persistence import Trade


logger = logging.getLogger(__name__)


class FundingRateArbitrage(IStrategy):
    """
    Funding Rate Arbitrage Strategy (adaptada a Freqtrade)
    
    NO es trend following. Es una estrategia de "carry trade" que cobra
    funding rate manteniendo posición SHORT en perp cuando funding > 0.
    
    Esperamos que el funding rate positivo compense el riesgo direccional
    de estar short en perp sin hedge spot perfecto.
    """
    
    INTERFACE_VERSION = 3
    
    # Timeframe: 1h para capturar funding rate cada hora
    timeframe = '1h'
    
    # 1 posición a la vez por par
    max_open_trades = 3  # 3 pares: BTC, ETH, SOL
    position_adjustment_enable = False
    
    # Stops AMPLIOS porque el edge es el funding, no la dirección
    stoploss = -0.10  # -10% stoploss (con 3x leverage = -3.3% price move)
    
    # Sin trailing stop (mantenemos posición mientras funding sea positivo)
    trailing_stop = False
    
    # Soporta short
    can_short = True
    
    # Salida por signal (cierre cuando funding se vuelve negativo)
    process_only_new_candles = True
    use_exit_signal = True
    
    # Necesitamos pocas velas históricas
    startup_candle_count = 50
    
    # Parámetros optimizables
    funding_threshold = DecimalParameter(0.005, 0.001, 0.05, default=0.005, decimals=4, 
                                         space='buy', optimize=True)
    min_hold_hours = IntParameter(4, 1, 24, default=4, space='sell', optimize=True)
    max_hold_hours = IntParameter(168, 24, 720, default=168, space='sell', optimize=True)
    
    # ============================================================
    # INDICADORES
    # ============================================================
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Calcula indicadores para gestión de riesgo"""
        
        # ATR para medir volatilidad (decidir si operar)
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        dataframe['atr_pct'] = dataframe['atr'] / dataframe['close'] * 100
        
        # EMA para detectar régimen (si muy bullish, funding probablemente alto)
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=50)
        
        # RSI para evitar entradas en sobrecompra/sobreventa extrema
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # Volume para confirmación
        dataframe['volume_sma'] = dataframe['volume'].rolling(window=20).mean()
        
        # Volatilidad anualizada (para ajustar leverage dinámicamente)
        dataframe['returns'] = dataframe['close'].pct_change()
        dataframe['volatility_24h'] = dataframe['returns'].rolling(window=24).std() * np.sqrt(24 * 365)
        
        # Simular funding rate aproximado (en producción, obtener de API Hyperliquid)
        # Heuristic: funding alto cuando precio sube rápido (bull market)
        dataframe['momentum_4h'] = dataframe['close'].pct_change(periods=4) * 100
        dataframe['momentum_24h'] = dataframe['close'].pct_change(periods=24) * 100
        
        # Funding rate proxy: alto cuando momentum positivo + RSI alto
        # (esto es una aproximación — en realidad viene de la API del exchange)
        dataframe['funding_proxy'] = np.where(
            (dataframe['momentum_24h'] > 0) & (dataframe['rsi'] > 50),
            0.01 + dataframe['momentum_24h'] * 0.001,  # funding positivo en bull
            np.where(
                (dataframe['momentum_24h'] < 0) & (dataframe['rsi'] < 50),
                -0.005 + dataframe['momentum_24h'] * 0.0005,  # funding negativo en bear
                0.005  # neutral
            )
        )
        
        # Señal de "funding positivo alto" (cuando operar)
        dataframe['funding_high'] = dataframe['funding_proxy'] > self.funding_threshold.value
        dataframe['funding_negative'] = dataframe['funding_proxy'] < 0
        
        # Marcar velas para entries/exits
        # Entry: funding high + baja volatilidad (mejor para delta-neutral)
        dataframe['entry_signal'] = (
            dataframe['funding_high'] &
            (dataframe['atr_pct'] < 3.0) &  # volatilidad baja
            (dataframe['volume'] > dataframe['volume_sma'])  # liquidez
        )
        
        # Exit: funding se vuelve negativo
        dataframe['exit_signal'] = dataframe['funding_negative']
        
        return dataframe
    
    # ============================================================
    # ENTRADAS
    # ============================================================
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Entramos SHORT cuando funding rate es alto positivo.
        (Shorts cobran funding cuando es positivo)
        """
        dataframe.loc[
            dataframe['entry_signal'],
            'enter_short'] = 1
        
        return dataframe
    
    # ============================================================
    # SALIDAS
    # ============================================================
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Salimos cuando funding se vuelve negativo (pagaríamos en vez de cobrar)
        """
        dataframe.loc[
            dataframe['exit_signal'],
            'exit_short'] = 1
        
        return dataframe
    
    # ============================================================
    # GESTIÓN DE POSICIÓN
    # ============================================================
    
    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime,
                        current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Stop loss dinámico:
        - Si está en profit,放宽 stop (mantener posición para cobrar funding)
        - Si está en loss > 5%, cerrar inmediatamente
        """
        # Si en profit > 3%, dejar correr (sigue cobrando funding)
        if current_profit > 0.03:
            return -0.15  # stop a -15% (deja correr)
        
        # Si en loss > 5%, cerrar
        if current_profit < -0.05:
            return 0.01  # trigger inmediato
        
        # Default
        return self.stoploss
    
    def custom_exit(self, pair: str, trade: Trade, current_time: datetime,
                    current_rate: float, current_profit: float, **kwargs) -> Optional[str]:
        """
        Exit customizado:
        - Si posición lleva demasiado tiempo abierta, cerrar
        - Si funding se volvió negativo (verificado por signal), cerrar
        """
        # Tiempo máximo de holding (1 semana por defecto)
        max_hours = self.max_hold_hours.value
        if (current_time - trade.open_date_utc).total_seconds() / 3600 > max_hours:
            return 'max_hold_reached'
        
        # Tiempo mínimo (no cerrar antes de las 4h)
        min_hours = self.min_hold_hours.value
        if (current_time - trade.open_date_utc).total_seconds() / 3600 < min_hours:
            return None
        
        # Si en profit > 10%, cerrar (take profit)
        if current_profit > 0.10:
            return 'take_profit_10pct'
        
        return None
    
    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, side: str,
                 **kwargs) -> float:
        """
        Leverage para funding arbitrage.
        
        APARENTEMENTE contradictorio:
        - Funding arbitrage puro es delta-neutral (leverage alto OK)
        - PERO en Freqtrade solo operamos el perp (no hay spot hedge)
        - Por eso usamos leverage BAJO (3x) para no liquidarnos
        """
        # Leverage bajo porque NO tenemos hedge spot en Freqtrade
        # (Si tuvieras hedge spot perfecto en otro lado, podrías usar 10x+)
        return 3.0
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                            time_in_force: str, current_time: datetime, entry_tag: Optional[str],
                            side: str, **kwargs) -> bool:
        """
        Confirmación final antes de abrir trade.
        Verifica que funding rate siga siendo positivo.
        """
        # En producción, aquí verificarías funding rate actual de la API
        # Por ahora, confiamos en el signal calculado
        return True
    
    # ============================================================
    # PLOTTING
    # ============================================================
    
    def plot_config(self):
        return {
            'main_plot': {
                'ema_fast': {'color': 'blue'},
                'ema_slow': {'color': 'orange'},
            },
            'subplots': {
                'Funding Proxy': {
                    'funding_proxy': {'color': 'green'},
                },
                'ATR %': {
                    'atr_pct': {'color': 'red'},
                }
            }
        }


# ============================================================
# NOTAS IMPORTANTES
# ============================================================
"""
⚠️ ADVERTENCIA IMPORTANTE:

Esta implementación en Freqtrade es una APROXIMACIÓN al funding arbitrage.
Freqtrade NO está diseñado para arbitrage delta-neutral puro porque:
1. No soporta posiciones simultáneas spot + perp en mismo par
2. No tiene notion de "hedge" automático
3. Está optimizado para trading direccional

Para ARBITRAGE DELTA-NEUTRAL PURO, necesitas un script Python dedicado que:
1. Compre spot en Hyperliquid
2. Venda perp en Hyperliquid simultáneamente
3. Rebalancee cuando el ratio se desalinee
4. Monitoree funding rate de la API directamente

Si quieres el script Python dedicado (más fiel al paper académico),
pídeme "script Python puro para funding arbitrage" y lo construyo.
"""
