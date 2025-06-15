# Rip & Ship Kings - Shopify Order Overlay Handleiding

Dit project toont Shopify bestellingen die een specifiek product bevatten (bijv. "Live stream") als een overlay in OBS, compleet met geluidsnotificaties. Er is ook een admin-paneel om de wachtrij te beheren.

---

## 1. Eenmalige Installatie (One-Time Setup)

Dit zijn de stappen die je één keer moet uitvoeren om alles op je pc in te stellen.

### Stap 1: Installeer Python
Als je nog geen Python hebt, download en installeer de laatste versie van [python.org](https://www.python.org/downloads/). **Belangrijk:** Zorg ervoor dat je tijdens de installatie het vinkje aanzet bij **"Add Python to PATH"**.

### Stap 2: Download de Projectbestanden
Download alle bestanden van dit project en plaats ze in een makkelijk te vinden map (bijv. `C:\Users\JouwNaam\Documents\ShopifyOverlay`).

### Stap 3: Installeer de Benodigde Python Packages
1.  Open een terminal (Command Prompt of PowerShell).
2.  Navigeer naar de projectmap met het `cd` commando. Bijvoorbeeld:
    ```bash
    cd C:\Users\JouwNaam\Documents\ShopifyOverlay\project
    ```
3.  Installeer de benodigde packages met dit commando:
    ```bash
    pip install -r requirements.txt
    ```

### Stap 4: Download en Configureer Ngrok
Ngrok maakt een veilige, openbare URL aan die naar jouw lokale computer wijst, zodat Shopify de orderdata kan sturen.
1.  Download ngrok van [ngrok.com/download](https://ngrok.com/download).
2.  Unzip het bestand. Je hebt nu `ngrok.exe`. Plaats dit bestand in je `Downloads` map.
3.  Maak een gratis account aan op [ngrok.com](https://dashboard.ngrok.com/signup).
4.  Ga naar de ["Your Authtoken"](https://dashboard.ngrok.com/get-started/your-authtoken) pagina op je dashboard en kopieer je token.
5.  Open een nieuwe terminal, navigeer naar je `Downloads` map en voer het volgende commando uit (vervang `<JOUW_AUTHTOKEN>` met de gekopieerde token):
    ```bash
    ngrok config add-authtoken <JOUW_AUTHTOKEN>
    ```
    Dit hoef je maar één keer te doen.

---

## 2. Gebruik voor een Live Stream

Volg deze stappen **elke keer** als je live gaat.

### Stap 1: Start de Applicatie Server
-   Open een terminal en navigeer naar je projectmap (bijv. `cd C:\..._map_\project`).
-   Start de server met:
    ```bash
    python main.py
    ```
-   Laat deze terminal open staan. Hij verwerkt alle binnenkomende orders.

### Stap 2: Start Ngrok
-   Open een **tweede, aparte** terminal.
-   Navigeer naar de map waar `ngrok.exe` staat (je `Downloads` map).
-   Start ngrok met:
    ```bash
    ngrok http 5000
    ```
-   Ngrok toont nu een **Forwarding URL**. Deze ziet eruit als `https://random-string.ngrok-free.app`.
-   Laat deze terminal ook open staan.

### Stap 3: Update de Shopify Webhook
-   Kopieer de `https://...` Forwarding URL uit je ngrok-terminal.
-   Ga naar je **Shopify Admin** -> **Settings** -> **Notifications**.
-   Scroll naar beneden naar **Webhooks**.
-   Klik op je bestaande `Order creation` webhook om deze te bewerken.
-   **Vervang de oude ngrok URL** met de nieuwe die je net hebt gekopieerd. Voeg `/webhook` toe aan het einde.
    -   Voorbeeld: `https://random-string.ngrok-free.app/webhook`
-   Klik op **Save**.

### Stap 4: Voeg toe aan OBS
-   In OBS, voeg een nieuwe **Browser** source toe.
-   Stel de URL in op: `http://127.0.0.1:5000/overlay`
-   Stel de breedte en hoogte naar wens in.
-   **Belangrijk voor geluid:** Klik met de rechtermuisknop op de source -> **Properties** -> vink **"Control audio via OBS"** aan.

### Stap 5: Beheer de Wachtrij
-   Open een browser en ga naar `http://127.0.0.1:5000/admin` om de wachtrij te zien en te beheren.

---

## 3. Probleemoplossing (Troubleshooting)

-   **Ik hoor geen geluid in OBS:** Ga in OBS naar **Advanced Audio Properties** en zet "Audio Monitoring" voor de browser source op "Monitor and Output".
-   **Bestellingen komen niet binnen:**
    1.  Check de ngrok-terminal. Zie je een `POST /webhook 200 OK`? Zo niet, dan is de URL in je Shopify webhook niet correct.
    2.  Check de `python main.py` terminal. Zie je een error of een "Skipping" bericht? Dit geeft aan wat er misgaat.
-   **Ngrok geeft `502 Bad Gateway` error:** Je `main.py` server draait niet. Start deze opnieuw.
