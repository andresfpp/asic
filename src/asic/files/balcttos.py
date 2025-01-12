import logging
import pathlib

# Third party imports
import pandas as pd

# Local application imports
from asic.reader import FileReader

from ..metadata import FileItemInfo

logger = logging.getLogger(__name__)

balcttos_format = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {},
    "dtype": {
        "CONCEPTO": str,
        "MERCADO": str,
        "CÓDIGO CONTRATO": str,
        "COMPRADOR": str,
        "VENDEDOR": str,
        "TIPO DE DESPACHO": str,
        "TIPO ASIGNA": str,
        "HORA 01": float,
        "HORA 02": float,
        "HORA 03": float,
        "HORA 04": float,
        "HORA 05": float,
        "HORA 06": float,
        "HORA 07": float,
        "HORA 08": float,
        "HORA 09": float,
        "HORA 10": float,
        "HORA 11": float,
        "HORA 12": float,
        "HORA 13": float,
        "HORA 14": float,
        "HORA 15": float,
        "HORA 16": float,
        "HORA 17": float,
        "HORA 18": float,
        "HORA 19": float,
        "HORA 20": float,
        "HORA 21": float,
        "HORA 22": float,
        "HORA 23": float,
        "HORA 24": float,
    },
}

class BALCTTOS(FileReader):
    def __init__(self):
        return super().__init__(balcttos_format.copy())


def balcttos_preprocess(filepath: pathlib.Path, item: FileItemInfo) -> pd.DataFrame:
    """
    balcttos: se publica un archivo por día.
    versiones: TX2, TXR y TXF
    CONCEPTO:
      EBRC: Energía en bolsa regulada a cargo, en kWh.
      EBOC: Energía en bolsa no regulada a cargo, en kWh.
    AGENTE:
      EPSC: Código SIC del agente comercializador
    """
    balcttos_reader = BALCTTOS()
    total = balcttos_reader.read(filepath)
    total["FECHA"] = f"{item.year:04d}-{item.month:02d}-{item.day:02d}"

    total["FECHA"] = pd.to_datetime(
        total["FECHA"],
        format="%Y-%m-%d",
    )
    total = (
        total.set_index(["FECHA","CONCEPTO","MERCADO","CÓDIGO CONTRATO","COMPRADOR","VENDEDOR","TIPO DE DESPACHO","TIPO ASIGNA"])
        .stack()
        .reset_index()
    )
    total = total.rename(columns={"level_8": "NOMBRE HORA", 0: "VALOR"})
    total["HORA"] = (total["NOMBRE HORA"].str.slice(start=-2)).astype(int) - 1
    total["HORA"] = pd.to_timedelta(total["HORA"], unit="h")
    total["FECHA_HORA"] = total["FECHA"] + total["HORA"]
    total["HORA"] = total["FECHA_HORA"].dt.strftime("%H:%M:%S")
    ret_cols = ["FECHA_HORA", "CONCEPTO","MERCADO","CÓDIGO CONTRATO","COMPRADOR","VENDEDOR","TIPO DE DESPACHO","TIPO ASIGNA", "VALOR"]
    return total[ret_cols]