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

model_struct2= {
    'A':{
        'links': ['B','C'],
    },
    'B':{
        'links': [],
    }, 
    'group':{
        'children':{
            'C':{
                'links':  [],
            },
            'D':{
                'links':  ['A'],
            },
            'E':{
                'links':  ['A'],
            },
            'F':{
                'links':  ['A'],
            },
            'G':{
                'links':  ['A'],
            },
            'H':{
                'links':  ['A','C'],
            }
        }
    }
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

    leaves=tree_fill_coordinates(tree, False)
    return (tree, leaves)


def _tree_from_model(model):
    elements=[]
    for k in model.keys():
        new = {'children' : [],
            'id':k
        }
        if 'children' in model[k]:
            children=_tree_from_model(model[k]['children'])
            new['children']=children

        elements.append(new)
    return elements


def tree_build_from_model(model):
    #initial tree
    tree = {'children' : _tree_from_model(model)}

    tree['x']=0;
    tree['y']=0;
    tree['w']=1;
    tree['h']=1;

    print(json.dumps(tree, indent=2))
    tree_fill_coordinates(tree, False)
    return tree



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





def tree_fill_coordinates(tree, dir_x:bool):
    parent=tree

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
            tree_fill_coordinates(child, not dir_x)


def tree_get_drawable_elements(tree):
    elts=[]

    for child in tree['children']:
        if 'id' in child.keys():
            elts.append(child)

        if len(child['children']) >0:
            # if grandchildren exist, recurse and divide in the other diirection
            e=tree_get_drawable_elements(child)
            elts+=e

    return elts


#flatten the tree into a list
def tree_get_all_elements(tree):
    elts=[]

    for child in tree['children']:
        elts.append(child)

        if len(child['children']) >0:
            # if grandchildren exist, recurse and divide in the other diirection
            e=tree_get_all_elements(child)
            elts+=e

    return elts

# return only elements that have children
# including the root !
def tree_get_all_parents(tree):
    elts=[]

    if len(tree['children'])>0:
        elts.append(tree)

    for child in tree['children']:
        if len(child['children']) >0:
            e=tree_get_all_parents(child)
            elts+=e

    return elts


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


def draw_svg(name, drawables, model_struct):
    dim=40*leaves_min_dimension(drawables)
    svg = svgwrite.Drawing(name, viewBox=('0 0 100 100'))

    for l in drawables:
        w=l['w']*100
        h=l['h']*100
        x=l['x']*100
        y=l['y']*100
        svg.add(svg.rect(insert=(x, y), size=(w, h), stroke=svgwrite.rgb(60, 60, 66, '%'), fill='white', fill_opacity=0))
        svg.add(svg.rect(insert=(x+w/2-dim, y+h/2-dim), size=(2*dim, 2*dim), stroke=svgwrite.rgb(10, 10, 16, '%'), fill='white'))
        svg.add(svg.text(l['id'], insert=(x+w/2-dim, y+h/2)))


    for d in drawables:
        s=model_obj_from_id(model_struct, d['id'])

        if 'links' in s.keys():
            for arrow in s['links']:
                # find target coordinates
                print(d['id']+'->'+arrow)
                for dt in drawables:
                    if dt['id']==arrow:
                        xo=(d['x']+d['w']/2)*100
                        yo=(d['y']+d['h']/2)*100
                        xt=(dt['x']+dt['w']/2)*100
                        yt=(dt['y']+dt['h']/2)*100
                        svg.add(svg.line(start=(xo, yo), end=(xt, yt), stroke=svgwrite.rgb(10, 100, 16, '%')))
                        break

    svg.save()

def model_obj_from_id(model_tree, obj_id):
    for (k,v) in model_tree.items():
        if k==obj_id:
            return v
        if 'children' in v.keys():
            r=model_obj_from_id(v['children'], obj_id)
            if r != None:
                return r
          
    return None  


def drawable_with_id(drawables, leaf_id):
    for lt in drawables:
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
def compute_cost(drawables, tree, model):
    segments=[]
    length=0
    for d in drawables:
        s=model_obj_from_id(model, d['id'])

        try:
            for arrow in s['links']:
                # find target coordinates
                dt=drawable_with_id(drawables, arrow)
                xo=(d['x']+d['w']/2)
                yo=(d['y']+d['h']/2)
                xt=(dt['x']+dt['w']/2)
                yt=(dt['y']+dt['h']/2)
                length+=(xt-xo)**2+(yt-yo)**2
                segments.append((xo, yo, xt, yt))
        except KeyError:
            pass
            
    #compute number of segment intersections
    intersections = 0
    for index, segment in enumerate(segments):
        for segb in segments[index:len(segments)]:
            if segments_intersect(segment, segb):
                intersections+=1

    #give bonus to segments that go down
    bonus=0
    for (xo, yo, xt, yt) in segments:
        if xo<xt:
            bonus +=0.1


    #give bonus to straight lines
        bonus=0
    for (xo, yo, xt, yt) in segments:
        if xo==xt:
            bonus +=0.1
        if yo==yt:
            bonus +=0.1            

    complexity = tree_longest_branch(tree)
    score = length + intersections/2 + complexity/2 + bonus
    return score


def random_mutate_tree(tree, max_size):
    new_tree = copy.deepcopy(tree)

    random_swap_siblings(new_tree)
    tree_fill_coordinates(new_tree, False)
    drawables=tree_get_drawable_elements(new_tree)

    return (new_tree, drawables)


def remove_dead_branches(tree):
    #remove all branches that don't end with a leaf with an id
    for child in tree['children']:
        remove_dead_branches(child)
        #test dead branch
        if len(child['children']) == 0 and not 'id' in child:
            tree['children'].remove(child)

    return tree



def random_swap_siblings(tree):
    flat = tree_get_all_parents(tree);

    #choose one random tree element
    node = flat[random.randint(0, len(flat)-1)]

    count = len(node['children'])
    if count <2:
        # need at least 2 children to swap
        return False

    #pick one child to remove
    i = random.randint(0, count-1)
    child = node['children'][i]
    node['children'].pop(i)
    i = random.randint(0, count-1)
    node['children'].insert(i, child)

    return tree






def main():

    tree=tree_build_from_model(model_struct2)
    #print(json.dumps(tree, indent=2))
    drawables= tree_get_drawable_elements(tree)


    # we can consider that objects are placed at a fixed place
    draw_svg('test.svg', drawables, model_struct2)


    score = compute_cost(drawables, tree, model_struct2)

    print(score)

    candidates=[]
    candidates.append((score, tree, drawables))

    for i in range(0,200):
        (new_tree, new_leaves) = random_mutate_tree(tree, len(structure_to_render))
        candidates.append((compute_cost(new_leaves, new_tree, model_struct2), new_tree, new_leaves))

    #sort array relative to score
    candidates.sort(key=lambda tup: tup[0])

    # number of evolution generations
    for j in range(0,50):
        #take the 20 best ones, mutate them and rebuild candidate list
        candidates = candidates[0:50]
        mutated = []
        for c in candidates:
            (new_tree, new_leaves) = random_mutate_tree(c[1], len(structure_to_render))
            mutated.append((compute_cost(new_leaves, new_tree,model_struct2), new_tree, new_leaves))
            (new_tree, new_leaves) = random_mutate_tree(new_tree, len(structure_to_render))
            mutated.append((compute_cost(new_leaves, new_tree, model_struct2), new_tree, new_leaves))
            (new_tree, new_leaves) = random_mutate_tree(new_tree, len(structure_to_render))
            mutated.append((compute_cost(new_leaves, new_tree, model_struct2), new_tree, new_leaves))

        candidates+=mutated
        #sort array relative to score
        candidates.sort(key=lambda tup: tup[0])
        print(candidates[0][0])

    draw_svg('test2.svg', candidates[0][2], model_struct2)
    print(candidates[0][0])



if __name__ == "__main__":
    # execute only if run as a script
    main()

