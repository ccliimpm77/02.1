import requests
import xml.etree.ElementTree as ET
import os
import gzip
import io

def main():
    url = "https://www.epgitalia.tv/guide2"
    canali_file = "canali.txt"
    output_file = "02.1.epg"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate'
    }

    if not os.path.exists(canali_file):
        print(f"ERRORE: {canali_file} non trovato.")
        return
    
    with open(canali_file, "r") as f:
        target_channels = [line.strip() for line in f if line.strip()]

    print(f"Scaricamento dati da {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        
        raw_data = response.content
        print(f"Dati ricevuti ({len(raw_data)} bytes).")

        # Gestione Decompressione GZIP
        # Se i primi due byte sono 1f 8b, il file è un GZIP
        if raw_data.startswith(b'\x1f\x8b'):
            print("Rilevato formato compresso (GZIP). Decompressione in corso...")
            try:
                raw_data = gzip.decompress(raw_data)
                print(f"Decompressione completata. Nuova dimensione: {len(raw_data)} bytes.")
            except Exception as e:
                print(f"Errore durante la decompressione: {e}")
                return

        # Analisi XML
        print("Analisi XML...")
        # Usiamo BytesIO per gestire correttamente la codifica durante il parsing
        root = ET.fromstring(raw_data)
        
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

        print(f"Filtro completato: {count_ch} canali e {count_pr} programmi trovati.")

        # Scrittura file finale
        tree = ET.ElementTree(new_root)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)
        
        if os.path.exists(output_file):
            print(f"SUCCESSO: File {output_file} creato ({os.path.getsize(output_file)} bytes).")
        else:
            print("ERRORE: Impossibile scrivere il file di output.")

    except ET.ParseError as e:
        print(f"ERRORE XML: Il file scaricato non è un XML valido. Dettagli: {e}")
        # Stampiamo i primi 100 caratteri per capire cosa abbiamo scaricato veramente
        print(f"Inizio dati: {raw_data[:100]}")
    except Exception as e:
        print(f"ERRORE CRITICO: {e}")
