import zipfile
from xml2obj import xml2obj

# get first sheet's rows
zf = zipfile.ZipFile('filename.xlsx')
sheetdata = zf.read('xl/worksheets/sheet1.xml')
xml = xml2obj(sheetdata)
rowdata = xml.sheetData.row

# get shared strings xml
stringdata = zf.read('xl/sharedStrings.xml')
xml = xml2obj(stringdata)
strings = xml.si

# extract cell values into rows; cell values are given
# as ordinal index references into sharedStrings.xml:ssi.si
# elements, whose string value is found in the node's .t attribute
rows = []
for row in rowdata:
    cells = row.c
    values = [strings[int(c.v)].t for c in cells]
    rows.append(values)

print rows
