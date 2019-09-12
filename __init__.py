from pprint import pprint
import re
import datetime
import functools
import enum
import PyPDF2
import pdftotext
import parsy
import attr

# ================================================================================
# Pdf
# ================================================================================
pdf_path = './pdfs/BORME-A-2019-172-28.pdf'
pdf_outline = []
with open(pdf_path, 'rb') as f:
    pdf = PyPDF2.PdfFileReader(f)
    pdf_outline = pdf.getOutlines()


def act_titles(pdf_outline):
    _, *pdf_outline = pdf_outline
    return [entry['/Title'] for entry in pdf_outline[0]]


pdf = None
with open(pdf_path, "rb") as f:
    pdf = pdftotext.PDF(f)

re_cve = r'cve:[\s]+BORME-A-\d{4}-\d+-\d{2}'
re_page_header = r'BOLETÍN[\s]+OFICIAL[\s]+DEL[\s]+REGISTRO[\s]+MERCANTIL[\s]+Núm.[\s]+\d+[\s]+(Lunes|Miércoles|Jueves)[\s]+\d{1,2}[\s]+de[\s]+(enero|agosto|septiembre)[\s]+de[\s]+\d{4}[\s]+Pág\.[\s]+\d+'

text = "\n\n".join(pdf)
text = re.sub(re_cve, '', text)
text = re.sub(re_page_header, '', text)
text = re.sub('\s+', ' ', text).strip()


# ================================================================================
# Converters
# ================================================================================
@attr.s
class ActList:
    acts = attr.ib()


@attr.s
class Act:
    title = attr.ib()
    fields = attr.ib()


@attr.s
class FieldList:
    fields = attr.ib()


@attr.s
class Field:
    name = attr.ib()
    content = attr.ib()


# ================================================================================
# Enums
# ================================================================================
class KeywordMain(enum.Enum):
    # single
    DECLARACION_DE_UNIPERSONALIDAD = 'Declaración de unipersonalidad.'
    PERDIDA_DEL_CARACTER_DE_UNIPERSONALIDAD = 'Pérdida del caracter de unipersonalidad.'
    EXTINCION = 'Extinción.'
    # not sure if this is a keyword, see: Jueves 5 de septiembre de 2019 MADRID, entry: 381477 - LUNA BARRIOS Y BONADEA SL.
    DEPOSITO_DE_LIBROS = 'Depósito de libros.'
    # simple
    SOCIO_UNICO = 'Socio único:'
    CAMBIO_DE_DENOMINACION_SOCIAL = 'Cambio de denominación social.'
    CONSTITUCION = 'Constitución.'
    EMPRESARIO_INDIVIDUAL = 'Empresario Individual.'
    AMPLIACION_DE_CAPITAL = 'Ampliación de capital.'
    FUSION_POR_UNION = 'Fusión por unión.'
    REVOCACIONES = 'Revocaciones.'
    MODIFICACIONES_ESTATUTARIAS = 'Modificaciones estatutarias.'
    CAMBIO_DE_OBJETO_SOCIAL = 'Cambio de objeto social.'
    CAMBIO_DE_DOMICILIO_SOCIAL = 'Cambio de domicilio social.'
    AMPLIACION_DEL_OBJETO_SOCIAL = 'Ampliacion del objeto social.'
    REELECCIONES = 'Reelecciones.'
    APERTURA_DE_SUCURSAL = 'Apertura de sucursal.'
    ARTICULO_378_5_DEL_REGLAMENTO_DEL_REGISTRO_MERCANTIL = 'Articulo 378.5 del Reglamento del Registro Mercantil.'
    OTROS_CONCEPTOS = 'Otros conceptos:'
    AMPLIACION_DEL_CAPITAL = 'Ampliación de capital.'
    REDUCCION_DE_CAPITAL = 'Reducción de capital.'
    SITUACION_CONCURSAL = 'Situación concursal.'
    FUSION_POR_ABSORCION = 'Fusión por absorción.'
    SUSPENSION_DE_PAGOS = 'Suspensión de pagos.'
    TRANSFORMACION_DE_SOCIEDAD = 'Transformación de sociedad.'
    CANCELACIONES_DE_OFICIO_DE_NOMBRAMIENTOS = 'Cancelaciones de oficio de nombramientos.'
    DESEMBOLSO_DE_DIVIDENDOS_PASIVOS = 'Desembolso de dividendos pasivos.'
    PAGINA_WEB_DE_LA_SOCIEDAD = 'Página web de la sociedad.'
    PRIMERA_SUCURSAL_DE_SOCIEDAD_EXTRANJERA = 'Primera sucursal de sociedad extranjera.'
    EMISION_DE_OBLIGACIONES = 'Emisión de obligaciones.'
    MODIFICACION_DE_PODERES = 'Modificación de poderes.'
    ESCISION_PARCIAL = 'Escisión parcial.'
    QUIEBRA = 'Quiebra.'
    SUCURSAL = 'Sucursal.'
    CESION_GLOBAL_DE_ACTIVO_Y_PASIVO = 'Cesión global de activo y pasivo.'
    SEGREGACION = 'Segregación.'
    PRIMERA_INSCRIPCION_OM_10_6_1997 = 'Primera inscripcion (O.M. 10/6/1.997).'
    ANOTACION_PREVENTIVA_DEMANDA_DE_IMPUGNACION_DE_ACUERDOS_SOCIALES = 'Anotación preventiva. Demanda de impugnación de acuerdos sociales.'
    ANOTACION_PREVENTIVA_DECLARACION_DE_DEUDOR_FALLIDO = 'Anotación preventiva. Declaración de deudor fallido.'
    CREDITO_INCOBRABLE = 'Crédito incobrable.'
    SOCIEDAD_UNIPERSONAL = 'Sociedad unipersonal.'
    REAPERTURA_DE_HOJA_REGISTRAL = 'Reapertura hoja registral.'
    ADAPTACION_DE_LEY_2_95 = 'Adaptación Ley 2/95.'
    ADAPTACION_DE_LEY_44_2015 = 'Adaptación Ley 44/2015.'
    ADAPTACION_SEGUN_DT_2_APARTADO_2_LEY_2_95 = 'Adaptada segun D.T. 2 apartado 2 Ley 2/95.'
    CIERRE_PROVISIONAL_HOJA_REGISTRAL_POR_BAJA_EN_EL_INDICE_DE_ENTIDADES_JURIDICAS = 'Cierre provisional hoja registral por baja en el índice de Entidades Jurídicas.'
    CIERRE_PROVISIONAL_DE_LA_HOJA_REGISTRAL_POR_REVOCACION_DEL_NIF = 'Cierre provisional de la hoja registral por revocación del NIF.'
    CIERRE_PROVISIONAL_HOJA_REGISTRAL_POR_REVOCACION_DEL_NIF_DE_ENTIDADES_JURIDICAS = 'Cierre provisional hoja registral por revocación del NIFde Entidades Jurídicas.'
    CIERRE_PROVISIONAL_HOJA_REGISTRAL_POR_ART_137_2_LEY_43_1995_IMPUESTO_DE_SOCIEDADES = 'Cierre provisional hoja registral art. 137.2 Ley 43/1995 Impuesto de Sociedades.'
    REACTIVACION_DE_LA_SOCIEDAD_ART_242_DEL_REGLAMENTO_DEL_REGISTRO_MERCANTIL = 'Reactivación de la sociedad (Art. 242 del Reglamento del Registro Mercantil).'
    ADAPTACION_DE_SOCIEDAD = 'Adaptación de sociedad.'
    CIERRE_DE_SUCURSAL = 'Cierre de Sucursal.'
    MODIFICACION_DE_DURACION = 'Modificación de duración:'
    FE_DE_ERRATAS = 'Fe de erratas:'
    ACUERDO_DE_AMPLIACION_DE_CAPITAL_SOCIAL_SIN_EJECUTAR_IMPORTE_DEL_ACUERDO = 'Acuerdo de ampliación de capital social sin ejecutar. Importe del acuerdo.'
    ESCISION_TOTAL = 'Escisión total.'
    DISOLUCION = 'Disolución.'
    # compound
    CESES_DIMISIONES = 'Ceses/Dimisiones.'
    NOMBRAMIENTOS = 'Nombramientos.'
    DATOS_REGISTRALES = 'Datos registrales.'


class KeywordPosition(enum.Enum):
    ADM_UNICO = 'Adm. Unico:'
    ADM_SOLID = 'Adm. Solid.:'
    LIQUIDADOR = 'Liquidador:'
    LIQUIDADOR_M = 'Liquidador M:'
    ADM_MANCOM = 'Adm. Mancom.:'
    APODERADO = 'Apoderado:'
    APO_MANC = 'Apo.Manc.:'
    APO_MAN_SOLI = 'Apo.Man.Soli:'
    APO_SOL = 'Apo.Sol.:'
    CONSEJERO = 'Consejero:'
    SOCIO_MIEMBR = 'Socio Miembr:'
    AUDITOR = 'Auditor:'
    AUDITOR_SUPLENTE = 'Aud.Supl.:'
    VSECRNOCONSJ = 'VsecrNoConsj:'
    CO_DE_MA_SO = 'Co.De.Ma.So:'
    ENT_GESTORA = 'Ent. Gestora:'
    PRESIDENTE = 'Presidente:'
    SECRETARIO = 'Secretario:'
    VICESECRET = 'Vicesecret.:'
    SECRENOCONSJ = 'SecreNoConsj:'
    SOC_PROF = 'Soc.Prof.:'
    REPRESENTAN = 'Representan:'
    CON_DELEGADO = 'Con.Delegado:'
    CON_IND = 'Con.Ind.:'
    CONS_EXT_DOM = 'Cons.Ext.Dom:'
    VICEPRESID = 'Vicepresid.:'
    CONS_EXTERNO = 'Cons.Externo:'
    CONSJ_DOMINI = 'Consj.Domini:'
    CONS_DEL_SOL = 'Cons.Del.Sol:'
    MIEM_COM_CTR = 'Miem.Com.Ctr:'
    PRES_COM_CTR = 'Pres.Com.Ctr:'
    VPR_COM_CTR = 'Vpr.Com.Ctr:'
    SECR_COM_CTR = 'Secr.Com.Ctr:'
    VICES_COM_CT = 'Vices.Com.Ct:'
    LIQUISOLI = 'LiquiSoli:'
    # not sure if are KeywordPositions
    # see: 385129 - ELCANO HIGH YIELD OPPORTUNITIES, SIL SA., Lunes 9 de septiembre de 2019 Madrid
    ENTIDDEPOSIT = 'EntidDeposit:'
    ENT_REG_CONT = 'Ent.Reg.Cont:'


# ================================================================================
# Utils
# ================================================================================
def flip(fn):
    @functools.wraps(fn)
    def fn_new(*args):
        return fn(*args[::-1])

    return fn_new


# ================================================================================
# Lang
# ================================================================================
def many_till(parser, parser_end):
    @parsy.Parser
    def _many_till(stream, index):
        index_start = index
        values = []
        parser_result = None
        while True:
            parser_end_result = parser_end(stream, index)
            if parser_end_result.status:
                return parsy.Result.success(index, values).aggregate(parser_result)

            parser_result = parser(stream, index).aggregate(parser_result)
            if parser_result.status:
                values.append(parser_result.value)
                index = parser_result.index

            if index >= len(stream):
                return parsy.Result.success(index_start, [])

    return _many_till


def any_till(parser):
    @parsy.generate
    def _any_till():
        return (yield many_till(
            parsy.any_char,
            parser
        ).combine(lambda *args: ''.join(args)))

    return _any_till


dot = parsy.string('.')
comma = parsy.string(',')
lparen = parsy.string('(')
rparen = parsy.string(')')
lexeme = lambda p: p << parsy.whitespace
nothing = parsy.index.map(lambda _: '')
keyword_main = parsy.from_enum(KeywordMain)
keyword_position = parsy.from_enum(KeywordPosition)
borme_string = parsy.string('BOLETÍN OFICIAL DEL REGISTRO MERCANTIL')
decimal_digits = parsy.decimal_digit.many().combine(lambda *args: int(''.join(args)))

day_name = parsy.alt(
    parsy.string('Lunes'),
    parsy.string('Martes'),
    parsy.string('Miércoles'),
    parsy.string('Jueves')
).map(lambda name: name.lower())

months_numbers_by_name = {
    'enero': 1,
    'febrero': 2,
    'marzo': 3,
    'abril': 4,
    'mayo': 5,
    'junio': 6,
    'julio': 7,
    'agosto': 8,
    'septiembre': 9,
    'octubre': 10,
    'noviembre': 11,
    'diciembre': 12,
}

month_name = parsy.alt(
    parsy.string('enero'),
    parsy.string('agosto'),
    parsy.string('septiembre'),
    parsy.string('octubre')
).map(lambda name: months_numbers_by_name[name])

date = parsy.seq(
    day_name.tag(None),
    parsy.whitespace.tag(None),
    decimal_digits.tag('day'),
    parsy.string(' de ').tag(None),
    month_name.tag('month'),
    parsy.string(' de ').tag(None),
    decimal_digits.tag('year')
).combine_dict(datetime.date)

province = parsy.alt(
    parsy.string('ALMERÍA'),
    parsy.string('MADRID'),
    parsy.string('JAÉN')
).map(lambda name: name.lower())

page_header = parsy.seq(
    borme_string.tag(None),
    parsy.whitespace.many().tag(None),
    parsy.string('Núm. ').tag(None),
    decimal_digits.tag('number'),
    parsy.whitespace.many().tag(None),
    date.tag('date'),
    parsy.whitespace.many().tag(None),
    parsy.string('Pág. ').tag(None),
    decimal_digits.tag(None),
    parsy.whitespace.many().tag(None)
).combine_dict(lambda **kwargs: kwargs)

doc_header = parsy.seq(
    parsy.whitespace.many().tag(None),
    parsy.string('SECCIÓN PRIMERA').tag(None),
    parsy.whitespace.many().tag(None),
    parsy.string('Empresarios').tag(None),
    parsy.whitespace.many().tag(None),
    parsy.string('Actos inscritos').tag(None),
    parsy.whitespace.many().tag(None),
    province.tag('province'),
    parsy.whitespace.tag(None)
).combine_dict(lambda **kwargs: kwargs)

cve = parsy.seq(
    parsy.string('cve: ').tag(None),
    parsy.string('BORME-A-').tag(None),
    decimal_digits.tag('year'),
    parsy.string('-').tag(None),
    decimal_digits.tag('number1'),
    parsy.string('-').tag(None),
    decimal_digits.tag('number2'),
    parsy.whitespace.tag(None)
).combine_dict(lambda **kwargs: kwargs)

borme_url = parsy.string('http://www.boe.es')

dl = parsy.seq(
    parsy.string('D.L.: '),
    parsy.any_char,
    parsy.string('-'),
    decimal_digits,
    parsy.string('/'),
    decimal_digits
).combine(lambda *args: ''.join([str(x) for x in args]))

issn = parsy.seq(
    parsy.string('ISSN: '),
    decimal_digits,
    parsy.string('-'),
    decimal_digits
).combine(lambda *args: ''.join([str(x) for x in args]))

doc_footer = parsy.seq(
    # cve.tag('cve'),
    borme_url.tag(None),
    parsy.whitespace.many().tag(None),
    borme_string.tag(None),
    parsy.whitespace.many().tag(None),
    dl.tag('dl'),
    parsy.string(' - ').tag(None),
    issn.tag('issn')
).combine_dict(lambda **kwargs: kwargs)


def field(name, body):
    @parsy.generate
    def _field_option():
        return (yield lexeme(parsy.string(name))), (yield body)

    return _field_option


act_title = parsy.seq(
    parsy.alt(*map(parsy.string, act_titles(pdf_outline))),
    parsy.whitespace,
).combine(lambda title, *_: title)

position = parsy.alt(
    field(
        KeywordPosition.ADM_UNICO.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.ADM_SOLID.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.LIQUIDADOR.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.LIQUIDADOR_M.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.ADM_MANCOM.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.APODERADO.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.APO_MANC.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.APO_MAN_SOLI.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.APO_SOL.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.CONSEJERO.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.SOCIO_MIEMBR.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.AUDITOR.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.AUDITOR_SUPLENTE.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.VSECRNOCONSJ.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.CO_DE_MA_SO.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.ENT_GESTORA.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.PRESIDENTE.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.SECRETARIO.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.VICESECRET.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.SECRENOCONSJ.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.SOC_PROF.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.REPRESENTAN.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.CON_DELEGADO.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.CON_IND.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.CONS_EXT_DOM.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.VICEPRESID.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.CONS_EXTERNO.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.CONSJ_DOMINI.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.CONS_DEL_SOL.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.MIEM_COM_CTR.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.PRES_COM_CTR.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.VPR_COM_CTR.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.SECR_COM_CTR.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.VICES_COM_CT.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.LIQUISOLI.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.ENTIDDEPOSIT.value,
        any_till(keyword_position | keyword_main)
    ),
    field(
        KeywordPosition.ENT_REG_CONT.value,
        any_till(keyword_position | keyword_main)
    ),
)

act_body = parsy.alt(
    field(
        KeywordMain.DECLARACION_DE_UNIPERSONALIDAD.value,
        any_till(nothing)
    ),
    field(
        KeywordMain.PERDIDA_DEL_CARACTER_DE_UNIPERSONALIDAD.value,
        any_till(nothing)
    ),
    field(
        KeywordMain.EXTINCION.value,
        any_till(nothing)
    ),
    field(
        KeywordMain.DEPOSITO_DE_LIBROS.value,
        any_till(nothing)
    ),
    field(
        KeywordMain.SOCIO_UNICO.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.CAMBIO_DE_DENOMINACION_SOCIAL.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.CONSTITUCION.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.EMPRESARIO_INDIVIDUAL.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.AMPLIACION_DE_CAPITAL.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.FUSION_POR_UNION.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.REVOCACIONES.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.MODIFICACIONES_ESTATUTARIAS.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.CAMBIO_DE_OBJETO_SOCIAL.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.CAMBIO_DE_DOMICILIO_SOCIAL.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.AMPLIACION_DEL_OBJETO_SOCIAL.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.REELECCIONES.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.APERTURA_DE_SUCURSAL.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.ARTICULO_378_5_DEL_REGLAMENTO_DEL_REGISTRO_MERCANTIL.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.OTROS_CONCEPTOS.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.REDUCCION_DE_CAPITAL.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.SITUACION_CONCURSAL.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.FUSION_POR_ABSORCION.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.SUSPENSION_DE_PAGOS.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.TRANSFORMACION_DE_SOCIEDAD.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.CANCELACIONES_DE_OFICIO_DE_NOMBRAMIENTOS.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.DESEMBOLSO_DE_DIVIDENDOS_PASIVOS.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.PAGINA_WEB_DE_LA_SOCIEDAD.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.PRIMERA_SUCURSAL_DE_SOCIEDAD_EXTRANJERA.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.EMISION_DE_OBLIGACIONES.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.MODIFICACION_DE_PODERES.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.ESCISION_PARCIAL.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.QUIEBRA.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.SUCURSAL.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.CESION_GLOBAL_DE_ACTIVO_Y_PASIVO.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.SEGREGACION.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.PRIMERA_INSCRIPCION_OM_10_6_1997.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.ANOTACION_PREVENTIVA_DEMANDA_DE_IMPUGNACION_DE_ACUERDOS_SOCIALES.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.ANOTACION_PREVENTIVA_DECLARACION_DE_DEUDOR_FALLIDO.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.CREDITO_INCOBRABLE.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.SOCIEDAD_UNIPERSONAL.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.REAPERTURA_DE_HOJA_REGISTRAL.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.ADAPTACION_DE_LEY_2_95.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.ADAPTACION_DE_LEY_44_2015.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.ADAPTACION_SEGUN_DT_2_APARTADO_2_LEY_2_95.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.CIERRE_PROVISIONAL_HOJA_REGISTRAL_POR_BAJA_EN_EL_INDICE_DE_ENTIDADES_JURIDICAS.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.CIERRE_PROVISIONAL_DE_LA_HOJA_REGISTRAL_POR_REVOCACION_DEL_NIF.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.CIERRE_PROVISIONAL_HOJA_REGISTRAL_POR_REVOCACION_DEL_NIF_DE_ENTIDADES_JURIDICAS.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.CIERRE_PROVISIONAL_HOJA_REGISTRAL_POR_ART_137_2_LEY_43_1995_IMPUESTO_DE_SOCIEDADES.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.REACTIVACION_DE_LA_SOCIEDAD_ART_242_DEL_REGLAMENTO_DEL_REGISTRO_MERCANTIL.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.ADAPTACION_DE_SOCIEDAD.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.CIERRE_DE_SUCURSAL.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.MODIFICACION_DE_DURACION.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.FE_DE_ERRATAS.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.ACUERDO_DE_AMPLIACION_DE_CAPITAL_SOCIAL_SIN_EJECUTAR_IMPORTE_DEL_ACUERDO.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.ESCISION_TOTAL.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.DISOLUCION.value,
        any_till(keyword_main)
    ),
    field(
        KeywordMain.CESES_DIMISIONES.value,
        position.many()
    ),
    field(
        KeywordMain.NOMBRAMIENTOS.value,
        position.many()
    ),

    field(
        KeywordMain.DATOS_REGISTRALES.value,
        any_till(act_title | doc_footer)
    ),
).many()

act = parsy.seq(
    act_title,
    act_body
)

acts = act.many()

doc = parsy.seq(
    # page_header,
    doc_header,
    acts,
    doc_footer
)
# ================================================================================
# Main
# ================================================================================
try:
    o = doc.parse(text)
    pprint(o)
except parsy.ParseError as e:
    message = str(e)
    m = re.search(r'[\d]\:[\d]+', message)
    if m:
        indexes = m.group(0)
        end = int(indexes.split(':')[1])
        pprint(text[end:])
        raise e
except Exception as e:
    raise e
