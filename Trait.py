import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import tkinter as tk


def get_coord_id(line, ind):
    x = float(line[0 + (3 * (ind - 1))])
    y = float(line[1 + (3 * (ind - 1))])
    return x, y


def parse_file(file_name, nb_poissons, frame_limit=0, aff='2d'):
    with open(file_name, 'r') as traj:
        i = 0
        coord = []
        for j in range(nb_poissons):
            if aff == '2d':
                coord.append([[], []])
            else:
                coord.append([[], [], []])
        a = traj.readline()
        while a and i < frame_limit:
            line = a.split('\t')
            line[-1] = line[-1][:-1]
            a = traj.readline()
            if i > 0:
                for j in range(1, nb_poissons):
                    x, y = get_coord_id(line, j)
                    coord[j - 1][0].append(x)
                    coord[j - 1][1].append(y)
                    if aff == '3d':
                        coord[j - 1][2].append(i)
            i += 1
    return coord


def show_plt(coord, nb_poissons, aff='2d'):
    if aff == '3d':
        plt.axes(projection='3d')
        for k in range(1, nb_poissons):
            plt.plot(coord[k - 1][0], coord[k - 1][1], coord[k - 1][2])
    else:
        for k in range(1, nb_poissons):
            plt.plot(coord[k - 1][0], coord[k - 1][1])

    plt.show()


def graph(file_name, nb_poissons, nb_frames, mode):
    coord = parse_file(file_name, nb_poissons, nb_frames, mode)
    show_plt(coord, nb_poissons, mode)


def main():
    fen = tk.Tk()
    fen.geometry('500x300')
    fen.title('Projet Goujons')

    mode = tk.StringVar()

    tk.Label(fen, text='Projet Goujons', font=('Impact', 25)).place(x=150, y=20)

    tk.Label(fen, text='Nom du fichier :').place(x=28, y=128)
    file_name_entry = tk.Entry(fen, width=17)
    file_name_entry.insert(0, 'trajectories.txt')
    file_name_entry.place(x=30, y=150)

    tk.Label(fen, text='Frames limtes :').place(x=378, y=128)
    nb_frames_spinbox = tk.Spinbox(fen, from_=1000, to_=20000, width=5, increment=1000)
    nb_frames_spinbox.place(x=390, y=150)
    for i in range(5):  # MIGOTO DESU
        nb_frames_spinbox.invoke(element='buttonup')

    tk.Label(fen, text='Nombre de poissons :').place(x=238, y=128)
    nb_poisson_spinbox = tk.Spinbox(fen, from_=1, to_=10, width=2)
    nb_poisson_spinbox.place(x=270, y=150)
    for i in range(4):  # MIGOTO DESU
        nb_poisson_spinbox.invoke(element='buttonup')

    tk.Label(fen, text='Mode :').place(x=163, y=128)
    b1 = tk.Radiobutton(fen, text='2D', variable=mode, value='2d')
    b1.place(x=180, y=145)
    b2 = tk.Radiobutton(fen, text='3D', variable=mode, value='3d')
    b2.place(x=180, y=165)
    b1.select()
    b2.deselect()

    b = tk.Button(fen, width=15, text='Generer Graphique',
                  command=lambda: graph(file_name_entry.get(), int(nb_poisson_spinbox.get()) + 1,
                                        int(nb_frames_spinbox.get()) + 1, mode.get()))
    b.place(x=250, y=260, anchor='center')
    fen.mainloop()


if __name__ == '__main__':
    main()
