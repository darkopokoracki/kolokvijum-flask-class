from flask import Flask, render_template, redirect, url_for, request, session
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Raf2022'

mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = '',
    database = 'kolokvijum2'
)

# Proba
@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return 'Hello World'


class Korisnik:
    __indeks: str
    __ime_prezime: str
    __godina: int
    __password: str
    __prosek: float
    __ispiti: int

    def __init__(self, indeks: str, ime_prezime: str, godina: int, password: str, prosek: float, ispiti: int) -> None:
        self.__indeks = indeks
        self.__ime_prezime = ime_prezime
        self.__godina = godina
        self.__password = password
        self.__prosek = prosek
        self.__ispiti = ispiti

    # Geteri
    def get_indeks(self):
        return self.__indeks
    
    def get_ime_prezime(self):
        return self.__ime_prezime

    def get_godina(self):
        return self.__godina

    def get_password(self):
        return self.__password

    def get_prosek(self):
        return self.__prosek

    def get_ispiti(self):
        return self.__ispiti

    
    # Seteri
    def set_indeks(self, novi_indeks):
        self.__indeks = novi_indeks
    
    def set_ime_prezime(self, novo_ime_prezime):
        self.__ime_prezime = novo_ime_prezime

    def set_godina(self, nova_godina):
        self.__godina = nova_godina

    def set_password(self, novi_password):
        self.__password = novi_password

    def set_prosek(self, novi_prosek):
        self.__prosek = novi_prosek

    def set_ispiti(self, novi_broj_ispita):
        self.__ispiti = novi_broj_ispita

    def __str__(self) -> str:
        res = f"Indeks: {self.__indeks}\n"
        res += f"Ime i prezime: {self.__ime_prezime}\n"
        res += f"Godina rodjenja: {self.__godina}\n"
        res += f"Password: {self.__password}\n"
        res += f"Prosek: {self.__prosek}\n"
        res += f"Polozeni ispiti: {self.__ispiti}\n"

        return res

    def __repr__(self) -> str:
        return self.__ime_prezime

    def register(self):
        cursor = mydb.cursor(prepared = True)
        sql = "INSERT INTO korisnik VALUES (null, ?, ?, ?, ?, ?, ?)"
        values = (self.__indeks, self.__ime_prezime, self.__godina, self.__password, self.__prosek, self.__ispiti)
        cursor.execute(sql, values)
        mydb.commit()


    def login(self):
        session['indeks'] = self.__indeks

    def update(self):
        cursor = mydb.cursor(prepared = True)
        sql = "UPDATE korisnik SET ime_prezime = ?, godina_rodjenja = ?, sifra = ?, prosek = ?, polozeni_ispiti = ? WHERE broj_indeksa = ?"
        values = (self.__ime_prezime, self.__godina, self.__password, self.__prosek, self.__ispiti, self.__indeks)
        cursor.execute(sql, values)
        mydb.commit()

    def delete(self):
        cursor = mydb.cursor(prepared = True)
        sql = "DELETE FROM korisnik WHERE broj_indeksa = ?"
        values = (self.__indeks, )
        cursor.execute(sql, values)
        mydb.commit()



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template(
            'register.html'
        )

    else:
        indeks = request.form['indeks']
        ime_prezime = request.form['ime_prezime']
        godina = request.form['godina']
        password = request.form['password']
        confirm = request.form['confirm']
        prosek = request.form['prosek']
        ispiti = request.form['ispiti']

        cursor = mydb.cursor(prepared = True)
        sql = "SELECT * FROM korisnik WHERE broj_indeksa = ?"
        values = (indeks, )
        cursor.execute(sql, values)

        res = cursor.fetchone()

        if res != None:
            return render_template(
                'register.html',
                indeks_error = 'Vec postoji nalog sa tim indeksom!'
            )

        if password != confirm:
            return render_template(
                'register.html',
                confirm_error = 'Lozinke se ne poklapaju!'
            )

        if float(prosek) < 6 or float(prosek) > 10:
            return render_template(
                'register.html',
                prosek_error = 'Prosek mora biti izmedju 6 i 10!'
            )

        if int(ispiti) < 0:
            return render_template(
                'register.html',
                ispiti_error = 'Broj polozenih ispita ne moze biti negativan!'
            )


        """
            Kada smo presli sve validacije input polja,
            pravimo jednog korisnika (jedan objekat) pomocu klase
            Korisnik:
        """
        korisnik = Korisnik(indeks, ime_prezime, godina, password, prosek, ispiti)
        
        korisnik.register() # Metoda klase Korisnik koja registruje korisnika.

        return redirect(
            url_for('show_all')
        )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'indeks' in session:
        return redirect('show_all')

    if request.method == 'GET':
        return render_template(
            'login.html'
        )

    indeks = request.form['indeks']
    password = request.form['password']

    cursor = mydb.cursor(prepared = True)
    sql = "SELECT * FROM korisnik WHERE broj_indeksa = ?"
    values = (indeks, )
    cursor.execute(sql, values)

    res = cursor.fetchone()

    if res == None:
        return render_template(
            'login.html',
            indeks_error = 'Indeks koji ste uneli ne postoji!'
        )

    res = dekodiraj(res)

    if password != res[4]:
        return render_template(
            'login.html',
            password_error = 'Pogresna lozinka!'
        )

    korisnik = Korisnik(res[1], res[2], res[3], res[4], res[5], res[6])
    korisnik.login() # Metoda klase Korisnik koja stavlja indeks u sesiju

    return redirect(
        url_for('show_all')
    )


@app.route('/logout')
def logout():
    if 'indeks' not in session:
        return redirect(
            url_for('show_all')
        )

    session.pop('indeks')
    return redirect(
        url_for('login')
    )


@app.route('/show_all')
def show_all():

    cursor = mydb.cursor(prepared = True)
    sql = "SELECT * FROM korisnik"
    cursor.execute(sql)
    
    res = cursor.fetchall()

    if res == None:
        'Ne postoji ni jedan korisnik u bazi'

    n = len(res)
    for i in range(n):
        res[i] = dekodiraj(res[i])

    korisnici = []

    for i in range(n):
        korisnik = Korisnik(res[i][1], res[i][2], res[i][3], res[i][4], res[i][5], res[i][6])
        korisnici.append(korisnik)


    return render_template(
        'show_all.html',
        korisnici = korisnici
    )


@app.route('/update/<indeks>', methods=['GET', 'POST'])
def update(indeks):

    if 'indeks' not in session:
        return 'Morate se prijaviti da bi ste modifikovali vas nalog!'
    
    if session['indeks'] != indeks:
        return 'Nemate pravo da modifikujete tudji nalog!'

    cursor = mydb.cursor(prepared = True)
    sql = "SELECT * FROM korisnik WHERE broj_indeksa = ?"
    values = (indeks, )
    cursor.execute(sql, values)

    res = cursor.fetchone()

    if res == None:
        return 'Ne postoji nalog sa tim indeksom'

    res = dekodiraj(res)

    korisnik = Korisnik(res[1], res[2], res[3], res[4], res[5], res[6])
    # res[1] = indeks
    # res[2] = ime_prezime
    # res[3] = godina
    # res[4] = password
    # res[5] = prosek
    # res[6] = ispiti

    if request.method == 'GET':
        return render_template(
            'update.html',
            korisnik = korisnik
        )

    if request.method == 'POST':
        ime_prezime = request.form['ime_prezime']
        godina = request.form['godina']
        password = request.form['password']
        confirm = request.form['confirm']
        prosek = request.form['prosek']
        ispiti = request.form['ispiti']

        if password != confirm:
            return render_template(
                'update.html',
                confirm_error = 'Lozinke se ne poklapaju!',
                korisnik = korisnik
            )

        if float(prosek) < 6 or float(prosek) > 10:
            return render_template(
                'update.html',
                prosek_error = 'Prosek mora biti izmedju 6 i 10!',
                korisnik = korisnik
            )

        if int(ispiti) < 0:
            return render_template(
                'update.html',
                ispiti_error = 'Broj polozenih ispita ne moze biti negativan!',
                korisnik = korisnik
            )

        korisnik.set_ime_prezime(ime_prezime)
        korisnik.set_godina(godina)
        korisnik.set_password(password)
        korisnik.set_prosek(prosek)
        korisnik.set_ispiti(ispiti)

        korisnik.update() # Metoda klase Korisnik koja updatuje korisnika

        return redirect(
            url_for('show_all')
        )


@app.route('/delete/<indeks>', methods=['POST'])
def delete(indeks):
    if 'indeks' not in session:
        return redirect(
            url_for('/login')
        )

    if session['indeks'] != indeks:
        return 'Ne mozete da brisete tudji nalog!'

    
    cursor = mydb.cursor(prepared = True)
    sql = "SELECT * FROM korisnik WHERE broj_indeksa = ?"
    values = (indeks, )
    cursor.execute(sql, values)

    res = cursor.fetchone()

    if res == None:
        return 'Ne postoji nalog sa tim indeksom'

    res = dekodiraj(res)
    korisnik = Korisnik(res[1], res[2], res[3], res[4], res[5], res[6])
    korisnik.delete()

    session.pop('indeks')

    return redirect(
        url_for('show_all')
    )


@app.route('/better_than_average/<average>')
def better_average(average):
    cursor = mydb.cursor(prepared = True)
    sql = "SELECT * FROM korisnik WHERE prosek > ?"
    values = (average, )
    cursor.execute(sql, values)

    res = cursor.fetchall()

    if res == None:
        return 'Ne postoji korisnik koji ima veci prosek od navedenog!'


    n = len(res)
    for i in range(n):
        res[i] = dekodiraj(res[i])


    korisnici = []
    for i in range(n):
        korisnik = Korisnik(res[i][1], res[i][2], res[i][3], res[i][4], res[i][5], res[i][6])
        korisnici.append(korisnik)


    return render_template(
        'average.html',
        korisnici = korisnici
    )


def dekodiraj(data):
    data = list(data)
    n = len(data)

    for i in range(n):
        if isinstance(data[i], bytearray):
            data[i] = data[i].decode()

    return data 


app.run(debug = True)