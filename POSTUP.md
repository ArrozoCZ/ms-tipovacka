# MS Hokej 2026 – Tipovačka
## Kompletní postup nasazení

---

## Co budeš potřebovat
- Účet na **github.com** (zdarma)
- Účet na **supabase.com** (zdarma)
- Účet na **render.com** (zdarma)

Kolegové nepotřebují žádný účet — jen odkaz.

---

## KROK 1 — GitHub (úložiště kódu)

1. Jdi na **github.com** a přihlaš se
2. Klikni na **"New repository"** (zelené tlačítko vpravo nahoře)
3. Název: `ms-tipovacka`, nastav **Public**, klikni **Create repository**
4. Na další stránce klikni **"uploading an existing file"**
5. Rozbal stažený ZIP a přetáhni VŠECHNY soubory do okna:
   - `app.py`
   - `requirements.txt`
   - `render.yaml`
   - `.gitignore`
   - složku `static/` (obsahuje `index.html`)
6. Dole klikni **"Commit changes"**

---

## KROK 2 — Supabase (databáze)

1. Jdi na **supabase.com** → klikni **"Start your project"**
2. Přihlaš se přes GitHub
3. Klikni **"New project"**
   - Organization: ponech výchozí
   - Name: `ms-tipovacka`
   - Database Password: vymysli si heslo a ZAPIŠ SI HO
   - Region: vyber **Central EU (Frankfurt)**
   - Klikni **"Create new project"** (trvá ~2 minuty)
4. Až projekt běží, jdi vlevo do menu na **Project Settings → Database**
5. Sjeď dolů na sekci **"Connection string" → URI**
6. Klikni na záložku **"URI"** a zkopíruj celý řetězec
   - Vypadá nějak takto:
     `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxx.supabase.co:5432/postgres`
   - Nahraď `[YOUR-PASSWORD]` heslem které sis zvolil v kroku 3
7. Tento řetězec si ulož — budeš ho potřebovat v Kroku 3

---

## KROK 3 — Render (hosting aplikace)

1. Jdi na **render.com** → klikni **"Get Started"**
2. Přihlaš se přes **"Sign in with GitHub"**
3. Klikni **"New +"** → **"Web Service"**
4. Vyber repo **ms-tipovacka**
5. Render načte `render.yaml` automaticky
6. Před deployem je potřeba přidat proměnnou prostředí:
   - Sjeď dolů na sekci **"Environment Variables"**
   - Klikni **"Add Environment Variable"**
   - Key: `DATABASE_URL`
   - Value: vlož connection string ze Supabase (z Kroku 2, bod 7)
7. Klikni **"Deploy Web Service"**
8. Počkej 2–3 minuty než se aplikace sestaví
9. Render ti zobrazí odkaz — např. `https://ms-tipovacka.onrender.com`

---

## KROK 4 — Hotovo!

- **Rozešli odkaz** kolegům — otevřou v prohlížeči, zaregistrují se
- **Ty se přihlaš jako `Admin`** — uvidíš navíc:
  - Pole pro zadávání výsledků u každého zápasu
  - Tlačítko "Načíst z IIHF.com" pro automatické stažení výsledků

---

## Poznámky

- **Free tier Renderu:** aplikace "usne" po 15 minutách nečinnosti.
  První načtení po probuzení trvá ~30 sekund — to je normální.
- **Supabase:** databáze běží trvale zdarma, data se neztratí.
- **Bodování:**
  - 🎯 Přesný výsledek + způsob (REG/OT/SO) = **3 body**
  - ✅ Správný vítěz = **1 bod**
- **Uzávěrka tipů:** automaticky 1 hodinu před každým zápasem.
