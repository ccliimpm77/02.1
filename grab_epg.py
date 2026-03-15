import requests
import xml.etree.ElementTree as ET
import os

def main():
    url = "https://www.epgitalia.tv/guide2"
    canali_file = "canali.txt"
    output_file = "02.1.epg"

    # Header per evitare il blocco (User-Agent)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    if not os.path.exists(canali_file):
        print(f"ERRORE: {canali_file} non trovato nel repository.")
        return
    
    with open(canali_file, "r") as f:
        target_channels = [line.strip() for line in f if line.strip()]

    if not target_channels:
        print("ERRORE: Il file canali.txt è vuoto.")
        return

    print(f"Scaricamento dati da {url}...")
    try:
        # Il parametro stream=True e l'header permettono di gestire meglio file grandi
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        
        print(f"Dati ricevuti ({len(response.content)} bytes). Analisi XML...")
        root = ET.fromstring(response.content)
        
        new_root = ET.Element("tv")
        for key, value in root.attrib.items():
            new_root.set(key, value)

        count_ch = 0
        count_pr = 0

        # Filtra i canali
        for channel in root.findall("channel"):
            if channel.get("id") in target_channels:
                new_root.append(channel)
                count_ch += 1

        # Filtra i programmi
        for programme in root.findall("programme"):
            if programme.get("channel") in target_channels:
                new_root.append(programme)
                count_pr += 1

        print(f"Trovati {count_ch} canali e {count_pr} programmi.")

        if count_ch == 0:
            print("ATTENZIONE: Nessun canale corrispondente trovato. Controlla gli ID in canali.txt")

        # Scrittura file
        tree = ET.ElementTree(new_root)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)
        
        if os.path.exists(output_file):
            print(f"SUCCESSO: File {output_file} creato (Dimensione: {os.path.getsize(output_file)} bytes).")
        else:
            print("ERRORE: Il file non è stato scritto su disco.")

    except Exception as e:
        print(f"ERRORE CRITICO: {e}")
        exit(1) # Forza l'errore nel workflow per debugging

if __name__ == "__main__":
    main()
