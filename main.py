import os.path
import Tkinter
import pickle
import tkFont

import tkSimpleDialog
import tkMessageBox
import dbhandler

class App(object):

    def __init__(self, parent):
        self.parent = parent
        self.parent.title('Book Library')
        self.parent.geometry('600x400+300+300')
        self.sw = self.parent.winfo_screenwidth()
        self.sh = self.parent.winfo_screenheight()
        self.dataBase = None
        self.loadPickle()

        self.topBar = TopBar(self.parent, self)
        self.sortBar = SortBar(self.parent, self)
        self.toolBar = ToolBar(self.parent, self)
        self.mainCanvas = MainCanvas(self.parent)

        self.initiateSettings()

        self.parent.bind_all('<Delete>', self.deleteEntry)

    def makePickle(self):
        self.settings = {'path': None, 'user': None}
        pickledFile = 'bookLibrarySettings.p'
        pickle.dump(self.settings, open(pickledFile, 'w+'))

    def savePickle(self):
        pickledFile = 'bookLibrarySettings.p'
        pickle.dump(self.settings, open(pickledFile, 'w+'))

    def loadPickle(self):
        pickledFile = 'bookLibrarySettings.p'
        if os.path.isfile(pickledFile):
            self.settings = pickle.load(open (pickledFile, 'r'))
        else:
            self.makePickle()
            self.loadPickle()
            print 'test make Pickle'

    def initiateSettings(self):
        if self.settings['user'] != None:
            self.dataBase = dbhandler.DataBase(self.settings['path'], self.settings['user'])
            self.createList(0)

    def createList(self, column):
        if self.settings['user'] != None:
            self.mainCanvas.clear()

            dbcontents = self.dataBase.contents()
            self.sortedCont = self.sort(column, dbcontents)

            count = 0
            for row in self.sortedCont:
                count += 1
                string = '{:<20.20} {:<20.20} {:<20.20}\n'.format(row[0], row[1], row[2])
                self.mainCanvas.addLine(string, count)

    def sort(self, column, contents):
        contents = sorted(contents, key=lambda item: str.lower(item[column]))
        return contents

    def deleteEntry(self, event):
        for entry in self.mainCanvas.selectedLabels:
            rowNum = self.mainCanvas.rows.index(entry)
            text = self.sortedCont[rowNum][0]
            self.dataBase.commit(self.dataBase.delete(text))
            entry.destroy()
        self.mainCanvas.selectedLabels = []


class TopBar(object):

    def __init__(self, parent, app):
        self.app = app
        self.parent = parent

        self.frame = Tkinter.Frame(self.parent)
        self.frame.pack(side='top', fill='x')

        self.linkDB = Tkinter.Button(self.frame, text='Switch User', command=self.linkDBCB)
        self.linkDB.grid(row=0, column=0)

        self.styles = Tkinter.Listbox(self.frame)

    def linkDBCB(self):
        dialog = userDialog(self.parent)
        if os.path.isdir(dialog.path):
            if os.path.isfile('%s/%s.db' % (dialog.path, dialog.user)):
                self.app.dataBase = dbhandler.DataBase(dialog.path, dialog.user)
                self.app.settings['path'] = dialog.path
                self.app.settings['user'] = dialog.user
                self.app.createList(0)
            else:
                if tkMessageBox.askokcancel('Caution', 'Are you sure you want to create a new database?'):
                    self.app.dataBase = dbhandler.DataBase(dialog.path, dialog.user)
                    self.app.settings['path'] = dialog.path
                    self.app.settings['user'] = dialog.user
                    self.app.createList(0)
                else:
                    print 'test'
        else:
            print 'Not a valid path'

        self.app.savePickle()

class ToolBar(object):

    def __init__(self, parent, app):
        self.app = app
        self.parent = parent

        self.frame = Tkinter.Frame(self.parent)
        self.frame.pack(side='bottom', fill='x')

        self.entryTitle = Tkinter.Entry(self.frame)
        self.entryTitle.grid(row=1, column=1, sticky='W')

        self.entryAuthor = Tkinter.Entry(self.frame)
        self.entryAuthor.grid(row=1, column=2)

        self.entryGenre = Tkinter.Entry(self.frame)
        self.entryGenre.grid(row=1, column=3)

        self.labelTitle = Tkinter.Label(self.frame, text='Title')
        self.labelTitle.grid(row=0, column=1)

        self.labelAuthor = Tkinter.Label(self.frame, text='Author')
        self.labelAuthor.grid(row=0, column=2)

        self.labelGenre = Tkinter.Label(self.frame, text='Genre')
        self.labelGenre.grid(row=0, column=3)

        self.inputButton = Tkinter.Button(self.frame, text='Enter', command=self.inputButtonCB)
        self.inputButton.grid(row=0, column=4, rowspan=2)

    def inputButtonCB(self):
        if self.app.dataBase is None:
            print 'Error no DataBase'
        else:
            acceptableInput = self.filter(self.entryTitle.get(), self.entryAuthor.get(), self.entryGenre.get())
            if acceptableInput:
                self.app.dataBase.commit(self.app.dataBase.addBook(self.entryTitle.get(), self.entryAuthor.get(), self.entryGenre.get()))
                self.app.createList(0)

    def filter(self, title, author, genre):
        passed = True
        if title == '' and author == '' and genre == '':
            print 'please enter somthing'
            passed = False
        else:
            for item in self.app.dataBase.contents():
                if title == item[0] and author == item[1] and genre == item[2]:
                    print 'already exists'
                    passed = False

        return passed


class SortBar(object):

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app

        self.frame = Tkinter.Frame(self.parent)
        self.frame.pack(side='top', fill='x')

        self.titleSort = Tkinter.Button(self.frame, width=25, text='Title A-Z', command=self.titleSortCB)
        self.titleSort.grid(row=0, column=1)

        self.authorSort = Tkinter.Button(self.frame, width=25, text='Author A-Z', command=self.authorSortCB)
        self.authorSort.grid(row=0, column=2)

        self.genreSort = Tkinter.Button(self.frame, width=25, text='Genre A-Z', command=self.genreSortCB)
        self.genreSort.grid(row=0, column=3)

    def titleSortCB(self):
        self.app.createList(0)

    def authorSortCB(self):
        self.app.createList(1)

    def genreSortCB(self):
        self.app.createList(2)

class MainCanvas(object):

    def __init__(self, parent):
        self.parent = parent
        self.rows = []
        self.selectedLabels = []

        self.canvas = Tkinter.Canvas(self.parent, background='#0ff')
        self.vScrollBar = Tkinter.Scrollbar(self.parent, command=self.canvas.yview)
        self.hScrollBar = Tkinter.Scrollbar(self.parent, orient='horizontal', command=self.canvas.xview)
        self.canvas.config(xscrollcommand=self.hScrollBar.set, yscrollcommand=self.vScrollBar.set)
        self.frame = Tkinter.Frame(self.canvas, background='#0ff')


        self.vScrollBar.pack(side='right', fill='y')
        self.hScrollBar.pack(side='bottom', fill='x')
        self.canvas.pack(fill='both', expand=True)
        self.canvas.create_window((0,0), window=self.frame, anchor='nw', tags='self.frame')

        self.frame.bind('<Configure>', self.onFrameConfigure)
        self.canvas.bind_all('<MouseWheel>', self._on_mouseWheel)

    def _on_mouseWheel(self, event):
        self.canvas.yview_scroll(-1*(event.delta / 120), 'units')

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the frame.'''
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def addLine(self, string, row):
        label = Tkinter.Label(self.frame, text=string, background='#0ff', font=('Consolas', 12))
        label.grid(row=row, column=1, sticky='w')
        self.rows.append(label)
        curRow = len(self.rows) - 1
        self.rows[curRow].bind("<Button-1>", lambda event, arg=self.rows[curRow]: self.setLabel(event, arg))

    def setLabel(self, event, arg):
        if arg.cget('fg') == 'red':
            arg.config(fg='black')
            self.selectedLabels.remove(arg)
        else:
            arg.config(fg='red')
            self.selectedLabels.append(arg)

    def deleteLabel(self):
        for label in self.selectedLabels:
            label.destroy()
            dbhandler.delete()
        self.selectedLabels = []

    def clear(self):
        for row in self.rows:
            row.destroy()
        self.rows = []


class userDialog(tkSimpleDialog.Dialog):

    def body(self, parent):
        Tkinter.Label(parent, text='User:').grid(row=0)
        Tkinter.Label(parent, text='Path:').grid(row=1)

        self.eUser = Tkinter.Entry(parent)
        self.ePath = Tkinter.Entry(parent)

        self.eUser.grid(row=0, column=1)
        self.ePath.grid(row=1, column=1)

    def apply(self):
        self.user = self.eUser.get()
        self.path = self.ePath.get()

def main():
    root = Tkinter.Tk()
    app = App(root)
    root.mainloop()  # Event handling starts at this point.

if __name__ == '__main__':
    main()
