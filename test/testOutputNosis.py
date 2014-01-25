
if __name__ == '__main__':

    import csv

    with open('../scraped/output.csv') as f:
        titles = f.next().strip().split(';')
        #Actividad ISIC Principal:	Actividad Principal AFIP:	CUIT:	Dom0	Dom1	Dom2	Perfil de Comercializacin:	Tipo de Perfil:

    with open('../scraped/output.csv') as f:
        cuilsScrapped=[]
        print titles
        reader= csv.DictReader(f,fieldnames=titles,delimiter=';')
        for rowdict in reader:
            if rowdict['CUIT:']=='CUIT:':
                continue #Skip the title
            cuilsScrapped.append(rowdict['CUIT:'])
        print cuilsScrapped