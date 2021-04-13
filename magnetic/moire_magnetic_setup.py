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
    get the angle by defining the moire number `n_moire`

    ----------
    Return:

    moire angle in radius
    """
    return np.arcsin(np.sqrt(3)*(2*n_moire+1)/(6*n_moire**2+6*n_moire+2))


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


def _set_moire_magnetic(n_moire:int, q:int)->tuple:
    """ 
    set up magnetic moire information 

    -------
    Returns:

    a tuple: Magnetic Moire information 
    """
    
    rt_angle = _set_moire_angle(n_moire)
    rt_mtrx_half = _set_rt_mtrx(rt_angle/2)

    # first `m_` represents for moire
    # moire unit vector
    m_unitvec_1 = (-n_moire*A_UNITVEC_1 + (2*n_moire +1)*A_UNITVEC_2)@rt_mtrx_half.T
    m_unitvec_2 = (-(2*n_moire+1)*A_UNITVEC_1 + (n_moire +1)*A_UNITVEC_2)@rt_mtrx_half.T

    # fist `mm_` represents for magnetic moire
    # magnetic moire unit vector
    mm_unitvec_1 = m_unitvec_1
    mm_unitvec_2 = m_unitvec_2*q

    # moire reciprocal vector
    m_g_unitvec_1 = A_G_UNITVEC_1@rt_mtrx_half.T - A_G_UNITVEC_1@rt_mtrx_half
    m_g_unitvec_2 = A_G_UNITVEC_2@rt_mtrx_half.T - A_G_UNITVEC_2@rt_mtrx_half

    # magnetic moire reciprocal vector
    mm_g_unitvec_1 = m_g_unitvec_1
    mm_g_unitvec_2 = m_g_unitvec_2/q

    # moire unit lattice size
    s = np.linalg.norm(np.cross(m_unitvec_1, m_unitvec_2))

    return (m_unitvec_1,    m_unitvec_2,  m_g_unitvec_1, m_g_unitvec_2, 
            mm_unitvec_1, mm_unitvec_2,   mm_g_unitvec_1, mm_g_unitvec_2, s)


def read_atom_pstn_list(path:str, n_moire:int)->list:
    """
    read the atom pstn list in a single moire lattice 
    """
    atom_pstn_list = np.loadtxt(path+"atom"+str(n_moire)+".csv", delimiter=',', comments='#')

    return list(atom_pstn_list)


def set_magnetic_atom_pstn(n_moire:int, q:int, path:str)->tuple:
    """
    magnetic moire lattice is q times bigger than the original one, the enlarge
    magnetic moire lattice is 9 times bigger than the magnetic moire lattice and it
    makes easy to find neighbours

    --------
    Returns:

    mm_atom_list: numpy 2d array (q*n, 3), n is # of moire atoms
    enlarge_mm_atom_list: numpy 2d array (9*q*n, 3)
    """

    (m_unitvec_1,    m_unitvec_2,  m_g_unitvec_1, m_g_unitvec_2, 
     mm_unitvec_1, mm_unitvec_2,   mm_g_unitvec_1, mm_g_unitvec_2, s) = _set_moire_magnetic(n_moire, q)
    
    # before translate the postions, add information `d` for mm_unitvec
    m_unitvec_2  = np.array([m_unitvec_2[0],  m_unitvec_2[1],  0])
    mm_unitvec_1 = np.array([mm_unitvec_1[0], mm_unitvec_1[1], 0])   
    mm_unitvec_2 = np.array([mm_unitvec_2[0], mm_unitvec_2[1], 0])
    # moire atoms
    m_atom_list = read_atom_pstn_list(path, n_moire)
    # split for `a1 b1 a2 b2` atoms
    atom_list_tuple = np.split(np.array(m_atom_list), 4)
    # magnetic moire atoms
    mm_atom_list = np.concatenate(tuple(atom_list+i*m_unitvec_2 for atom_list in atom_list_tuple for i in range(q)))

    # 9 times bigger than the original magnetic lattice
    area1 = mm_atom_list+mm_unitvec_1
    area2 = mm_atom_list+mm_unitvec_2
    area3 = mm_atom_list-mm_unitvec_1
    area4 = mm_atom_list-mm_unitvec_2
    area5 = mm_atom_list+mm_unitvec_1+mm_unitvec_2
    area6 = mm_atom_list+mm_unitvec_1-mm_unitvec_2
    area7 = mm_atom_list-mm_unitvec_1+mm_unitvec_2
    area8 = mm_atom_list-mm_unitvec_1-mm_unitvec_2

    enlarge_mm_atom_list = np.concatenate((mm_atom_list, area1, area2, area3, area4, area5, area6, area7, area8))

    # print("enlarge mm atom list shape:", enlarge_mm_atom_list.shape)
    # print("mm atom list shape:", mm_atom_list.shape)

    return (mm_atom_list, enlarge_mm_atom_list)


def set_magnetic_atom_neighbour_list(mm_atom_list, enlarge_mm_atom_list, distance=2.5113*A_0):
    """
    find neighours within `distance` by using kdtree algorithm

    -----
    Return

    all_nns: numpy array (index)
    """

    # only use first two dimentional information
    x = enlarge_mm_atom_list[:, :2]
    y = mm_atom_list[:, :2]
    tree = KDTree(x)
    ind = tree.query_radius(y, r=distance)
    
    # the kdtree algotithm provided by sklearn will return the index 
    # including itself, the following code will remove them
    all_nns = np.array([np.array([idx for idx in nn_indices if idx != i]) for i, nn_indices in enumerate(ind)], dtype=object)

    return all_nns


def set_relative_dis_ndarray(mm_atom_list, enlarge_mm_atom_list, atom_neighbour_index)->tuple:
    """
    construct relative distance ndarry

    -------
    Returns:

    (atom_pstn_2darray, atom_neighbour_2darray, row, col)
    """
  
    # magnetic moire atom number
    num_atom = mm_atom_list.shape[0]

    # tricky code here
    # construct Ri list
    neighbour_len_list = [subindex.shape[0] for subindex in atom_neighbour_index]
    atom_pstn_2darray = np.repeat(mm_atom_list, neighbour_len_list, axis=0) 

    # print(atom_neighbour_index.shape)
    # print(atom_neighbour_index[0])
    # print(np.array(enlarge_mm_atom_list)[atom_neighbour_index[0]])
    # atom_neighbour_2darray = np.concatenate(tuple(enlarge_mm_atom_list[subindex] for subindex in atom_neighbour_index))

    # construct Rj near Ri list
    atom_neighbour_2darray = enlarge_mm_atom_list[np.hstack(atom_neighbour_index)]
    # print(atom_neighbour_2darray.shape)
    assert atom_pstn_2darray.shape == atom_neighbour_2darray.shape

    ind = atom_neighbour_index%num_atom
    # (row, col) <=> (index_i, index_j)
    row = [iatom for iatom in range(num_atom) for n in range(ind[iatom].shape[0])]
    col = [jatom for subindex in ind for jatom in subindex]

    assert len(row) == len(col)

    return (atom_pstn_2darray, atom_neighbour_2darray, row, col)