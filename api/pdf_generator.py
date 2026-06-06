"""
api/pdf_generator.py
Replica el formato visual del PDF original de Esperanza del Valle.
"""
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

AZUL   = colors.HexColor("#003399")
BLANCO = colors.white
NEGRO  = colors.black

_REQ_DEP = [
    "Copia de cédula (deudor - cónyuge)",
    "Copia de papeleta de votación (deudor - cónyuge)",
    "Copia de servicio básico (agua, luz o teléfono)",
    "Copia del impuesto predial (si posee)",
    "Copia de matrícula del vehículo (si posee)",
    "Certificado de ingreso y 3 últimos roles de pago",
    "Movimientos bancarios (3 últimos meses)",
]

_REQ_IND = [
    "Copia de cédula (deudor - cónyuge)",
    "Copia de papeleta de votación (deudor - cónyuge)",
    "Copia de servicio básico (agua, luz o teléfono)",
    "Copia del impuesto predial (si posee)",
    "Copia de matrícula del vehículo (si posee)",
    "Copia del R.U.C. 3 últimas declaraciones del I.V.A.",
    "Copia del impuesto a la renta (último año)",
    "Movimientos bancarios (3 últimos meses)",
]

_REQ_AMBOS = list(dict.fromkeys(_REQ_DEP + _REQ_IND))

_REQUISITOS = {
    "Dependiente":   ("REQUISITOS TRABAJADORES DEPENDIENTES",                 _REQ_DEP),
    "Independiente": ("REQUISITOS TRABAJADORES INDEPENDIENTES",                _REQ_IND),
    "Ambos":         ("REQUISITOS TRABAJADORES DEPENDIENTES E INDEPENDIENTES", _REQ_AMBOS),
}


def _fmt(v) -> str:
    n = float(v or 0)
    return f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(v) -> str:
    return f"{float(v or 0):.2f}%"


def _mes_es(n: int) -> str:
    return ["enero","febrero","marzo","abril","mayo","junio",
            "julio","agosto","septiembre","octubre","noviembre","diciembre"][n-1]


def _fecha_es() -> str:
    hoy = datetime.now()
    return f"{hoy.day} de {_mes_es(hoy.month)} de {hoy.year}"


def _e(nombre, **kw) -> ParagraphStyle:
    base = dict(fontName="Helvetica", fontSize=9, leading=13, textColor=NEGRO)
    base.update(kw)
    return ParagraphStyle(nombre, **base)


E_INST   = _e("inst",   fontName="Helvetica-Bold", fontSize=12, textColor=BLANCO, alignment=1, leading=17)
E_COT    = _e("cot",    fontName="Helvetica-Bold", fontSize=10, textColor=BLANCO, alignment=1)
E_FECHA  = _e("fecha",  fontSize=9, alignment=2)
E_SOCIO  = _e("socio",  fontName="Helvetica-Bold", fontSize=9)
E_INTRO  = _e("intro",  fontSize=9, leading=13)
E_LBL_W  = _e("lblw",   fontName="Helvetica-Bold", fontSize=8, textColor=BLANCO, alignment=2)
E_VAL    = _e("val",    fontSize=9, alignment=2)
E_SEC    = _e("sec",    fontName="Helvetica-Bold", fontSize=9, textColor=BLANCO, alignment=1)
E_NOTA   = _e("nota",   fontSize=9, leading=13)
E_REQ    = _e("req",    fontSize=9)
E_NUM_W  = _e("numw",   fontName="Helvetica-Bold", fontSize=9, textColor=BLANCO, alignment=1)
E_PIE    = _e("pie",    fontName="Helvetica-Oblique", fontSize=8,
             textColor=BLANCO, alignment=1, leading=13)
E_ASESOR = _e("asesor", fontName="Helvetica-Bold", fontSize=9, textColor=AZUL)
E_ASDET  = _e("asdet",  fontName="Helvetica-Bold", fontSize=9)
E_ASTLF  = _e("astlf",  fontSize=9)


def _tabla_credito_cuenta(datos, W):
    tipo_credito    = datos.get("creditType", "Consumo").upper()
    monto           = float(datos.get("amount", 0))
    plazo           = int(datos.get("term", 0))
    tasa            = float(datos.get("interest", 0))
    cuota           = float(datos.get("monthlyPayment", 0))
    neto            = float(datos.get("netAmount", 0))          # = financedAmount
    encaje_pct      = float(datos.get("encajeRate", 0))
    encaje_monto    = float(datos.get("encajeAmount", 0))
    apertura        = float(datos.get("apertura", 0))
    destino         = (datos.get("destino", "") or "—").upper()
    desgravamen_act = bool(datos.get("desgravamenActivo", False))
    desgravamen_amt = float(datos.get("desgravamenAmount", 0))
    financed        = float(datos.get("financedAmount", monto))
    total_encaje    = encaje_monto + apertura

    TW    = W * 0.90
    pad   = (W - TW) / 2
    mitad = TW / 2 - 1*mm
    lbl_w = mitad * 0.56
    val_w = mitad * 0.44

    def fila(lbl, val):
        return [Paragraph(lbl, E_LBL_W), Paragraph(val, E_VAL)]

    # ── CRÉDITO ──────────────────────────────────────────────
    cred_data = [
        [Paragraph("CRÉDITO", E_SEC), ""],
        fila("Tipo de crédito",         tipo_credito),
        fila("Destino del Crédito",     destino),
        fila("Monto solicitado",        f"$ {_fmt(monto)}"),
        fila("Monto financiado",        f"$ {_fmt(financed)}"),
        fila("Plazo (meses)",           str(plazo)),
        fila("Interés",                 _pct(tasa)),
        fila("Cuotas mensuales fijas",  f"$ {_fmt(cuota)}"),
    ]

    # ── CUENTA Y GARANTÍA ─────────────────────────────────────
    desgravamen_str = f"$ {_fmt(desgravamen_amt)}" if desgravamen_act else "No incluido"
    cuen_data = [
        [Paragraph("CUENTA Y GARANTÍA", E_SEC), ""],
        fila("Seguro de desgravamen",        desgravamen_str),
        fila("Apertura de Cuenta",           f"$ {_fmt(apertura)}"),
        fila(f"Encaje {int(encaje_pct)}%",   f"$ {_fmt(encaje_monto)}"),
        fila("TOTAL encaje + apertura",      f"$ {_fmt(total_encaje)}"),
        fila("Monto a Recibir",              f"$ {_fmt(neto)}"),
    ]

    # Igualar número de filas
    while len(cuen_data) < len(cred_data):
        cuen_data.append(["", ""])
    while len(cred_data) < len(cuen_data):
        cred_data.append(["", ""])

    def estilo_mitad(destacar_bold=()):
        s = [
            ("SPAN",          (0,0),(1,0)),
            ("BACKGROUND",    (0,0),(1,0),   AZUL),
            ("ALIGN",         (0,0),(1,0),   "CENTER"),
            ("TOPPADDING",    (0,0),(1,0),   5),
            ("BOTTOMPADDING", (0,0),(1,0),   5),
            ("BACKGROUND",    (0,1),(0,-1),  AZUL),
            ("ALIGN",         (0,1),(0,-1),  "RIGHT"),
            ("TOPPADDING",    (0,1),(0,-1),  4),
            ("BOTTOMPADDING", (0,1),(0,-1),  4),
            ("RIGHTPADDING",  (0,1),(0,-1),  5),
            ("LEFTPADDING",   (0,1),(0,-1),  5),
            ("BACKGROUND",    (1,1),(1,-1),  BLANCO),
            ("ALIGN",         (1,1),(1,-1),  "RIGHT"),
            ("TOPPADDING",    (1,1),(1,-1),  4),
            ("BOTTOMPADDING", (1,1),(1,-1),  4),
            ("RIGHTPADDING",  (1,1),(1,-1),  5),
            ("BOX",           (0,0),(-1,-1), 0.5, AZUL),
            ("INNERGRID",     (0,0),(-1,-1), 0.4, AZUL),
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ]
        for fi in destacar_bold:
            s += [("FONTNAME", (0,fi),(1,fi), "Helvetica-Bold")]
        return TableStyle(s)

    t_cred = Table(cred_data, colWidths=[lbl_w, val_w])
    t_cuen = Table(cuen_data, colWidths=[lbl_w, val_w])
    t_cred.setStyle(estilo_mitad())
    t_cuen.setStyle(estilo_mitad(destacar_bold=[4, 5]))

    t_doble = Table(
        [["", t_cred, t_cuen, ""]],
        colWidths=[pad, mitad, mitad, pad],
    )
    t_doble.setStyle(TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
        ("TOPPADDING",   (0,0),(-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 0),
    ]))
    return t_doble


def _tabla_requisitos(tipo_socio: str, W: float):
    titulo, lista = _REQUISITOS.get(tipo_socio, _REQUISITOS["Dependiente"])

    TW  = W * 0.90
    pad = (W - TW) / 2

    t_header = Table(
        [["", Paragraph(titulo, E_SEC), ""]],
        colWidths=[pad, TW, pad],
    )
    t_header.setStyle(TableStyle([
        ("BACKGROUND",    (1,0),(1,0), AZUL),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
    ]))

    num_w = 8*mm
    req_w = TW - num_w

    filas = [[Paragraph(str(i+1), E_NUM_W), Paragraph(req, E_REQ)]
             for i, req in enumerate(lista)]

    t_body = Table(filas, colWidths=[num_w, req_w])
    t_body.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(0,-1), AZUL),
        ("BACKGROUND",    (1,0),(1,-1), BLANCO),
        ("ALIGN",         (0,0),(0,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("BOX",           (0,0),(-1,-1), 0.5, AZUL),
        ("INNERGRID",     (0,0),(-1,-1), 0.4, AZUL),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (1,0),(1,-1), 8),
        ("RIGHTPADDING",  (1,0),(1,-1), 6),
    ]))

    t_body_wrap = Table(
        [["", t_body, ""]],
        colWidths=[pad, TW, pad],
    )
    t_body_wrap.setStyle(TableStyle([
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
        ("TOPPADDING",   (0,0),(-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 0),
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
    ]))

    return t_header, t_body_wrap


def generar_pdf(datos: dict, base_dir: str) -> str:
    tipo_socio = datos.get("tipo_socio", "Dependiente")
    nombre     = (datos.get("nombre",   "") or "").strip().upper() or "—"
    cedula     = (datos.get("cedula",   "") or "").strip() or "—"
    asesor     = (datos.get("asesor",   "") or "Asesor de crédito").strip()
    telefono   = (datos.get("telefono", "") or "").strip()
    tipo_cred  = datos.get("creditType", "Consumo")

    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = os.path.join(base_dir, f"Cotizacion_{tipo_cred}_{tipo_socio}_{ts}.pdf")

    doc = SimpleDocTemplate(
        ruta, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=12*mm,  bottomMargin=12*mm,
    )
    W     = A4[0] - 36*mm
    items = []

    # ── Encabezado ────────────────────────────────────────────
    logo_path = ""
    for ext in ("logo.jpg", "logo.png"):
        p = os.path.join(base_dir, "img", ext)
        if os.path.exists(p):
            logo_path = p
            break

    logo_w, logo_h = 18*mm, 18*mm
    logo_cel = Image(logo_path, width=logo_w, height=logo_h) \
               if logo_path else Paragraph("", E_INST)

    t_enc = Table([[
        logo_cel,
        [Paragraph("COTIZADOR", E_COT),
         Paragraph("CAJA DE AHORRO Y CRÉDITO ESPERANZA DEL VALLE", E_INST)],
    ]], colWidths=[logo_w + 4*mm, W - logo_w - 4*mm])
    t_enc.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(0,0),   BLANCO),
        ("BACKGROUND",    (1,0),(1,0),   AZUL),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ALIGN",         (0,0),(0,0),   "CENTER"),
        ("ALIGN",         (1,0),(1,0),   "CENTER"),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 2),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
    ]))
    items.append(t_enc)
    items.append(Spacer(1, 4*mm))

    items.append(Paragraph(f"Quito, {_fecha_es()}", E_FECHA))
    items.append(Spacer(1, 2*mm))

    items.append(Paragraph(f'<b>SR(A).</b>  {nombre}', E_SOCIO))
    items.append(Paragraph(f'<b>C.I</b>  {cedula}', E_SOCIO))
    items.append(Spacer(1, 3*mm))

    items.append(Paragraph(
        "En respuesta a su solicitud de crédito, <b>ESPERANZA DEL VALLE,</b> "
        "se complace en entregar la siguiente cotización pre-aprobada.",
        E_INTRO
    ))
    items.append(Spacer(1, 4*mm))

    items.append(_tabla_credito_cuenta(datos, W))
    items.append(Spacer(1, 4*mm))

    items.append(Paragraph(
        "Importante recalcar que una vez entregada la cotización, en respuesta a su "
        "solicitud de crédito, tiene una vigencia no mayor a <b>7 días laborables.</b>",
        E_NOTA
    ))
    items.append(Spacer(1, 4*mm))

    req_header, req_body = _tabla_requisitos(tipo_socio, W)
    items.append(req_header)
    items.append(req_body)
    items.append(Spacer(1, 6*mm))

    # ── Firma ─────────────────────────────────────────────────
    firma_items = [
        Paragraph(asesor, E_ASESOR),
        Paragraph("Asesor de crédito", E_ASDET),
    ]
    if telefono:
        firma_items.append(Paragraph(telefono, E_ASTLF))

    t_firma = Table([[p] for p in firma_items], colWidths=[W * 0.45], hAlign="LEFT")
    t_firma.setStyle(TableStyle([
        ("LINEABOVE",     (0,0),(0,0), 0.8, NEGRO),
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 2),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("ALIGN",         (0,0),(-1,-1), "LEFT"),
    ]))
    items.append(t_firma)
    items.append(Spacer(1, 6*mm))

    # ── Pie ───────────────────────────────────────────────────
    t_pie = Table([[Paragraph(
        '"Un producto creado para satisfacer las necesidades de las personas, '
        'es un producto que tiene por objetivo, servir y confiar en las personas".',
        E_PIE
    )]], colWidths=[W])
    t_pie.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), AZUL),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 10),
    ]))
    items.append(t_pie)

    doc.build(items)
    return ruta