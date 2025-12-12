# töö nimi: "Kuulsuste äraarvamismäng"
# Kadri-Liis Alber, Matilda Manju Mody
# käivitusjuhend: Terminal, installi Pygame'i, kirjuta käsuviibale python3 main.py

import random, json #aitab lugeda json andmeid
import os, pygame, sys, requests, io
# operatsioonisüsteemid, pygame'i teek (graafika, klaviatuur jne)
# sys aitab Pythoniga suhelda ennast käitava süsteemiga
# requests - teeb veebipäringuid, meil pildid
# io - võimaldab töödelda andmeid otse mälus, ilma et peaks salvestama
from PIL import Image
# PIL - aitab pilte töödelda (avada, salvestada jne)
# andmete avamine
f = open("nimed.json", "r", encoding="utf-8")
andmed = json.load(f)
f.close()

# muutujad
kategooriad = list(andmed.keys())
praegune_fail = None
praegune_kategooria = None
praegune_nimi = None
õige_vastus = 0
vale_vastus = 0
sisend = "" # mangija vastus
algusaeg = None
mangu_algus = False
running = True

# pygame algus
pygame.init() # kaivitab pygame'i moodulid 
aken = pygame.display.set_mode((800, 600)) # loob mänguakna, suurus
pygame.display.set_caption("Eesti kuulsuste äraarvamismäng") # akna pealkiri, ülemisel ribal
font = pygame.font.SysFont("Arial", 30) # teksti font
väike_font = pygame.font.SysFont("Arial", 20) # teksti 2.font
clock = pygame.time.Clock() # hoiab mängu kiirust ühtlasena

# kategooriate nupud
nupud = []
for i, kat in enumerate(kategooriad):
# võtab andmetest kategooriad, enumerate - nupude järjestus üksteise alla
    x = 50
    y = 100 + i * 60 # nuppudel 60 pikslit vahet
    w = 200
    h = 50
    nupud.append((kat, x, y, w, h))
pildid_järjendis = []  # kategooria pildid juhuslikus järjekorras
pildi_indeks = 0
pildid_mälus = {}
def laadi_pildid(kategooria):
    global pildid_mälus
    pildid_mälus[kategooria] = [] #salvestab kõik selle kategooria pildid
    for fail in andmed[kategooria].keys():
        try:
            response = requests.get(fail)#laeb pilte alla internetist
            image_bytes = io.BytesIO(response.content)
            pil_img = Image.open(image_bytes).convert("RGB")
            pil_img = pil_img.resize((400, 400))
            mode = pil_img.mode
            size = pil_img.size
            data = pil_img.tobytes()
            pilt = pygame.image.fromstring(data, size, mode)
            pildid_mälus[kategooria].append(pilt)#pilte ei pea uuesti internetist laadima, vahetuvad kiiremini
        except Exception as e:
            print("Pildi laadimine ebaõnnestus:", e)

# Funktsioon mängu alustamiseks, segab pildid ja alustab indeksiga 0
def alusta_mangu(kategooria):
    global pildid_järjendis, pildi_indeks
    if kategooria not in pildid_mälus: #kontrollib, kas pildid mälus olemas
        laadi_pildid(kategooria)
    pildid_järjendis = list(range(len(pildid_mälus[kategooria])))#loob indeksite järjendi, piltide arvu järgi
    random.shuffle(pildid_järjendis)#piltide indeksid suvalises järjekorras
    pildi_indeks = 0


def kuva_järgmine_pilt():
    global praegune_fail, praegune_nimi, pildi_indeks
    if pildi_indeks >= len(pildid_järjendis):
        return None  # kõik pildid näidatud, mäng läbi
    indeks = pildid_järjendis[pildi_indeks]
    praegune_fail = list(andmed[praegune_kategooria].keys())[indeks]#salvestab url-i, et vastust kontrollida 
    praegune_nimi = andmed[praegune_kategooria][praegune_fail]#salvestab õige nime
    pilt = pildid_mälus[praegune_kategooria][indeks]#võtab mälust pildi ja kuvab
    pildi_indeks += 1 # et järgmine kord tuleks uus pilt
    return pilt

# kategooriate nuppude kuvamine
def joonista_nupud():
    for kat, x, y, w, h in nupud:
        pygame.draw.rect(aken, (70, 130, 180), (x, y, w, h)) # joonistab ristküliku
        tekst = font.render(kat, True, (0, 0, 0)) # kategooria nimi muudetakse tekstiks
        aken.blit(tekst, (x + 10, y + 10)) # joonistab teksti nupu peale
def kuva_tulemused():
    aken.fill((0, 0, 0))
    õige_tekst = font.render(f"Õigeid vastuseid: {õige_vastus}", True, (0, 255, 0))
    vale_tekst = font.render(f"Valesid vastuseid: {vale_vastus}", True, (255, 0, 0))
    aken.blit(õige_tekst, (200, 200))
    aken.blit(vale_tekst, (200, 300))
    pygame.display.flip()
    pygame.time.wait(10000)  # näitab 10 sekundit
# põhitsükkel
pilt = None
while running:
    aken.fill((255, 255, 255)) # ekraan mustaks
    sündmused = pygame.event.get() #salvestab tegevused järjendisse

    for sündmus in sündmused:
        if sündmus.type == pygame.QUIT: #mängu sulgemine
            running = False

        if not mangu_algus:# kontrollib et mäng pole alanud, valid kategooriat
            if sündmus.type == pygame.MOUSEBUTTONDOWN: #kategooria valimine
                mx, my = sündmus.pos #salvestab hiirekliki koordinaadid
                for kat, x, y, w, h in nupud: #käib läbi kõikide kategooriat nupud
                    if x <= mx <= x + w and y <= my <= y + h: #hiirekloikk nupu sees
                        praegune_kategooria = kat #salvestab kategooria
                        alusta_mangu(kat) 
                        pilt = kuva_järgmine_pilt()
                        algusaeg = pygame.time.get_ticks() #salvestab mängu algusaja
                        mangu_algus = True #mäng algas
                        break #ülejäänud nuppe ei kontrolli
        else: #kui mäng on alanud
            if sündmus.type == pygame.KEYDOWN: #kas mõängija vajutas mingit klahvi
                if sündmus.key == pygame.K_RETURN: #kui vajutati enter, siis vaatab vastuse üle
                    if sisend.lower().strip() == praegune_nimi.lower():
                        õige_vastus += 1
                    else:
                        vale_vastus += 1
                    sisend = "" #kustutab eelmise vastuse, et saaks tulla uus pilt
                    pilt = kuva_järgmine_pilt()
                elif sündmus.key == pygame.K_BACKSPACE: #kustutab viimase tähe
                    sisend = sisend[:-1]
                elif sündmus.unicode.isprintable():
                    sisend += sündmus.unicode #sisendisse kirjutatakse kõik klaviatuuril vajutatavad tähed

            elif sündmus.type == pygame.MOUSEBUTTONDOWN:
                # liigu järgmisele pildile hiireklikkides
                pilt = kuva_järgmine_pilt()
                sisend = ""

            if pilt is None:
                running = False  # kõik pildid näidatud
 

    # kuvamine
    if not mangu_algus:
        pealkiri = font.render("Vali kategooria:", True, (0, 0, 0)) #teeb pildi, et pygame saaks kuvada ekraanile
        aken.blit(pealkiri, (50, 50)) #tektsi koordinaadid
        joonista_nupud()
    else: #mäng alanud
        if pilt:
            aken.blit(pilt, (200, 100)) #pildi koordinaadid
        juhis = font.render("Kirjuta kuulsuse nimi ja vajuta Enter:", True, (255, 255, 255)) #käsk pildina ekraanil
        aken.blit(juhis, (50, 50)) #koordinaadid
        sisend_tekst = font.render(sisend, True, (0, 0, 0)) #pildina mängija sisend
        aken.blit(sisend_tekst, (50, 550)) #koordinaadid

        # timer
        jäänud = max(0, 90 - (pygame.time.get_ticks() - algusaeg) // 1000) #pygame.time.get_ticks() mitu millisekundit möödunud käivitamisest
        timer_tekst = font.render(f"Aega jäänud: {jäänud}s", True, (0, 0, 0))
        aken.blit(timer_tekst, (550, 50)) #Kollasena aeg

        if jäänud <= 0:
            running = False #mäng läbi, kui aeg läbi

    pygame.display.flip()#näitab asju, mida tsükliga läbisime
    clock.tick(30)


kuva_tulemused()
pygame.quit()
sys.exit()
