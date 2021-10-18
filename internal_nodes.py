def find_internal_nodes_num(tree): 
    root = -1
    tree_details = {'all_nodes': [], 'parent_nodes': {}}
    for leaf in tree:
        if leaf == root:
            continue
        # Ensure we have all nodes from 0 to node
        if len(tree_details.get('all_nodes')) < leaf:
            tree_details['all_nodes'] = (list(range(-1, leaf + 2)))
        if leaf not in tree_details.get('parent_nodes'):
            tree_details['parent_nodes'][leaf] = 0
        tree_details['parent_nodes'][leaf] += 1
    return len(tree_details['parent_nodes'].keys())


my_tree = [4, 4, 1, 5, -1, 4, 5]
print(find_internal_nodes_num(my_tree))
