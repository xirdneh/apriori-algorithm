#! /usr/bin/env python2.7
from sys import argv
from operator import itemgetter
import urllib2
import csv

def print_list(list):
    for l in list:
        print "[ {0} ]".format(l)

def print_support(support):
    for s in support:
        print "[ {0} = {1} ]".format(s, support[s])

def print_freq_items(sets, support):
    for ss in sets:
        for s in ss:
            print "Frequent set: {{ {0} }}, support: {1:.2f}".format(",".join(s), support[s])

def print_freq_items_tofile(sets, support):
    f = open('mfis.txt', 'w')
    for ss in sets:
        for s in ss:
            f.write("Frequent set: {{ {0} }}, support: {1:.2f}\n".format(",".join(s), support[s]))
    f.close()

def print_rules(rules):
    for rule in rules:
        print "{{ {0} }} --> {{ {1} }}, conf: {2:.2f}".format(",".join(rule[0]), ",".join(rule[1]), rule[2])

def print_rules_tofile(rules):
    f = open('topar.txt', 'w')
    for rule in rules:
        f.write("{{ {0} }} --> {{ {1} }}, conf: {2:.2f} \n".format(",".join(rule[0]), ",".join(rule[1]), rule[2]))
    f.close()

def apriori(data, min_sup=0.3):
    single_candidates = get_single_candidates(data)
    #print "Single Candidates" #DEBUG
    #print_list(single_candidates) #DEBUG
    datasets = map(set, data)
    frequent_singles, sup_cnts = prune_by_support(datasets, single_candidates, min_sup)
    #print "Freq Item Sets" #DEBUG
    #print_list(frequent_singles) #DEBUG
    #print "Supports " #DEBUG
    #print_support(sup_cnts) #DEBUG
    frequent_sets = []
    frequent_sets.append(frequent_singles)
    k = 0
    while(len(frequent_sets[k]) > 0):
        candidates = get_candidates(frequent_sets[k])
        #print "{0} iter".format(k) #DEBUG
        #print "Candidates: " #DEBUG
        #print_list(candidates) #DEBUG
        freq_k_sets, sup_k_cnts = prune_by_support(datasets, candidates, min_sup)
        #print "Freq Sets:" #DEBUG
        #print_list(freq_k_sets) #DEBUG
        #print "Supports: " #DEBUG
        #print_support(sup_k_cnts) #DEBUG
        sup_cnts.update(sup_k_cnts)
        frequent_sets.append(freq_k_sets)
        k += 1
    return frequent_sets, sup_cnts

def get_single_candidates(dataset):
    single_candidates = []
    for transaction in dataset:
        for item in transaction:
            c = [item]
            if not c in single_candidates:
                single_candidates.append(c)

    single_candidates.sort()
    return map(frozenset, single_candidates)

def get_candidates(frequent_sets):
    ret_frequent = []
    freq_len = len(frequent_sets)
    #print "get_candidates : freq_sets = {0}, len = {1}".format(frequent_sets, freq_len)
    for i in range(freq_len):
        for j in range(i+1, freq_len):
            fli = list(frequent_sets[i])
            fli.sort()
            #print "fli: {0}, {1}".format(fli, i)
            flj = list(frequent_sets[j])
            flj.sort()
            #print "flj: {0}, {1}".format(flj, j)
            if (len(fli) < 2):
                fsi = fli[0]
                fsj = flj[0]
                #print "fsi == fsj : {0} == {1}".format(fsi, fsj)
                ret_frequent.append(frequent_sets[i] | frequent_sets[j])
            else:
                fsi = fli[:-1]
                fsj = flj[:-1]
                #print "fsi == fsj : {0} == {1}".format(fsi, fsj)
                if fsi == fsj:
                    ret_frequent.append(frequent_sets[i] | frequent_sets[j])
    return ret_frequent

def prune_by_support(datasets, candidates, min_sup):
    items_cnts = {}
    data_len = float(len(datasets))
    prunned_items = []
    support_cnts = {}
    for transaction in datasets:
        for candidate in candidates:
            if candidate.issubset(transaction):
                items_cnts.setdefault(candidate, 0)
                items_cnts[candidate] += 1

    for candidate_set in items_cnts:
        support = items_cnts[candidate_set] / data_len
        if support >= min_sup:
            prunned_items.append(candidate_set)
        support_cnts[candidate_set] = support

    return prunned_items, support_cnts

def generate_rules(f_set, Hm, sup_cnts, min_conf):
    k = len(f_set)
    m = len(Hm[0])
    ret = []
    if (k > m + 1):
        Hm1 = get_candidates(Hm)
        Hm1 = prune_by_confidence(f_set, Hm1, sup_cnts, min_conf)
        ret = ret + Hm1
        if len(Hm1) > 1:
            generate_rules(f_set, Hm1, sup_cnts, min_conf)
    return ret

def prune_by_confidence(f_set, H, sup_cnts, min_conf):
    ret = []
    for consequence in H:
        rule = f_set - consequence
        confidence = sup_cnts[f_set] / sup_cnts[rule]
        if confidence > min_conf:
            ret.append((rule, consequence, confidence))
    return ret
    

def get_rules(f, sup_cnts, min_conf = 0.6):
    rules = []
    for i in range(1, len(f)):
        for f_set in f[i]:
            Hm = [frozenset([itemset]) for itemset in f_set]
            if (i == 1):
                rules_set = prune_by_confidence(f_set, Hm, sup_cnts, min_conf)
                rules = rules + rules_set
            else:
                rules_set = generate_rules(f_set, Hm, sup_cnts, min_conf)
                rules = rules + rules_set
    return rules

def get_data_from_url(url):
    response = urllib2.urlopen(url)
    cr = csv.reader(response)
    return cr

def get_data_from_file(file_name):
    file_data = []
    with open(file_name, 'rb') as csvfile:
        data = csv.reader(csvfile)
        file_data = data
    return file_data

def transform_data(data):
    ret = []
    transformer = [
                    {'democrat':'Democrat', 'republican':'Republican'},
                    {'y': 'Handicapped Infants', 'n': 'Not Handicapped Infants', '?':'HI N/A'},
                    {'y': 'Water Project Cost Sharing', 'n': 'Not Water Project Cost Sharing', '?':' WPCS N/A'},
                    {'y': 'Adoption of the Budget Resolution', 'n':'Not Adoption of the Budget Resolution', '?':'ABR N/A'},
                    {'y': 'Physician Fee Freeze', 'n':'Not Physician Fee Freeze', '?':'PFF N/A'},
                    {'y': 'El Salvador Aid', 'n':'Not El Salvador Aid', '?':'ESA N/A'},
                    {'y': 'Religious Groups in Schools', 'n':'Not Religious Groups in Schools', '?':'RGS N/A'},
                    {'y': 'Anti Satellite Test Band', 'n':'Not Anty Satellite Test Band', '?':'ASTB N/A'},
                    {'y': 'Aid to Nicaraguan Contras', 'n':'Not Aid to Nicaraguan Contras', '?':'ANC N/A'},
                    {'y': 'MX Missile', 'n': 'Not MX Missile', '?':'MXM N/A'},
                    {'y': 'Immigration', 'n': 'Not Immigration', '?':'IM N/A'},
                    {'y': 'Synfuels Corporation Cutback', 'n':'Not Synfuel Corporatino Cutback', '?': 'SCC N/A'},
                    {'y': 'Education Spending', 'n': 'Education Spending', '?': 'ES N/A'},
                    {'y': 'Superfund Right to Sue', 'n':'Not Superfund Right to Sue', '?' :'SRS N/A'},
                    {'y': 'Crime', 'n':'Not Crime', '?': 'CR N/A'},
                    {'y': 'Duty Free Exports', 'n': 'Not Duty Free Exports', '?':'DFE N/A'},
                    {'y': 'Export Administration Act South Africa', 'n': 'Not Export Administration Act South Africa', '?':'EAASA N/A'}

                ]
    for d in data:
        ret.append(
                    [
                        transformer[0][d[0]],
                        transformer[1][d[1]],
                        transformer[2][d[2]],
                        transformer[3][d[3]],
                        transformer[4][d[4]],
                        transformer[5][d[5]],
                        transformer[6][d[6]],
                        transformer[7][d[7]],
                        transformer[8][d[8]],
                        transformer[9][d[9]],
                        transformer[10][d[10]],
                        transformer[11][d[11]],
                        transformer[12][d[12]],
                        transformer[13][d[13]],
                        transformer[14][d[14]],
                        transformer[15][d[15]],
                        transformer[16][d[16]]
                    ]
                   )
    return ret

if __name__ == '__main__':
    args = argv[1:]
    if len(args) > 0:
        if (args[0] != 'url'):
            data_str = args[0]
            i = data_str.find('//')
            if i > 1:
                url = args[0]
                data = get_data_from_url(url)
            elif (data_str.find('.csv') == (len(data_str) - 4)):
                file_name = args[0]
                data = get_data_from_file(file_name)
            else:
                print "I only know how to read data from an URI or a CSV file"

        else:
            url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/voting-records/house-votes-84.data'
            data = get_data_from_url(url)
        data = transform_data(data)
    else:
        print "Using test data"
        data = [
                        ['Bread', 'Milk'],
                        ['Bread', 'Diapers', 'Beer', 'Eggs'],
                        ['Milk', 'Diapers', 'Beer', 'Coke'],
                        ['Bread', 'Milk', 'Diapers', 'Beer'],
                        ['Bread', 'Milk', 'Diapers', 'Coke']
                    ]
    if len(args) >= 3:
        min_sup = int(args[1])
        min_conf = int(args[2])

    else:
        min_sup = .3
        min_conf = .6

    frequent_sets, sup_cnts = apriori(data, min_sup)
    frequent_sets = frequent_sets[:-1]
    print "Final Frequent Sets:"
    #print_list(frequent_sets)
    #print_support(sup_cnts)
    print_freq_items_tofile(frequent_sets, sup_cnts)
    rules = get_rules(frequent_sets, sup_cnts, min_conf)
    print "Rules: "
    rules.sort(key = itemgetter(2))
    print_rules_tofile(rules)
