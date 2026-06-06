"""
main.py — Punto de entrada del Cotizador EV
Ejecutar: python main.py
"""
import os
import webview
from api.pdf_generator import generar_pdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Api:
    """
    Métodos accesibles desde JS via:
        window.pywebview.api.nombre_metodo(args)
    """

    def generar_pdf(self, datos: dict) -> dict:
        """
        Genera el PDF de cotización y lo abre con el visor del sistema.

        Args:
            datos: {
                creditType, amount, term, interest,
                monthlyPayment, netAmount, encajeRate, encajeAmount,
                desgravamenAmount, solcaAmount, totalDiscounts,
                nombre, cedula, tipo_socio, apertura, destino,
                asesor, telefono
            }
        Returns:
            { ok: bool, ruta: str, error: str }
        """
        try:
            ruta = generar_pdf(datos, BASE_DIR)
            os.startfile(ruta)
            return {"ok": True, "ruta": ruta, "error": ""}
        except Exception as e:
            return {"ok": False, "ruta": "", "error": str(e)}

    def ping(self) -> str:
        return "pong"


def main():
    api = Api()
    index = os.path.join(BASE_DIR, "index.html")

    window = webview.create_window(
        title="Cotizador — Esperanza del Valle",
        url=index,
        js_api=api,
        maximized=True,
        min_size=(900, 600),
        resizable=True,
    )

    webview.start(gui="edgechromium", debug=False)


if __name__ == "__main__":
    main()
