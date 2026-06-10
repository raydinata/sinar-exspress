from engine import NLPEngine
import re
import math

# Definisi State Dasar
GREETING = "GREETING"
SELECT_SERVICE = "SELECT_SERVICE"
AWAITING_TRACKING_ID = "AWAITING_TRACKING_ID"
AWAITING_TARIFF_CITY = "AWAITING_TARIFF_CITY"
AWAITING_COMPLAINT_DETAILS = "AWAITING_COMPLAINT_DETAILS"
AWAITING_PICKUP_ADDRESS = "AWAITING_PICKUP_ADDRESS"
END = "END"

class ChatbotFSM:
    def __init__(self):
        self.engine = NLPEngine()
        
        # --- DATABASE SIMULASI YANG LEBIH REALISTIS ---
        self.mock_database = {
            "JNE12345678": {
                "courier": "JNE", 
                "origin": "Semarang", 
                "destination": "Solo", 
                "transit": "Hub Transitan Semarang", 
                "status": "Paket sedang dalam perjalanan menuju Hub Solo", 
                "eta": "Estimasi tiba: Besok sore"
            },
            "JNT99887766": {
                "courier": "J&T Express", 
                "origin": "Pekalongan", 
                "destination": "Magelang", 
                "transit": "Drop Point Magelang", 
                "status": "Paket telah sampai di Drop Point tujuan", 
                "eta": "Estimasi tiba: 1 hari lagi"
            },
            "SPC55664433": {
                "courier": "SiCepat", 
                "origin": "semarang", 
                "destination": "pemalang", 
                "transit": "Sorting Center tegal", 
                "status": "Paket sedang di-sorting center", 
                "eta": "Estimasi tiba: Hari ini"
            },
            "TIKI11223344": {
                "courier": "Tiki", 
                "origin": "Kudus", 
                "destination": "Pekalongan", 
                "transit": "Agen Kudus", 
                "status": "Paket telah diambil oleh kurir pengirim", 
                "eta": "Estimasi tiba: Lusa"
            },
            "SPX99001122": {
                "courier": "Shopee Express", 
                "origin": "Tegal", 
                "destination": "Semarang", 
                "transit": "Hub Semarang", 
                "status": "Paket sedang dalam perjalanan menuju buyer (Out for Delivery)", 
                "eta": "Estimasi tiba: Besok pagi"
            }
        }

    # --- FUNGSI HELPER UNTUK FORMAT TAMPILAN RESI ---
    def _format_tracking_response(self, tracking_code, data):
        # Menggunakan emoji agar tampilan chatbot lebih menarik dan terstruktur
        return (
            f" *Detail Pengiriman ({tracking_code})*\n"
            f" Ekspedisi : {data['courier']}\n"
            f" Asal       : {data['origin']}\n"
            f" Tujuan     : {data['destination']}\n"
            f" Transit    : {data['transit']}\n"
            f" Status     : {data['status']}\n"
            f" Estimasi   : {data['eta']}\n\n"
            f"Ada yang bisa dibantu lagi? (Ketik 'selesai' untuk akhiri)"
        )

    def process(self, user_input, current_state):
        intent = self.engine.detect_intent(user_input)
        entities = self.engine.parse_orders(user_input)
        response = ""
        next_state = current_state

        if intent == 'exit':
            return "Terima kasih telah menggunakan layanan Sinar Express! Sampai jumpa.", END

        # ================= AWAL FSM =================
        if current_state == GREETING:
            tracking_code = next((e['value'] for e in entities if e['type'] == 'tracking_code'), None)
            city = next((e['value'] for e in entities if e['type'] == 'city'), None)
            
            if tracking_code:
                if tracking_code in self.mock_database:
                    data = self.mock_database[tracking_code]
                    response = self._format_tracking_response(tracking_code, data)
                else:
                    response = f"Nomor resi {tracking_code} tidak ditemukan di sistem kami.\n\nAda yang bisa dibantu lagi?"
                next_state = SELECT_SERVICE
                
            elif city:
                next_state = f"AWAITING_WEIGHT_{city.lower()}"
                response = f"Tujuan {city.capitalize()} dicatat. Untuk menghitung tarif, masukkan berat paket Anda (dalam Kg, contoh: 2.5):"
                
            elif intent in ['complaint', 'prohibited', 'info_branch', 'pickup']:
                response = self._get_menu_text()
                next_state = SELECT_SERVICE
                
            elif intent == 'greet' or intent == 'unknown':
                response = "Halo! Selamat datang di Sinar Express. Silakan pilih layanan:\n1. Cek Resi\n2. Cek Tarif\n3. Pengaduan (Rusak/Hilang)\n4. Info Agen & Jam Operasional\n5. Daftar Barang Terlarang\n6. Jemput Paket (Pickup)\n(Ketik angka 1-6)"
                next_state = SELECT_SERVICE
            elif intent == 'track':
                response = "Baik, silakan masukkan nomor resi Anda."
                next_state = AWAITING_TRACKING_ID
            elif intent == 'tariff':
                response = "Baik, silakan ketik kota tujuan pengiriman."
                next_state = AWAITING_TARIFF_CITY

        elif current_state == SELECT_SERVICE:
            tracking_code = next((e['value'] for e in entities if e['type'] == 'tracking_code'), None)
            city = next((e['value'] for e in entities if e['type'] == 'city'), None)
            
            if tracking_code:
                if tracking_code in self.mock_database:
                    data = self.mock_database[tracking_code]
                    response = self._format_tracking_response(tracking_code, data)
                else:
                    response = f"Nomor resi {tracking_code} tidak ditemukan.\n\nAda yang bisa dibantu lagi?"
                next_state = SELECT_SERVICE
                
            elif city:
                next_state = f"AWAITING_WEIGHT_{city.lower()}"
                response = f"Tujuan {city.capitalize()} dicatat. Masukkan berat paket Anda (dalam Kg, contoh: 1.5):"

            elif intent == 'complaint' or '3' in user_input:
                response = "Mohon maaf atas ketidaknyamanannya. Silakan ketik keluhan Anda secara singkat beserta NOMOR RESI."
                next_state = AWAITING_COMPLAINT_DETAILS
                
            elif intent == 'info_branch' or '4' in user_input:
                response = "Kantor Pusat Cekk Ajaa: Jl. Plewan No. 1, Semarang.\nJam Operasional: Senin - Sabtu (08.00 - 20.00 WIB).\n\nAda yang bisa dibantu lagi?"
                next_state = SELECT_SERVICE
                
            elif intent == 'prohibited' or '5' in user_input:
                response = "Barang terlarang: Cairan mudah terbakar, Baterai, Uang tunai, Obat-obatan terlarang, Hewan hidup.\n\nAda yang bisa dibantu lagi?"
                next_state = SELECT_SERVICE
                
            elif intent == 'pickup' or '6' in user_input:
                response = "Layanan Jemput Paket tersedia. Silakan ketik alamat lengkap penjemputan Anda."
                next_state = AWAITING_PICKUP_ADDRESS
                
            elif '1' in user_input or intent == 'track':
                response = "Silakan masukkan nomor resi Anda."
                next_state = AWAITING_TRACKING_ID
                
            elif '2' in user_input or intent == 'tariff':
                response = "Silakan ketik kota tujuan Anda (Jawa Tengah)."
                next_state = AWAITING_TARIFF_CITY
                
            else:
                response = "Pilihan tidak valid. Ketik angka 1-6 atau langsung masukkan nomor resi/kota tujuan."
                next_state = SELECT_SERVICE

        elif current_state == AWAITING_TRACKING_ID:
            tracking_code = next((e['value'] for e in entities if e['type'] == 'tracking_code'), None)
            if tracking_code:
                if tracking_code in self.mock_database:
                    data = self.mock_database[tracking_code]
                    response = self._format_tracking_response(tracking_code, data)
                else:
                    prefix = tracking_code[:3]
                    courier_map = {"JNE": "JNE", "JNT": "J&T Express", "SPC": "SiCepat", "TIK": "Tiki", "SPX": "Shopee Express"}
                    courier_name = courier_map.get(prefix, "Tidak Dikenali")
                    response = f"Nomor resi {tracking_code} terdeteksi milik {courier_name}, namun data tidak ditemukan. Coba lagi?"
                next_state = SELECT_SERVICE
            else:
                response = "Nomor resi tidak valid. Format diawali kode ekspedisi (JNE/JNT/SPC/TIKI/SPX). Coba lagi?"
                next_state = AWAITING_TRACKING_ID

        elif current_state == AWAITING_TARIFF_CITY:
            city = next((e['value'] for e in entities if e['type'] == 'city'), None)
            if city:
                next_state = f"AWAITING_WEIGHT_{city.lower()}"
                response = f"Tujuan {city.capitalize()} terdeteksi. Untuk estimasi tarif, masukkan berat paket Anda (dalam Kg, contoh: 2.5):"
            else:
                response = "Maaf, kami hanya melayani ekspedisi area Jawa Tengah. Coba kota lain?"
                next_state = AWAITING_TARIFF_CITY

        elif current_state.startswith("AWAITING_WEIGHT_"):
            city_name = current_state.replace("AWAITING_WEIGHT_", "")
            weight_entity = next((e['value'] for e in entities if e['type'] == 'weight'), None)
            weight_kg = None
            
            if weight_entity:
                weight_num_str = re.search(r'(\d+(?:[.,]\d+)?)', weight_entity)
                if weight_num_str:
                    weight_kg = float(weight_num_str.group(1).replace(',', '.'))
            else:
                num_match = re.search(r'^\d+(?:[.,]\d+)?$', user_input.strip())
                if num_match:
                    weight_kg = float(num_match.group(0).replace(',', '.'))

            if weight_kg and weight_kg > 0:
                base_tariff = 15000
                additional_per_kg = 5000
                rounded_kg = math.ceil(weight_kg) 
                
                if rounded_kg == 1:
                    total_tariff = base_tariff
                else:
                    total_tariff = base_tariff + ( (rounded_kg - 1) * additional_per_kg )
                
                response = f"Estimasi ongkir ke {city_name.capitalize()} untuk berat {weight_kg} Kg (pembulatan {rounded_kg} Kg) adalah Rp {total_tariff:,}.\n\nAda yang bisa dibantu lagi?"
                next_state = SELECT_SERVICE
            else:
                response = "Format berat tidak valid. Mohon masukkan angka dalam Kg (contoh: 1.5 atau 3)."
                next_state = current_state

        elif current_state == AWAITING_COMPLAINT_DETAILS:
            response = "Terima kasih, aduan Anda telah kami catat (Tiket: ADU-20231099). Tim CS akan menghubungi Anda 1x24 jam.\n\nAda yang bisa dibantu lagi?"
            next_state = SELECT_SERVICE

        elif current_state == AWAITING_PICKUP_ADDRESS:
            response = "Terima kasih! Permintaan penjemputan sedang kami proses. Kurir akan menghubungi Anda 1-2 jam ke depan.\n\nAda yang bisa dibantu lagi?"
            next_state = SELECT_SERVICE

        elif current_state == END:
            response = "Sesi berakhir. Ketik 'Halo' untuk memulai kembali."
            next_state = GREETING

        return response, next_state
        
    def _get_menu_text(self):
        return "Silakan pilih layanan:\n1. Cek Resi\n2. Cek Tarif\n3. Pengaduan (Rusak/Hilang)\n4. Info Agen & Jam Operasional\n5. Daftar Barang Terlarang\n6. Jemput Paket (Pickup)\n(Ketik angka 1-6)"
