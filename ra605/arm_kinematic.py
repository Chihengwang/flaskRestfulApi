"""
FK:
input:dict() including 6dof value of robotic arm
return 4x4 nparray(transformation matrix)

IK:
input: 4x4 nparray(transformation matrix)
return: dict() including j1~j6
EX:
example
6dof={
    'j1': float,
    'j2': float,
    'j3': float,
    'j4': float,
    'j5': float,
    'j6': float,
}
"""
import math
import numpy as np
def t_matrix(theta,d,a,alpha):
    output=[
        [math.cos(theta),-math.sin(theta)*math.cos(alpha),math.sin(theta)*math.sin(alpha),a*math.cos(theta)],
        [math.sin(theta), math.cos(theta)*math.cos(alpha), -math.cos(theta)*math.sin(alpha), a*math.sin(theta)],
        [0, math.sin(alpha), math.cos(alpha), d],
        [0,0,0,1]
    ]
    return np.array(output)

def forward_kinematic(six_dof_dic):
    print('forward kinematic cal...')
    # extract value from dict
    for key in six_dof_dic:
        six_dof_dic[key]=six_dof_dic[key]/180*math.pi
    theta1=six_dof_dic['j1']
    theta2=six_dof_dic['j2']
    theta3=six_dof_dic['j3']
    theta4=six_dof_dic['j4']
    theta5=six_dof_dic['j5']
    theta6=six_dof_dic['j6']
    # define global parameter
    # DH table
    # unit mm
    DH_table=np.array([
        [-math.pi/2,30,theta1,375],
        [0,340,-math.pi/2+theta2,0],
        [-math.pi/2,40,theta3,0],
        [math.pi/2, 0,theta4, 338],
        [-math.pi/2, 0, theta5, 0],
        [0, 0, theta6, 86]
    ])
    dh_tf_matrices=[]
    t0_6=np.eye(4)
    for i in range(len(DH_table)):
        dh_tf_matrices.append(t_matrix(DH_table[i,2],DH_table[i,3],DH_table[i,1],DH_table[i,0]))
    
    for i in range(len(DH_table)):
        t0_6=np.dot(t0_6, dh_tf_matrices[i])
    return t0_6

# ======================================================
# ik parameter setting up
l5=86
l4=338
l3=40
l3_5=(l3**2+l4**2)**(0.5)
l2=340
l1=30
l0=375
# ======================================================
def inverse_kinematic(t0_6):
    print("inverse kinematic cal...")
    x3=t0_6[0,3]-l5*t0_6[0,2]
    y3=t0_6[1,3]-l5*t0_6[1,2]
    z3=t0_6[2,3]-l5*t0_6[2,2]

    theta1=math.atan2(y3,x3)
    x1=l1*math.cos(theta1)
    y1=l1*math.sin(theta1)
    z1=l0
    theta3_5=math.atan2(l4,l3)

    x1_x3=((x3-x1)**2+(y3-y1)**2+(z3-z1)**2)**(0.5)

    theta=math.acos((l3_5**2+l2**2-x1_x3**2)/(2*l3_5*l2))
    theta3=math.pi-theta3_5-theta

    x_prime=(((x3-x1)**2+(y3-y1)**2)**(0.5))*(x3-x1)*math.cos(theta1)/abs((x3-x1)*math.cos(theta1))
    a=l2-l3_5*math.cos(theta)
    b=l3_5*math.sin(theta)
    sin_theta2=a*x_prime-b*(z3-z1)
    cos_theta2=a*(z3-z1)+b*x_prime
    theta2=math.atan2(sin_theta2,cos_theta2)
    DH_table=np.array([
        [-math.pi/2,30,theta1,375],
        [0,340,-math.pi/2+theta2,0],
        [-math.pi/2,40,theta3,0],
    ])
    dh_tf_matrices=[]
    t0_3=np.eye(4)
    for i in range(len(DH_table)):
        dh_tf_matrices.append(t_matrix(DH_table[i,2],DH_table[i,3],DH_table[i,1],DH_table[i,0]))
    
    for i in range(len(DH_table)):
        t0_3=np.dot(t0_3, dh_tf_matrices[i])
    # get rotation matrix from the tf matrix
    r0_3=t0_3[0:3,0:3]
    r0_6=t0_6[0:3,0:3]
    r3_6=np.dot(np.linalg.inv(r0_3),r0_6)
    if((r3_6[2,0]**2+r3_6[2,1]**2)*100>=0.1):
        print('Theta5 is not equal to zero!!')
        theta5=math.acos(r3_6[2,2])
        if(abs(math.atan2(r3_6[2,1]/math.sin(theta5),-r3_6[2,0]/math.sin(theta5)))>abs(math.atan2(-r3_6[2,1]/math.sin(theta5),r3_6[2,0]/math.sin(theta5)))):
            theta4=math.atan2(-r3_6[1,2],-r3_6[0,2])
            theta6=math.atan2(-r3_6[2,1],r3_6[2,0])
        else:
            theta4=math.atan2(r3_6[1,2],r3_6[0,2])
            theta6=math.atan2(r3_6[2,1],-r3_6[2,0])
            theta5=-theta5
    else:
        print('Theta5 is equal to 0 or 180')
        if(r3_6[2,2]>0):
            print('r33 should be equal to 1')
            theta5=0
            if(abs(math.atan2(-r3_6[1,0],r3_6[0,0]))<math.atan2(r3_6[1,0],-r3_6[0,0])):
                theta4=0
                theta6=math.atan2(-r3_6[0,1],r3_6[0,0])
            else:
                theta4=math.pi
                theta6=math.atan2(r3_6[0,1],-r3_6[0,0])
        else:
            theta5=math.pi
            if(abs(math.atan2(r3_6[1,0],-r3_6[0,0]))<math.atan2(-r3_6[1,0],r3_6[0,0])):
                theta4=0
                theta6=math.atan2(r3_6[0,1],-r3_6[0,0])
            else:
                theta4=math.pi
                theta6=math.atan2(-r3_6[0,1],r3_6[0,0])     
    six_dof_dic={
        'j1':theta1/math.pi*180,
        'j2':theta2/math.pi*180,
        'j3':theta3/math.pi*180,
        'j4':theta4/math.pi*180,
        'j5':theta5/math.pi*180,
        'j6':theta6/math.pi*180,
    }
    return six_dof_dic
# ===============================================================
if __name__=='__main__':
    print("testing....")
    # np 4x4 matrix
    print('t_matrix size: ',str(t_matrix(20,10,3,60).shape))

    # testing data
    theta1=48
    theta2=-29
    theta3=13
    theta4=-93
    theta5=50
    theta6=124

    six_dof_dic={
        'j1':theta1,
        'j2':theta2,
        'j3':theta3,
        'j4':theta4,
        'j5':theta5,
        'j6':theta6,
    }
    print('-'*20)
    print('pre data: ',str(six_dof_dic))
    t0_6=forward_kinematic(six_dof_dic)
    print('fk transformation matrix:\n', str(np.around(t0_6,4)))
    print(type(t0_6))
    print(t0_6.shape)
    print('-'*20)
    # # test ik from matlab
    # t0_6=np.array([
    #     [-0.4226,-0.0047,0.9063,236.5040],
    #     [0.7677,-0.5334,0.3552,-173.6657],
    #     [0.4817,0.8459,0.2290,349.0915],
    #     [0,0,0,1]
    # ])
    six_dof_dic_ik=inverse_kinematic(t0_6)
    print('ik 6dof data: ',str(six_dof_dic_ik))
    t0_6_ik=forward_kinematic(six_dof_dic_ik)
    print('ik transformation matrix:\n', str(np.around(t0_6_ik,4)))
    # with all colse method, we can tolerate some difference btw them.
    print('-'*20)
    print('Is t0_6 equal to t0_6_ik?: ',np.allclose(t0_6,t0_6_ik))