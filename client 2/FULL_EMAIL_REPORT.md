# 📊 RAPORT COMPLET: Reconciliere GA4 vs Backend - Client 2
**Data Analiză:** 2026-01-26
**Perioada Analizată:** Ultimele 3 luni (Oct-Dec 2025 + Jan 2026)

---

## 🔴 SUMAR EXECUTIV
- **Comenzi Complete (Backend):** 49,022
- **Comenzi Găsite în GA4:** 42,228
- **Comenzi Lipsă din GA4:** 6,794
- **Valoare Lipsă:** 11,483,607 RON
- **Rată Tracking Overall:** 86.1%

---

## 🚨 PROBLEME CRITICE PE METODE DE PLATĂ

### A. Metode cu Redirect Extern (Problematice)

**LeanPay** are **0.0%** tracking:
- 369 comenzi în backend, doar 0 în GA4
- **369 comenzi lipsă** (valoare: **1,129,493 RON**)
- *Cauză:* Redirect-ul extern nu revine la pagina Thank You sau sesiunea GA4 se pierde complet.

**Tbi** are **0.0%** tracking:
- 1,006 comenzi în backend, doar 0 în GA4
- **1,006 comenzi lipsă** (valoare: **2,312,932 RON**)
- *Cauză:* Redirect-ul extern nu revine la pagina Thank You sau sesiunea GA4 se pierde complet.

**Oney** are **86.5%** tracking:
- 1,783 comenzi în backend, doar 1,542 în GA4
- **241 comenzi lipsă** (valoare: **483,267 RON**)

**BTDirect** are **57.0%** tracking:
- 79 comenzi în backend, doar 45 în GA4
- **34 comenzi lipsă** (valoare: **133,032 RON**)
- *Cauză:* Parte din utilizatori nu ajung pe Thank You page după plată cu card (3DS, timeout, etc).

**Card** are **88.9%** tracking:
- 21,575 comenzi în backend, doar 19,183 în GA4
- **2,392 comenzi lipsă** (valoare: **4,062,097 RON**)

### B. Metode FĂRĂ Redirect (Funcționează Bine)
- **Numerar la livrare:** 90.4% tracking ✅
- **Plata la locker:** 91.2% tracking ✅
- **Numerar sau card in magazin:** 91.1% tracking ✅

*Concluzie:* Metodele fără redirect extern funcționează bine pentru că utilizatorul rămâne pe site și pixelul se declanșează corect.

---

## ⚠️ INFLARE FALSĂ: Comenzi Anulate în GA4
**Total Comenzi Anulate găsite în GA4:** 5,967
**Valoare Inflată Fals:** 11,270,574 RON

Aceste comenzi au fost anulate în backend dar au fost contorizate ca venituri în GA4:

| Metodă Plată | Comenzi Anulate în GA4 | Valoare Inflată |
| :--- | :--- | :--- |
| Numerar sau card in magazin | 2,981.0 | 4,246,135 RON |
| Card | 1,139.0 | 2,181,372 RON |
| Numerar la livrare | 1,123.0 | 2,079,326 RON |
| BTDirect | 280.0 | 1,547,725 RON |
| OP | 255.0 | 755,337 RON |

*Cauză principală:* 'Ridicare din Magazin' reprezintă 50% din falsele pozitive - utilizatorul comandă online, pixelul se declanșează, dar ulterior anulează comanda la magazin.

---

## 📋 RECOMANDĂRI
1. **Prioritate 1 - LeanPay & Tbi:** Verificați implementarea redirect-ului. Zero tracking înseamnă că utilizatorii nu ajung niciodată pe Thank You page după aprobare.
2. **Prioritate 2 - Card (64.5%):** Investigați 3D Secure flow și timeouts. 35% din venituri lipsă sunt de pe Card.
3. **Server-Side Tracking:** Singura soluție definitivă pentru metodele cu redirect este să implementați Server-Side GTM care trimite evenimentul direct din backend după confirmarea plății.
4. **Refund Events:** Pentru a corecta inflatarea de la 'Ridicare Magazin', implementați evenimente de Refund în GA4 când o comandă este anulată.

---

## 📊 TABEL COMPLET (TOATE METODELE)

| Metodă Plată | Comenzi Backend | Comenzi GA4 | Rată Tracking | Comenzi Lipsă | Valoare Lipsă (RON) |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Card | 21,575 | 19,183 | 88.9% | 2,392 | 4,062,097 |
| Tbi | 1,006 | 0 | 0.0% | 1,006 | 2,312,932 |
| Numerar la livrare | 18,140 | 16,393 | 90.4% | 1,747 | 1,940,917 |
| LeanPay | 369 | 0 | 0.0% | 369 | 1,129,493 |
| OP | 791 | 254 | 32.1% | 537 | 1,036,146 |
| Oney | 1,783 | 1,542 | 86.5% | 241 | 483,267 |
| Numerar sau card in magazin | 3,682 | 3,354 | 91.1% | 328 | 292,863 |
| BTDirect | 79 | 45 | 57.0% | 34 | 133,032 |
| Plata la locker | 1,597 | 1,457 | 91.2% | 140 | 92,859 |