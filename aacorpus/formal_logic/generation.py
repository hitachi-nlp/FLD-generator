import random
import copy
from typing import List, Tuple, Optional, Iterable, Union
from aacorpus.formal_logic.formula import PREDICATE_POOL, CONSTANT_POOL
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
    is_satisfiable as is_formulas_satisfiable,
)
import logging
import kern_profiler

logger = logging.getLogger(__name__)

_NG_FORMULAS = [
    Formula('(x): Fx -> Fx'),
    Formula('(Ex): Fx -> Fx'),
]


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

    def depth_first_traverse(self,
                             start_node: Optional[ProofNode] = None,
                             depth=0,
                             get_depth=False) -> Iterable[Union[ProofNode, Tuple[ProofNode, int]]]:
        start_node = start_node or self.root_node
        for child_node in start_node.children:
            yield from self.depth_first_traverse(start_node=child_node, depth=depth + 1, get_depth=get_depth)
        yield (start_node, depth) if get_depth else start_node

    def __repr__(self):
        return 'ProofTree(...)'

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


@profile
def generate_tree(arguments: List[Argument], depth=1) -> ProofTree:
    proof_tree = _generate_stem(arguments, depth, PREDICATE_POOL, CONSTANT_POOL)
    _extend_braches(proof_tree, arguments, depth, PREDICATE_POOL, CONSTANT_POOL)
    return proof_tree


@profile
def _generate_stem(arguments: List[Argument],
                   depth: int,
                   predicate_pool: List[str],
                   constant_pool: List[str],
                   max_retry=30):

    def update(premise_nodes: List[ProofNode],
               conclusion_node: ProofNode,
               argument: Argument,
               proof_tree: ProofTree):
        for premise_node in premise_nodes:
            conclusion_node.add_child(premise_node)
        conclusion_node.argument = argument
        for node in premise_nodes + [conclusion_node]:
            proof_tree.add_node(node)

    proof_tree = ProofTree()
    cur_arg = random.choice(arguments)
    cur_conclusion_node = ProofNode(cur_arg.conclusion)
    cur_premise_nodes = [ProofNode(premise) for premise in cur_arg.premises]
    update(cur_premise_nodes, cur_conclusion_node, cur_arg, proof_tree)

    cur_depth = 0
    retry = 0
    while True:
        if retry >= max_retry:
            logger.warning('Exit since retry exceeded max_retry(%d)', max_retry)
            break

        if cur_depth >= depth:
            break

        cur_conclusion = cur_conclusion_node.formula

        # Choose next argument
        chainable_args = [
            arg for arg in arguments
            if any([premise_replaced.rep == cur_conclusion.rep
                    for premise in arg.premises
                    for premise_replaced, _ in generate_replaced_formulas(premise, cur_conclusion)])
        ]
        next_arg_unreplaced = random.choice(chainable_args)

        # Choose mapping
        mappings = list(
            generate_replacement_mappings_from_formula(
                next_arg_unreplaced.premises + [next_arg_unreplaced.conclusion],
                [cur_conclusion] + [Formula(' '.join(constant_pool)), Formula(' '.join(predicate_pool))]
            )
        )
        is_proper_mapping = False
        for mapping in random.sample(mappings, len(mappings)):
            next_arg_replaced = replace_argument(next_arg_unreplaced, mapping)
            if all([premise.rep != cur_conclusion.rep
                    for premise in next_arg_replaced.premises]):
                continue

            if _has_ng_premises(next_arg_replaced):
                continue

            if len(_get_premises_already_in_tree(next_arg_replaced, proof_tree)) >= 2:  # 1 for the chained promise:
                continue

            if not _is_satisfiable(next_arg_replaced, proof_tree):
                continue

            if not _new_formula_is_deduced(next_arg_replaced, proof_tree):
                continue

            is_proper_mapping = True
            break

        if not is_proper_mapping:
            logger.info('Retry since proper mapping could not be chosen...')
            continue

        # Update tree
        next_conclusion_node = ProofNode(next_arg_replaced.conclusion)
        next_conclusion_node.argument = next_arg_replaced
        next_premise_nodes = [
            cur_conclusion_node if premise.rep == cur_conclusion.rep else ProofNode(premise)
            for premise in next_arg_replaced.premises
        ]
        update(next_premise_nodes, next_conclusion_node, next_arg_replaced, proof_tree)

        cur_arg = next_arg_replaced
        cur_conclusion_node = next_conclusion_node
        cur_premise_nodes = next_premise_nodes
        cur_depth += 1

    return proof_tree


@profile
def _extend_braches(proof_tree: ProofTree,
                    arguments: List[Argument],
                    steps: int,
                    predicate_pool: List[str],
                    constant_pool: List[str],
                    max_retry=30):
    cur_step = 0
    retry = 0
    while True:
        if retry >= max_retry:
            logger.warning('Exit since retry exceeded max_retry(%d)', max_retry)
            break
        retry += 1

        if cur_step >= steps:
            break

        leaves = proof_tree.leaf_nodes
        leaf_node = random.choice(leaves)

        # Choose next argument
        chainable_args = [
            arg for arg in arguments
            if any([conclsion_replaced.rep == leaf_node.formula.rep
                    for conclsion_replaced, _ in generate_replaced_formulas(arg.conclusion, leaf_node.formula)])
        ]
        if len(chainable_args) == 0:
            continue
        next_arg_unreplaced = random.choice(chainable_args)

        # Choose mapping
        # The following two nested loop is for speedup:
        # 1. First, we generate the small number of mappings by using small number of symbols. Then, we find appropriate sub-mappings
        # 2. Second, we generate full number of mappings, using the sub-mappings as filters.
        is_proper_mapping = False
        for conclusion_mapping in generate_replacement_mappings_from_formula([next_arg_unreplaced.conclusion],
                                                                             [leaf_node.formula] + [Formula(' '.join(constant_pool + predicate_pool))],
                                                                             shuffle=True):
            conclusion_replaced = replace_formula(next_arg_unreplaced.conclusion, conclusion_mapping)
            if conclusion_replaced.rep != leaf_node.formula.rep:
                continue

            for mapping in generate_replacement_mappings_from_formula(
                next_arg_unreplaced.all_formulas,
                [leaf_node.formula] + [Formula(' '.join(constant_pool + predicate_pool))],
                constraints=conclusion_mapping,
                shuffle=True,
            ):
                next_arg_replaced = replace_argument(next_arg_unreplaced, mapping)
                if next_arg_replaced.conclusion.rep != leaf_node.formula.rep:
                    raise Exception()

                if _has_ng_premises(next_arg_replaced):
                    continue

                if len(_get_premises_already_in_tree(next_arg_replaced, proof_tree)) >= 1:
                    continue

                if not _is_satisfiable(next_arg_replaced, proof_tree):
                    continue

                is_proper_mapping = True
                break
            
            if is_proper_mapping:
                break

        if not is_proper_mapping:
            logger.info('Retry since proper mapping could not be chosen...')

        # Upate tree
        leaf_node.argument = next_arg_replaced
        next_premise_nodes = [ProofNode(premise)
                              for premise in next_arg_replaced.premises]
        for premise_node in next_premise_nodes:
            proof_tree.add_node(premise_node)
            leaf_node.add_child(premise_node)
        cur_step += 1


def _has_ng_premises(arg: Argument) -> bool:
    return any([
        ng_formula_replaced.rep == premise.rep
        for premise in arg.premises
        for ng_formula in _NG_FORMULAS
        for ng_formula_replaced, _ in generate_replaced_formulas(ng_formula, premise)
    ])


def _get_premises_already_in_tree(arg: Argument, proof_tree: ProofTree) -> List[Formula]:
    return [
        premise
        for existent_node in proof_tree.nodes
        for premise in arg.premises
        if premise.rep == existent_node.formula.rep
    ]


def _is_satisfiable(arg: Argument, proof_tree: ProofTree) -> bool:
    return is_formulas_satisfiable([node.formula for node in proof_tree.nodes]
                                   + arg.premises
                                   + [arg.conclusion])


def _new_formula_is_deduced(arg: Argument, proof_tree: ProofTree) -> bool:
    return all([
        arg.conclusion.rep != node.formula.rep
        for node in proof_tree.nodes
    ])
