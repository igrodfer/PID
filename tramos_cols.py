cols = []
with open("trabajo2/tramos_cols.txt", "r") as f:

    for line in f.readlines():
        cols.append( line[3:52])

# printea cols como una tabla de  latex donde la primera columna es el contenido y kla segunda está vacía
for c in cols:
    print(c.replace("_","\\_") + " & " + " \\\\")

