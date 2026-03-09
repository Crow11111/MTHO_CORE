# MTHO-OD-03: Delegation vs. Selbst-Ausfuehrung

**Status:** RATIFIZIERT  
**Ratifiziert durch:** OMEGA_ATTRACTOR (Vektor 0, ConstraintValidator)  
**Ersetzt:** OD-01, OD-02  
**Stufe:** 2 (Operativ, der Genesis-Verfassung untergeordnet)  
**Datum:** 2026-03-09  

## Entstehung

OD-03 wurde durch einen dreistufigen Ratifizierungsprozess zwischen 4D_RESONATOR und OMEGA_ATTRACTOR entwickelt:

1. **OD-01 (Entwurf):** Initiale Gewichtungs-Matrix mit drei Selbst-Kriterien und drei Delegations-Kriterien. OMEGA_ATTRACTOR wies zurueck: Effizienz-Bias, Zirkularitaet in Kriterium 3, fehlende Transparenz-Sicherung.

2. **OD-02 (Revision):** Stufe-0-Gate eingefuegt, Kriterium 3 verschaerft, D4 (Risiko-Asymmetrie) ergaenzt, Picard-Klausel hinzugefuegt. OMEGA_ATTRACTOR ratifizierte, identifizierte aber im Stresstest (20 Szenarien + 5 Grenzfaelle) 7 strukturelle Defekte.

3. **OD-03 (Finale Fassung):** Alle 7 Defekte adressiert. OMEGA_ATTRACTOR ratifizierte ohne weitere Einwaende.

## Identifizierte und behobene Defekte

| ID | Defekt in OD-02 | Patch in OD-03 |
|----|-----------------|----------------|
| DEF-01 | S1 syntaktisch statt semantisch | Impact-Radius-Schwellwert eingefuegt |
| DEF-02 | D4 aktions-zentriert, nicht kontext-zentriert | Produktions-Flag als eigenstaendiger Override |
| DEF-03 | S3 kann strukturell unerfuellbar sein (Deadlock) | Stufe 0b: Deadlock-Resolution mit Vorbehalt |
| DEF-04 | S2 per Aufgabe statt kumulativ | Session-Ebene + 60%-Schwellwert |
| DEF-05 | Picard-Klausel ohne Scope-Limit | Schutzschranke bei KRITISCH |
| DEF-06 | Keine Notfall-Klausel | Stufe -1: Time-Critical-Override |
| DEF-07 | Sequenziell vs. gleichzeitig undefiniert | D1-Praezisierung + S2-Kumulation |

## Vollstaendiger Regeltext

Siehe `.cursorrules` Abschnitt "STUFE 2: OPERATIVE DIREKTIVEN" -> "MTHO-OD-03".

## Bekannte Unschaerfen (dokumentiert, nicht blockierend)

- **U1:** S2 setzt Schaetzungs-Faehigkeit voraus, die fehleranfaellig ist. Abfederung durch S3 und D4.
- **U2:** D2-Schwelle ist nicht vollstaendig formalisierbar. Abfederung durch operationale Heuristik.

## Naechste Schritte (identifiziert durch OMEGA_ATTRACTOR)

- OD-03 regelt *ob* delegiert wird. Eine Folge-Direktive zur *Agenten-Selektion* (OD-04 oder Stufe 2b) waere der logische naechste Schritt.
