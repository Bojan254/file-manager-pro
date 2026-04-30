import zipfile
import xml.etree.ElementTree as ET

# Stavi putanju do svog Excel fajla ovdje
filepath = r"C:\Users\BojanZivkovicBDCorpo\OneDrive - BD Corporate Services doo Podgorica\Desktop\Slike to pdf\Excel"

with zipfile.ZipFile(filepath, 'r') as zip_ref:
    svi_fajlovi = zip_ref.namelist()

    print("=== SVI FAJLOVI U XLSX ===")
    for f in svi_fajlovi:
        print(f)

    print("\n=== MEDIA FAJLOVI ===")
    media = [f for f in svi_fajlovi if "media" in f]
    for f in media:
        print(f)

    print("\n=== SHEET NAMES ===")
    try:
        with zip_ref.open("xl/workbook.xml") as wb_file:
            tree = ET.parse(wb_file)
            root = tree.getroot()
            ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for j, sheet in enumerate(root.findall('.//ns:sheet', ns), start=1):
                print("Sheet {}: {}".format(j, sheet.get('name')))
    except Exception as e:
        print("Greska sheet names:", e)

    print("\n=== RELS FAJLOVI ===")
    rels = [f for f in svi_fajlovi if "_rels" in f]
    for f in rels:
        print(f)
        try:
            with zip_ref.open(f) as rels_file:
                content = rels_file.read().decode("utf-8")
                if "image" in content.lower():
                    print("   >>> SADRZI SLIKE:")
                    print("   ", content[:500])
        except Exception as e:
            print("   Greska:", e)