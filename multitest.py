from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Frame, Spacer
from reportlab.lib.pagesizes import  A4
from random import shuffle

from simpletest import SingleTest

class MultiTest:
    '''Put more shuffled SimpleTest together and save as flowable
    '''
    def __init__(self, testsLst, c):
        shuffle(testsLst)
        
        self.testsLst = []
        for test, count in zip(testsLst, range(1, len(testsLst) + 1)):
            sTest = SingleTest(testID=count, **test)
            self.testsLst.append(sTest)
            
        self.c = c

        A4width, A4height = A4

        self.boundary = False
        
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightHead', fontSize=10,
                                  alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftHead', fontSize=10,
                                  alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CenterFooter', fontSize=10,
                                  alignment=TA_CENTER))
        
        self.rightH = styles['RightHead']
        self.leftH = styles['LeftHead']
        self.centerF = styles['CenterFooter']

        # How much of the sheet is taken by main frame
        widthFactor = 0.9
        heightFactor = 0.9

        self.frameW = A4width * widthFactor
        self.frameH = A4height * heightFactor
        self.frameXLowLeftCorner = 0 + (A4width - self.frameW) / 2
        self.frameYLowLeftCorner = 0 + (A4height - self.frameH) / 2

        self.headerXLowLeftCorner = self.frameXLowLeftCorner
        self.headerYLowLeftCorner = self.frameYLowLeftCorner + self.frameH + 1
        self.headerW = self.frameW
        self.headerH = (A4height - self.frameH) * 0.5

        self.footerXLowLeftCorner = self.frameXLowLeftCorner
        self.footerYLowLeftCorner = 0
        self.footerW = self.frameW
        self.footerH = (A4height - self.frameH) * 0.5

        self.sp = Spacer(mm, mm*20)

        return

    def __str__(self):
        return ''.join([item.__str__() + '\n' for item in self.testsLst])
        
    def save(self):
        f = Frame(self.frameXLowLeftCorner,
                  self.frameYLowLeftCorner,
                  self.frameW, self.frameH)
        if self.boundary:
            f.drawBoundary(self.c)

        header = Frame(self.headerXLowLeftCorner,
                       self.headerYLowLeftCorner,
                       self.headerW, self.headerH)
        if self.boundary:
            header.drawBoundary(self.c)

        footer = Frame(self.footerXLowLeftCorner,
                       self.footerYLowLeftCorner,
                       self.footerW, self.footerH)
        if self.boundary:
            footer.drawBoundary(self.c)
        
        hPara = Paragraph(self.headerTxt, self.rightH)
        header.add(hPara, self.c)

        ftext = 'Pag. ' + str(self.c.getPageNumber())
        fPara = Paragraph(ftext, self.centerF)
        footer.add(fPara, self.c)

        flowLst = [item.getFlowable()[0] for item in self.testsLst]
        
        for item in flowLst:
            if not f.add(item, self.c):
                self.c.showPage()
                f = Frame(self.frameXLowLeftCorner,
                          self.frameYLowLeftCorner,
                          self.frameW, self.frameH)
                if self.boundary:
                    f.drawBoundary(self.c)
                
                header = Frame(self.headerXLowLeftCorner,
                               self.headerYLowLeftCorner,
                               self.headerW, self.headerH)
                if self.boundary:
                    header.drawBoundary(self.c)

                footer = Frame(self.footerXLowLeftCorner,
                               self.footerYLowLeftCorner,
                               self.footerW, self.footerH)
                if self.boundary:
                    footer.drawBoundary(self.c)

                f.add(item, self.c)

                hPara = Paragraph(self.headerTxt, self.rightH)
                header.add(hPara, self.c)

                ftext = 'Pag. ' + str(self.c.getPageNumber())
                fPara = Paragraph(ftext, self.centerF)
                footer.add(fPara, self.c)
                
            f.add(self.sp, self.c) # spaces between questions

        self.c.save()

        return

    def setHeader(self, headerTxt):
        self.headerTxt = headerTxt

def main():
    from reportlab.pdfgen.canvas import Canvas
    from pathlib import Path
    test1 = {'question': '''Lorem ipsum dolor sit amet, consectetur adipiscing
elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore
eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident,
sunt in culpa qui officia deserunt mollit anim id est laborum. (4 risposte)''',
             'image': Path('/home/ago/Devel/Reportlab/image/a.png'),
             'answers': ['giusta', 'Ad astra per aspera.',
                         'Aliena vitia in oculis habemus, a tergo nostra sunt.',
                         '''At pulchrum est digito monstrari et dicier:
hic est!'''],
             'altro 1': 'altro',
             'altro 2': 'altro'}
    test2 = {'question': '''Non sa niente, e crede di saper tutto.
             Questo fa chiaramente prevedere una carriera politica (2 risposte)''',
             'image': '',
             'answers': ['giusta', '''La politica è forse l’unica professione
per la quale non si ritiene necessaria alcuna preparazione''', '', ''],
             'altro 1': 'altro'}
    test3 = {'question': '''Il peggio che può capitare a un
genio è di essere compreso (1 risposta)''',
             'image': Path('/home/ago/Devel/Reportlab/image/b.png'),
             'answers': ['giusta'],
             'altro 1': 'altro',
             'altro 2': 'altro'}

    fileName = 'output.pdf'
    c = Canvas(fileName, pagesize=A4)

    c.setAuthor('Me')
    c.setTitle('Test esame con tre domande')
    c.setSubject('Formazione')

    tests = MultiTest([test1, test2, test3], c)
    tests.setHeader('file: ' + fileName)
    tests.save()

    return

if __name__ == '__main__':
    main()

