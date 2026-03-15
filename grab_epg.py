import requests
import xml.etree.ElementTree as ET
import os
import gzip
import sys

def main():
    url = "https://www.epgitalia.tv/guide2"
    canali_file = "canali.txt"
    output_file = "02.1.epg"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)',
        'Accept-Encoding': 'gzip, deflate'
    }

    # 1. Carica canali.txt
    if not os.path.exists(canali_file):
        print(f"ERRORE: Manca il file {canali_file}")
        sys.exit(1)
    
    with open(canali_file, "r") as f:
        target_channels = [line.strip() for line in f if line.strip()]
    print(f"Canali cercati (da canali.txt): {target_channels}")

    # 2. Scarica i dati
    print(f"Scaricamento da {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.content
        print(f"Byte ricevuti: {len(data)}")

        # 3. Decompressione GZIP se necessaria
        if data.startswith(b'\x1f\x8b'):
            print("Dati compressi rilevati. Decompressione...")
            data = gzip.decompress(data)
            print(f"Dimensione decompressa: {len(data)}")

        # 4. Parsing XML
        root = ET.fromstring(data)
        
        new_root = ET.Element("tv", root.attrib)
        
        # Log per vedere cosa c'è nell'XML originale
        all_channels_in_xml = [ch.get("id") for ch in root.findall("channel")]
        print(f"Primi 10 canali trovati nell'XML: {all_channels_in_xml[:10]}")

        # 5. Filtro
        count_ch = 0
        for channel in root.findall("channel"):
            if channel.get("id") in target_channels:
                new_root.append(channel)
                count_ch += 1

        count_pr = 0
        for programme in root.findall("programme"):
            if programme.get("channel") in target_channels:
                new_root.append(programme)
                count_pr += 1

        print(f"Trovati {count_ch} canali e {count_pr} programmi corrispondenti.")

        # 6. Salvataggio (anche se vuoto, creiamo il file per non far fallire Git)
        tree = ET.ElementTree(new_root)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)
        print(f"File {output_file} salvato correttamente.")

    except Exception as e:
        print(f"ERRORE DURANTE L'ESECUZIONE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
