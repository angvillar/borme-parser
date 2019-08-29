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
with open("./pdfs/BORME-A-2019-1-04.pdf", "rb") as f:
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
    parsy.string('Miércoles')
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
    parsy.string('MADRID')
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
    decimal_digits.tag('month'),
    parsy.string('-').tag(None),
    decimal_digits.tag('day'),
    parsy.whitespace.tag(None)
).combine_dict(datetime.date)

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

act_title = parsy.alt(*map(parsy.string, act_titles(pdf_outline)))

act_body = many_till(
    parsy.any_char,
    parsy.alt(
        act_title,
        doc_footer
    )
).combine(lambda *args: ''.join(args))

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
