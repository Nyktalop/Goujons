from math import isnan
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import tkinter as tk

class Goujon :
    def __init__(self,num):
        self.coordX = []
        self.coordY = []
        self.coordZ = []
        self.nbContact = 0
        self.liste_contact = []
        self.contact_avec = []
        self.num = num
        self.zones = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0}
        self.frames_par_zones = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0}
        self.nage_dans_zones = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0}
        self.frames_nage = 0
        self.zone_prec = None
        self.somme_distance = 0
        self.nbZones = 1



#Inter principale
FICHIER_RESULT = 'result.txt'
NOMBRE_POISSON = 5
FPS = 30
DIM_X_PIX = 1920
DIM_Y_PIX = 1080
DIM_X_CM = 75
DIM_Y_CM = 50

def pix_to_cm(x):
    return x*(DIM_Y_CM/DIM_Y_PIX)

def cm_to_pix(x):
    return x*(DIM_Y_PIX/DIM_Y_CM)

#Tweaks
FRAMES_NAGE = 5  # nb de frames pour la nage
DIST_NAGE = cm_to_pix(0.5)  # distance (en pixels) parcourue en FRAMES_NAGE frames pour etre considere en nage
RAYON_CONTACT = cm_to_pix(2.4)  # rayon du cercle dans lequel un poisson doit etre pour etre en contact vec un autre
FRAMES_CONTACT = 10  # duree en frame durant laquelle des poissons doivent etre separes pour que un contact soit nouveau

zones = [['A','D'],['B','E'],['C','F']]

def get_coord_id(line, ind):
    x = float(line[0 + (3 * (ind))])
    y = float(line[1 + (3 * (ind))])
    return x, y


def parse_file(file_name):
    with open(file_name, 'r') as traj:
        i = 0
        liste_poisson = []
        for j in range(NOMBRE_POISSON):
            liste_poisson.append(Goujon(j+1))
        a = traj.readline()
        while a:
            line = a.split('\t')
            line[-1] = line[-1][:-1]
            a = traj.readline()
            if i > 0:
                for j in range(NOMBRE_POISSON):
                    x, y = get_coord_id(line, j)
                    liste_poisson[j].coordX.append(x)
                    liste_poisson[j].coordY.append(y)
                    liste_poisson[j].coordZ.append(i)
            i += 1
    return liste_poisson

def calc_dist(x0,y0,x1,y1):
    return ((x0-x1)**2+(y0-y1)**2)**0.5

def is_in_contact(x0,y0,x1,y1,r):
    dist = calc_dist(x0,y0,x1,y1)

    return dist < r*2

def get_time_from_frame(num_frame):
    return num_frame/FPS

def process(liste_poisson):
    with open('log.txt', 'w') as log:
        for poisson in liste_poisson :
            poisson.zone = get_zone(poisson.coordX[0], poisson.coordY[0])
            poisson.zones[poisson.zone] += 1
            poisson.frames_par_zones[poisson.zone] += 1
        for i in range(len(liste_poisson[0].coordX)):
            for poisson in liste_poisson :
                poisson.liste_contact.append([])
            log.write('\n\t{x} secondes\t\n'.format(x=round(get_time_from_frame(i), 2)))
            for x in range(len(liste_poisson)):
                zone_actuelle = get_zone(liste_poisson[x].coordX[i],liste_poisson[x].coordY[i])
                if zone_actuelle:
                    liste_poisson[x].frames_par_zones[zone_actuelle] += 1
                    if i > FRAMES_NAGE-1:
                        diff = calc_dist(liste_poisson[x].coordX[i-FRAMES_NAGE],liste_poisson[x].coordY[i-FRAMES_NAGE],liste_poisson[x].coordX[i],liste_poisson[x].coordY[i])
                        if diff > DIST_NAGE :
                            liste_poisson[x].nage_dans_zones[zone_actuelle] += 1
                            liste_poisson[x].frames_nage += 1
                if zone_actuelle != liste_poisson[x].zone and zone_actuelle:
                    log.write('poisson {x} change de zone {y} -> {z}\n'.format(x=x+1,y=liste_poisson[x].zone,z=zone_actuelle))
                    liste_poisson[x].zone = zone_actuelle
                    liste_poisson[x].nbZones += 1
                    liste_poisson[x].zones[zone_actuelle] += 1

                distances = []
                for l in range(len(liste_poisson)):
                    if l != x:
                        distances.append(calc_dist(liste_poisson[x].coordX[i], liste_poisson[x].coordY[i], liste_poisson[l].coordX[i], liste_poisson[l].coordY[i]))
                dist_min = min(distances)
                if not isnan(dist_min):
                    liste_poisson[x].somme_distance += dist_min

                for y in range(x+1, len(liste_poisson)):
                    if is_in_contact(liste_poisson[x].coordX[i], liste_poisson[x].coordY[i], liste_poisson[y].coordX[i], liste_poisson[y].coordY[i], RAYON_CONTACT):
                        liste_poisson[x].liste_contact[i].append(y)
                        liste_poisson[y].liste_contact[i].append(x)
                        log.write('Contact {x} , {y}\n'.format(x=x + 1, y=y + 1))

        with open(FICHIER_RESULT, 'w') as result:
            log.seek(0)
            log.write('\n\n')
            for poisson in liste_poisson :
                contacts = []
                poisson.contact_avec = []
                for i in range (len(liste_poisson)):
                    poisson.contact_avec.append(0)
                for i in range(FRAMES_CONTACT):
                    contacts.append(poisson.liste_contact[i])
                for i in range(FRAMES_CONTACT,len(poisson.liste_contact)):
                    for p in contacts[-1]:
                        premier_contact = True
                        j = 0
                        while premier_contact and j < len(contacts)-1:
                            premier_contact = p not in contacts[j]
                            j += 1
                        if premier_contact :
                            log.write('poisson {x} entre en contact avec {y} a {z} sec\n'.format(x=poisson.num,y=p+1,z=get_time_from_frame(i)))
                            poisson.nbContact += 1
                            poisson.contact_avec[p] += 1
                    contacts.append(poisson.liste_contact[i])
                    contacts = contacts[1:]
                log.write('\n\n')
                result.write('-> poisson {x} ({y} contacts, {z} crossings, ANND : {w} cm, {k}% a nager ({o}/{p} sec) :\n'.format(x=poisson.num,
                                                                                                                                 y=poisson.nbContact,
                                                                                                                                 z=poisson.nbZones,
                                                                                                                                 w=round(pix_to_cm(poisson.somme_distance/len(poisson.coordX)),3),
                                                                                                                                 k = round((poisson.frames_nage / len(poisson.coordX))*100, 2),
                                                                                                                                 o = round(get_time_from_frame(poisson.frames_nage),2),
                                                                                                                                 p = round((get_time_from_frame(len(poisson.coordX))),2)))
                result.write('\tCONTACTS :\n')
                for k in range(len(liste_poisson)):
                    if k+1 != poisson.num:
                        result.write('\t\t-poisson {x} : {y}\n'.format(x=k+1,y=poisson.contact_avec[k]))
                result.write('\n\tZONES :\n')
                for i in range(2):
                    for j in range(3):
                        result.write('\t\t-zone {x} : {y} passages, {z} sec à l\'interieur, dont {w} sec a nager\n'.format(x=zones[j][i],y=poisson.zones[zones[j][i]],z=round(get_time_from_frame(poisson.frames_par_zones[zones[j][i]]),2),w=round(get_time_from_frame(poisson.nage_dans_zones[zones[j][i]]),2)))
                result.write('\n')

def get_zone(x,y):
    if isnan(x) or isnan(y):
        return None
    return zones[int((x/DIM_X_PIX)*3)][int((y/DIM_Y_PIX)*2)]

def show_plt(liste_poisson, aff='3d'):

    if aff == '3d':
        plt.axes(projection='3d')
        for poisson in liste_poisson:
            plt.plot(poisson.coordX,poisson.coordY,poisson.coordZ,label='Poisson {x}'.format(x=poisson.num))
    else:
        for poisson in liste_poisson:
            plt.plot(poisson.coordX,poisson.coordY,label='Poisson {x}'.format(x=poisson.num))

    plt.gca().invert_yaxis()
    plt.legend()
    plt.show()

def validate_entry_int(text):
    try :
        float(text)
        return True
    except :
        return len(text) == 0

def maj_param():
    global NOMBRE_POISSON, FPS, DIM_X_PIX, DIM_Y_PIX, DIM_X_CM, DIM_Y_CM, FICHIER_RESULT
    global FRAMES_NAGE, DIST_NAGE, RAYON_CONTACT, FRAMES_CONTACT

    NOMBRE_POISSON = int(nb_poisson_spinbox.get())
    FICHIER_RESULT = file_result_entry.get()
    FPS = int(entry_fps.get())
    DIM_X_PIX = int(entry_x_pix.get())
    DIM_Y_PIX = int(entry_y_pix.get())
    DIM_X_CM = int(entry_x_cm.get())
    DIM_Y_CM = int(entry_y_cm.get())
    print(NOMBRE_POISSON, FPS, DIM_X_PIX, DIM_Y_PIX, DIM_X_CM, DIM_Y_CM)

    FRAMES_NAGE = int(entry_frames_nage.get())
    DIST_NAGE = int(cm_to_pix(float(entry_dist_nage.get())))
    RAYON_CONTACT = int(cm_to_pix(float(entry_rayon_contact.get())))
    FRAMES_CONTACT = int(entry_frames_contact.get())
    print(FRAMES_NAGE,DIST_NAGE,FRAMES_CONTACT,RAYON_CONTACT)

def graphe(file_name, mode):
    maj_param()
    liste_poisson = parse_file(file_name)
    show_plt(liste_poisson, mode)

def gen_res(file_name):
    maj_param()
    liste_poisson = parse_file(file_name)
    process(liste_poisson)
    afficher_contenu()

def afficher_contenu():
    with open(FICHIER_RESULT,'r') as fich :
        a = fich.read()
    top = tk.Toplevel()
    top.title(FICHIER_RESULT)
    top.geometry('600x600')
    top.resizable(False,False)

    scb = tk.Scrollbar(top)
    scb.pack(side=tk.RIGHT,fill=tk.Y)


    msg = tk.Text(top,font=("Helvetica",9),padx=10,height=40,yscrollcommand=scb.set)
    msg.insert(tk.INSERT,a)
    msg.pack()

    scb.config(command=msg.yview)
    msg.config(state=tk.DISABLED)




fen = tk.Tk()
fen.geometry('500x500')
fen.title('Projet Goujons')
fen.resizable(False,False)
valid_command = fen.register(validate_entry_int)

C = tk.Canvas(fen,width=502,height=502)
C.place(x=-1,y=-1)

C.create_rectangle(2,100,499,180)
tk.Label(C,text='Parametres Generaux :',font=('',10)).place(x=8,y=102)
C.create_rectangle(2,180,200,280)
tk.Label(C,text='Parametres Graphiques:',font=('',10)).place(x=8,y=182)
C.create_rectangle(200,180,499,280)
tk.Label(C,text='Parametres Video:',font=('',10)).place(x=205,y=182)
C.create_rectangle(80,280,420,400)
tk.Label(C,text='Parametres de Detection:',font=('',10)).place(x=88,y=282)


mode = tk.StringVar()

tk.Label(fen, text='Projet Goujons', font=('Impact', 25)).place(x=250, y=40, anchor='center')
tk.Label(fen, text='Francois Gaits, Axel Ipsum, Cyprian Kauffman, Guillaume Nibert', font=('',7)).place(x=250,y=80,anchor='center')

tk.Label(fen, text='Nom du fichier IdTracker:').place(x=30, y=128)
file_name_entry = tk.Entry(fen, width=17)
file_name_entry.insert(0, 'trajectories.txt')
file_name_entry.place(x=52, y=150)

tk.Label(fen, text='Nom du fichier resultat:').place(x=195, y=128)
file_result_entry = tk.Entry(fen, width=17)
file_result_entry.insert(0, str(FICHIER_RESULT))
file_result_entry.place(x=210, y=150)


tk.Label(fen, text='Nombre de poissons :').place(x=358, y=128)
nb_poisson_spinbox = tk.Spinbox(fen, from_=1, to_=10, width=2)
nb_poisson_spinbox.place(x=390, y=150)
for i in range(NOMBRE_POISSON-1):
    nb_poisson_spinbox.invoke(element='buttonup')

tk.Label(fen, text='Mode :').place(x=78, y=208)
b1 = tk.Radiobutton(fen, text='2D', variable=mode, value='2d')
b1.place(x=90, y=225)
b2 = tk.Radiobutton(fen, text='3D', variable=mode, value='3d')
b2.place(x=90, y=245)
b1.select()
b2.deselect()

tk.Label(fen,text='X :',font=('',11)).place(x=220,y=205)
tk.Label(fen,text='Cm :').place(x=220,y=227)
tk.Label(fen,text='Pix  :').place(x=220,y=250)
entry_x_cm = tk.Entry(fen,width=8,validate='key',vcmd=(valid_command, '%P'))
entry_x_cm.place(x=250,y=227)
entry_x_pix = tk.Entry(fen,width=8,validate='key',vcmd=(valid_command, '%P'))
entry_x_pix.place(x=250,y=250)
entry_x_cm.insert(0,str(DIM_X_CM))
entry_x_pix.insert(0,str(DIM_X_PIX))

tk.Label(fen,text='Y :',font=('',11)).place(x=310,y=205)
tk.Label(fen,text='Cm :').place(x=310,y=227)
tk.Label(fen,text='Pix  :').place(x=310,y=250)
entry_y_cm = tk.Entry(fen,width=8,validate='key',vcmd=(valid_command, '%P'))
entry_y_cm.place(x=340,y=227)
entry_y_pix = tk.Entry(fen,width=8,validate='key',vcmd=(valid_command, '%P'))
entry_y_pix.place(x=340,y=250)
entry_y_cm.insert(0,str(DIM_Y_CM))
entry_y_pix.insert(0,str(DIM_Y_PIX))

tk.Label(fen,text='Fps :').place(x=400,y=227)
entry_fps = tk.Entry(fen,width=5,validate='key',vcmd=(valid_command, '%P'))
entry_fps.place(x=430,y=227)
entry_fps.insert(0,str(FPS))

tk.Label(fen,text='Frames nage :').place(x=98,y=325)
tk.Label(fen,text='frames',font=('',7)).place(x=213,y=331)
entry_frames_nage = tk.Entry(fen,width=5,validate='key',vcmd=(valid_command, '%P'))
entry_frames_nage.place(x=180,y=328)
entry_frames_nage.insert(0,str(FRAMES_NAGE))

tk.Label(fen,text='Distance nage :').place(x=88,y=355)
tk.Label(fen,text='cm',font=('',7)).place(x=213,y=361)
entry_dist_nage = tk.Entry(fen,width=5,validate='key',vcmd=(valid_command, '%P'))
entry_dist_nage.place(x=180,y=358)
entry_dist_nage.insert(0,str(pix_to_cm(DIST_NAGE)))

tk.Label(fen,text='Rayon contact :').place(x=258,y=355)
tk.Label(fen,text='cm',font=('',7)).place(x=383,y=361)
entry_rayon_contact = tk.Entry(fen,width=5,validate='key',vcmd=(valid_command, '%P'))
entry_rayon_contact.place(x=350,y=358)
entry_rayon_contact.insert(0,str(pix_to_cm(RAYON_CONTACT)))

tk.Label(fen,text='Frames contact :').place(x=258,y=325)
tk.Label(fen,text='frames',font=('',7)).place(x=383,y=331)
entry_frames_contact = tk.Entry(fen,width=5,validate='key',vcmd=(valid_command, '%P'))
entry_frames_contact.place(x=350,y=328)
entry_frames_contact.insert(0,str(FRAMES_CONTACT))



b_graphique = tk.Button(fen, width=15, text='Generer Graphique',
            command=lambda: graphe(file_name_entry.get(), mode.get()))
b_graphique.place(x=120, y=450, anchor='center')

b_res = tk.Button(fen, width=15,text='Afficher resultats',command=afficher_contenu)
b_res.place(x=380,y=450,anchor='center')

b_process = tk.Button(fen, width=15, text='Generer Resultats',command=lambda: gen_res(file_name_entry.get()))
b_process.place(x=250,y=450,anchor='center')
fen.mainloop()


#process(parse_file('trajectories.txt'))
