import xlsxwriter


def export_check(text):
    def write_products(dct, worksheet, lenght):
        count = 0
        for i in sorted(dct.keys()):
            name, kol_vo = i.split('\t')
            worksheet.write(count, 0, name)
            worksheet.write(count, 1, int(kol_vo))
            worksheet.write(count, 2, dct[i])
            worksheet.write(count, 3, '=B{}*C{}'.format(count + 1, count + 1))
            count += 1
        worksheet.write(lenght, 0, 'Итого')
        worksheet.write(lenght, 3, '=SUM(D1:D{})'.format(lenght))

    workbook = xlsxwriter.Workbook('res.xlsx')
    new_text = text.split('\n---\n')
    for i in range(len(new_text)):
        dct = {}
        count = workbook.add_worksheet()
        text = new_text[i].split('\n')
        for j in range(len(text)):
            product = text[j].split('\t')
            name = '\t'.join((product[0], product[1]))
            if name in dct.keys():
                dct[name] = int(product[2]) + dct[name]
            else:
                dct[name] = int(product[2])
        write_products(dct, count, len(dct.keys()))

    workbook.close()
