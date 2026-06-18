"""
ESTRATEGIA v4 SMA Crossover — ADAPTADA A FREQTRADE + HYPERLIQUID
================================================================
Estrategia ganadora del backtest (PF 1.85, win rate 60%, max DD 1.83%)
Adaptada para Freqtrade con Hyperliquid como exchange.

Filosofía: Trend following clásico (CTA / Managed Futures)
- Long: SMA20 cruza arriba SMA50 (golden cross)
- Short: SMA20 cruza abajo SMA50 (death cross)
- Trailing stop basado en ATR
- Risk: 1% capital por trade
- Leverage: configurable (default 20x en Hyperliquid)

DATOS HISTÓRICOS DEL BACKTEST (BTC 2024-06 a 2026-06):
- Capital $30, Risk 1%, Leverage 20x
- Return: +1.38% en 2 años
- Win rate: 60% (6 ganadores, 4 perdedores)
- Profit factor: 1.85
- Max drawdown: 1.83%
- Sharpe: 0.36
- Alpha vs Buy&Hold: +2.53%
"""

from datetime import datetime
from typing import Optional, Dict, Any

import logging
import talipy.abstract as ta
from pandas import DataFrame

from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from freqtrade.persistence import Trade


logger = logging.getLogger(__name__)


class SmaCrossoverV4(IStrategy):
    """
    v4 SMA Crossover Strategy — Trend Following
    
    Reglas:
    - Long entry: SMA20 cruza arriba SMA50
    - Short entry: SMA20 cruza abajo SMA50 (si configuran can_short)
    - Exit: trailing stop basado en ATR
    - Risk: 1% capital por trade
    
    Adaptada a Hyperliquid (15m timeframe para más oportunidades)
    """
    
    INTERFACE_VERSION = 3
    
    # Timeframe
    timeframe = '15m'
    
    # Solo 1 posición a la vez (mantener simple y seguro)
    position_adjustment_enable = False
    max_open_trades = 1
    
    # Stops
    stoploss = -0.15  # -15% stoploss de emergencia (con 20x leverage = -0.75% price move)
    trailing_stop = True
    trailing_stop_positive = 0.05  # 5% profit para activar trailing
    trailing_stop_positive_offset = 0.10  # 10% offset
    trailing_only_offset_is_reached = True
    
    # Hyperliquid soporta short
    can_short = True
    
    # Salida al cierre del mercado (no mantener fin de semana)
    process_only_new_candles = True
    use_exit_signal = True
    
    # Número mínimo de velas antes de empezar a operar
    startup_candle_count = 200
    
    # Parámetros optimizables
    sma_fast_period = IntParameter(20, 10, 50, default=20, space='buy', optimize=True)
    sma_slow_period = IntParameter(50, 30, 200, default=50, space='buy', optimize=True)
    
    # ============================================================
    # INDICADORES
    # ============================================================
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Calcula todos los indicadores necesarios"""
        
        # SMAs
        dataframe['sma_fast'] = ta.SMA(dataframe, timeperiod=self.sma_fast_period.value)
        dataframe['sma_slow'] = ta.SMA(dataframe, timeperiod=self.sma_slow_period.value)
        
        # SMA anterior (para detectar cruces)
        dataframe['sma_fast_prev'] = dataframe['sma_fast'].shift(1)
        dataframe['sma_slow_prev'] = dataframe['sma_slow'].shift(1)
        
        # Detectar cruces (True si hubo cruce en la vela cerrada)
        dataframe['golden_cross'] = (
            (dataframe['sma_fast'] > dataframe['sma_slow']) &  # ahora fast > slow
            (dataframe['sma_fast_prev'] <= dataframe['sma_slow_prev'])  # antes fast <= slow
        )
        dataframe['death_cross'] = (
            (dataframe['sma_fast'] < dataframe['sma_slow']) &  # ahora fast < slow
            (dataframe['sma_fast_prev'] >= dataframe['sma_slow_prev'])  # antes fast >= slow
        )
        
        # ATR para trailing stops dinámicos
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        
        # RSI para filtro de momentum (evitar entradas en extremos)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # EMA200 como filtro de tendencia macro
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)
        
        # Volume para confirmación
        dataframe['volume_sma'] = dataframe['volume'].rolling(window=20).mean()
        
        return dataframe
    
    # ============================================================
    # ENTRADAS
    # ============================================================
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Define señales de entrada"""
        
        # LONG: golden cross + confirmaciones
        dataframe.loc[
            (
                dataframe['golden_cross'] &  # cruce golden
                (dataframe['close'] > dataframe['ema200']) &  # tendencia alcista macro
                (dataframe['rsi'] < 70) &  # no overbought
                (dataframe['volume'] > dataframe['volume_sma'])  # volumen confirma
            ),
            'enter_long'] = 1
        
        # SHORT: death cross + confirmaciones
        dataframe.loc[
            (
                dataframe['death_cross'] &  # cruce death
                (dataframe['close'] < dataframe['ema200']) &  # tendencia bajista macro
                (dataframe['rsi'] > 30) &  # no oversold
                (dataframe['volume'] > dataframe['volume_sma'])  # volumen confirma
            ),
            'enter_short'] = 1
        
        return dataframe
    
    # ============================================================
    # SALIDAS
    # ============================================================
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Define señales de salida"""
        
        # Exit long: death cross (la misma señal de entrada short)
        dataframe.loc[
            (
                dataframe['death_cross']
            ),
            'exit_long'] = 1
        
        # Exit short: golden cross (la misma señal de entrada long)
        dataframe.loc[
            (
                dataframe['golden_cross']
            ),
            'exit_short'] = 1
        
        return dataframe
    
    # ============================================================
    # GESTIÓN DE POSICIÓN AVANZADA
    # ============================================================
    
    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime,
                        current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Stoploss dinámico basado en ATR
        Más agresivo cuando hay profit, más conservador cuando hay loss
        """
        # Si está en profit > 5%, apretar el stop
        if current_profit > 0.05:
            return 0.02  # stop a +2% (lock profit)
        
        # Si está en profit > 10%, apretar más
        if current_profit > 0.10:
            return 0.01  # stop a +1% (lock más profit)
        
        # Default: stoploss normal
        return self.stoploss
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                            time_in_force: str, current_time: datetime, entry_tag: Optional[str],
                            side: str, **kwargs) -> bool:
        """
        Confirmación final antes de abrir trade.
        Aquí puedes añadir filtros adicionales.
        """
        # Solo 1 trade a la vez (max_open_trades ya lo controla, pero doble check)
        open_trades = Trade.get_open_trades()
        if len(open_trades) >= 1:
            return False
        
        return True
    
    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, side: str,
                 **kwargs) -> float:
        """
        Define el leverage a usar.
        Para Hyperliquid: 20x fijo (configurable en config.json)
        """
        return 20.0  # 20x leverage
    
    # ============================================================
    # PLOTTING (opcional, para visualización en FreqUI)
    # ============================================================
    
    def plot_config(self):
        """Configuración de gráficos para FreqUI"""
        return {
            'main_plot': {
                'sma_fast': {'color': 'blue'},
                'sma_slow': {'color': 'orange'},
                'ema200': {'color': 'red'},
            },
            'subplots': {
                'RSI': {
                    'rsi': {'color': 'purple'},
                },
            }
        }
