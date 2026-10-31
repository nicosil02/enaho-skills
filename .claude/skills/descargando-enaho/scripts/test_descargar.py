"""Comprueba que un zip dañado o sin datos del año se rechace."""
import tempfile
import zipfile
from pathlib import Path

from descargar import zip_valido

with tempfile.TemporaryDirectory() as t:
    bueno = Path(t) / "bueno.zip"
    with zipfile.ZipFile(bueno, "w") as z:
        z.writestr("966-Modulo34/sumaria-2024.dta", "x" * 5000)
    assert zip_valido(bueno, 2024)
    assert not zip_valido(bueno, 2023)

    cortado = Path(t) / "cortado.zip"
    cortado.write_bytes(bueno.read_bytes()[:100])
    assert not zip_valido(cortado, 2024)

    alterado = Path(t) / "alterado.zip"
    datos = bytearray(bueno.read_bytes())
    datos[60] ^= 0xFF  # Un byte dentro del contenido comprimido
    alterado.write_bytes(datos)
    assert not zip_valido(alterado, 2024)

print("ok")
