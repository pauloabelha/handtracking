import autograd.numpy as np  # Thinly-wrapped numpy
from autograd import grad
import math
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D #<-- Note the capitalization!

class Joint(object):
    def __init__(self, bone=None, axes=None):
        self.bone = bone
        self.axes = axes


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis/math.sqrt(np.dot(axis, axis))
    a = math.cos(theta/2.0)
    b, c, d = -axis*math.sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])

def get_rot_mtx(axis, theta):
    if theta == 0.0:
        return np.eye(3)
    rot_mtx = np.eye(3)
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    if axis == 0:
        rot_mtx[1, 1] = cos_theta
        rot_mtx[1, 2] = -sin_theta
        rot_mtx[2, 1] = sin_theta
        rot_mtx[2, 2] = cos_theta
    elif axis == 1:
        rot_mtx[0, 0] = cos_theta
        rot_mtx[0, 2] = sin_theta
        rot_mtx[2, 0] = -sin_theta
        rot_mtx[2, 2] = cos_theta
    elif axis == 2:
        rot_mtx[0, 0] = cos_theta
        rot_mtx[0, 1] = -sin_theta
        rot_mtx[1, 0] = sin_theta
        rot_mtx[1, 1] = cos_theta
    else:
        return None
    return rot_mtx

def skeleton_joints():
    x_axis = [1.0, 0.0, 0.0]
    y_axis = [0.0, 1.0, 0.0]
    z_axis = [0.0, 0.0, 1.0]
    thumb_mcp_axis = [0.1875, 0.1875, 0.625]
    thumb_dip_axis = [0.5, 0.5, 0.0]
    joints = []
    # handroot
    joints[0] = Joint(0, [x_axis, y_axis, z_axis])
    # thumb
    joints[1] = Joint(1, [thumb_mcp_axis, thumb_dip_axis])
    joints[2] = Joint(2, [thumb_dip_axis])
    joints[3] = Joint(3, [thumb_dip_axis])
    # index
    joints[4] = Joint(4, )


def skeleton_bone_lengths():
    '''

    :return skeleton model fixed bone lengths in mm
    '''
    bone_lengths = np.zeros((20, 1))
    # thumb
    bone_lengths[0] = 40
    bone_lengths[1] = 50
    bone_lengths[2] = 40
    bone_lengths[3] = 30
    # index
    bone_lengths[4] = 110
    bone_lengths[5] = 40
    bone_lengths[6] = 20
    bone_lengths[7] = 20
    # middle
    bone_lengths[8] = 110
    bone_lengths[9] = 40
    bone_lengths[10] = 20
    bone_lengths[11] = 20
    # ring
    bone_lengths[12] = 100
    bone_lengths[13] = 40
    bone_lengths[14] = 20
    bone_lengths[15] = 20
    # little
    bone_lengths[16] = 90
    bone_lengths[17] = 30
    bone_lengths[18] = 20
    bone_lengths[19] = 20
    return bone_lengths

def skeleton_bone_angles():
    '''

    :return: canonical global angles of resting skeleton
    '''
    bone_angles = [0] * 20
    # thumb
    bone_angles[0] = 5.495
    # index\
    bone_angles[4] = 5.8875
    # middle
    bone_angles[8] = 0.0
    # ring
    bone_angles[12] = 0.3925
    # little
    bone_angles[16] = 0.785
    return bone_angles

def plot_bone_line(bones):
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.set_color_cycle('rgbyk')
    ax.plot([0, bones[0][0]],
            [0, bones[0][1]],
            [0, bones[0][2]])
    i = 1
    while i < len(bones):
        ax.plot([bones[i-1][0], bones[i][0]],
                [bones[i-1][1], bones[i][1]],
                [bones[i-1][2], bones[i][2]])
        i += 1
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_xlim3d([-150, 150])
    ax.set_ylim3d([-150, 150])
    ax.set_zlim3d([-150, 150])
    plt.show()

def plot_bone_lines(bone_lines, handroot=None, fig=None, show=True, lim=200):
    if fig is None:
        fig = plt.figure()
    ax = Axes3D(fig)
    ax.set_color_cycle('rgby')
    if handroot is None:
        handroot = np.zeros((1, 3))
    for i in range(len(bone_lines)):
        ax.plot([handroot[0], bone_lines[i][0][0]],
                [handroot[1], bone_lines[i][0][1]],
                [handroot[2], bone_lines[i][0][2]])
        j = 1
        while j < len(bone_lines[i]):
            ax.plot([bone_lines[i][j - 1][0], bone_lines[i][j][0]],
                    [bone_lines[i][j - 1][1], bone_lines[i][j][1]],
                    [bone_lines[i][j - 1][2], bone_lines[i][j][2]])
            j += 1
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_xlim3d([-lim, lim])
    ax.set_ylim3d([-lim, lim])
    ax.set_zlim3d([-lim, lim])
    if show:
        plt.show()
    return fig

def update_point_and_children(joints_Theta, bone_lengths, bone_angles, bone_ix, axes_theta_ix, children_points, eps=1e-6):
    main_point = [bone_lengths[bone_ix][0], 0, 0]
    for i in range(len(children_points)):
        children_points[i] += main_point
    rotations = [None, None, None]
    for ax_ix in range(3):
        theta_ix = axes_theta_ix[ax_ix]
        if theta_ix is None:
            continue
        rotations[ax_ix] = get_rot_mtx(ax_ix, joints_Theta[theta_ix])
    if bone_angles[bone_ix] > eps:
        rotations[1] = np.dot(rotations[1], get_rot_mtx(1, bone_angles[bone_ix]))
    # add hand root rotation
    if bone_ix % 4 == 0:
        for i in range(3):
            if joints_Theta[i] > eps:
                rotations = [get_rot_mtx(i, joints_Theta[i])] + rotations
    for rotation in rotations:
        if rotation is None:
            continue
        main_point = np.dot(rotation, main_point)
        for i in range(len(children_points)):
            children_points[i] = np.dot(rotation, children_points[i])
    return main_point, children_points

def get_bone_line_args(finger_ix):
    bone_ixs = [3, 2, 1, 0]
    bone_ixs = [x + (finger_ix * 4) for x in bone_ixs]
    axes_theta = []
    for i in range(4):
        axis_theta = [None, None, None]
        if i < 3:
            if finger_ix == 0:
                ax_ix = 1
            else:
                ax_ix = 2
            axis_theta[ax_ix] = (6 + (finger_ix * 4)) - i
        if i == 2:
            axis_theta[1] = (6 + (finger_ix * 4)) - i
            axis_theta[2] = (6 + (finger_ix * 4)) - i - 1
        if i == 3:
            axis_theta = [2, 1, 0]
        axes_theta.append(axis_theta)
    return bone_ixs, axes_theta

def skeleton_bone_lines(joints_Theta, eps=1e-6):
    '''

    :param joints_Theta:
    :return: skeleton relative pose from 13 joint angles and global handroot 3D position (16 parameters in total)
    '''
    bone_lengths = skeleton_bone_lengths()
    bone_angles = skeleton_bone_angles()
    fingers_bone_lines = []
    for finger_ix in [0, 1, 2, 3, 4]:
        bone_ixs, axes_thetas = get_bone_line_args(finger_ix)
        finger_points = []
        for i in range(4):
            bone_ix = bone_ixs[i]
            axes_theta = axes_thetas[i]
            finger_main_pt, finger_children = update_point_and_children(
                joints_Theta, bone_lengths, bone_angles, bone_ix, axes_theta, finger_points)
            finger_points = [finger_main_pt] + finger_points
        for i in range(4):
            finger_points[i] += joints_Theta[-3:]
        fingers_bone_lines.append(finger_points)
    return fingers_bone_lines

def fingers_bone_lines_to_matrix(fingers_bone_lines, handroot):
    hand_matrix = np.zeros((21, 3))
    ix = 1
    for i in range(5):
        for j in range(4):
            hand_matrix[ix, :] = fingers_bone_lines[i][j]
            ix += 1
    hand_matrix[0, :] = handroot
    return hand_matrix


def joints_theta_ok():
    joints_Theta = [0] * 26
    joints_Theta[4] = 5.75
    joints_Theta[7] = 1.57
    joints_Theta[9] = 1.57
    joints_Theta[10] = 0.7
    joints_Theta[11] = 1.57
    joints_Theta[12] = 0.7
    joints_Theta[13] = 1.57
    joints_Theta[14] = 0.7
    joints_Theta[15] = 1.57
    joints_Theta[16] = 0.7
    joints_Theta[17] = 1.57
    joints_Theta[18] = 0.7
    joints_Theta[19] = 1.57
    joints_Theta[21] = 1.57

    joints_Theta[23] = 100
    return joints_Theta

joints_Theta = joints_theta_ok()

def joints_Theta_to_hand_matrix(joints_Theta):
    fingers_bone_lines = skeleton_bone_lines(joints_Theta)
    hand_matrix = fingers_bone_lines_to_matrix(fingers_bone_lines, joints_Theta[-3:])
    return hand_matrix

def animate_skeleton(pausing=0.2):
    fig = None
    for h in range(3):
        joints_Theta = [0] * 26
        joints_Theta[h] = 0.75
        for i in range(23):
            joints_Theta[i+3] = 0.75
            fingers_bone_lines = skeleton_bone_lines(joints_Theta)
            fig = plot_bone_lines(fingers_bone_lines, handroot=joints_Theta[-3:], fig=fig, show=False)
            plt.pause(pausing)
            plt.clf()
    plt.show()

def E_pos3D(joints_Theta, joints_pred):
    hand_matrix = joints_Theta_to_hand_matrix(joints_Theta)
    dist = np.abs((hand_matrix - joints_pred)).sum()
    return dist

grad_E_pos3D = grad(E_pos3D(joints_Theta, np.zeros((21, 3))))

print(grad_E_pos3D(joints_Theta, np.zeros((21, 3))))
