#!/usr/bin/python3
import random
import json
import math
import svgwrite
import copy

structure_to_render= {
    'A': ['B','C'], #A->B, A->C
    'B': ['C'],     #B->C
    'C': [],
    'D': ['C','A'],
    'E': ['A'],
    'F': ['A'],
    'G': ['A'],
    'H': ['A'],
}


space_tree= {
    'children' : [
        {'children' : []}
    ]
}

def build_random_tree(size):
    #initial tree
    tree = {'children' : []}
    for i in range(0,size-1):
        tree = add_random_leaf(tree, size)

    tree['x']=0;
    tree['y']=0;
    tree['w']=1;
    tree['h']=1;

    leaves=fill_coordinates_from_tree(tree, False)
    return (tree, leaves)


def add_random_leaf(tree, max_size):
    # pick random position

    pos =[tree]

    max_steps = random.randint(1, math.ceil(max_size/2));

    while len(pos)!=0 and max_steps>0:
        i = random.randint(0, len(pos)-1)
        max_steps-=1
        pos = pos[i]['children']

    if len(pos)==0:
        #pos is a leaf. Create 2 leaves below
        pos.append({'children' : []})
        pos.append({'children' : []})
    else:
        #just create a leaf below
        pos.append({'children' : []})

    return tree

#return the minimum dimension in a list of leaves (either width or height)
def leaves_min_dimension(leaves):
    min_dim=1.0
    for l in leaves:
        if l['w'] < min_dim:
            min_dim=l['w']
        if l['h'] < min_dim:
            min_dim=l['h'] 

    return min_dim





def fill_coordinates_from_tree(tree, dir_x:bool):
    parent=tree
    leaves=[]

    n =len(parent['children'])
    i=0
    x=tree['x']
    y=tree['y']


    for child in parent['children']:
        if dir_x:
            w=tree['w']/n
            h=tree['h']
            child['w']=w
            child['h']=h
            child['x']=x+i*w
            child['y']=y
        else: 
            w=tree['w']
            h=tree['h']/n
            child['w']=w
            child['h']=h
            child['x']=x
            child['y']=y+i*h

        i+=1

        if len(child['children']) >0:
            # if grandchildren exist, recurse and divide in the other diirection
            l=fill_coordinates_from_tree(child, not dir_x)
            leaves+=l
        else:
            leaves.append(child)

    return leaves


def tree_count_elements(tree):
    n =0
    for child in tree['children']:
        n+=1
        if len(child['children']) >0:
            n+=tree_count_elements(child)
    return n


def tree_longest_branch(tree):
    l =0
    for child in tree['children']:
        
        if len(child['children']) >0:
            n=tree_longest_branch(child)
            if l< n+1:
                l=n+1
        else:
            if l<1:
                l=1
    return l


def draw_rect(svg, xo, yo, xt, yt):
    if xo<xt:
        x=xo
        w=xt-xo
    else:
        x=xt
        w=xo-xt
    if yo<yt:
        y=yo
        h=yt-yo
    else:
        y=yt
        h=yo-yt
    svg.add(svg.rect(insert=(x, y), size=(w, h), stroke=svgwrite.rgb(100, 100, 16, '%'), fill_opacity="0"))



# build a list of valid connectors orderred by order of preference
def build_connectors(origin, target, objects):
    wo=origin['w']
    ho=origin['h']
    xo=origin['x']
    yo=origin['y']
    wt=target['w']
    ht=target['h']
    xt=target['x']
    yt=target['y']

    # try straight horizontal or vertical connector


def draw_svg(name, leaves):
    dim=40*leaves_min_dimension(leaves)
    svg = svgwrite.Drawing(name, viewBox=('0 0 100 100'))

    for l in leaves:
        s=structure_to_render[l['id']]

        w=l['w']*100
        h=l['h']*100
        x=l['x']*100
        y=l['y']*100
        #svg.add(svg.rect(insert=(x, y), size=(w, h), stroke=svgwrite.rgb(10, 10, 16, '%'), fill='white'))
        svg.add(svg.rect(insert=(x+w/2-dim, y+h/2-dim), size=(2*dim, 2*dim), stroke=svgwrite.rgb(10, 10, 16, '%'), fill='white'))
        svg.add(svg.text(l['id'], insert=(x+w/2-dim, y+h/2)))


    for l in leaves:
        s=structure_to_render[l['id']]
        for arrow in s:
            # find target coordinates
            print(l['id']+'->'+arrow)
            for lt in leaves:
                if lt['id']==arrow:
                    xo=(l['x']+l['w']/2)*100
                    yo=(l['y']+l['h']/2)*100
                    xt=(lt['x']+lt['w']/2)*100
                    yt=(lt['y']+lt['h']/2)*100
                    #draw_rect(svg, xo, yo, xt, yt)
                    svg.add(svg.line(start=(xo, yo), end=(xt, yt), stroke=svgwrite.rgb(10, 100, 16, '%')))
                    break

    svg.save()

def leaf_with_id(leaves, leaf_id):
    for lt in leaves:
        if lt['id']==leaf_id:
            return lt
    return None

#return Trus if segments intersect
#with a twist : segments are allowed to have the same endpoints and to be aligned. 
#I'm only interested in intersections that will cause problems later during connectors routing
def segments_intersect(sega, segb):
    (xa1, ya1, xa2, ya2) = sega
    (xb1, yb1, xb2, yb2) = segb

    xmina = min(xa1, xa2)
    ymina = min(ya1, ya2)
    xmaxa = max(xa1, xa2)
    ymaxa = max(ya1, ya2)
    xminb = min(xb1, xb2)
    yminb = min(yb1, yb2)
    xmaxb = max(xb1, xb2)
    ymaxb = max(yb1, yb2)    

    #if segments have same endpoint: that's not an intersection
    if (xa1 == xb1 and ya1 == yb1)  \
            or (xa2 == xb2 and ya2 == yb2) \
            or (xa1 == xb2 and ya1 == yb2) \
            or (xa2 == xb1 and ya2 == yb1) :

            if xa1 == xa2 and xb1 == xb2 :
                #segments overlapping on x are colliding
                if ymaxb <= ymina or ymaxa <= yminb:
                    return False
            elif ya1 == ya2 and yb1 == yb2 :
                #segments overlapping on y are colliding
                if xmaxb <= xmina or xmaxa <= xminb:
                    return False
            else:
                return False

    # segment intersection can be reduced to an overlap of bounding rectangles
    # if rectangles don't overlap I'm confident I'll be able to route connectors later
 

    if xmina > xmaxb:
        return False
    if xmaxa < xminb:
        return False
    if ymina > ymaxb:
        return False
    if ymaxa < yminb:
        return False

    return True




#compute a cost estimation of arrows length + intersections
def compute_cost(leaves, tree):
    segments=[]
    length=0
    for l in leaves:
        s=structure_to_render[l['id']]

        for arrow in s:
            # find target coordinates
            lt=leaf_with_id(leaves, arrow)
            xo=(l['x']+l['w']/2)
            yo=(l['y']+l['h']/2)
            xt=(lt['x']+lt['w']/2)
            yt=(lt['y']+lt['h']/2)
            length+=(xt-xo)**2+(yt-yo)**2
            segments.append((xo, yo, xt, yt))
            
    #compute number of segment intersections
    intersections = 0
    for index, segment in enumerate(segments):
        for segb in segments[index:len(segments)]:
            if segments_intersect(segment, segb):
                intersections+=1

    complexity = tree_longest_branch(tree)
    score = length + intersections/2 + complexity/2
    return score


def random_mutate_tree(tree, max_size):
    new_tree = copy.deepcopy(tree)

    new_tree = random_move_leaf(new_tree, max_size)
    leaves = fill_coordinates_from_tree(new_tree, False)
    return (new_tree, leaves)



def remove_dead_branches(tree):
    #remove all branches that don't end with a leaf with an id
    for child in tree['children']:
        remove_dead_branches(child)
        #test dead branch
        if len(child['children']) == 0 and not 'id' in child:
            tree['children'].remove(child)

    return tree


def random_move_leaf(tree, max_size):
    node=tree
    parent=tree

    #choose one random leaf
    while len(node['children'])!=0:
        i = random.randint(0, len(node['children'])-1)
        parent = node['children']
        node = node['children'][i]

    if node ==parent: 
        return

    #print("moving node "+ node['id'])
    parent.remove(node)

    #Maybe we created a dead branch with this operation
    #make a clean pass
    tree = remove_dead_branches(tree)


    new_pos = tree
    parent = tree
    max_steps = random.randint(1, math.ceil(max_size/2));

    while len(new_pos['children'])!=0 and max_steps>0:
        i = random.randint(0, len(new_pos['children'])-1)
        max_steps-=1
        parent = new_pos['children']
        new_pos = new_pos['children'][i]

    if len(new_pos['children'])==0:
        #new pos is a leaf. mutate this into a branch with 2 leaves
        parent.remove(new_pos)
        parent.append({'children' : [new_pos, node]})
    else:
        #insert 
        new_pos['children'].append(node)



    return tree


def main():
    (tree, leaves) = build_random_tree(len(structure_to_render))
    #print(json.dumps(tree, indent=2))
    #print(json.dumps(leaves, indent=2))

    leaves_iter =myit = iter(leaves)
    for k in structure_to_render.keys():
        l = next(leaves_iter)
        l['id']=k

    # we can consider that objects are placed at a fixed place
    arrows=[]
    draw_svg('test.svg', leaves)

    score = compute_cost(leaves, tree)

    print(score)

    candidates=[]
    candidates.append((score, tree, leaves))

    for i in range(0,200):
        (new_tree, new_leaves) = random_mutate_tree(tree, len(structure_to_render))
        candidates.append((compute_cost(new_leaves, new_tree), new_tree, new_leaves))

    #sort array relative to score
    candidates.sort(key=lambda tup: tup[0])

    # number of evolution generations
    for j in range(0,50):
        #take the 20 best ones, mutate them and rebuild candidate list
        candidates = candidates[0:50]
        mutated = []
        for c in candidates:
            (new_tree, new_leaves) = random_mutate_tree(c[1], len(structure_to_render))
            mutated.append((compute_cost(new_leaves, new_tree), new_tree, new_leaves))
            (new_tree, new_leaves) = random_mutate_tree(new_tree, len(structure_to_render))
            mutated.append((compute_cost(new_leaves, new_tree), new_tree, new_leaves))
            (new_tree, new_leaves) = random_mutate_tree(new_tree, len(structure_to_render))
            mutated.append((compute_cost(new_leaves, new_tree), new_tree, new_leaves))

        candidates+=mutated
        #sort array relative to score
        candidates.sort(key=lambda tup: tup[0])
        print(candidates[0][0])

    draw_svg('test2.svg', candidates[0][2])
    print(candidates[0][0])



if __name__ == "__main__":
    # execute only if run as a script
    main()

