"""Validates BiomassCompounds and Reactions files in Templates folder"""

from csv import DictReader
import os
import sys
import argparse


def get_id_set(tsv_path):
    with open(tsv_path) as infile:
        ids = set()
        for line in DictReader(infile, dialect='excel-tab'):
            #if 'is_obsolete' in line and int(line['is_obsolete']):
            #    continue
            if 'status' in line and ("MI:C" in line['status']):
                continue
            ids.add(line['id'])
    return ids


def validate_biomass_compounds(path, comp_set):
    with open(path) as infile:
        template_compounds = set()
        for line in DictReader(infile, dialect='excel-tab'):
            template_compounds.add(line['id'])
            if line['linked_compounds'] == 'null':
                continue
            template_compounds.update([x.split(':')[0] for x
                                       in line['linked_compounds'].split('|')])
        return template_compounds - comp_set


def validate_reaction_list(path, rxn_set, complex_set):
    with open(path) as infile:
        template_rxns = set()
        template_complexes = set()
        for line in DictReader(infile, dialect='excel-tab'):
            template_rxns.add(line['id'])
            template_complexes.update(line['complexes'].strip().split("|"))
        return template_rxns - rxn_set, template_complexes - complex_set

if __name__ == '__main__':
    script_dir = os.path.dirname(__file__)
    parser = argparse.ArgumentParser(
        description='Validates BiomassCompounds and Reactions files in Templates folder')
    parser.add_argument('-c', dest='comp_tsv',
                        default=script_dir+'/../../Biochemistry/compounds.tsv',
                        help='Path to the compounds file')
    parser.add_argument('-r', dest='rxn_tsv',
                        default=script_dir+'/../../Biochemistry/reactions.tsv',
                        help='Path to the reaction file')
    parser.add_argument('-C', dest='complex_tsv',
                        default=script_dir+'/../../Annotations/Complexes.tsv',
                        help='Path to the complexes file')
    parser.add_argument('-t', dest='template_dir',
                        default=script_dir+'/../../Templates',
                        help='Path to the templates directory')
    args = parser.parse_args()
    comp_ids = get_id_set(args.comp_tsv)
    rxn_ids = get_id_set(args.rxn_tsv)
    complex_ids = get_id_set(args.complex_tsv) | {'universal', 'null'}
    exit_code = 0
    for template in os.listdir(args.template_dir):
        if not os.path.isdir(os.path.join(args.template_dir, template)):
            continue
        print("Validating %s template" % template)
        undef_comps = validate_biomass_compounds(
            '%s/%s/BiomassCompounds.tsv' % (args.template_dir, template),
            comp_ids)
        undef_rxns, undef_complex = validate_reaction_list(
            '%s/%s/Reactions.tsv' % (args.template_dir, template), rxn_ids,
            complex_ids)

        if undef_comps:
            print("ERROR-%s Invalid Compounds: %s"
                  % (len(undef_comps), ", ".join(undef_comps)))
            exit_code = 1
        if undef_rxns:
            print("ERROR-%s Invalid Reactions: %s"
                  % (len(undef_rxns), ", ".join(undef_rxns)))
            exit_code = 1
        if undef_complex:
            print("ERROR-%s Invalid Complexes: %s"
                  % (len(undef_complex), ", ".join(undef_complex)))
            exit_code = 1

    exit(exit_code)
