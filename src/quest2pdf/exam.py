#!/usr/bin/env python
# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import  A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import mm
from pathlib import Path
from datetime import datetime
import os
import platform
import logging

from multiquest import MultiQuest
from numberedcanvas import NumberedCanvas

LOGNAME = 'quest2pdf.' + __name__
LOGGER = logging.getLogger(LOGNAME)

class ExamDoc:
    def __init__(self, quests, nDoc=1,
                 exam_filename='Exam',
                 correction_filename='Correction',
                 destination=None,
                 to_shuffle=False,
                 heading=False):

        author = os.getlogin() + '@' + platform.node()
        title = exam_filename
        subject = 'Formazione'

        correction_file = Path(correction_filename)

        now = datetime.now().strftime('%Y-%m-%d-T%H-%M-%S-%f')
        correction_filename = ''.join((correction_file.stem, '-', now)) + '.pdf'
        correction_filepath = Path(destination) / correction_filename
        self.correctionDoc = SimpleDocTemplate(str(correction_filepath))
        self.correctionText = []    

        exam_filename = Path(exam_filename)

        self.examDoc = []

        self.questions = []

        dictLst = [self._setDictionary(row) for row in quests]

        self.evenHead = []
        self.oddHead = []

        for i in range(nDoc):
            story = []
            # %f are microseconds
            now = datetime.now().strftime('%Y-%m-%d-T%H-%M-%S-%f')
            exam_filename = ''.join((exam_filename.stem, '-', now)) + '.pdf'
            exam_filepath = Path(destination) / exam_filename

            if heading is False:
                heading = ''
            elif heading is True:
                heading = exam_filename

            self.evenHead.append(lambda d, c : self._evenHead(d, c,
                                                            text=heading))
            self.oddHead.append(lambda d, c : self._oddHead(d, c,
                                                          text=heading))
            
            doc = SimpleDocTemplate(str(exam_filepath), pagesize=A4, allowSplitting=0,
                                    author=author, title=title, subject=subject)
            self.examDoc.append(doc)

            self.questions.append(MultiQuest(dictLst, to_shuffle))

            self._fillCorrectionFile(exam_filename)

        return

    def _setDictionary(self, row):
        """Give the right format for SimpleTest argument.
        """
        try:
            output = {"subject": row.get('subject', ""),
                      'question': row['question'],
                      'image': row.get('image', "")
                      }
            answerKeys = ('A', 'B', 'C', 'D') # TODO da 2 a n opzioni
            answers = [row[key] for key in answerKeys]
        except KeyError:
            LOGGER.critical("Chiave non trovata: %s", row)
            raise

        output['answers'] = answers
        
        return output

    def _fillCorrectionFile(self, examFileName):
        styles = getSampleStyleSheet()
        text = examFileName + '\n' + self.questions[-1].__str__()
        
        for line in text.split('\n'):
            para = Paragraph(line+'\n', styles["Normal"])
            self.correctionText.append(para)

        self.correctionText.append(Spacer(mm, mm * 20)) 

        return


    def _evenHead(self, canvas, doc, text=''):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()
        header_text = text

        # Header
        header = Paragraph(header_text, styles['Normal'])
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.bottomMargin + doc.topMargin/2 - h)

        # Release the canvas
        canvas.restoreState()

        return

    def _oddHead(self, canvas, doc, text=''):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()
        header_text = text

        # Header
        header = Paragraph(header_text, styles['Normal'])
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.bottomMargin + doc.topMargin/2 - h)

        # Release the canvas
        canvas.restoreState()

        return

    def _footer(self, canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()
        text = 'This is a multi-line footer.  It goes on every page.   ' * 5

        # Footer
        footer = Paragraph(text, styles['Normal'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)

        # Release the canvas
        canvas.restoreState()

        return

    def close(self) -> bool:
        self.correctionDoc.build(self.correctionText)

        story = []

        for q, doc, h1, h in zip(self.questions, self.examDoc,
                                 self.evenHead, self.oddHead):
            for f in q.get_flowables():
                story.append(f)
                story.append(Spacer(mm, mm*20))

            doc.build(story, onFirstPage=h1,
                      onLaterPages=h, canvasmaker=NumberedCanvas)
        return True
