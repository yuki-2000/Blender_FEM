import numpy as np
import matplotlib.pyplot as plt
import csv  




#条件　ファイルから読み込んでもよい

#節点数
num_node  = 1331
#要素数
num_eleme = 1000
#表示倍率
amp = 10


node        = np.empty((num_node,3), dtype=np.float64) #節点座標
eleme       = np.empty((num_eleme,8),dtype=np.int32) #各要素のコネクティビティ #つまりある六面体elementを構成する接点node番号(1スタートに注意)
eleme_value = np.empty((num_node), dtype=np.float64)  #要素における値　これで色を付ける  



#節点番号、座標ファイルの読み込み   
with open('H:/programing/blender/output_disp2.dat') as f: 
    reader = csv.reader(f, delimiter=' ')
    l = [row for row in reader]
    
    for i in range(num_node):
        node[i,0] = l[i][1].replace('d','e')
        node[i,1] = l[i][2].replace('d','e')
        node[i,2] = l[i][3].replace('d','e')


#要素番号、コネクティビティファイルの読み込み  
with open('H:/programing/blender/input_eleme.txt') as f:
    reader = csv.reader(f)
    l = [row for row in reader]

    for i in range(num_eleme):
        eleme[i] = l[i][1:9]

        
#要素値ファイルの読み込み        
with open('H:/programing/blender/output_ave_strain2.dat') as f:   
    reader = csv.reader(f, delimiter=' ')    
    #reader = csv.reader(f)
    l = [row for row in reader]

    for i in range(num_eleme):
        eleme_value[i] = l[i][1].replace('d','e')
    

        
#正規化する関数
#https://deepage.net/features/numpy-normalize.html
def min_max(x, axis=None):
    min = x.min(axis=axis, keepdims=True)
    max = x.max(axis=axis, keepdims=True)
    result = (x-min)/(max-min)
    return result
        
#0から1に正規化した要素値を0から255に変更        
eleme_value = min_max(eleme_value, axis=None) * 255
#要素の値からmatplotlibのカラーマップ機能を使用して(R, G, B, A)に変換
cm_color = [plt.cm.jet(int(value)) for value in eleme_value]        
        
 
import bpy     



for item in bpy.data.meshes:
    bpy.data.meshes.remove(item)
for item in bpy.data.materials:
    bpy.data.materials.remove(item)









verts = np.zeros((8,3), dtype=np.float64) #ある六面体要素を構成する6接点のxyz座標
for i in range(num_eleme):
    for j in range(8): #節点の8
        #eleme[i,j]つまり要素値が1始まりなので0始まりのPython配列に合わせて-1している
        verts[j,0] = node[eleme[i,j]-1,0]
        verts[j,1] = node[eleme[i,j]-1,1]
        verts[j,2] = node[eleme[i,j]-1,2]
    
    #表示倍率を適用    
    verts *= amp
    #面を構成する節点の場所
    faces = [[0,1,2,3], [0,4,5,1], [1,5,6,2], [2,6,7,3], [0,3,7,4], [4,7,6,5]]
    
    #メッシュの作成
    msh = bpy.data.meshes.new(name=f"cubemesh{i}")
    msh.from_pydata(verts, [], faces)
    msh.update()

    #オブジェクトの作成
    obj = bpy.data.objects.new(name=f"cube{i}", object_data=msh)
    scene = bpy.context.scene
    scene.collection.objects.link(obj)
    
    #マテリアルの作成
    material = bpy.data.materials.new(f"cubematerial{i}")
    obj.data.materials.append(material)        
    material.use_nodes = True    

    #マテリアルの設定
    color = cm_color[i]
    p_BSDF = material.node_tree.nodes["Principled BSDF"]
    p_BSDF.inputs[0].default_value = color
    p_BSDF.inputs[9].default_value = 0
    p_BSDF.inputs[17].default_value = 1


#環境光で全体を明るく
#環境色を(R, G, B, A)で指定、今回は白
bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
#強さ
bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 1

