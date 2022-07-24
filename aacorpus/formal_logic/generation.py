import random
import copy
from typing import List, Tuple, Optional, Iterable, Union
from aacorpus.formal_logic import (
    generate_replacement_mappings,
    generate_replacement_mappings_from_formula,
    generate_replacement_mappings_from_terms,
    generate_replaced_formulas,
    generate_replaced_arguments,
    Formula,
    Argument,
    replace_formula,
    replace_argument,
    replace_rep,
    is_satisfiable,
)
import logging

logger = logging.getLogger(__name__)


class MultipleParentError(Exception):
    pass


class ProofNode:

    def __init__(self, formula: Formula):
        self.formula = formula
        self.argument: Optional[Argument] = None
        self.parent: Optional[ProofNode] = None
        self._children: List['ProofNode'] = []
        # self._tree: Optional['ProofTree'] = None

    def add_child(self, node: 'ProofNode') -> None:
        if node.parent is not None:
            raise MultipleParentError('Can\'t add child since it already has a parent.')

        node.parent = self
        if node not in self._children:
            self._children.append(node)

    def delete_child(self, node: 'ProofNode') -> None:
        for _node in self._children:
            if _node  == node:
                self._children.remove(node)
                break
        if len(self._children) == 0:
            self.argument = None

    @property
    def children(self):
        return self._children

    def __str__(self) -> str:
        return f'ProofNode({self.formula.rep})'

    def __repr__(self) -> str:
        return str(self)


class ProofTree:

    def __init__(self):
        self._nodes: List[ProofNode] = []

    def add_node(self, node: ProofNode) -> None:
        if node not in self._nodes:
            self._nodes.append(node)
            # node._tree = self

    def delete_node(self, node: ProofNode) -> None:
        self._nodes.remove(node)
        # node._tree = None
        for _node in self._nodes:
            if _node.parent == node:
                _node.parent = None
            _node.delete_child(node)

    @property
    def nodes(self) -> List[ProofNode]:
        return self._nodes

    @property
    def leaf_nodes(self) -> List[ProofNode]:
        return [node for node in self._nodes
                if len(node.children) == 0]

    @property
    def root_node(self) -> ProofNode:
        return [node for node in self._nodes
                if node.parent is None][0]

    # def get_parent_node(self, node: ProofNode) -> Optional[ProofNode]:
    #     for _node in self._nodes:
    #         if node in _node.children:
    #             return _node
    #     return None

    def depth_first_traverse(self,
                             start_node: Optional[ProofNode] = None,
                             depth=0,
                             get_depth=False) -> Iterable[Union[ProofNode, Tuple[ProofNode, int]]]:
        start_node = start_node or self.root_node
        for child_node in start_node.children:
            yield from self.depth_first_traverse(start_node=child_node, depth=depth + 1, get_depth=get_depth)
        yield (start_node, depth) if get_depth else start_node

    def __repr__(self):
        return 'ProofTree()'

    def __str__(self):
        return self.__repr__()

    @property
    def format_str(self):
        rep = 'ProofTree(\n'
        for node, depth in self.depth_first_traverse(get_depth=True):
            rep += '\n'
            rep += '    ' + '    ' * depth + f'node     : {node}\n'
            rep += '    ' + '    ' * depth + f' argument : {node.argument}'
            rep += '\n'
        rep += '\n)'
        return rep


def generate_tree(arguments: List[Argument],
                  depth=1,
                  predicate_pool: Optional[List[str]] = None,
                  constant_pool: Optional[List[str]] = None):
    predicate_pool = predicate_pool or ['F', 'G', 'H', 'I', 'J', 'K', 'L']
    constant_pool = constant_pool or ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    
    proof_tree = ProofTree()
    cur_arg = random.choice(arguments)
    cur_conclusion_node = ProofNode(cur_arg.conclusion)
    cur_premise_nodes = [ProofNode(premise) for premise in cur_arg.premises]
    update(cur_premise_nodes, cur_conclusion_node, cur_arg, proof_tree)

    cur_depth = 0
    while True:
        if cur_depth >= depth:
            break

        cur_conclusion = cur_conclusion_node.formula

        # Listup chainable arguments
        chainable_args = []
        for arg in arguments:
            is_chainable = False
            for premise in arg.premises:
                for premise_variant_replaced, _ in generate_replaced_formulas(premise, cur_conclusion):
                    if premise_variant_replaced.rep == cur_conclusion.rep:
                        is_chainable = True
                        break
                if is_chainable:
                    break
            if is_chainable:
                chainable_args.append(arg)
        assert(len(chainable_args) == 1)

        next_arg_unreplaced = random.choice(chainable_args)

        # Chose one premise which is chainable from the conclusion
        chainable_premises_unreplaced = [
            premise for premise in next_arg_unreplaced.premises
            if any([premise_variant_replaced.rep == cur_conclusion.rep
                    for premise_variant_replaced, _ in generate_replaced_formulas(premise, cur_conclusion)])
        ]
        premise_to_chain_unreplaced = random.choice(chainable_premises_unreplaced)

        # Chose one premise variant which is chainable from the conclusion
        premise_variants_replaced = [
            (premise_variant_replaced, premise_mapping)
            for premise_variant_replaced, premise_mapping in generate_replaced_formulas(premise_to_chain_unreplaced, cur_conclusion)
            if premise_variant_replaced.rep == cur_conclusion.rep
        ]
        premise_variant_replaced, premise_mapping = random.choice(premise_variants_replaced)

        # Chose argument mapping which is consistent with the premise mapping above.
        argument_mappings = []
        src_predicates = list(set([
            term.rep
            for formula in next_arg_unreplaced.premises + [next_arg_unreplaced.conclusion]
            for term in formula.predicates
        ]))
        src_constants = list(set([
            term.rep
            for formula in next_arg_unreplaced.premises + [next_arg_unreplaced.conclusion]
            for term in formula.constants
        ]))
        tgt_predicates = list(set([
            term.rep
            for term in premise_to_chain_unreplaced.predicates
        ] + predicate_pool))
        tgt_constants = list(set([
            term.rep
            for term in premise_to_chain_unreplaced.constants
        ] + constant_pool))

        for mapping in generate_replacement_mappings_from_terms(src_predicates, src_constants,
                                                                tgt_predicates, tgt_constants):
            if all([mapping.get(key, None) == val
                    for key, val in premise_mapping.items()]):
                argument_mappings.append(mapping)
        mapping = random.choice(argument_mappings)

        # Get the argument replaced by the mapping.
        next_arg_replaced = replace_argument(next_arg_unreplaced, mapping)

        # Prepare nodes
        next_conclusion_node = ProofNode(next_arg_replaced.conclusion)
        next_conclusion_node.argument = next_arg_replaced
        next_premise_nodes = []
        premise_already_in_tree = False
        for premise in next_arg_replaced.premises:
            if premise.rep == premise_variant_replaced.rep:
                next_premise_nodes.append(cur_conclusion_node)
            else:
                for existent_node in proof_tree.nodes:
                    if premise.rep == existent_node.formula.rep:
                        logger.info('Retry the step since the premise already exists in the tree, which will result in a graph rather than tree.')
                        premise_already_in_tree = True
                        break
                        # next_premise_nodes.append(existent_node)
                if premise_already_in_tree:
                    break

                next_premise_nodes.append(ProofNode(premise))

        if premise_already_in_tree:
            continue

        if not is_satisfiable([node.formula for node in proof_tree.nodes + next_premise_nodes + [next_conclusion_node]]):
            logger.info('Retry step since the step generated formulas contradicting the existing formulas.')
            continue

        update(next_premise_nodes, next_conclusion_node, next_arg_replaced, proof_tree)

        cur_arg = next_arg_replaced
        cur_conclusion_node = next_conclusion_node
        cur_premise_nodes = next_premise_nodes
        cur_depth += 1

    return proof_tree


def update(premise_nodes: List[ProofNode],
           conclusion_node: ProofNode,
           argument: Argument,
           proof_tree: ProofTree):
    for premise_node in premise_nodes:
        conclusion_node.add_child(premise_node)
    conclusion_node.argument = argument
    for node in premise_nodes + [conclusion_node]:
        proof_tree.add_node(node)
