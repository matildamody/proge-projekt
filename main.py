# töö nimi: "Kuulsuste äraarvamismäng"
# Kadri-Liis Alber, Matilda Manju Mody
# käivitusjuhend: Terminal, installi Pygame'i, kirjuta käsuviibale python3 manin.py

import random, json #aitab lugeda json andmeid
import os, pygame, sys, requests, io
# operatsioonisüsteemid, pygame'i teek (graafika, klaviatuur jne)
# sys aitab Pythoniga suhelda ennast käitava süsteemiga
# requests - teeb veebipäringuid, meil pildid
# io - võimaldab töödelda andmeid otse mälus, ilma et peaks salvestama
from PIL import Image
# PIL - aitab pilte töödelda (avada, salvestada jne)
# andmete avamine
f = open("andmed/nimed.json", "r", encoding="utf-8")
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


def kuva_juhuslik_pilt():
    # valib juhusliku pildi valitd (aktiivsest) kategooriast ja tagastab pildina
    global praegune_fail, praegune_nimi # global - muutujad kasutusel üle kogu programmi
    praegune_fail = random.choice(list(andmed[praegune_kategooria].keys())) # valib juhusliku faili
    praegune_nimi = andmed[praegune_kategooria][praegune_fail] # leiab selle pildi õige nime

    # pildi laadimine internetist, sest meil URL-id 
    try:
        response = requests.get(praegune_fail) # teeb päringu URL-lingile
        image_bytes = io.BytesIO(response.content) # pildibaidid -> "virtuaalne fail" - saab lugeda nagu tavalist faili
        pil_img = Image.open(image_bytes).convert("RGB") # muudab pildi RGB formaati (värvid õiged)
        pil_img = pil_img.resize((400, 400)) # muudab pildi suurust (pikslit)
        pil_img.save("temp.jpg")  # ajutine fail pygame'i jaoks
        pilt = pygame.image.load("temp.jpg") # salvestatud pilt laetakse pygame'i ekraanile
        return pilt 
    except Exception as e: # ebaõnnestumine
        print("Pildi laadimine ebaõnnestus:", e)
        return None

# kategooriate nuppude kuvamine
def joonista_nupud():
    for kat, x, y, w, h in nupud:
        pygame.draw.rect(aken, (70, 130, 180), (x, y, w, h)) # joonistab ristküliku
        tekst = font.render(kat, True, (0, 0, 0)) # kategooria nimi muudetakse tekstiks
        aken.blit(tekst, (x + 10, y + 10)) # joonistab teksti nupu peale

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
                        pilt = kuva_juhuslik_pilt()
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
                    pilt = kuva_juhuslik_pilt()
                elif sündmus.key == pygame.K_BACKSPACE: #kustutab viimase tähe
                    sisend = sisend[:-1]
                else:
                    sisend += sündmus.unicode #sisendisse kirjutatakse kõik klaviatuuril vajutatavad tähed

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
        jäänud = max(0, 120 - (pygame.time.get_ticks() - algusaeg) // 1000) #pygame.time.get_ticks() mitu millisekundit möödunud käivitamisest
        timer_tekst = font.render(f"Aega jäänud: {jäänud}s", True, (0, 0, 0))
        aken.blit(timer_tekst, (550, 50)) #Kollasena aeg

        if jäänud <= 0:
            running = False #mäng läbi, kui aeg läbi

    pygame.display.flip()#näitab asju, mida tsükliga läbisime
    clock.tick(30)

kuva_tulemused()
pygame.quit()
sys.exit()