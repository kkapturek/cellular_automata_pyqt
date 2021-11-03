import sys
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QCheckBox, QWidget,QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
from automatTranslated import *
import numpy as np
import matplotlib.pyplot as plt
import traceback

class Automat(QMainWindow):
    def __init__(self):
        ### Deklaracje zmiennych należących do layout'u:
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        ### Połączenie elementów okienka z funkcjami
        self.ui.buttonWykonaj.clicked.connect(self.wykonaj_automat)
        self.ui.buttonReset.clicked.connect(self.wyczysc_dane)
        self.ui.buttonZapisz.clicked.connect(self.zapisz_plik)
        self.ui.checkBox.clicked.connect(self.zmiana)
        self.ui.pushButtonWyswietlPoza.clicked.connect(self.pokaz_tablice_poza_oknem)
        self.show()

    def losuj_binarna(self):
        """Losuje regułę na podstawie prawdopodobieństwa podanego przez użytkownika"""
        try:
            pstwo = float(self.ui.linePstwo.text())
            lista = [1, 0]
            binarna = np.random.choice(lista, 8, p=[f'{pstwo}', f'{(1 - pstwo)}'])
            binarna = list(binarna)
            nowa = ''.join(map(str, binarna))
            wzory = [
                (1, 1, 1),
                (1, 1, 0),
                (1, 0, 1),
                (1, 0, 0),
                (0, 1, 1),
                (0, 1, 0),
                (0, 0, 1),
                (0, 0, 0)
            ]
            mapa = dict(zip(wzory, nowa))
            return mapa
        except Exception as wyjatek:
            QMessageBox.critical(self,'Błąd',f'Podano błędną wartość: \n{wyjatek}')


    def zmiana(self):
        "Blokuje i odblokowuje okna w aplikacji zależnie od stanu Check Boxa"
        if self.ui.checkBox.isChecked():
            self.ui.linePstwo.setEnabled(True)
            self.ui.lineRegula.clear()
            self.ui.lineRegula.setDisabled(True)
        else:
            self.ui.linePstwo.setEnabled(False)
            self.ui.lineRegula.setDisabled(False)
            self.ui.linePstwo.clear()

    def reguly(self):
        """Zamienia liczbę decymalną na binarną;
        tworzy mapę (słownik) między binarną regułą a możliwymi stanami komórki"""
        try:
            liczba = int(self.ui.lineRegula.text())
            if liczba < 256:
                if liczba == 1:
                    regula = ("0000000" + bin(liczba)[2:])
                elif 1 < liczba < 4:
                    regula = ("000000" + bin(liczba)[2:])
                elif 3 < liczba < 8:
                    regula = ("00000" + bin(liczba)[2:])
                elif 7 < liczba < 16:
                    regula = ("0000" + bin(liczba)[2:])
                elif 15 < liczba < 32:
                    regula = ("000" + bin(liczba)[2:])
                elif 31 < liczba < 64:
                    regula = ("00" + bin(liczba)[2:])
                elif 63 < liczba < 128:
                    regula = ("0" + bin(liczba)[2:])
                elif liczba > 127:
                    regula = (bin(liczba)[2:])

            wzory = [
                (1, 1, 1),
                (1, 1, 0),
                (1, 0, 1),
                (1, 0, 0),
                (0, 1, 1),
                (0, 1, 0),
                (0, 0, 1),
                (0, 0, 0)
            ]
            mapa = dict(zip(wzory, regula))
            return mapa
        except Exception as wyjatek:
            QMessageBox.critical(self,'Błąd',f'Podano błędną wartość: \n{wyjatek}')


    def pokolenia(self, tablica, regula):
        """Tworzy tablicę wykorzystywaną do iteracji przy generowaniu wykresu"""
        tablica = np.pad(tablica, (1, 1), 'constant', constant_values=(0, 0))
        nowa_tablica = np.zeros_like(tablica)

        for i in range(1, tablica.shape[0] - 1):
            nowa_tablica[i] = regula[tuple(tablica[i - 1:i + 2])]

        return nowa_tablica[1:-1]

    def generuj(self, pierwsza, regula):
        """Generuje tablicę wykorzystując funkcję pokolenia,
        będącą wzorem do wytworzenia wykresu"""
        try:
            linia = int(self.ui.linePokolenia.text())

            if isinstance(pierwsza, list):
                tablica = np.array(pierwsza)
            else:
                tablica = pierwsza

            tablica = np.pad(tablica, (linia, linia), 'constant', constant_values=(0, 0))

            rzedy = [tablica]
            for i in range(linia):
                tablica = self.pokolenia(tablica, regula)
                rzedy.append(tablica)

            rzedy = np.array(rzedy)
            return rzedy
        except Exception as wyjatek:
            QMessageBox.critical(self,'Błąd',f'Podano błędną wartość: \n{wyjatek}')


    def pokaz_tablice(self, tablica):
        try:
            """Pokazuje wykres na podstawie wygenerowanej tablicy"""
            plik = 'wykres.png'
            plt.figure(figsize=(5, 2.5))
            self.wykres_plt = plt.imshow(tablica, cmap="twilight")
            plt.axis("off")
            self.wykres_plt.get_figure().savefig(plik)
            wykres_png = QPixmap(plik)
            self.ui.wykres.setPixmap(wykres_png)
            self.ui.wykres.resize(wykres_png.width(), wykres_png.height())
            self.resize(wykres_png.width() + 500, wykres_png.height() + 300)
        except Exception as e:
            print(e)

    def pokaz_tablice_poza_oknem(self, tablica):
        """Umożliwia pokazanie wykresu w osobnym oknie"""
        try:
            if self.ui.checkBox.isChecked():
                regula = self.losuj_binarna()
                tablica = self.generuj([0, 1, 0], regula)
            else:
                regula = self.reguly()
                tablica = self.generuj([0, 1, 0], regula)
            plik = 'wykres.png'
            self.wykres_plt2 = plt.imshow(tablica, cmap="twilight")
            plt.axis("off")
            self.wykres_plt2.get_figure().savefig(plik)
            plt.show()
        except Exception as e:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            print(e)

    def wykonaj_automat(self):
        try:
            """Generuje automat i pokazuje go w odpowiednim okienku"""
            if self.ui.checkBox.isChecked():
                regula = self.losuj_binarna()
                tablica = self.generuj([0, 1, 0], regula)
                self.pokaz_tablice(tablica)
            else:
                regula = self.reguly()
                tablica = self.generuj([0, 1, 0], regula)
                self.pokaz_tablice(tablica)
        except Exception as e:
            print(e)

    def zmiana(self):
        "Blokuje i odblokowuje okna w aplikacji zależnie od stanu Check Boxa"
        if self.ui.checkBox.isChecked():
            self.ui.linePstwo.setEnabled(True)
            self.ui.lineRegula.clear()
            self.ui.lineRegula.setDisabled(True)
        else:
            self.ui.linePstwo.setEnabled(False)
            self.ui.lineRegula.setDisabled(False)
            self.ui.linePstwo.clear()

    def zapisz_plik(self):
        """Zapisuje wykres w wybranym formacie"""
        plik, _ = QFileDialog.getSaveFileName(
            self,
            "Zapisz wykres jako",
            ".png",
            "Wszystkie pliki (*);;" +
            "Pliki bitmapowe (*.png *jpg);;" +
            "Pliki wektorowe (*.svg *.pdf)",
        )
        if plik:
            self.wykres_plt.get_figure().savefig(plik)

    def wyczysc_dane(self):
        """ Czysci okienka aplikacji """
        self.ui.linePokolenia.clear()
        self.ui.lineRegula.clear()
        self.ui.linePstwo.clear()
        self.ui.wykres.clear()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w= Automat()
    w.show()
    sys.exit(app.exec_())