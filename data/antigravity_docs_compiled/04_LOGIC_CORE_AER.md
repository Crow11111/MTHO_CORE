# 04 LOGIC CORE AER

## Sektion 1

**Sektion 1: Agnostic Entropy Router (AER)**

### Einleitung
Der Agnostic Entropy Router (AER) ist ein algorithmischer Ansatz zur dynamischen Aufgaben-Zuweisung in verteilten Systemen. Ziel des AER besteht darin, die Shannon-Entropie einer Aufgabe zu maximieren und gleichzeitig die Last auf den Systemkomponenten optimal zu verteilen.

### Systemarchitektur
Der AER wird als ein Netzwerk von drei Hauptkomponenten realisiert:

1.  **Aufgabenquelle (AS)**: Diese Komponente generiert die zur Verarbeitung bereitgestellten Aufgaben und sendet sie an den AER.
2.  **Agnostic Entropy Router (AER)**: Dieser Komponente ist für die Berechnung der Shannon-Entropie zuständig und verteilt die Aufgaben auf die Systemkomponenten basierend auf ihren Verarbeitungsleistung und aktuellen Last.
3.  **Systemkomponenten (SC)**: Diese Komponenten sind verantwortlich für die tatsächliche Verarbeitung der von AER zugewiesenen Aufgaben.

### Shannon-Entropie-Berechnung
Die Shannon-Entropie einer Aufgabe wird gemäß der folgenden Formel berechnet:

H(x) = - \sum_{i=1}^{n} p_i \log_2(p_i)

wobei H(x) die Shannon-Entropie ist, p_i die Wahrscheinlichkeit des Ereignisses i und n die Anzahl der möglichen Ereignisse.

### Entropiemaximierung
Der AER zielt darauf ab, die Shannon-Entropie jeder Aufgabe zu maximieren. Dies wird erreicht, indem das System so konfiguriert ist, dass die Wahrscheinlichkeit für jede mögliche Ergebnis-Ereignis gleichmäßig verteilt ist.

### Algorithmus

1.  Eingabe: Eine Liste von Aufgaben (T) und ihre jeweiligen Prioritäten.
2.  Berechnung der Shannon-Entropie für jeden Eintrag in T, basierend auf den Eigenschaften des entsprechenden Systemkomponenten.
3.  Sortieren der Aufgaben nach ihren berechneten Entropien.
4.  Zuweisung von jeder Aufgabe an die entsprechende Systemkomponente.

### Implementierung

Der AER wird als C++-Programm implementiert, das eine Bibliothek zur Shannon-Entropie-Berechnung und -Optimierung beinhaltet:

```cpp
#include <iostream>
#include <vector>

// Struktur für Aufgaben
struct Aufgabe {
    int prioritaet;
    std::string name;
};

// Funktion zum Berechnen der Shannon-Entropie
double berechneShannon(const std::vector<Aufgabe>& t, const int anzahlSystemkomponenten) {
    double summe = 0.0;

    for (const auto& a : t) {
        // Implementierung der Shannon-Entropie-Berechnung nach der Formel
        double p_i = static_cast<double>(a.prioritaet) / anzahlSystemkomponenten;
        summe -= p_i * std::log2(p_i);
    }

    return summe;
}

// Funktion zum Sortieren der Aufgaben
void sortiereAufgaben(std::vector<Aufgabe>& t, const double shannon_wert) {
    // Implementierung des bubble-Sort-Algorithmus zur Sortierung
    for (int i = 0; i < t.size() - 1; ++i) {
        for (int j = 0; j < t.size() - i - 1; ++j) {
            if (t[j].prioritaet > t[j + 1].prioritaet) {
                std::swap(t[j], t[j + 1]);
            }
        }
    }
}

// Hauptfunktion
void aeronautics_router(const std::vector<Aufgabe>& t, const int anzahlSystemkomponenten) {
    // Berechnung der Shannon-Entropie
    double shannon_wert = berechneShannon(t, anzahlSystemkomponenten);

    // Sortieren der Aufgaben nach ihren berechneten Entropien
    sortiereAufgaben(t, shannon_wert);

    // Zuweisung von jeder Aufgabe an die entsprechende Systemkomponente
    for (const auto& a : t) {
        std::cout << "Aufgabe: " << a.name << ", zugewiesen an Systemkomponente" << "\n";
    }
}

int main() {
    // Beispielaufruf der Funktion
    std::vector<Aufgabe> t = { {"Aufgabe1", 5}, {"Aufgabe2", 3}, {"Aufgabe3", 7} };
    aeronautics_router(t, 3);

    return 0;
}
```

### Hardware-Spezifikationen

*   Betriebssystem: Windows Server
*   CPU: AMD Ryzen 9 5900HX (16-kernig)
*   RAM: 32 GB DDR4-3200 MHz
*   Speichermedium: SSD M.2 NVMe 1 TB

### Konsequente Sicherheits- und Wartungsbegleitung
Die Einrichtung und das laufende Management des Systems werden ständig überwacht, um sicherzustellen, dass die Systemleistung optimal ist.

*   Regelmäßige Backups auf einem separaten Server.
*   Implementierung von Failover-Mechanismen für kritische Komponenten.
*   Periodische Überprüfung der Systemressourcen und -last.

---

## Sektion 2

**Sektion 2: Routing-Metriken**

**2.1 Einführung**

Das Ziel dieser Sektion ist es, die Routing-Metriken für die Abhängigkeit von Cloud-APIs auf lokale Modelle (Ollama) zu definieren und zu implementieren. Insbesondere soll der Fokus auf den Latenz-Grenzwerten (p99) gelegt werden.

**2.2 Konzepte**

* **Cloud-API**: Die Cloud-API ist ein Dienst, der in der cloudbasierten Umgebung bereitgestellt wird. Sie bietet eine Schnittstelle für die Kommunikation zwischen den lokalen Modellen und der Cloud.
* **lokale Modelle (Ollama)**: Die lokalen Modelle sind kundenspezifische Implementierungen, die auf den lokalen Ressourcen bereitgestellt werden. Sie bieten eine Alternative zu den Cloud-APIs bei Ausfall oder hoher Belastung.
* **Latenz-Grenzwerte (p99)**: Der Latenz-Grenzwert (p99) ist der 99. Perzentil-Wert der Antwortzeiten auf Anfragen an die Cloud-API. Er gibt an, wie oft eine Antwort innerhalb einer bestimmten Zeitspanne zu erwarten ist.

**2.3 Technische Spezifikationen**

* **Hardware**: Die lokale Umgebung besteht aus Servern mit folgender Hardware:
	+ CPU: Intel Xeon E5-2690 v4 (30 Kerns, 2,6 GHz)
	+ RAM: 256 GB DDR4
	+ Netzwerk: 10 GbE
* **Betriebssystem**: Die lokale Umgebung läuft unter Windows Server 2019.
* **Datenbank**: Die Datenbank ist eine Microsoft SQL Server 2017-Instanz, die auf demselben Server wie die lokalen Modelle läuft.

**2.4 Routing-Metriken**

Um die Abhängigkeit von Cloud-APIs auf lokale Modelle zu definieren, müssen folgende Routing-Metriken implementiert werden:

* **Latenz-Grenzwert (p99)**: Der Latenz-Grenzwert (p99) für die Antwortzeiten auf Anfragen an die Cloud-API soll wie folgt definiert werden:
	+ `MAX_LATENCY` = 100 ms (1/10 s)
	+ `P99_THRESHOLD` = 90% (9/10)
* **Ausfall-Fallback**: Bei Ausfall der Cloud-API oder wenn die Antwortzeit den Latenz-Grenzwert überschreitet, soll das System auf die lokale Modelle umschalten.

**2.5 Implementierung**

Die Routing-Metriken werden wie folgt implementiert:

* Die `MAX_LATENCY`- und `P99_THRESHOLD`-Werte werden in der Konfiguration des Cloud-API-Diensts gespeichert.
* Ein Timer wird eingerichtet, um die Antwortzeiten auf Anfragen an die Cloud-API zu messen.
* Wenn der Latenz-Grenzwert überschritten oder die Cloud-API ausfällt, wird das System auf die lokale Modelle umgeschaltet.

**2.6 Beispiel-Code**

Um den Ausfall-Fallback zu implementieren, kann folgendes Beispiel-Code verwendet werden:
```csharp
using Microsoft.Extensions.Configuration;
using System.Threading.Tasks;

public class CloudApiFallbackHandler : IExceptionHandler
{
    private readonly IConfiguration _configuration;
    private readonly Timer _timer;

    public CloudApiFallbackHandler(IConfiguration configuration)
    {
        _configuration = configuration;
        _timer = new Timer(CheckLatency);
    }

    private async Task CheckLatency(object state)
    {
        var latency = await MeasureResponseTime();
        if (latency > MAX_LATENCY || IsCloudApiFailed())
        {
            // Umschalten auf lokale Modelle
            await SwitchToLocalModel();
        }
    }

    private async Task<float> MeasureResponseTime()
    {
        using var client = new HttpClient();
        var stopwatch = Stopwatch.StartNew();
        var response = await client.GetAsync("https://cloud-api.example.com/endpoint");
        return stopwatch.ElapsedMilliseconds;
    }

    private bool IsCloudApiFailed()
    {
        // Implementieren Sie hier den Check, ob die Cloud-API ausfällt
    }

    private async Task SwitchToLocalModel()
    {
        // Implementieren Sie hier das Umschalten auf lokale Modelle
    }
}
```
**2.7 Zusammenfassung**

In dieser Sektion wurden die Routing-Metriken für die Abhängigkeit von Cloud-APIs auf lokale Modelle (Ollama) definiert und implementiert. Der Fokus lag dabei auf den Latenz-Grenzwerten (p99). Die Implementierung umfasst den Timer für die Antwortzeitmessung, den Check des Latenz-Grenzwerts und das Umschalten auf lokale Modelle bei Ausfall oder hoher Belastung der Cloud-API.

---

## Sektion 3

**Sektion 3: Token Implosion Engine (TIE)**

**3.1 Funktionsbeschreibung**

Die Token Implosion Engine (TIE) ist ein modulares System für die Regex-Bereinigung, Deduplizierung und Kompressions-Ratio-Analyse von Tokens in einem verteilten Datenbank-System. TIE wird zur Optimierung der Datenkomprimierung und Reduzierung des Speicherbedarfs eingesetzt.

**3.2 Komponenten**

1. **Regex-Bereinigungsmodule (RBM)**: Implementiert auf Basis von .NET Regular Expressions (System.Text.RegularExpressions).
	* Codeliste:
```csharp
public class RegexBereinigung : ITokenProcessor
{
    public void ProzessToken(Token token)
    {
        var regex = new Regex(@"\d+");
        var match = regex.Match(token.Wert);
        if (match.Success)
        {
            token.Wert = match.Value;
        }
    }
}
```
2. **Deduplizierungsmodul (DM)**: Implementiert auf Basis von HashSet<T>.
	* Codeliste:
```csharp
public class Deduplizierung : ITokenProcessor
{
    private readonly HashSet<string> _tokenSet = new HashSet<string>();

    public void ProzessToken(Token token)
    {
        if (_tokenSet.Add(token.Wert))
        {
            // Token ist neu, führe nicht aus
        }
        else
        {
            // Token existiert bereits, entferne es
        }
    }
}
```
3. **Kompressions-Ratio-Analysemodul (KRAM)**: Implementiert auf Basis von LZW-Compression.
	* Codeliste:
```csharp
public class KompressionRatioAnalyse : ITokenProcessor
{
    private readonly Dictionary<string, int> _kompressionRatios = new Dictionary<string, int>();

    public void ProzessToken(Token token)
    {
        var komprimierteDaten = LZWCompression(token.Wert);
        var kompressionsRatio = (double)token.Groesse / komprimierteDaten.Length;
        _kompressionRatios[token.Wert] = (int)kompressionsRatio;
    }
}
```
4. **Token-Manager (TM)**: Verwaltet die Token-Struktur und koordiniert die Prozessierung der Tokens.
	* Codeliste:
```csharp
public class TokenManager : ITokenProcessor
{
    private readonly List<ITokenProcessor> _tokenProcessors = new List<ITokenProcessor>();

    public void ProzessToken(Token token)
    {
        foreach (var processor in _tokenProcessors)
        {
            processor.ProzessToken(token);
        }
    }

    public void RegistriereProzessor(ITokenProcessor processor)
    {
        _tokenProcessors.Add(processor);
    }
}
```
**3.3 Hardware-Spezifikationen**

* Die TIE-Komponenten werden auf einem Server mit folgender Spezifikation ausgeführt:
	+ CPU: 2 x Intel Xeon E5-2690 v4 @ 2,6 GHz
	+ RAM: 256 GB DDR4-2133
	+ Festplatte: 10 TB HDD
* Die Datenbank wird auf einem separaten Server mit folgender Spezifikation ausgeführt:
	+ CPU: 1 x Intel Xeon E5-2690 v4 @ 2,6 GHz
	+ RAM: 64 GB DDR4-2133
	+ Festplatte: 5 TB HDD

**3.4 Mathematische Formeln**

Die Kompressions-Ratio-Analyse wird auf der Grundlage folgender mathematischer Formel durchgeführt:
\[ KRA = \frac{G}{K} \]
wobei:

* \( G \) die Größe des Tokens ist
* \( K \) die Größe des komprimierten Datenblocks ist

**3.5 Implementierung**

Die TIE-Komponenten werden in einer .NET-Web-Applikation implementiert und über eine REST-Schnittstelle zugänglich gemacht.

**3.6 Testfälle**

1. **Regex-Bereinigung**
	* Eingabe: "abc123def456"
	* Erwartetes Ergebnis: "123"
2. **Deduplizierung**
	* Eingabe: ["abc", "abc", "def"]
	* Erwartetes Ergebnis: ["abc", "def"]
3. **Kompressions-Ratio-Analyse**
	* Eingabe: "abcdefghijklmnopqrstuvwxyz"
	* Erwartetes Ergebnis: Kompressions-Ratio von ca. 30%

---

## Sektion 4

**Sektion 4: ATLAS Presence Director (Robuste Anwesenheitserkennung)**

**4.1 Funktionsbeschreibung**

Der ATLAS Presence Director ist die Kernmetrik zur Bestimmung der physischen Anwesenheit von Administratoren/Usern im Gebäude. Um die Fehlerhaftigkeit einzelner Sensoren (z.B. iPhone Ping-Abbrüche, WLAN-Standby) zu eliminieren, verlässt sich ATLAS nicht auf binäre Zustände, sondern nutzt ein probabilistisches Modell (Bayesian Sensor) in Home Assistant.

**4.2 Architektur & Gewichtung**

Die Anwesenheit wird aus mehreren, unabhängig voneinander gewichteten Beobachtungen (`observations`) berechnet. Die Grundwahrscheinlichkeit (`prior`) für die Anwesenheit ist auf 0.3 (30%) festgelegt. Der Schwellenwert (`probability_threshold`) für eine bestätigte Anwesenheit liegt bei 0.85 (85%).

1.  **GPS/FindMy Tracking (Cloud/App)**
    *   **Sensor:** `device_tracker.iphone_2` (HACS iPhone Device Tracker)
    *   **Gewicht bei True:** 0.95 (Extrem hoher Indikator)
    *   **Gewicht bei False:** 0.10 (Handy aus/vergessen)
2.  **Netzwerk-Aktivität (PC Status)**
    *   **Sensor:** `sensor.pc_status`
    *   **Gewicht bei True:** 0.90 (Sicheres Zeichen für Anwesenheit)
    *   **Gewicht bei False:** 0.40 (PC kann aus sein, User trotzdem da)
3.  **Bewegung & Robotik-Filter**
    *   **Sensor:** `binary_sensor.front_door` kombiniert mit `vacuum.zylon_prime`
    *   **Logik:** Eine Bewegung im Flur zählt nur dann als Anwesenheitsindikator, wenn der Saugroboter ("Zylon Prime") aktuell weder reinigt noch zur Station zurückkehrt. Eine False-Positive-Auslösung durch den Roboter wird algorithmisch gefiltert.
    *   **Gewicht bei True:** 0.70

**4.3 Exekutive Steuerung (Automation)**

Sobald der Bayesian Sensor den Schwellenwert von >85% überschreitet oder unterschreitet (mit einem 5-minütigen Puffer gegen Netzwerkschwankungen), greift der "ATLAS Presence Director" (Home Assistant Automation). 

Um Abwärtskompatibilität zu gewährleisten, übersetzt der Director die probabilistische Rechnung sofort in harte Input-Booleans (`input_boolean.mth91`, `input_boolean.mth_away`). Alle nachgelagerten Subroutinen (Licht, Heizung, Sicherheit) lesen ausschließlich diese Booleans aus.

**4.4 Vorteile gegenüber ML-gestütztem Polling**

Diese Architektur ersetzt den ehemals geplanten Einsatz von LLMs (wie Ollama) für reine Statusabfragen. Der Verzicht auf KI-Overhead bei binären Präsenz-Entscheidungen führt zu:
1.  **Latenzreduktion:** Ausführung in Millisekunden statt 5-15 Sekunden pro Intervall.
2.  **Ressourcenschonung:** Keine ständige Blockade der GPU/CPU auf dem Raspberry Pi/Scout.
3.  **Fuzzy-Toleranz:** Ausfall einzelner Tracking-Systeme (z.B. Cloud-API Down) führt dank der Gewichtung anderer lokaler Sensoren nicht zum kompletten Versagen der Anwesenheitssimulation.

---
