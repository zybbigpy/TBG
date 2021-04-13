import numpy as np

from itertools import product
from sklearn.neighbors import KDTree

# lattice constant (angstrom)
A_0 = 2.46
A_EDGE = A_0 / np.sqrt(3)

# moire information (angstrom)
D_LAYER = 3.433333333 
D1_LAYER = 0.027777778
D_AB = 3.35 
 
# unit vector for atom system
A_UNITVEC_1 = np.array([np.sqrt(3)*A_0/2, -A_0/2])
A_UNITVEC_2 = np.array([np.sqrt(3)*A_0/2,  A_0/2])

# reciprocal unit vector for atom system
A_G_UNITVEC_1 = np.array([2*np.pi/(3*A_EDGE), -2*np.pi/(np.sqrt(3)*A_EDGE)])
A_G_UNITVEC_2 = np.array([2*np.pi/(3*A_EDGE),  2*np.pi/(np.sqrt(3)*A_EDGE)])

# atom postion in graphene
ATOM_PSTN_1 = np.array([0, 0])
ATOM_PSTN_2 = np.array([2*A_0/np.sqrt(3), 0])


def _set_moire_angle(n_moire:int)->float:
    """
    get the angle by defining the moire number n_moire

    ----------
    Return:
    moire angle in radius
    """
    
    angle_r = np.arcsin(np.sqrt(3)*(2*n_moire+1)/(6*n_moire**2+6*n_moire+2))
    print("nmoire:", n_moire, ", equals angle(degree):", angle_r/np.pi*180)

    return angle_r

def _set_rt_mtrx(theta:float):
    """
    create the rotation matrix

    -----------
    Parameters:

    theta: rotation angle in radius

    --------
    Returns:

    rt_mtrx: numpy array with shape (2, 2)
    """

    rt_mtrx = np.array([[np.cos(theta), -np.sin(theta)],
                        [np.sin(theta), np.cos(theta)]])

    return rt_mtrx


def _set_moire(n_moire:int)->tuple:
    """
    set up the parameters for the moire system

    -------
    Returns:

    parameter tuple

    """

    rt_angle = _set_moire_angle(n_moire)
    rt_mtrx = _set_rt_mtrx(rt_angle)
    rt_mtrx_half = _set_rt_mtrx(rt_angle/2)

    # first `m_` represents for moire
    # moire unit vector
    m_unitvec_1 = (-n_moire*A_UNITVEC_1 + (2*n_moire +1)*A_UNITVEC_2)@rt_mtrx_half.T
    m_unitvec_2 = (-(2*n_moire+1)*A_UNITVEC_1 + (n_moire +1)*A_UNITVEC_2)@rt_mtrx_half.T
    
    # moire reciprocal vector
    m_g_unitvec_1 = A_G_UNITVEC_1@rt_mtrx_half.T - A_G_UNITVEC_1@rt_mtrx_half
    m_g_unitvec_2 = A_G_UNITVEC_2@rt_mtrx_half.T - A_G_UNITVEC_2@rt_mtrx_half
    
    # high symmetry points
    m_gamma_vec = np.array([0, 0])
    m_k1_vec = (m_g_unitvec_1 + m_g_unitvec_2)/3 + m_g_unitvec_2/3
    m_k2_vec = (m_g_unitvec_1 + m_g_unitvec_2)/3 + m_g_unitvec_1/3
    m_m_vec = (m_k1_vec + m_k2_vec)/2

    return (m_unitvec_1,   m_unitvec_2, m_g_unitvec_1, 
            m_g_unitvec_2, m_gamma_vec, m_k1_vec,    
            m_k2_vec,      m_m_vec,     rt_mtrx_half)


def set_atom_pstn_list(n_moire:int)->list:
    """
    find all (A1 B1 A2 B2) atoms in a single moire unit lattice after rotation
    
    ------
    Return:

    atom_pstn_list
    """

    (m_unitvec_1,   m_unitvec_2, m_g_unitvec_1, 
     m_g_unitvec_2, m_gamma_vec, m_k1_vec,    
     m_k2_vec,      m_m_vec,     rt_mtrx_half) =_set_moire(n_moire)
    
    atom_b_pstn = ATOM_PSTN_2 - A_UNITVEC_1
    small_g_vec = np.array([m_g_unitvec_1, m_g_unitvec_2, -m_g_unitvec_1-m_g_unitvec_2])
    
    ly = m_unitvec_1[1]
    n  = int(2*ly/A_0)+2
    
    
    delta = 0.0001

    atom_pstn_list = []
    num_a1 = num_b1 = num_a2 = num_b2 =0

    # find A1 atoms
    for (ix, iy) in product(range(n), range(n)):
        atom_pstn = -ix*A_UNITVEC_1 + iy*A_UNITVEC_2
        atom_pstn= atom_pstn @ rt_mtrx_half.T
        x = atom_pstn.dot(m_g_unitvec_1)/(2*np.pi)
        y = atom_pstn.dot(m_g_unitvec_2)/(2*np.pi)
        if (x>-delta) and (x<(1-delta)) and (y>-delta) and (y<(1-delta)):
            d = 0.5*D_LAYER + D1_LAYER*np.sum(np.cos(np.dot(small_g_vec, atom_pstn)))
            atom = np.array([atom_pstn[0], atom_pstn[1], d])
            atom_pstn_list.append(atom)
            num_a1 += 1

    # find B1 atoms
    for (ix, iy) in product(range(n), range(n)):
        atom_pstn = -ix*A_UNITVEC_1 + iy*A_UNITVEC_2 + atom_b_pstn
        atom_pstn= atom_pstn @ rt_mtrx_half.T
        x = atom_pstn.dot(m_g_unitvec_1)/(2*np.pi)
        y = atom_pstn.dot(m_g_unitvec_2)/(2*np.pi)
        if (x>-delta) and (x<(1-delta)) and (y>-delta) and (y<(1-delta)):
            d = 0.5*D_LAYER + D1_LAYER*np.sum(np.cos(np.dot(small_g_vec, atom_pstn)))
            atom = np.array([atom_pstn[0], atom_pstn[1], d])
            atom_pstn_list.append(atom)
            num_b1 += 1

    # find A2 atoms
    for (ix, iy) in product(range(n), range(n)):
        atom_pstn = -ix*A_UNITVEC_1 + iy*A_UNITVEC_2
        atom_pstn = atom_pstn @ rt_mtrx_half
        x = atom_pstn.dot(m_g_unitvec_1)/(2*np.pi)
        y = atom_pstn.dot(m_g_unitvec_2)/(2*np.pi)
        if (x>-delta) and (x<(1-delta)) and (y>-delta) and (y<(1-delta)):
            d = -0.5*D_LAYER - D1_LAYER*np.sum(np.cos(np.dot(small_g_vec, atom_pstn)))
            atom = np.array([atom_pstn[0], atom_pstn[1], d])
            atom_pstn_list.append(atom)
            num_a2 += 1
            
    # find B2 atoms
    for (ix, iy) in product(range(n), range(n)):
        atom_pstn = -ix*A_UNITVEC_1 + iy*A_UNITVEC_2 + atom_b_pstn
        atom_pstn = atom_pstn @ rt_mtrx_half
        x = atom_pstn.dot(m_g_unitvec_1)/(2*np.pi)
        y = atom_pstn.dot(m_g_unitvec_2)/(2*np.pi)
        if (x>-delta) and (x<(1-delta)) and (y>-delta) and (y<(1-delta)):
            d = -0.5*D_LAYER - D1_LAYER*np.sum(np.cos(np.dot(small_g_vec, atom_pstn)))
            atom = np.array([atom_pstn[0], atom_pstn[1], d])
            atom_pstn_list.append(atom)
            num_b2 += 1

    assert(num_a1 == num_a2 == num_b1 == num_b2)
    
    return atom_pstn_list


def set_atom_neighbour_list(atom_pstn_list:list, m_unitvec_1, m_unitvec_2, distance=2.5113*A_0):
    
    print("num of atoms (code in moire set up):", len(atom_pstn_list))
    num_atoms = len(atom_pstn_list)
    atom_pstn_list = np.array(atom_pstn_list)
    # add information for `d`
    m_unitvec_1 = np.array([m_unitvec_1[0],m_unitvec_1[1], 0])
    m_unitvec_2 = np.array([m_unitvec_2[0],m_unitvec_2[1], 0])

    # 9 times larger than the original primitive lattice for searching nearest neighours
    area1 = atom_pstn_list+m_unitvec_1
    area2 = atom_pstn_list+m_unitvec_2
    area3 = atom_pstn_list-m_unitvec_1
    area4 = atom_pstn_list-m_unitvec_2
    area5 = atom_pstn_list+m_unitvec_1+m_unitvec_2
    area6 = atom_pstn_list+m_unitvec_1-m_unitvec_2
    area7 = atom_pstn_list-m_unitvec_1+m_unitvec_2
    area8 = atom_pstn_list-m_unitvec_1-m_unitvec_2

    enlarge_atom_pstn_list = np.concatenate((atom_pstn_list, area1, area2, area3, area4, area5, area6, area7, area8))

    # kdtree search, only use first 2D information
    x = enlarge_atom_pstn_list[:, :2]
    y = atom_pstn_list[:, :2]
    tree = KDTree(x)
    ind = tree.query_radius(y, r=distance)

    # the kdtree algotithm provided by sklearn will return the index 
    # including itself, the following code will remove them
    all_nns = np.array([np.array([idx for idx in nn_indices if idx != i]) for i, nn_indices in enumerate(ind)], dtype=object)

    return (all_nns, enlarge_atom_pstn_list)


def set_relative_dis_ndarray_new(atom_pstn_list, enlarge_atom_pstn_list, all_nns):
    """
    new realization, based on KDTree algorithm, we can construct neighbour list very fast.
    """
    #print("num of atoms (code in moire set up):", len(atom_pstn_list))
    num_atoms = len(atom_pstn_list)
    atom_pstn_list = np.array(atom_pstn_list)

    # tricky code here
    # construct Ri list
    neighbour_len_list = [subindex.shape[0] for subindex in all_nns]
    atom_pstn_2darray = np.repeat(atom_pstn_list, neighbour_len_list, axis=0) 
    
    # construct Rj near Ri list
    atom_neighbour_2darray = enlarge_atom_pstn_list[np.hstack(all_nns)]
    assert atom_pstn_2darray.shape == atom_neighbour_2darray.shape
    
    ind = all_nns%num_atoms
    # ind = [np.sort(subind) for subind in ind]
    # (row, col) <=> (index_i, index_j)
    row = [iatom for iatom in range(num_atoms) for n in range(ind[iatom].shape[0])]
    col = [jatom for subindex in ind for jatom in subindex]

    assert len(row) == len(col)
    
    dr = (atom_pstn_2darray-atom_neighbour_2darray)[:,:2]
    dd = (atom_pstn_2darray-atom_neighbour_2darray)[:,-1]

    return (dr, dd, row, col)


def set_relative_dis_ndarray(atom_pstn_list:list, atom_neighbour_list:list, m_g_unitvec_1, 
                             m_g_unitvec_2,       m_unitvec_1,              m_unitvec_2)->tuple:
    """
    construct relative distance ndarry

    -------
    Returns:

    (atom_pstn_2darray, atom_neighbour_2darray, row, col)
    """

    # Tricky code here
    # construct Ri list
    neighbour_len_list = [len(sublist) for sublist in atom_neighbour_list]
    atom_pstn_2darray = np.repeat(np.array(atom_pstn_list), neighbour_len_list, axis=0) 
    # construct Rj near Ri list
    atom_neighbour_2darray = np.array([atom_pstn_list[i] for sublist in atom_neighbour_list for i in sublist])
    
    # (row, col) <=> (index_i, index_j)
    row = [iatom for iatom in range(len(atom_pstn_list)) for n in range(len(atom_neighbour_list[iatom]))]
    col = [jatom for sublist in atom_neighbour_list for jatom in sublist]

    dr = (atom_pstn_2darray-atom_neighbour_2darray)[:, :2]
    dd = (atom_pstn_2darray-atom_neighbour_2darray)[:, -1]
    x  = np.dot(dr, m_g_unitvec_1)/(2*np.pi)
    y  = np.dot(dr, m_g_unitvec_2)/(2*np.pi)

    # reconstruct dr (tricky here)
    x = x - np.trunc(2*x)
    y = y - np.trunc(2*y)

    dr = (x.reshape(-1, 1))*m_unitvec_1 + (y.reshape(-1, 1))*m_unitvec_2
    
    return (dr, dd, row, col)


def system_info_log(n_moire:int):

    (m_unitvec_1,   m_unitvec_2, m_g_unitvec_1, 
     m_g_unitvec_2, m_gamma_vec, m_k1_vec,      
     m_k2_vec,      m_m_vec,     rt_mtrx_half) = _set_moire(n_moire)
    
    np.set_printoptions(6)
    print("atom unit vector".ljust(30), ":", A_UNITVEC_1, A_UNITVEC_2)
    print("atom reciprotocal unit vector".ljust(30), ":", A_G_UNITVEC_1, A_G_UNITVEC_2)
    print("moire unit vector".ljust(30), ":", m_unitvec_1, m_unitvec_2)
    print("moire recoprotocal unit vector".ljust(30), ":", m_g_unitvec_1, m_g_unitvec_2)


def save_atom_pstn_list(atom_pstn_list:list, path:str, n_moire:int):
    
    atoms = np.array(atom_pstn_list)
    np.savetxt(path+"atom"+str(n_moire)+".csv", atoms, header="Rx, Ry, d", delimiter=',')


def read_atom_neighbour_list(path:str, n_moire:int)->list:
    """
    aborted, we wont generate neighbour list file any more.
    """

    with open(path+"Nlist"+str(n_moire)+".dat","r") as f:
        print("Open file Nlist...\n")
        lines = f.readlines()
        atom_neighbour_list = []
        for line in lines:
            line_data = line.split()
            data = [int(data_str) for data_str in line_data]
            atom_neighbour_list.append(data)

    return atom_neighbour_list


def read_atom_pstn_list(path:str, n_moire:int)->list:

    atom_pstn_list = np.loadtxt(path+"atom"+str(n_moire)+".csv", delimiter=',', comments='#')

    return list(atom_pstn_list)