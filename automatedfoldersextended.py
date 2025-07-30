import os
import shutil
import re
import xml.etree.ElementTree as ET

def find_model_names_in_file(file_path):
    """Kinyeri a model neveket a különböző konfigurációs fájlokból"""
    model_names = set()
    
    if not os.path.exists(file_path):
        return model_names
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Különböző regex minták a különböző fájltípusokhoz
            if file_path.endswith('vehicles.meta'):
                # vehicles.meta - <modelName>...</modelName>
                pattern = r'<modelName>(.*?)<\/modelName>'
            elif file_path.endswith('carvariations.meta'):
                # carvariations.meta - <modelName>...</modelName>
                pattern = r'<modelName>(.*?)<\/modelName>'
            elif file_path.endswith('handling.meta'):
                # handling.meta - <handlingName>...</handlingName>
                pattern = r'<handlingName>(.*?)<\/handlingName>'
            elif file_path.endswith('carcols.meta'):
                # carcols.meta - <modelName>...</modelName>
                pattern = r'<modelName>(.*?)<\/modelName>'
            elif file_path.endswith('vehiclelayouts.meta'):
                # vehiclelayouts.meta - <layoutName>...</layoutName>
                pattern = r'<layoutName>(.*?)<\/layoutName>'
            else:
                return model_names
            
            matches = re.findall(pattern, content, re.IGNORECASE)
            model_names.update(matches)
            
    except Exception as e:
        print(f"Hiba a fájl olvasásakor ({file_path}): {str(e)}")
    
    return model_names

def process_vehicle_folder(vehicle_folder, source_folder):
    """Feldolgoz egy jármű mappát és kezeli a stream mappát"""
    stream_folder = os.path.join(vehicle_folder, "stream")
    
    # Létrehozzuk a stream mappát ha nem létezik
    os.makedirs(stream_folder, exist_ok=True)
    
    # Konfigurációs fájlok amiket keresünk
    config_files = [
        'handling.meta',
        'carcols.meta',
        'carvariations.meta',
        'vehiclelayouts.meta',
        'vehicles.meta'
    ]
    
    # Összegyűjtjük az összes modellnevet
    all_model_names = set()
    
    for config_file in config_files:
        config_path = os.path.join(vehicle_folder, config_file)
        if os.path.exists(config_path):
            model_names = find_model_names_in_file(config_path)
            all_model_names.update(model_names)
    
    # Ha nem találtunk model neveket, próbáljuk a mappa nevét használni
    if not all_model_names:
        folder_name = os.path.basename(vehicle_folder)
        all_model_names.add(folder_name)
        print(f"Nem találtam modellneveket a konfigfájlokban, a mappa nevet használom: {folder_name}")
    
    # Minden modellnévhez megkeressük a fájlokat
    for model_name in all_model_names:
        # Tisztítjuk a modell nevet (eltávolítjuk a whitespace-t és speciális karaktereket)
        clean_model_name = re.sub(r'[^a-zA-Z0-9_]', '', model_name)
        
        # Megkeressük a forrásfájlokat
        yft_file = os.path.join(source_folder, f"{clean_model_name}.yft")
        ytd_file = os.path.join(source_folder, f"{clean_model_name}.ytd")
        
        # Másoljuk a .yft fájlt ha létezik
        if os.path.exists(yft_file):
            dest_yft = os.path.join(stream_folder, f"{clean_model_name}.yft")
            shutil.copy2(yft_file, dest_yft)
            print(f"Másoltam: {yft_file} -> {dest_yft}")
        else:
            print(f"Hiányzó YFT fájl: {yft_file}")
        
        # Másoljuk a .ytd fájlt ha létezik
        if os.path.exists(ytd_file):
            dest_ytd = os.path.join(stream_folder, f"{clean_model_name}.ytd")
            shutil.copy2(ytd_file, dest_ytd)
            print(f"Másoltam: {ytd_file} -> {dest_ytd}")
        else:
            print(f"Hiányzó YTD fájl: {ytd_file}")

def process_all_vehicle_folders(root_folder, source_folder):
    """Feldolgozza az összes jármű mappát a root_folder-ben"""
    for root, dirs, files in os.walk(root_folder):
        # Ha a mappában van bármelyik konfigfájl, akkor jármű mappa
        has_config = any(f.lower() in [
            'handling.meta',
            'carcols.meta',
            'carvariations.meta',
            'vehiclelayouts.meta',
            'vehicles.meta'
        ] for f in files)
        
        if has_config:
            print(f"\nFeldolgozom: {root}")
            process_vehicle_folder(root, source_folder)

if __name__ == "__main__":
    print("==== Jármű Stream Mappa Készítő ====")
    root_dir = input("Add meg a fő mappa elérési útját (ahol a jármű mappák vannak): ").strip()
    source_dir = input("Add meg a forrásmappa elérési útját (ahol a .yft és .ytd fájlok vannak): ").strip()
    
    if not os.path.isdir(root_dir):
        print("Hibás fő mappa elérési út!")
    elif not os.path.isdir(source_dir):
        print("Hibás forrásmappa elérési út!")
    else:
        process_all_vehicle_folders(root_dir, source_dir)
    
    print("\nFolyamat befejezve!")
    input("Nyomj Entert a kilépéshez...")