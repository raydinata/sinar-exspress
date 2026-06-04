import re

class NLPEngine:
    def __init__(self):
        self.intent_patterns = {
            'greet': r'\b(halo|hai|hello|hi|selamat)\b',
            'track': r'\b(cek|lacak|resi|kiriman|track|where)\b',
            'tariff': r'\b(tarif|ongkir|biaya|harga|kirim|berapa)\b',
            'complaint': r'\b(komplain|aduan|rugi|rusak|hilang|lama|cepat|salah|retur)\b',
            'info_branch': r'\b(lokasi|alamat|kantor|agen|drop point|jam buka|jam operasional|cabang)\b',
            'prohibited': r'\b(larangan|dilarang|barang terlarang|cair|baterai|murahan|parfum|mie instan)\b',
            'pickup': r'\b(jemput|pickup|ambil|pick up|kurir panggil|request)\b',
            'exit': r'\b(bye|keluar|selesai|terima kasih|dah)\b'
        }
        
        self.entity_patterns = {
            'tracking_code': r'\b(?:JNE|JNT|SPC|TIKI|JTR|SPX)[A-Z]?\d{8,12}\b', 
            'city': r'\b(semarang|solo|surakarta|magelang|pekalongan|salatiga|tegalsari|tegal|brebes|purwokerto|cilacap|kudus|jepara|demak|kendal|batang|pekalongan|pemalang|klaten|boyolali|karanganyar|wonogiri|sukoharjo|wonosobo|temanggung|kendal|blora|rembang|pati|grobogan|sragen)\b',
            # TAMBAHAN: Deteksi angka diikuti kg/kilo (contoh: 2.5kg, 3 kg, 1kilo)
            'weight': r'(\d+(?:[.,]\d+)?)\s*(?:kg|kilo|kilogram)'
        }

    def detect_intent(self, text):
        text = text.lower()
        for intent, pattern in self.intent_patterns.items():
            if re.search(pattern, text):
                return intent
        return 'unknown'

    def _parse_single_segment(self, text):
        for entity_type, pattern in self.entity_patterns.items():
            target_text = text.upper() if entity_type == 'tracking_code' else text.lower()
            match = re.search(pattern, target_text)
            if match:
                return {'type': entity_type, 'value': match.group()}
        return None

    def parse_orders(self, text):
        entities = []
        entity = self._parse_single_segment(text)
        if entity:
            entities.append(entity)
        return entities