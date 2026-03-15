import requests
import xml.etree.ElementTree as ET
import os

def main():
    url = "https://www.epgitalia.tv/guide2"
    canali_file = "canali.txt"
    output_file = "02.1.epg"

    # 1. Carica la lista dei canali desiderati
    if not os.path.exists(canali_file):
        print(f"Errore: {canali_file} non trovato.")
        return
    
    with open(canali_file, "r") as f:
        target_channels = [line.strip() for line in f if line.strip()]

    print(f"Scaricamento dati da {url}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Nota: Se l'URL restituisce un file compresso (GZ), requests non lo decomprime automaticamente se l'header non è corretto.
        # Ma assumiamo che sia testo/xml come richiesto.
        xml_content = response.content
        root = ET.fromstring(xml_content)
        
        # Crea un nuovo albero XML per l'output
        new_root = ET.Element("tv")
        # Copia gli attributi (es. generator-info-name)
        for key, value in root.attrib.items():
            new_root.set(key, value)

        # 2. Filtra i canali
        for channel in root.findall("channel"):
            if channel.get("id") in target_channels:
                new_root.append(channel)

        # 3. Filtra i programmi associati ai canali
        for programme in root.findall("programme"):
            if programme.get("channel") in target_channels:
                new_root.append(programme)

        # 4. Salva il file
        tree = ET.ElementTree(new_root)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)
        print(f"File {output_file} creato con successo.")

    except Exception as e:
        print(f"Errore durante l'elaborazione: {e}")

if __name__ == "__main__":
    main()
