# 🏠 System inteligentnego domu oparty na Raspberry Pi i frameworku Django

👨‍🎓 Autor
Andrii Kupriianov
Nr albumu: 82571
Społeczna Akademia Nauk
Kierunek: Informatyka
Stopień: Inżynier

> Projekt dyplomowy autorstwa **Andrii Kupriianov** zrealizowany w ramach studiów inżynierskich na kierunku Informatyka w Społecznej Akademii Nauk.

---

## 📄 Opis projektu

System inteligentnego domu umożliwia:

- zdalne sterowanie oświetleniem,
- sterowanie roletami,
- zarządzanie systemem kontroli dostępu,
- aktywację i dezaktywację alarmu.

Głównym urządzeniem sterującym jest **Raspberry Pi**, działające na systemie **Raspberry Pi OS (Raspbian)**. Backend zbudowany został w języku **Python** z wykorzystaniem frameworka **Django**, natomiast frontend oparty jest na **Bootstrapie**.

---

## 🛠️ Technologie użyte w projekcie

- Python 3
- Django
- Raspberry Pi OS
- Bootstrap 5
- HTML/CSS
- Raspberry Pi

---

## ⚙️ Jak uruchomić projekt lokalnie

1. **Sklonuj repozytorium:**

```bash
git clone https://github.com/

2. Utwórz i aktywuj wirtualne środowisko:
python3 -m venv env
source env/bin/activate  # Linux/macOS
env\Scripts\activate     # Windows

3. Zastosuj migracje bazy danych:
python manage.py makemigrations
python manage.py migrate

4. Uruchom serwer deweloperski Django:
python manage.py runserver

📌 Status projektu
✅ Projekt zakończony jako praca dyplomowa.
🚀 Planowany dalszy rozwój:

integracja z czujnikami temperatury i wilgotności,

aplikacja mobilna,

sterowanie głosowe,

harmonogramy automatyzacji.

⚖️ Licencja i prawa autorskie
Ten projekt jest moją oryginalną pracą dyplomową. Wszelkie użycie kodu w celach edukacyjnych lub komercyjnych wymaga podania autora.
Plagiat oraz kopiowanie projektu bez zgody autora jest zabronione.

