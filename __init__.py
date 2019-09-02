from pprint import pprint
import re
import datetime
import PyPDF2
import pdftotext
import parsy

pdf_path = './pdfs/BORME-A-2019-1-04.pdf'
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

text = "\n\n".join(pdf)
text = re.sub('\s+', ' ', text).strip()


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


borme_string = parsy.string('BOLETÍN OFICIAL DEL REGISTRO MERCANTIL')

decimal_digits = parsy.decimal_digit.many().map(lambda digits: int(''.join(digits)))

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
    cve.tag('cve'),
    borme_url.tag(None),
    parsy.whitespace.many().tag(None),
    borme_string.tag(None),
    parsy.whitespace.many().tag(None),
    dl.tag('dl'),
    parsy.string(' - ').tag(None),
    issn.tag('issn')
).combine_dict(lambda **kwargs: kwargs)

act_title = parsy.seq(
    parsy.alt(*map(parsy.string, act_titles(pdf_outline))),
    parsy.whitespace
).combine(lambda title, _: title)


@parsy.generate
def position():
    return (yield parsy.alt(
        parsy.seq(
            parsy.string('Adm. Unico:'),
            many_till(
                parsy.any_char,
                parsy.alt(
                    position,
                    keyword
                )
            ).combine(lambda *args: ''.join(args))
        ),
        parsy.seq(
            parsy.string('Adm. Solid.:'),
            many_till(
                parsy.any_char,
                parsy.alt(
                    position,
                    keyword
                )
            ).combine(lambda *args: ''.join(args))
        ),
        parsy.seq(
            parsy.string('Liquidador:'),
            many_till(
                parsy.any_char,
                parsy.alt(
                    position,
                    keyword
                )
            ).combine(lambda *args: ''.join(args))
        ),
        parsy.seq(
            parsy.string('Liquidador M:'),
            many_till(
                parsy.any_char,
                parsy.alt(
                    position,
                    keyword
                )
            ).combine(lambda *args: ''.join(args))
        ),
        parsy.seq(
            parsy.string('Adm. Mancom.:'),
            many_till(
                parsy.any_char,
                parsy.alt(
                    position,
                    keyword
                )
            ).combine(lambda *args: ''.join(args))
        ),
    ))


@parsy.generate
def constitution():
    return (yield parsy.alt(
        parsy.seq(
            parsy.string('Comienzo de operaciones:'),
            many_till(
                parsy.any_char,
                parsy.alt(
                    constitution,
                    keyword
                )
            ).combine(lambda *args: ''.join(args))
        ),
        parsy.seq(
            parsy.string('Objeto social:'),
            many_till(
                parsy.any_char,
                parsy.alt(
                    constitution,
                    keyword
                )
            ).combine(lambda *args: ''.join(args))
        ),
        parsy.seq(
            parsy.string('Domicilio:'),
            many_till(
                parsy.any_char,
                parsy.alt(
                    constitution,
                    keyword
                )
            ).combine(lambda *args: ''.join(args))
        ),
        parsy.seq(
            parsy.string('Capital:'),
            many_till(
                parsy.any_char,
                parsy.alt(
                    constitution,
                    keyword
                )
            ).combine(lambda *args: ''.join(args))
        ),
    ))


@parsy.generate
def ampliacion_de_capital():
    return (yield parsy.alt(
        parsy.seq(
            parsy.string('Capital:'),
            many_till(
                parsy.any_char,
                parsy.alt(
                    ampliacion_de_capital,
                    keyword
                )
            ).combine(lambda *args: ''.join(args))
        ),
        parsy.seq(
            parsy.string('Resultante Suscrito:'),
            many_till(
                parsy.any_char,
                parsy.alt(
                    ampliacion_de_capital,
                    keyword
                )
            ).combine(lambda *args: ''.join(args))
        )
    ))


@parsy.generate
def keyword():
    return (yield parsy.alt(
        # keyword with unordered subfields
        parsy.seq(
            parsy.string('Ceses/Dimisiones.'),
            parsy.whitespace,
            position.many()
        ),
        parsy.seq(
            parsy.string('Nombramientos.'),
            parsy.whitespace,
            position.many()
        ),
        # keyword with ordered subfields
        parsy.seq(
            parsy.string('Datos registrales.'),
            parsy.whitespace,
            parsy.seq(
                parsy.seq(
                    parsy.string('T'),
                    many_till(
                        parsy.any_char,
                        parsy.string('F')
                    ).combine(lambda *args: ''.join(args))
                ),
                parsy.seq(
                    parsy.string('F'),
                    many_till(
                        parsy.any_char,
                        parsy.string('S')
                    ).combine(lambda *args: ''.join(args))
                ),
                parsy.seq(
                    parsy.string('S'),
                    many_till(
                        parsy.any_char,
                        parsy.string('H')
                    ).combine(lambda *args: ''.join(args))
                ),
                parsy.seq(
                    parsy.string('H'),
                    many_till(
                        parsy.any_char,
                        parsy.string('I/A')
                    ).combine(lambda *args: ''.join(args))
                ),
                parsy.seq(
                    parsy.string('I/A'),
                    many_till(
                        parsy.any_char,
                        parsy.alt(
                            act_title,
                            doc_footer
                        )
                    ).combine(lambda *args: ''.join(args))
                ),
            )
        ),
        # keyword with body
        parsy.seq(
            parsy.string('Declaración de unipersonalidad. Socio único:'),
            parsy.whitespace,
            many_till(
                parsy.any_char,
                keyword
            ).combine(lambda *args: ''.join(args))
        ),
        parsy.seq(
            parsy.string('Cambio de denominación social.'),
            parsy.whitespace,
            many_till(
                parsy.any_char,
                keyword
            ).combine(lambda *args: ''.join(args))
        ),
        # keyword with no body
        parsy.seq(
            parsy.string('Pérdida del caracter de unipersonalidad.'),
            parsy.whitespace
        ),
        parsy.seq(
            parsy.string('Constitución.'),
            parsy.whitespace,
            constitution.many()
        ),
        parsy.seq(
            parsy.string('Empresario Individual.'),
            parsy.whitespace,
            many_till(
                parsy.any_char,
                keyword
            ).combine(lambda *args: ''.join(args))
        ),
        parsy.seq(
            parsy.string('Ampliación de capital.'),
            parsy.whitespace,
            ampliacion_de_capital.many()
        ),
        parsy.seq(
            parsy.string('Disolución.'),
            parsy.whitespace,
            parsy.alt(
                parsy.string('Fusion.'),
                parsy.string('Voluntaria.')
            ),
            parsy.whitespace
        ),
        parsy.seq(
            parsy.string('Extinción.'),
            parsy.whitespace
        ),
        parsy.seq(
            parsy.string('Fusión por unión.'),
            parsy.whitespace,
            parsy.seq(
                parsy.string('Sociedades que se fusiónan:'),
                many_till(
                    parsy.any_char,
                    keyword
                ).combine(lambda *args: ''.join(args))
            )
        ),
    ))


act_body = keyword.many()

act = parsy.seq(
    act_title,
    act_body
)

doc = parsy.seq(
    page_header,
    doc_header,
    act.many(),
    doc_footer
)


o = doc.parse(text)
pprint(o)
