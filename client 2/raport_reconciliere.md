# Raport Reconciliere Tranzactii - Client 2

**Data raport:** 23 Ianuarie 2026  
**Perioada analizata:** 22 Octombrie 2025 - 22 Ianuarie 2026 (92 zile)

---

## Sumar Executiv

Analiza a identificat **discrepante semnificative** intre datele din backend-ul ecommerce si Google Analytics 4. Principala cauza este **lipsa completa a tracking-ului** pentru metodele de plata LeanPay si Tbi, precum si tracking deficitar pentru Oney si BTDirect.

### Metrici Cheie

| Indicator | Ecommerce | GA4 | Diferenta |
|-----------|-----------|-----|-----------|
| **Numar tranzactii** | 84,999 | 52,128 | 32,871 (38.7%) |
| **Valoare totala** | 171,051,878 | 74,597,222 | 96,454,656 (56.4%) |
| **Tranzactii comune** | - | - | 51,869 |
| **Precizia valorii (tranzactii comune)** | - | - | 99.9% |

---

## Analiza Detaliata pe Metode de Plata

### Rata de Tracking GA4 pe Metoda de Plata

| Metoda Plata | Total Comenzi | In GA4 | Lipsa | Rata Tracking | Valoare Pierduta |
|--------------|---------------|--------|-------|---------------|------------------|
| LeanPay | 5,223 | 2 | 5,221 | **0.0%** | 21,527,551 |
| Tbi | 3,580 | 3 | 3,577 | **0.1%** | 13,254,158 |
| BTDirect | 2,079 | 326 | 1,753 | **15.7%** | 8,100,615 |
| Oney | 8,880 | 1,732 | 7,148 | **19.5%** | 23,401,896 |
| Card | 33,215 | 21,412 | 11,803 | 64.5% | 25,938,463 |
| OP (Ordin de Plata) | 1,321 | 907 | 414 | 68.7% | 888,385 |
| Numerar la livrare | 21,586 | 19,530 | 2,056 | **90.5%** | 2,469,265 |
| Plata la locker | 1,945 | 1,768 | 177 | **90.9%** | 118,004 |
| Numerar/card in magazin | 7,170 | 6,546 | 624 | **91.3%** | 742,440 |

---

## Probleme Critice Identificate

### 🔴 CRITICA: LeanPay - 0% Tracking

**Situatie:** Din 5,223 comenzi LeanPay, doar **2 au fost inregistrate** in GA4.

**Impact:** 
- 5,221 comenzi lipsa
- 21.5 milioane RON valoare neuramarita

**Cauza probabila:** 
Evenimentul `purchase` din GA4 nu se declanseaza pentru fluxul LeanPay. Utilizatorul este redirectionat catre platforma LeanPay pentru finantare, iar la intoarcere pe site tracking-ul nu se mai executa.

**Detalii pe metoda de livrare:**
- Livrare la domiciliu: 4,751 comenzi, 0.0% in GA4
- Rezervare in magazin: 283 comenzi, 0.0% in GA4
- Livrare la magazin: 119 comenzi, 0.0% in GA4
- Livrare la locker: 70 comenzi, 0.0% in GA4

---

### 🔴 CRITICA: Tbi - 0.1% Tracking

**Situatie:** Din 3,580 comenzi Tbi, doar **3 au fost inregistrate** in GA4.

**Impact:**
- 3,577 comenzi lipsa
- 13.3 milioane RON valoare neuramarita

**Cauza probabila:**
Identica cu LeanPay - redirect extern catre platforma Tbi pentru finantare, fara return tracking functional.

---

### 🟠 RIDICATA: Oney - 19.5% Tracking

**Situatie:** Din 8,880 comenzi Oney, doar **1,732 au fost inregistrate** (19.5%).

**Impact:**
- 7,148 comenzi lipsa
- 23.4 milioane RON valoare neuramarita

**Cauza probabila:**
Redirect extern catre platforma Oney. Tracking-ul functioneaza partial - posibil ca unele fluxuri (aprobare imediata) returneaza corect pe pagina de multumire, dar majoritatea nu.

---

### 🟠 RIDICATA: BTDirect - 15.7% Tracking

**Situatie:** Din 2,079 comenzi BTDirect, doar **326 au fost inregistrate** (15.7%).

**Impact:**
- 1,753 comenzi lipsa
- 8.1 milioane RON valoare neuramarita

---

### 🟡 MEDIE: Card - 64.5% Tracking

**Situatie:** Din 33,215 comenzi cu Card, **21,412 au fost inregistrate** (64.5%).

**Impact:**
- 11,803 comenzi lipsa
- 25.9 milioane RON valoare neuramarita

**Cauza probabila:**
- Ad blockere (15-25% din utilizatori)
- Redirect 3D Secure care pierde sesiunea
- Erori JavaScript pe pagina de multumire
- Safari ITP blocheaza cookies

---

## Metode de Plata cu Tracking Bun

### ✅ Numerar la livrare - 90.5% Tracking
- Nu necesita redirect extern
- Client-ul finalizeaza comanda direct pe site
- Tracking-ul se declanseaza corect

### ✅ Plata la locker - 90.9% Tracking
- Similar cu numerar la livrare
- Plata se face la ridicare, nu online

### ✅ Numerar/card in magazin - 91.3% Tracking
- Rezervare online, plata in magazin
- Nu implica redirect extern

---

## Analiza pe Metode de Livrare

| Metoda Livrare | Total | In GA4 | Rata |
|----------------|-------|--------|------|
| Livrare la magazin | 2,788 | 1,247 | 44.7% |
| Livrare la domiciliu | 66,861 | 39,589 | 59.2% |
| Livrare la locker | 4,750 | 3,444 | 72.5% |
| Rezervare in magazin | 10,592 | 7,942 | 75.0% |

**Observatie:** Rata de tracking variaza semnificativ pe metoda de livrare, dar aceasta este corelata cu metoda de plata folosita. Comenzile "Livrare la magazin" au rata mai mica probabil pentru ca includ mai multe plati cu finantare.

---

## Concluzii

### Problema Principala
**Lipsa completa a tracking-ului pentru metodele de finantare** (LeanPay, Tbi) si tracking deficitar pentru Oney si BTDirect reprezinta cauza principala a diferentelor dintre backend si GA4.

### Valoare Totala Afectata
- **LeanPay + Tbi:** 34.8 milioane RON (0% tracking)
- **Oney + BTDirect:** 31.5 milioane RON (~17% tracking)
- **Total metode finantare:** 66.3 milioane RON

### Precizia Datelor
Pentru tranzactiile care SUNT inregistrate in ambele sisteme, precizia valorii este de **99.9%**, ceea ce indica ca implementarea de baza a tracking-ului este corecta. Problema este doar la metodele cu redirect extern.

---

## Recomandari

### 1. URGENT: Implementare Server-Side Tracking
**Prioritate:** Critica  
**Termen:** Imediat

Implementati Google Analytics 4 Measurement Protocol pentru a trimite evenimentele `purchase` direct din server:
- LeanPay: La confirmarea platii de la LeanPay webhook
- Tbi: La confirmarea platii de la Tbi webhook
- Oney: La confirmarea platii de la Oney webhook
- BTDirect: La confirmarea platii de la BTDirect webhook

Aceasta metoda bypasses complet problemele de client-side tracking.

### 2. Adaugare Domenii la Unwanted Referrals
**Prioritate:** Ridicata  
**Termen:** Aceasta saptamana

In GA4 Admin > Data Streams > Configure tag settings, adaugati:
- leanpay.ro
- tbi.ro  
- oney.ro / oney.com
- btdirect.ro

### 3. Verificare Link Decoration
**Prioritate:** Ridicata  
**Termen:** Aceasta saptamana

Asigurati-va ca parametrul `_gl` este transmis corect in URL-urile de return de la procesatorii de plata. Verificati:
- Return URL-urile contin `_gl` parameter
- Cross-domain tracking este configurat corect

### 4. Audit Pagina de Multumire
**Prioritate:** Medie  
**Termen:** 2 saptamani

Verificati ca evenimentul `purchase` se declanseaza corect pentru TOATE fluxurile de plata:
- Testati fiecare metoda de plata in parte
- Verificati ca dataLayer push se executa
- Verificati ca nu exista erori JavaScript

### 5. Implementare Factor de Corectie
**Prioritate:** Scazuta  
**Termen:** Ongoing

Pana la rezolvarea problemelor, aplicati un factor de corectie in rapoartele GA4:
- Factor multiplicator recomandat: **1.64** (pentru a ajusta de la 61% la 100%)
- Sau folositi datele din backend ca sursa de adevar pentru revenue

---

## Anexa: Metodologie

### Surse de Date
1. **Ecommerce Backend:** Export Excel cu toate comenzile din perioada analizata
2. **GA4:** Export Free Form cu Transaction ID, Date, Total Revenue

### Matching Logic
- Transaction ID-urile au fost comparate dupa curatarea formatarii
- ID-urile cu sufix "-1" au fost normalizate

### Calcul Rate Matching
- Rata = (Comenzi in GA4 / Total Comenzi din Backend) * 100

---

**Raport generat automat**  
**Data:** 23 Ianuarie 2026
