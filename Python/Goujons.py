from math import isnan

class Goujon :
    def __init__(self,num):
        self.coordX = []
        self.coordY = []
        self.nbContact = 0
        self.liste_contact = []
        self.contact_avec = []
        self.num = num
        self.zones = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0}
        self.frames_par_zones = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0}
        self.zone_prec = None
        self.nbZones = 1

def get_coord_id(line, ind):
    x = float(line[0 + (3 * (ind))])
    y = float(line[1 + (3 * (ind))])
    return x, y


def parse_file(file_name, nb_poissons, frame_limit=10000):
    with open(file_name, 'r') as traj:
        i = 0
        liste_poisson = []
        for j in range(nb_poissons):
            liste_poisson.append(Goujon(j+1))
        a = traj.readline()
        while a and i < frame_limit:
            line = a.split('\t')
            line[-1] = line[-1][:-1]
            a = traj.readline()
            if i > 0:
                for j in range(nb_poissons):
                    x, y = get_coord_id(line, j)
                    liste_poisson[j].coordX.append(x)
                    liste_poisson[j].coordY.append(y)
            i += 1
    return liste_poisson

def is_in_contact(x0,y0,x1,y1,r):
    dist = ((x0-x1)**2+(y0-y1)**2)**0.5

    return dist < r*2

def get_time_from_frame(num_frame):
    return num_frame/30

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
                if zone_actuelle != liste_poisson[x].zone and zone_actuelle:
                    log.write('poisson {x} change de zone {y} -> {z}\n'.format(x=x+1,y=liste_poisson[x].zone,z=zone_actuelle))
                    liste_poisson[x].zone = zone_actuelle
                    liste_poisson[x].nbZones += 1
                    liste_poisson[x].zones[zone_actuelle] += 1
                for y in range(x+1, len(liste_poisson)):
                    if is_in_contact(liste_poisson[x].coordX[i], liste_poisson[x].coordY[i], liste_poisson[y].coordX[i], liste_poisson[y].coordY[i], 50):
                        liste_poisson[x].liste_contact[i].append(y)
                        liste_poisson[y].liste_contact[i].append(x)
                        log.write('Contact {x} , {y}\n'.format(x=x + 1, y=y + 1))
        with open('result.txt', 'w') as result:
            log.seek(0)
            log.write('\n\n')
            for poisson in liste_poisson :
                contacts = []
                poisson.contact_avec = []
                for i in range (len(liste_poisson)):
                    poisson.contact_avec.append(0)
                for i in range(10):
                    contacts.append(poisson.liste_contact[i])
                for i in range(10,len(poisson.liste_contact)):
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
                result.write('-> poisson {x} ({y} contacts, {z} crossings) :\n'.format(x=poisson.num,y=poisson.nbContact,z=poisson.nbZones))
                result.write('\tCONTACTS :\n')
                for k in range(len(liste_poisson)):
                    if k+1 != poisson.num:
                        result.write('\t\t-poisson {x} : {y}\n'.format(x=k+1,y=poisson.contact_avec[k]))
                result.write('\n\tCROSSINGS :\n')
                for i in range(2):
                    for j in range(3):
                        result.write('\t\t-zone {x} : {y} passages, {z} sec à l\'interieur\n'.format(x=zones[j][i],y=poisson.zones[zones[j][i]],z=round(get_time_from_frame(poisson.frames_par_zones[zones[j][i]]),2)))
                result.write('\n')

def get_zone(x,y):
    if isnan(x) or isnan(y):
        return None
    return zones[int((x/1920)*3)][int((y/1080)*2)]

zones = [['A','D'],['B','E'],['C','F']]
process(parse_file('trajectories.txt', 5))
