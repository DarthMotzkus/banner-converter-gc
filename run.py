import os
import struct
from PIL import Image

def convert_to_gcrebuilder_bmp(input_path, output_path):
    try:
        # 1. Abre a imagem e força o modo RGBA
        img = Image.open(input_path).convert("RGBA")
    except Exception as e:
        print(f"[-] Erro ao abrir {os.path.basename(input_path)}: {e}")
        return False

    # 2. Força o tamanho padrão de banner do GameCube
    WIDTH, HEIGHT = 96, 32
    if img.size != (WIDTH, HEIGHT):
        img = img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

    # 3. Lê os componentes dos pixels
    pixels = list(img.getdata())
    pixel_bytes = bytearray()

    # BMP lê as linhas de baixo para cima
    for y in reversed(range(HEIGHT)):
        for x in range(WIDTH):
            r, g, b, a = pixels[y * WIDTH + x]
            
            # Converte canais de 8-bit para 5-bit (R5 G5 B5)
            r5 = (r >> 3) & 0x1F
            g5 = (g >> 3) & 0x1F
            b5 = (b >> 3) & 0x1F

            # IMPORTANTE: NÃO setar o bit de alpha (bit15) -> mantém em 0.
            # O GCRebuilder tem "ignoreBannerAlpha" fixo em TRUE e, no import, faz
            # (byte_baixo | 0x8000) + (byte_alto << 8). Se o bit15 já vier 1, a soma
            # estoura o bit 16 e ZERA o bit15 -> o pixel é lido como A3R4G4B4 = ruído.
            # Com bit15=0, o próprio GCRebuilder força o opaco (bit15=1) corretamente.
            packed_pixel = (r5 << 10) | (g5 << 5) | b5
            pixel_bytes.extend(struct.pack("<H", packed_pixel))

    # 4. Cabeçalho BMP no formato EXATO que o GCRebuilder aceita.
    #    NÃO é o header V3 com BI_BITFIELDS. O GCRebuilder exige o
    #    BITMAPINFOHEADER clássico de 40 bytes, com biCompression = 0 (BI_RGB)
    #    e SEM máscaras de cor. Em BI_RGB, 16bpp já significa X1R5G5B5, que o
    #    GCRebuilder lê como A1 R5 G5 B5 (o bit mais alto = alpha).
    #    Header de referência exportado pelo próprio GCRebuilder:
    #    42 4d 36 18 00 00 00 00 00 00 36 00 00 00 28 00 00 00 60 00 ...
    pixel_data_size = len(pixel_bytes)
    header_size = 14
    info_size = 40
    pixel_offset = header_size + info_size          # 54 (0x36)
    total_file_size = pixel_offset + pixel_data_size

    bmp_file_header = struct.pack(
        "<2sIHHI", b'BM', total_file_size, 0, 0, pixel_offset
    )

    bmp_info_header = struct.pack(
        "<IiiHHIIiiII",
        info_size,   # biSize = 40 (BITMAPINFOHEADER)
        WIDTH,       # biWidth = 96
        HEIGHT,      # biHeight = 32
        1,           # biPlanes = 1
        16,          # biBitCount = 16
        0,           # biCompression = 0 (BI_RGB)  <-- NÃO use 3 (BITFIELDS)
        0,           # biSizeImage (0 é válido para BI_RGB)
        0, 0,        # biX/YPelsPerMeter
        0, 0         # biClrUsed / biClrImportant
    )

    # 5. Salva o arquivo final na pasta de destino
    with open(output_path, "wb") as f:
        f.write(bmp_file_header)
        f.write(bmp_info_header)
        f.write(pixel_bytes)
        
    return True

def main():
    # Define o diretório atual onde o script está rodando
    current_dir = os.path.dirname(os.path.abspath(__file__)) if __file__ else os.getcwd()
    output_dir = os.path.join(current_dir, "output")

    # Cria a pasta output se ela não existir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("[*] Pasta 'output' criada com sucesso.")

    # Extensões de imagem permitidas
    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp')
    
    # Lista arquivos no diretório atual
    files = os.listdir(current_dir)
    converted_count = 0

    print("[*] Iniciando a varredura de imagens...")
    
    for filename in files:
        # Pula arquivos que não sejam imagens suportadas
        if not filename.lower().endswith(valid_extensions):
            continue
            
        input_path = os.path.join(current_dir, filename)
        
        # Define o nome de saída mantendo o nome original, mudando apenas para .bmp
        name_without_ext = os.path.splitext(filename)[0]
        output_filename = f"{name_without_ext}.bmp"
        output_path = os.path.join(output_dir, output_filename)

        print(f" -> Convertendo: {filename}...")
        if convert_to_gcrebuilder_bmp(input_path, output_path):
            converted_count += 1

    print(f"\n[+] Concluído! Total de {converted_count} imagens processadas salvas em 'output'.")

if __name__ == "__main__":
    main()
